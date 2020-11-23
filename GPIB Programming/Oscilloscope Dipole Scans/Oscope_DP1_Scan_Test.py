import GPIB_FUNCS as GPIB #Importing our GPIB communication functions for easier comprehension and use
import pyvisa #import GPIB communication module
import time #imports time to sleep program temporarily
import Workhorse as Horse
import numpy as np
import Tag_Database as Tags
from datetime import datetime
import os

RM = pyvisa.ResourceManager() #pyVISA device manager
Resources = RM.list_resources() #Printing out all detected device IDs
print(Resources)
try:
    SG = RM.open_resource(Resources[0]) #Opening the Signal generator as an object
    OS = RM.open_resource(Resources[1]) #Opening the oscilloscope as an object
    
    Start_Freq = float(SG.query("FREQ:CW?"))
    print("Starting Frequency of Signal Generator: {} Hz".format(Start_Freq))
except:
    SG = RM.open_resource(Resources[1]) #Opening the Signal generator as an object
    OS = RM.open_resource(Resources[0]) #Opening the oscilloscope as an object
    
    Start_Freq = float(SG.query("FREQ:CW?"))
    print("Starting Frequency of Signal Generator: {} Hz".format(Start_Freq))

Client = Horse.Make_Client('10.50.0.10')


End_Value = float(input("What is the ending amperage that you want to ramp the magnet to? (Amps)   "))

#Grabbing all of our data for the system snapshot
#################################################
Pulsing_Status = bool(Horse.Read(Client, Tags.Pulsing_Output, Bool = True))
Emission_Setpoint = Horse.Read(Client, Tags.Emission_Set)

if Pulsing_Status:
    Emission_Actual = Horse.Read(Client, Tags.Emitted_Current, Average = True, count = 50, sleep_time = 0.010)
else:
    Emission_Actual = Horse.Read(Client, Tags.Emitted_Current, Average = True, count = 20, sleep_time = 0.010)
    
IR_Temp = Horse.Read(Client, Tags.IR_Temp)
VA_Temp = Horse.Read(Client, Tags.VA_Temp)
V0_Setpoint = Horse.Read(Client, Tags.V0_SP)
V0_Read = Horse.Read(Client, Tags.V0_Read)
Cathode_V = Horse.Read(Client, Tags.Voltage_Read)
Cathode_I = Horse.Read(Client, Tags.Current_Read)
Cathode_Z = Horse.Read(Client, Tags.Impedance_Read)
Cathode_P = Horse.Read(Client, Tags.Power_Read)
CU_Gun_Pf = Horse.Read(Client, Tags.CU_Pf)
CU_Gun_Pr = Horse.Read(Client, Tags.CU_Pr)
CU_Gun_Pt = Horse.Read(Client, Tags.CU_Pt)
CU_Gun_V = Horse.Read(Client, Tags.CU_V)
BH_Gun_Pf = Horse.Read(Client, Tags.BH_Pf)
BH_Gun_Pr = Horse.Read(Client, Tags.BH_Pr)
BH_Gun_Pt = Horse.Read(Client, Tags.BH_Pt)
SRF_Pf = Horse.Read(Client, Tags.SRF_Pf)
SRF_Pr = Horse.Read(Client, Tags.SRF_Pr)
SRF_Pt = Horse.Read(Client, Tags.SRF_Pt)
Pulse_Freq = Horse.Read(Client, Tags.Pulse_Frequency)
Pulse_Duty = Horse.Read(Client, Tags.Pulse_Duty)

Threshold_Percent = 0.1

#Uncomment to make variable number of runs
#Runs = int(input("How many runs do you want the Dipole to make?   "))

Runs = 1 #Number of times you want to ramp to the input value and back to the start
Dipole_Tag = Tags.DP1 #Modbus address of the magnet we are writing to
Step_size = .001 #Step Size, in Amps, that we are taking to reach our goal
Read = Tags.DBA_Bypass #Modbus address of the value we want to Read while we scan the magnet
count = 20 #Number of times we want to average the Read Tag value
pulsing_count = 50 #number of times we want to average the Read Tag value if pulsing

Start_Value = Horse.Read(Client, Dipole_Tag) #Recording the starting value of the Dipole
print("Started at {0:.3f} Amps".format(Start_Value))

DP1_Values = list()
DBA_Collection = list()
colors = list()
Oscope_Data = list()

print("Beginning Scan")
for i in range(Runs):
    print("Going to target value")
    
    if Pulsing_Status:
        DP1_Vals, DBA_Col = Horse.Ramp_One_Way(Client, Dipole_Tag, End_Value, Max_Step = Step_size, Return = "Y", Read_Tag = Read, count = pulsing_count)
        Oscope_Data.append(GPIB.cursor_vbar_read_mv(OS))
    else:
        DP1_Vals, DBA_Col = Horse.Ramp_One_Way(Client, Dipole_Tag, End_Value, Max_Step = Step_size, Return = "Y", Read_Tag = Read, count = count)
        Oscope_Data.append(GPIB.cursor_vbar_read_mv(OS))
        #The above function walks the magnet to the endpoint ,and returns the data
    
    DP1_Values += DP1_Vals #Adding the recorded data to the lists
    DBA_Collection += DBA_Col 
    
    
    colors += ['chocolate' for i in list(range(len(DP1_Vals)))] #Appending 'chocolate' as the color for this data set
    
    print("Going to start")
    
    if Pulsing_Status:
        DP1_Vals, DBA_Col = Horse.Ramp_One_Way(Client, Dipole_Tag, Start_Value, Max_Step = Step_size, Return = "Y", Read_Tag = Read, count = pulsing_count)
    else:
        DP1_Vals, DBA_Col = Horse.Ramp_One_Way(Client, Dipole_Tag, Start_Value, Max_Step = Step_size, Return = "Y", Read_Tag = Read, count = count)
    #The above statement walks us back to the start, and returns the data
    
    DP1_Values += DP1_Vals
    DBA_Collection += DBA_Col

    colors += ['firebrick' for i in list(range(len(DP1_Vals)))] #Appending 'firebrick' as the color for this data set
    
    
DP1_Values = np.array(DP1_Values)
DBA_Collection = np.array(DBA_Collection)
Oscope_List = np.array(Oscope_Data)

#Converting into millimeters
x_mindex = 1 + np.where(DBA_Collection == min(DBA_Collection[:len(DBA_Collection)//(Runs*2)]))[0][0] #Gathering the peak point

x_maxdex = 0
for max_value_index, value in enumerate(Oscope_List):
    if abs(value) > (Threshold_Percent * max(abs(Oscope_List))):
        x_maxdex = max_value_index
        break


mms = (max(DP1_Values[x_maxdex:x_mindex]) - DP1_Values[x_maxdex:x_mindex])/\
    (max(DP1_Values[x_maxdex:x_mindex]) - min(DP1_Values[x_maxdex:x_mindex]))*10

Percent_Collection = abs(Oscope_List/Emission_Setpoint)*100

for iteration in range(x_maxdex):
    mms = np.insert(mms, 0, None)

while len(DP1_Values) > len(mms):
    mms = np.append(mms, None)

now = datetime.today().strftime('%y%m%d_%H%M') #Grabbing the time and date in a common format to save the plot and txt file to
Emission_String = str(int(abs(Emission_Actual)*1000))
V0_String = str(round(V0_Setpoint,2)).replace('.', '_')

plt.figure(figsize = (12,8))
plt.scatter(DP1_Values,Oscope_List,color = colors, alpha = 0.5)

plt.grid(True,alpha = 0.25,which = 'both',color = 'gray') #Making a grid
plt.minorticks_on() #Setting the minor ticks

#Naming
plt.ylabel("DBA current collected (mV)")
plt.xlabel("Magnet Setting (A)")
plt.title("Dipole 1 current collected over walk from {0:.3f}A to {1:.3f}A".format(Start_Value, End_Value, Emission_Actual))
plt.suptitle("Orange = Ascending, Red = Descending",fontsize = 8, alpha = 0.65)

plt.gca().invert_xaxis()
plt.gca().invert_yaxis()

plt.savefig(now + '_V0_' + V0_String + '_' + '_graph.png', dpi = 450, trasnparent = True) #Saving to the time and date as png

save_list = np.array([DP1_Values, DBA_Collection, Percent_Collection, mms, Oscope_List])

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
    f.write("Raw DP1(Amps), Raw Collection(mA), Percent Collection , Conversion to mms, Oscope Reading(mV)" + '\n')
    for row in range(len(save_list[0,:])):
        for column in range(len(save_list[:,0])):
            f.write(str(save_list[column,row]) + ', ')
        f.write('\n')
    f.close()
plt.show()
exit()
