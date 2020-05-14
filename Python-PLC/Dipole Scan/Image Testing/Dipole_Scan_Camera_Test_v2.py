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
import time



####################################################################################################
####################################################################################################
####################################################################################################
# Camera imports go here
import cv2
import tisgrabber as IC

####################################################################################################
####################################################################################################
####################################################################################################

def merge(list1, list2): 
      '''
      Merges two lists
      '''
    merged_list = [(list1[i], list2[i]) for i in range(0, len(list1))] 
    return merged_list

def Make_Client(IP):
    '''
        -Inputs: IP Address of modbus to communicate with. Input as a string.
        
        -Outputs: A client to be used by pymodbus for reading and writing
        
        -Required imports
        from pymodbus.client.sync import ModbusTcpClient

        -example:
        Client = Make_Client('192.168.1.2')

    '''

    #Using pymodbus to establish the client we are reaching
    Client = ModbusTcpClient(str(IP))
    return Client

def Read(Client, Tag_Number):
    '''
        -Inputs: Client, see "Client" Above
            __ Tag_Number: which modbus to read, convention is this: input the modbus start tag number. Must have a modbus tag.

        -Must have established client before attempting to read from the client
        
        -Outputs: The value of that Moodbus tag

        Method: Grab holding register value
                - Decode that value into a 32 bit float
                - Convert from 32 bit float to regular float
        
        -Required imports
        from pymodbus.client.sync import ModbusTcpClient
        from pymodbus.payload import BinaryPayloadDecoder
        from pymodbus.constants import Endian

        -example:
        Client = Make_Client('192.168.1.2')
        Dipole_1_Current = Read(Client,22201)

    '''
    Tag_Number = int(Tag_Number)-1
    
    Payload = Client.read_holding_registers(Tag_Number,2,unit=1)
    Tag_Value_Bit = BinaryPayloadDecoder.fromRegisters(Payload.registers, byteorder=Endian.Big, wordorder=Endian.Big)
    Tag_Value = Tag_Value_Bit.decode_32bit_float()

    return Tag_Value

def Write(Client, Tag_Number, New_Value):
    '''  -Future: input a safety method to make sure we aren't drastically changing values

        Inputs: Client, see "Client" Above
            __ Tag_Number: which modbus to read, convention is this: input the modbus start tag number. Must have a modbus tag.
            __ New_Value: New value which you want the modbus to output to

        -Must have established client before attempting to write to the client
        
        -Outputs: The value of that Moodbus tag

        Method:
                - Build a payload to send to register
                - Add float value to that payload
                - Build payload path (path to register)
                - Build the payload
                - Write the new value
        
        -Required imports
        from pymodbus.client.sync import ModbusTcpClient
        from pymodbus.payload import BinaryPayloadDecoder
        from pymodbus.constants import Endian

        -example:
        Client = Make_Client('192.168.1.2')
        Dipole_1_Current = Write(Client,22201,0.450)


    '''
    Tag_Number = int(Tag_Number)-1
    
    Builder = BinaryPayloadBuilder(byteorder=Endian.Big, wordorder=Endian.Big)
    Builder.add_32bit_float(New_Value)
    Payload = Builder.to_registers()
    Payload = Builder.build()
    Client.write_registers(Tag_Number, Payload, skip_encode=True, unit=1)

    return

def Ramp_One_Way(Client, Tag_Number, End_Value = 0, Max_Step = 0.010, Return = "N", Read_Tag = "00000", count = 25,step_time = 0.25, sleep_time = 0.020):
    '''  -Future: input a safety method to make sure we aren't drastically changing values

        Inputs: Client, see "Client" Above
            __ Tag_Number: which modbus to read, convention is this: input the modbus start tag number. Must have a modbus tag.
            __ End_Value: End value which you want the modbus to ramp the magnet to
            __ Max_Step: The maximum change in amerage you want the magnet to be able to move, default 10 mA
            __ Return: "N" if you don't want the data in a list, "Y" if you do want the data in a list. Default "N"
            __ Read_Tag: Which value do you want to be recording, if "00000" no value is recorded, otherwise it reads that tag. Default "00000"
            __ count: how many datapoints do you want to average over for the Read_Tag function. Default is 25

        -Must have established client before attempting to write to the client
        
        -Outputs: Writes to the specified magnet, outputs either a list of the written values,
            or a list of the written values with a list of the collected Read_Tag values merged with written mag values.

        Method:
                - Define the start and end value, take the difference between the two
                - Define the number of steps needed to safely walk to that value
                - Check that there hasn't been any human intervention
                - Write a new value to PLC (see Write())
                - Record both written value and the value of a selected tag
                - Check if there is a requested save
                - Save, or exit
        
        -Required imports
        from pymodbus.client.sync import ModbusTcpClient
        from pymodbus.payload import BinaryPayloadDecoder
        from pymodbus.constants import Endian

        -example:
        Client = Make_Client('192.168.1.2')
        DBA_Collection_Through_Aperture = Ramp_One_Way(Client, 22201, .450,.010,"Y","11109")

        #User plotting choice:
        plot(DBA_Collection_Through_Aperture[0],DBA_Collection_Through_Aperture[1])


    '''
    
    Start_Value = Read(Client,Tag_Number)
    
    Delta = End_Value-Start_Value

    Steps = 10

    #Insures that we are making step sizes with the appropriate scaling
    while abs(Delta/Steps) >= Max_Step:
        Steps += 1

    #print("Difference between start and end value: {0:.3f} Amps".format(Delta))

    write_value_list = []
    collected_list = []

    for i in range(Steps + 1):

        #This is to enforce that any human intervention will break the program and prevent it from running further
        #Note that we are using the write value from the last run in the loop to check that the value is the same as the loop left it
        if i != 0:
            temp_check = Read(Client,Tag_Number)

            if abs(temp_check - write_value) >= 0.001:
                exit()
        
            
        write_value = Start_Value + (Delta/Steps)*i

        write_value_list.append(write_value)

        Write(Client, Tag_Number, write_value)

        if Read_Tag != "00000":
            
            temp_list = []
            for i in range(count):
                temp_list.append(Read(Client,Read_Tag))

                time.sleep(sleep_time) #Sleep for 33 ms, this is tested to not overload PLC or give redundant data

            collected_list.append(sum(temp_list)/count)
            
            time.sleep(step_time/2)
            
            ####################################################################################################
            ####################################################################################################
            ####################################################################################################
            # Snap image of current frame
            Camera.SnapImage()
            image = Camera.GetImage()
            image = cv2.flip(image, 0) # note image is saved in BGR color code
                        
            # we will save image sequences in the imgs directory
            timestamp = datetime.now() # data acquisition time stamp. need to be moved?
            fname = './imgs/' +  timestamp.strftime("%y%m%d_%H-%M-%S.%f") +
                'exp' + str(def_exp) + '-gain' + str(def_gain) + '-dipolescan.bmp'
            cv2.imwrite(fname, image)
            
            ####################################################################################################
            ####################################################################################################
            ####################################################################################################
            
            time.sleep(step_time/2)
                
            

    if Return == "N":
        return
    if Return == "Y":
        if Read_Tag != "00000":
            return write_value_list, collected_list
        else:
            return write_value_list

Client = Make_Client('192.168.1.2')

End_Value = float(input("What is the ending amperage that you want to ramp the magnet to? (Amps)   "))

Runs = 1 #Number of times you want to ramp to the input value and back to the start
Dipole_Tag = 22201 #Modbus address of the magnet we are writing to
Step_size = .001 #Step Size, in Amps, that we are taking to reach our goal
Read = 11109 #Modbus address of the value we want to read while we scan the magnet
count = 20 #Number of times we want to average the Read Tag value

Start_Value = Read(Client, Dipole_Tag) #Recording the starting value of the Dipole
print("Started at {0:.3f} Amps".format(Start_Value))

DP1_Values = []
DBA_Collection = []
colors = []

####################################################################################################
####################################################################################################
####################################################################################################
# Camera setup
resolution = '1920x1080'
def_exp, def_gain = 0.01, 480  # exp in units of sec, gain in units of 1/10 dB

# Access CCD data and grab initial frame
Camera = IC.TIS_CAM()
Camera.ShowDeviceSelectionDialog() 

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

####################################################################################################
####################################################################################################
####################################################################################################


for i in range(Runs):
    
    DP1_Vals, DBA_Col = Ramp_One_Way(Client, Dipole_Tag, End_Value, Max_Step = Step_size, Return = "Y", Read_Tag = Read, count = count)
    #The above function walks the magnet to the endpoint ,and returns the data
    
    DP1_Values += DP1_Vals #Adding the recorded data to the lists
    DBA_Collection += DBA_Col 
    
    colors += ['chocolate' for i in list(range(len(DP1_Vals)))] #Appending 'chocolate' as the color for this data set

    DP1_Vals, DBA_Col = Ramp_One_Way(Client, Dipole_Tag, Start_Value, Max_Step = Step_size, Return = "Y", Read_Tag = Read, count = count)
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