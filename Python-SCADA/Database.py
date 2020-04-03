import time
import numpy as np
from Tag_Database import *
import Master as M

# Parameters
txt_file_length = 10000

#############################################
# Don't touch it
#############################################

Vacuums = [Gun_Vac, Gun_Cross, SRF_Cavity_Vac, HE_Sraight_Vac, 
           Insulating_Vac, E_Station_Vac]

Temps = [BH_OC_Temp, DBA_Pipe_Temp, Cu_Gun_Temp, HE_Straight_Col, 
         DBA_Dump_CHWR, DBA_Dump_CHWS, Tuner_Plate_Temp, 
         Gate_Valve_Downstream_Temp, Gate_Valve_Upstream_Temp, 
         Loop_Bypass_CHWS, Loop_Bypass_CHWR, DBA_Coupler, 
         Coupler_Shoulder, Solenoid_4_Temp, Solenoid_5_Temp]

DST_Conversion = 3
if time.localtime().tm_isdst == 1:
    DST_Conversion = 4
    
Client = M.Make_Client("192.168.1.6")

while True:

    temp_list = [time.time()*10**3-DST_Conversion*60*60*1000]
    
    for Tag in Vacuums:
        temp_list.append(M.Read(Client,Tag))
    for Tag in Temps:
        temp_list.append(M.Read(Client,Tag))
    
    file = open("Data.txt",'a')
    file.write(str(temp_list).strip("[]")+"\n")
    #file.write(str(temp_list).strip("[]")+"\n")
    file.close()
    #mid_loop_time = time.time()
    with open("Data.txt", "r+") as file:
        contents = file.readlines()
        #print(np.shape(contents)[0])
        if np.shape(contents)[0] > txt_file_length:
            file.seek(0)
            for num,j in enumerate(contents):
                if num != 1:
                    file.write(j)
            file.truncate()
    file.close()