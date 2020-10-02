# import Master as M
import Tag_Database as Tags
import numpy as np
import matplotlib.pyplot as plt
import time

Client = M.Make_Client("10.50.0.10")
M.Read(Client, Tags.WF1H) #Arbitrary read to establish trust (I think this part is weird to me)

V0_resolution = 0.01 #Resolution of steps taken in both cutoff measurements
Num_sawtooths_1 = 20 #number of points taken in the first cutoff
Num_sawtooths_2 = 20 #second cutoff


################################################################
### Grab the operator input of V0 ranges #######################
################################################################

V0_1 = float(input("V0 Setpoint 1  "))
V0_2 = float(input("V0 Setpoint 2  "))
V0_3 = float(input("V0 Setpoint 3  "))
V0_4 = float(input("V0 Setpoint 4  "))

################################################################
### List of tags to read at every step #########################
################################################################

Tag_List = [[Tags.CU_Pf, False], [Tags.CU_Pr, False], [Tags.CU_Pt, False], [Tags.CU_V, False], \
            [Tags.BH_Pf, False], [Tags.BH_Pr, False], [Tags.BH_Pt, False], \
            [Tags.HV_Bias, False], [Tags.V0_SP, False], [Tags.V0_Read, False], \
            [Tags.Gun_Vac, False], [Tags.IR_Temp, False], [Tags.VA_Temp, False], [Tags.Heater_Amps_Set, False], \
            [Tags.Temperature_Set, False], [Tags.Emission_Set, False], [Tags.Voltage_Read, False], \
            [Tags.Current_Read, False], [Tags.Impedance_Read, False], [Tags.Power_Read, False]]

Full_Data_Set = list()

################################################################
### Set up the lists to run and then run the loop ##############
################################################################
V0_List_1 = np.arange(V0_1, V0_2 + V0_resolution, V0_resolution)
V0_List_2 = np.arange(V0_3, V0_4 + V0_resolution, V0_resolution)

sleep_time = 0 #Don't sleep on the first pass through

for index in range(Num_sawtooths_1): #First loop with V0_1 and V0_2
    
    time.sleep(sleep_time)
    
    if not index:
        start_time = time.time()
        
    for value in V0_List_1:
        M.Write(Client, Tags.V0_SP, value)
        Full_Data_Set.append(M.Gather(Client, Tag_List))
    
    if not index:
        sleep_time = time.time() - start_time
        
    time.sleep(sleep_time)
    
    for value in V0_List_1[::-1]:
        M.Write(Client, Tags.V0_SP, value)
        Full_Data_Set.append(M.Gather(Client, Tag_List))
        
################################################################
### Cutoff 1 done. Now turning off BH and taking cutoff 2 ######
################################################################
    
M.Write(Client, Tags.BH_VVA_SP, 0)

for index in range(Num_sawtooths_2):
    
    #Maybe maybe maybe maybe
    if not index:
        start_time = time.time()
        
    for value in V0_List_2:
        M.Write(Client, Tags.V0_SP, value)
        Full_Data_Set.append(M.Gather(Client, Tag_List))
    
    #Maybe maybe maybe maybe
    if not index:
        sleep_time = time.time() - start_time
        
    time.sleep(sleep_time)
    
    for value in V0_List_2[::-1]:
        M.Write(Client, Tags.V0_SP, value)
        Full_Data_Set.append(M.Gather(Client, Tag_List))

        
################################################################
### All measurements done. Now it's just storing the data
################################################################

with open("Testing_Cutoffs.txt",'w') as f: 
    for line in Full_Data_Set:
        f.write(str(line).strip("([])")+'\n') #Writing each line in that file
    f.close() #Closing the file to save it
    
    Full_Data_Array = np.array(Full_Data_Set) #Converting from a list to an array