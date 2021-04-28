''' Creator: Austin Czyzewski

Date Created: 11/20/2020
Date Last Updated: 
Tested and Approved: 

Purpose: Move the first dipole up and down while taking data of collected current

Route: Gather user input for changes to dipole 1 to be made
    - Take a system snapshot before the scan
    - Define the parameters of data gathering
    - Read the value, perform safety checks
    - Write new Dipole one setting
    - Read Collected current
    - Repeat in ascending order
    - Repeat in descending order until reaching starting value
    - Plot
    - Save plot and txt file w/ snapshot as header

Changes from V3:
    Adding a config file for easier version control
    Adding config file confirmations
    Adding a system snapshot
'''

import matplotlib.pyplot as plt
from datetime import datetime
import time
import numpy as np
#import Master as M

import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, '..\\')

import Master as M
import Tag_Database_West as Tags


Tunnel, PLC_IP, Threshold_Percent, Runs, Step_Size, count, pulsing_count, Oscope = M.config_reader('dp1_scan_config.txt', "Dipole Scan")

print(Tunnel, PLC_IP, Threshold_Percent, Runs, Step_Size, count, pulsing_count, Oscope)

Client = M.Make_Client(PLC_IP)


End_Value = float(input("What is the ending amperage that you want to ramp the magnet to? (Amps)   "))

#Grabbing all of our data for the system snapshot
#################################################
Pulsing_Status = bool(M.Read(Client, Tags.Pulsing_Output, Bool = True))
Emission_Setpoint = M.Read(Client, Tags.Emission_Set)

if Pulsing_Status:
    Emission_Actual = M.Read(Client, Tags.Emitted_Current, Average = True, count = pulsing_count, sleep_time = 0.025)
else:
    Emission_Actual = M.Read(Client, Tags.Emitted_Current, Average = True, count = count, sleep_time = 0.010)

Dipole_Tag = Tags.DP1
    
IR_Temp = M.Read(Client, Tags.IR_Temp)
VA_Temp = M.Read(Client, Tags.VA_Temp)
V0_Setpoint = M.Read(Client, Tags.V0_SP)
V0_Read = M.Read(Client, Tags.V0_Read)
Cathode_V = M.Read(Client, Tags.Voltage_Read)
Cathode_I = M.Read(Client, Tags.Current_Read)
Cathode_Z = M.Read(Client, Tags.Impedance_Read)
Cathode_P = M.Read(Client, Tags.Power_Read)
CU_Gun_Pf = M.Read(Client, Tags.CU_Pf)
CU_Gun_Pr = M.Read(Client, Tags.CU_Pr)
CU_Gun_Pt = M.Read(Client, Tags.CU_Pt)
CU_Gun_V = M.Read(Client, Tags.CU_V)
BH_Gun_Pf = M.Read(Client, Tags.BH_Pf)
BH_Gun_Pr = M.Read(Client, Tags.BH_Pr)
BH_Gun_Pt = M.Read(Client, Tags.BH_Pt)
SRF_Pf = M.Read(Client, Tags.SRF_Pf)
SRF_Pr = M.Read(Client, Tags.SRF_Pr)
SRF_Pt = M.Read(Client, Tags.SRF_Pt)
Pulse_Freq = M.Read(Client, Tags.Pulse_Frequency)
Pulse_Duty = M.Read(Client, Tags.Pulse_Duty)

Start_Value = M.Read(Client, Dipole_Tag) #Recording the starting value of the Dipole
print("Started at {0:.3f} Amps".format(Start_Value))

DP1_Values = []
DBA_Collection = []
colors = []

print("Beginning Scan")
for i in range(Runs):
    print("Going to target value")
    
    if Pulsing_Status:
        DP1_Vals, DBA_Col = M.Ramp_One_Way(Client, Dipole_Tag, End_Value, Max_Step = Step_size, Return = "Y", Read_Tag = Read, count = pulsing_count)
    else:
        DP1_Vals, DBA_Col = M.Ramp_One_Way(Client, Dipole_Tag, End_Value, Max_Step = Step_size, Return = "Y", Read_Tag = Read, count = count)
    #The above function walks the magnet to the endpoint ,and returns the data
    
    DP1_Values += DP1_Vals #Adding the recorded data to the lists
    DBA_Collection += DBA_Col 
    
    colors += ['chocolate' for i in list(range(len(DP1_Vals)))] #Appending 'chocolate' as the color for this data set
    
    print("Going to start")
    
    if Pulsing_Status:
        DP1_Vals, DBA_Col = M.Ramp_One_Way(Client, Dipole_Tag, Start_Value, Max_Step = Step_size, Return = "Y", Read_Tag = Read, count = pulsing_count)
    else:
        DP1_Vals, DBA_Col = M.Ramp_One_Way(Client, Dipole_Tag, Start_Value, Max_Step = Step_size, Return = "Y", Read_Tag = Read, count = count)
    #The above statement walks us back to the start, and returns the data
    
    DP1_Values += DP1_Vals
    DBA_Collection += DBA_Col

    colors += ['firebrick' for i in list(range(len(DP1_Vals)))] #Appending 'firebrick' as the color for this data set
    
    
DP1_Values = np.array(DP1_Values)
DBA_Collection = np.array(DBA_Collection)

#Converting into millimeters
x_mindex = np.where(DBA_Collection == min(DBA_Collection[:len(DBA_Collection//(Runs*2))]))[0][0] #Gathering the peak point
x_maxdex = np.argmin(abs(DBA_Collection) > Threshold_Percent * abs(min(DBA_Collection))) #First point higher than the threshold percent of collection

mms = (max(DP1_Values[x_maxdex:x_mindex]) - DP1_Values[x_maxdex:x_mindex])/\
    (max(DP1_Values[x_maxdex:x_mindex]) - min(DP1_Values[x_maxdex:x_mindex]))*10

Percent_Collection = abs(DBA_Collection/Emission_Setpoint)*100

for iteration in range(x_maxdex):
    mms = np.insert(mms, 0, None)

while len(DP1_Values) > len(mms):
    mms = np.append(mms, None)

now = datetime.today().strftime('%y%m%d_%H%M') #Grabbing the time and date in a common format to save the plot and txt file to
Emission_String = str(int(abs(Emission_Actual)*1000))
V0_String = str(round(V0_Setpoint,2)).replace('.', '_')

plt.figure(figsize = (12,8))
plt.scatter(DP1_Values,DBA_Collection,color = colors, alpha = 0.5)

plt.grid(True,alpha = 0.25,which = 'both',color = 'gray') #Making a grid
plt.minorticks_on() #Setting the minor ticks

#Naming
plt.ylabel("DBA current collected (mA)")
plt.xlabel("Magnet Setting (A)")
plt.title("Dipole 1 current collected over walk from {0:.3f} to {1:.3f}".format(Start_Value, End_Value))
plt.suptitle("Orange = Ascending, Red = Descending",fontsize = 8, alpha = 0.65)

plt.savefig(now + '_V0_' + V0_String + '_' +  Emission_String.zfill(4) + '_graph.png', dpi = 450, trasnparent = True) #Saving to the time and date as png

save_list = np.array([DP1_Values, DBA_Collection, Percent_Collection, mms])

with open(now + '_V0_' + V0_String + '_' +  Emission_String.zfill(4) + 'EC.txt', 'w') as f:
    f.write("EC_Setpoint: {:.4f}, EC_Read: {:.4f}, IR_Temp: {:.4f}, VA_Temp: {:.4f}".format(Emission_Setpoint, Emission_Actual, \
                                                    IR_Temp, VA_Temp) + '\n')
    f.write("V0_Set: {:.4f}, V0_Read {:.4f}, Pulse_Bool: {:.4f}, Rise_Threshold: {:.4f}".format(V0_Setpoint, V0_Read, \
                                                    Pulsing_Status, Threshold_Percent) + '\n')
    
    f.write("Cathode Voltage: {:.4f}, Cathode Current: {:.4f}, Cathode Impedance: {:.4f}, Cathode Power: {:.4f}".format(Cathode_V, Cathode_I, \
                                                    Cathode_Z, Cathode_P) + '\n')
    f.write("Cu Gun Pf: {:.4f}, Cu Gun Pr: {:.4f}, Cu Gun Pt: {:.4f}, Cu Gun V: {:.4f}".format(CU_Gun_Pf, CU_Gun_Pr, \
                                                    CU_Gun_Pt, CU_Gun_V) + '\n')
    f.write("BH Pf: {:.4f}, BH Pr: {:.4f}, BH Pt: {:.4f}, Pulse Frequency: {:.4f}".format(BH_Gun_Pf, BH_Gun_Pr, \
                                                    BH_Gun_Pt, Pulse_Freq) + '\n')
    f.write("SRF Pf: {:.4f}, SRF Pr: {:.4f}, SRF Pt: {:.4f}, Pulse Duty: {:.4f}".format(SRF_Pf, SRF_Pr, \
                                                    SRF_Pt, Pulse_Duty) + '\n')
    f.write("Raw DP1(Amps), Raw Collection(mA), Percent Collection , Conversion to mms" + '\n')
    for row in range(len(save_list[0,:])):
        for column in range(len(save_list[:,0])):
            f.write(str(save_list[column,row]) + ', ')
        f.write('\n')
    f.close()
plt.show()
exit()
