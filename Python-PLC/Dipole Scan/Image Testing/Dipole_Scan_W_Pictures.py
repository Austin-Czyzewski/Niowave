''' Creator: Austin Czyzewski

Date Created: 12/04/2019
Date Last Updated: 01/17/2020

Purpose: Move the first dipole up and down while taking data of collected current

Route: Gather user input for changes to dipole 1 to be made
    - Define the parameters of data gathering
    - Read the value, perform safety checks
    - Write new Dipole one setting
    - Read Collected current
    - Snap a picture
    - Repeat in ascending order
    - Repeat in descending order until reaching starting value
    - Plot
    - Save plot and txt file


Additions to configure CCD camera and acquire image
    - Need OpenCV python module
    - ImagingSource Python+OpenCV API
'''

import matplotlib.pyplot as plt
from datetime import datetime
import time
import numpy as np
import Master_Image as M
import Tag_Database as Tags
#Camera Imports:
import cv2
import tisgrabber as IC

Client = M.Make_Client('192.168.1.2')


End_Value = float(input("What is the ending amperage that you want to ramp the magnet to? (Amps)   "))

Emission_Setpoint = M.Read(Client, Tags.Emission_Set)
Emission_Actual = M.Read(Client, Tags.Emitted_Current, Average = True)
IR_Temp = M.Read(Client, Tags.IR_Temp)
VA_Temp = M.Read(Client, Tags.VA_Temp)
V0_Setpoint = M.Read(Client, Tags.V0_SP)
V0_Read = M.Read(Client, Tags.V0_Read)
Pulsing_Status = M.Read(Client, Tags.Output_Status)
Threshold_Percent = 0.05

#Uncomment to make variable number of runs
#Runs = int(input("How many runs do you want the Dipole to make?   "))

Runs = 1 #Number of times you want to ramp to the input value and back to the start
Dipole_Tag = Tags.DP1 #Modbus address of the magnet we are writing to
Step_size = .001 #Step Size, in Amps, that we are taking to reach our goal
Read = Tags.DBA_Bypass #Modbus address of the value we want to Read while we scan the magnet
count = 20 #Number of times we want to average the Read Tag value

Start_Value = M.Read(Client, Dipole_Tag) #Recording the starting value of the Dipole
print("Started at {0:.3f} Amps".format(Start_Value))

DP1_Values = []
DBA_Collection = []
colors = []

###############################################################################
###############################################################################
# Camera setup
resolution = '1920x1080'
def_exp, def_gain = 0.01, 480  # exp in units of sec, gain in units of 1/10 dB

# # Access CCD data and grab initial frame
# Camera = IC.TIS_CAM()
# Camera.ShowDeviceSelectionDialog() 

###############################################################################
# Access CCD data to get initial image
Camera = IC.TIS_CAM()
Camera.ShowDeviceSelectionDialog() 

if Camera.IsDevValid() == 1:
    
    # Set a video format
    temp = "RGB32 (" + resolution + ")"
    Camera.SetVideoFormat(temp); del temp
    Camera.SetPropertyAbsoluteValue("Exposure","Value", def_exp)
    Camera.SetPropertyValue("Gain","Value", def_gain)

    # Communicate with camera
    Camera.StartLive(1)
    
    # Initial image snap
    Camera.SnapImage()
    
    # Get image
    init_img = Camera.GetImage()
    init_img = cv2.flip(init_img, 0)
    init_img = cv2.cvtColor(init_img, cv2.COLOR_BGR2RGB)
    
else:
    Camera.StopLive()
    exit()

''' At this point we have successfully communicated with the camera. Camera is 
now actively in standby mode and can take image snapshot upon request.'''


###############################################################################
# Begin Dipole Scan
###############################################################################

print("Beginning Scan")
for i in range(Runs):
    print("Going to target value")
    DP1_Vals, DBA_Col = M.Ramp_One_Way(Client, Dipole_Tag, End_Value, Max_Step = Step_size, \
                                       Return = "Y", Read_Tag = Read, count = count, image = True)
    #The above function walks the magnet to the endpoint ,and returns the data
    
    DP1_Values += DP1_Vals #Adding the recorded data to the lists
    DBA_Collection += DBA_Col 
    
    colors += ['chocolate' for i in list(range(len(DP1_Vals)))] #Appending 'chocolate' as the color for this data set
    
    print("Going to start")
    DP1_Vals, DBA_Col = M.Ramp_One_Way(Client, Dipole_Tag, Start_Value, Max_Step = Step_size, Return = "Y", Read_Tag = Read, count = count)
    #The above statement walks us back to the start, and returns the data
    
    DP1_Values += DP1_Vals
    DBA_Collection += DBA_Col

    colors += ['firebrick' for i in list(range(len(DP1_Vals)))] #Appending 'firebrick' as the color for this data set
    
    
DP1_Values = np.array(DP1_Values)
DBA_Collection = np.array(DBA_Collection)

#Converting into millimeters
x_mindex = np.where(DBA_Collection == min(DBA_Collection[:len(DBA_Collection//2)]))[0][0] #Gathering the peak point
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
    f.write("Raw DP1(Amps), Raw Collection(mA), Percent Collection , Conversion to mms" + '\n')
    for row in range(len(save_list[0,:])):
        for column in range(len(save_list[:,0])):
            f.write(str(save_list[column,row]) + ', ')
        f.write('\n')
    f.close()
plt.show()
exit()
