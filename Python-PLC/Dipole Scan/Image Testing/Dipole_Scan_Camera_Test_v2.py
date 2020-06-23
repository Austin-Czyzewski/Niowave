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

import numpy as np
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.payload import BinaryPayloadBuilder
from pymodbus.constants import Endian
import matplotlib.pyplot as plt
from datetime import datetime
import Tag_Database as Tags
import time

Client = Make_Client('192.168.1.2')

End_Value = float(input("What is the ending amperage that you want to ramp the magnet to? (Amps)   "))

Runs = 1 #Number of times you want to ramp to the input value and back to the start
Dipole_Tag = Tags.Sol1 #Modbus address of the magnet we are writing to
Step_size = .001 #Step Size, in Amps, that we are taking to reach our goal
Read = Tags.DBA_Bypass #Modbus address of the value we want to read while we scan the magnet
count = 20 #Number of times we want to average the Read Tag value

Start_Value = Read(Client, Dipole_Tag) #Recording the starting value of the Dipole
print("Started at {0:.3f} Amps".format(Start_Value))

DP1_Values = []
DBA_Collection = []
colors = []

for i in range(Runs):
    
    DP1_Vals, DBA_Col = Ramp_One_Way(Client, Dipole_Tag, End_Value, Max_Step = Step_size, Return = "Y", Read_Tag = Read, count = count, Image = True)
    #The above function walks the magnet to the endpoint ,and returns the data
    
    DP1_Values += DP1_Vals #Adding the recorded data to the lists
    DBA_Collection += DBA_Col 
    
    colors += ['chocolate' for i in list(range(len(DP1_Vals)))] #Appending 'chocolate' as the color for this data set

    DP1_Vals, DBA_Col = Ramp_One_Way(Client, Dipole_Tag, Start_Value, Max_Step = Step_size, Return = "Y", Read_Tag = Read, count = count, Image = True)
    #The above statement walks us back to the start, and returns the data
    
    DP1_Values += DP1_Vals
    DBA_Collection += DBA_Col

    colors += ['firebrick' for i in list(range(len(DP1_Vals)))] #Appending 'firebrick' as the color for this data set
    
    

now = datetime.today().strftime('%y%m%d_%H%M') #Grabbing the time and date in a common format to save the plot and txt file to
plt.figure(figsize = (12,8))
plt.scatter(DP1_Values,DBA_Collection,color = colors, alpha = 0.5)

plt.grid(True,alpha = 0.25,which = 'both',color = 'gray') #Making a grid
plt.minorticks_on() #Setting the minor ticks

#Naming
plt.ylabel("DBA current collected (mA)")
plt.xlabel("Magnet Setting (A)")
plt.title("Dipole 1 current collected over walk from {0:.3f} to {1:.3f}".format(Start_Value, End_Value))
plt.suptitle("Orange = Ascending, Red = Descending",fontsize = 8, alpha = 0.65)

plt.savefig(now + '_graph.png', dpi = 450, trasnparent = True) #Saving to the time and date as png

save_list = merge(DP1_Values,DBA_Collection)
with open(now+'.txt', 'w') as f:
    for item in save_list:
        f.write(str(item)+'\n')
    f.close()
plt.show()

# Close camera 
Camera.StopLive()

exit()