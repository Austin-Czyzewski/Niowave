''' Creator: Austin Czyzewski

Date: 12/04/2019
Last Updated: 12/10/2020 -- NEEDS SERIOUS COMMENTING --

Purpose: Define functions to make code more modular and add functionality
    - Set up the code in a way that we have functions that can be used with imports and make easy code to write

Functions to be found:
    - Establish client
        - Set an IP address and save to act for functions
        
    - Read from client
        - Read the output from a modbus tag
        
    - Write to client
        - Similar to read, however, give a new value to write to. Be careful, there is no safety in magnet step size here
        
    - Ramp one way
        - Select the magnet, set an end value, and define a step size and this will walk the magnet to that value

    - Ramp two way
        - Select the magnet, set an end value, define a step size, and this will walk the magnet to and from that value
        
    - Plot
        - Currently not very useful, don't use this
    
    - Rapid_T_Scan
        - This takes a 2 axis magnet and rapidly scans in a t shape, this can prove to be useful for taking large datasets


Example Code to Write a script that reads the value of dipole 1 and then writes a new value. Then it checks that it actually wrote:

from Master import *
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.payload import BinaryPayloadBuilder
from pymodbus.constants import Endian

Client = Make_Client('192.186.10.2') #Establish Client
Dipole_1_Before = Read(Client,22201) #Read DP1

New_Dipole_1 = 0.123 #Amps, Set new value to be set

Dipole_1 = Write(Client,22201,New_Dipole_1) #Write to DP1 
Dipole_1_After = Read(Client,22201) #Read DP1



if Dipole_1_After == Dipole_1_Before:
    print("True")
else:
    print("False")

'''

from pymodbus.client.sync import ModbusTcpClient
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.payload import BinaryPayloadBuilder
from pymodbus.constants import Endian
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import time
import concurrent.futures
import re
import pyvisa

sleep_time = 0.020 #time in seconds before grabbing a consecutive data point

UseCamera = False

if UseCamera:
    import tisgrabber as IC
    import cv2
    resolution = '1920x1080'
    def_exp, def_gain = 0.01, 480  # exp in units of sec, gain in units of 1/10 dB

    # Access CCD data and grab initial frame
    Camera = IC.TIS_CAM()
    Camera.ShowDeviceSelectionDialog() #Brings up camera catalog for selection

    if Camera.IsDevValid() == 1:

        # Set a video format
        temp = "RGB32 (" + resolution + ")"
        Camera.SetVideoFormat(temp); del temp
        Camera.SetPropertyAbsoluteValue("Exposure","Value", def_exp)
        Camera.SetPropertyValue("Gain","Value", def_gain)

        # Communicate with camera
        Camera.StartLive(1)

        # Initial image snap
        Camera.SnapImage() #Take an image

        # Get image
        init_img = Camera.GetImage()
        init_img = cv2.flip(init_img, 0)
        init_img = cv2.cvtColor(init_img, cv2.COLOR_BGR2RGB)

    else:
        Camera.StopLive()
        exit()

def snap(Camera, def_exp = 0.01, def_gain = 480, fname = None):
    '''
    Inputs:
        __ Camera: The camera that we are connected to through TIS
        __ def_exp: The exposure time of the image that we want
        __ def_gain: Gain of the image that we want
    
    Outputs:
        A .bmp file with the name that contains the time at which the image is taken
        
    Required imports:
        - datetime
        - cv2
        - tisgrabber
        
    Example: 
        Camera = IC.TIS_CAM()
        snap(Camera, def_exp = 1/3, def_gain = 0)
        
    '''
    def_exp = def_exp #exposure (seconds)
    def_gain = def_gain  # gain in units of 1/10 dB
    
    Camera.SnapImage()
    image = Camera.GetImage()
    image = cv2.flip(image, 0) # note image is saved in BGR color code

                # we will save image sequences in the imgs directory
    timestamp = datetime.now() # data acquisition time stamp. need to be moved?
    
    if fname == None:
        fname = './imgs/' +  timestamp.strftime("%y%m%d_%H-%M-%S.%f") + \
            'exp' + str(def_exp) + '-gain' + str(def_gain) + '-dipolescan.bmp'
        
    cv2.imwrite(fname, image)
    
def merge(list1, list2): 
      
    merged_list = [(list1[i], list2[i]) for i in range(0, len(list1))] 
    return merged_list

def progress_bar(current, total, number_of_bars = 25):
    print("[{}{}]\r".format("#"*int(round(current/total,10)*number_of_bars),\
                            " "*(-1 + number_of_bars - int(round(current/total,10)*number_of_bars))), end = '')



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



def Read(Client, Tag_Number, Average = False, count = 20,sleep_time = .010, Bool = False):
    '''
        -Inputs: Client, see "Client" Above
            __ Tag_Number: which modbus to read, convention is this: input the modbus start tag number. Must have a modbus tag.
            __ Average: Tells us wether or not to average these data points
            __ Count: The number of points that we will average over if Average == True
            __ sleep_time: Time (ms) that we will rest before grabbing the next piece of data

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


    if Bool == False:
        
        if Average == True:
            
            temp_list = []
            for i in range(count):
                Payload = Client.read_holding_registers(Tag_Number,2,unit=1)
                Tag_Value_Bit = BinaryPayloadDecoder.fromRegisters(Payload.registers, byteorder=Endian.Big, wordorder=Endian.Big)
                Tag_Value = Tag_Value_Bit.decode_32bit_float()
                temp_list.append(Tag_Value)

                time.sleep(sleep_time)

            return (sum(temp_list)/count)
        else:
            Payload = Client.read_holding_registers(Tag_Number,2,unit=1)
            Tag_Value_Bit = BinaryPayloadDecoder.fromRegisters(Payload.registers, byteorder=Endian.Big, wordorder=Endian.Big)
            Tag_Value = Tag_Value_Bit.decode_32bit_float()
            return Tag_Value
        
    if Bool == True:
        Tag_Value = Client.read_coils(Tag_Number,unit=1).bits[0]

    return Tag_Value


def Gather(Client, tag_list, count = 20, sleep_time = 0.010):
    """
    Inputs: Client, see "Client" Above
        __ tag_list: a list of tags and whether or not to average them. The list must be in the following format: [[Tag#, True],[Tag#, False],[Tag#, True]]
                    where True and False indicate whether you want the Read to be averaged.
        __ count: how many reads to average over, see "Read" above
        __ sleep_time: how long to sleep between each averaged read, see "Read" above
        
    Method:
        - Build an empty list we will add to later
        - Import the threading tool, start up a threaded executor
        - Build workers, have them work. Store values in order as executed
        - When all are finished, add the results to the list
        - Output list
    """
    
    temp_list = [] #initialize temporary list
    with concurrent.futures.ThreadPoolExecutor() as executor:
        
        results = [executor.submit(Read, Client = Client, Tag_Number = tag, Average = avg, count = count, sleep_time=sleep_time) for tag,avg in tag_list]
        
        for f in results:
            temp_list.append(f.result())
            
    return temp_list


def Snapshot(Client, Tunnel, filename, start = 8, save = True, feedback = False):
    
    import sys
# insert at 1, 0 is the script path (or '' in REPL)
    sys.path.insert(1, '..\\')
    
    if Tunnel.lower() == 'west':
        import Tag_Database_West as Tags
    if Tunnel.lower() == 'east':
        import Tag_Database_East as Tags
    
    Read(Client,Tags.CU_V)
    
    variables = vars(Tags)
    variables = np.array(list(variables.items()))
    variables = variables[start:]
    #variables[:,1] = variables[:,1].astype(int)
    #variables = variables[variables[:,1].argsort()]
    Tag_List = []
    for item in variables:
        Tag_List.append([item[1], False])
            
    temp_list = []
    temp_list.append(Gather(Client, Tag_List, count = 20, sleep_time = 0.010))
    
    if save:
    
        with open(filename,'w') as f: #Opening a file with the current date and time
            for num, line in enumerate(temp_list[0]):
                f.write(variables[num,0] + ": " + str(line).strip("([])")+'\n') #Writing each line in that file
            f.close() #Closing the file to save it
            
    if feedback:
        return variables, temp_list
        
        
def Write(Client, Tag_Number, New_Value, Bool = False):
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

    if Bool == False:
        
        Builder = BinaryPayloadBuilder(byteorder=Endian.Big, wordorder=Endian.Big)
        Builder.add_32bit_float(New_Value)
        Payload = Builder.to_registers()
        Payload = Builder.build()
        Client.write_registers(Tag_Number, Payload, skip_encode=True, unit=1)

    if Bool == True:
        Client.write_coils(Tag_Number, [New_Value], skip_encode=False, unit=1)

    return

def Write_Multiple(Client, Start_Tag_Number, New_Value_List):
    
    '''
    Inputs:
        __ Client: See client
        __ Start_Tag_Number: This is the starting tag value, this will increment
            by two for each of the items in the New_Values_List
        __ New_Values_List: This is a list of new values that you want to write, this
            is typically the same number repeated once for each time that you want
            to write to each magnet. This is done this way so that you can write
            different values to each magnet if you want to. (Typically by a scaled
            amount if you are doing that.)
        
        - Must have an established Client before running this function.
        
        - Outputs:
            __ Writes to a number of user defined magnets, may, in the future,
                allow one value to be written to a specified number of magnets.
                
        - Method:
                - Set up the Client
                - Define the start tag value, 22201 for dipole 1 for example
                - For each dipole you want to step, you define the new value 
                    you want written to it.
        - Example (Writing to 8 Dipoles starting with DP1)
        
        List = [0.100,0.100,0.100,0.100,0.100,0.100,0.100,0.100]
        DP1_Tag = 22201
        
        Client = M.Make_Client('192.168.1.2')
        
        M.Write_Multiple(Client, DP1_Tag, List)
        
            - Result: All of the Dipoles (Assuming there are 8 will be written to 0.100) 
    
    '''
    
    Tag_Number = int(Start_Tag_Number)-1
    
    Builder = BinaryPayloadBuilder(byteorder=Endian.Big, wordorder=Endian.Big)
    
    for value in New_Value_List:
        Builder.add_32bit_float(value)
        
    Payload = Builder.to_registers()
    Payload = Builder.build()
    
    Client.write_registers(Tag_Number, Payload, skip_encode=True, unit=1)
    
    return

def Ramp_One_Way(Client, Tag_Number, End_Value = 0, Max_Step = 0.010, Return = "N", Read_Tag = None, \
                 count = 25, sleep_time = 0.020, step_time = 0.25, Image = False, Oscope = False, \
                 Measurement_1 = 1, Measurement_2 = 2, os_address = "GPIB0::1::INSTR"):
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

    if Oscope:
        RM = pyvisa.ResourceManager() #pyVISA device manager
        Resources = RM.list_resources() #Printing out all detected device IDs
        print(Resources)

        OS = RM.open_resource(os_address) #Opening the oscilloscope as an object

        Long = False
        Measurement = Measurement_1
        M2 = Measurement_2
        Read_Start_Voltage = True
        statement = OS.query("MEASU:MEAS{}:VAL?".format(Measurement))
        
        try: #Quick test to determine short or long form oscilloscope output
            short_test = float(statement)
            if Read_Start_Voltage == True:
                Error_signal_offset = short_test
            pass
        
        except:
            #long_test = float(OS.query("MEASU:MEAS{}:VAL?".format(Measurement)).split(' ')[0].strip("\n"))
            long_test = float(statement[-11:])
            Long = True
            if Read_Start_Voltage == True:
                Error_signal_offset = long_test
            pass
    
    Start_Value = Read(Client,Tag_Number)
    
    Delta = End_Value-Start_Value

    if np.isclose(0,Delta) == True:
        #print("skip")
        return


    Steps = 10

    #Ensures that we are making step sizes with the appropriate scaling
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
                break
        
            
        write_value = Start_Value + (Delta/Steps)*i

        write_value_list.append(write_value)

        Write(Client, Tag_Number, write_value)

        if Read_Tag != None:

            collected_list.append(Read(Client,Read_Tag,Average = True,count = count))
            
            if Image:
                time.sleep(step_time/2)
                
                snap(Camera)
                
            if Oscope:
                oscope_temp_list = list()
                oscope_temp_list_2 = list()

                collected_list.append(Read(Client,Read_Tag,Average = False,count = count))
                for _ in range(5):
                    #GPIB_Read_Value = GPIB.cursor_vbar_read_mv(OS)
                    GPIB_Read_Value = GPIB.read_mv(OS, long = Long, measurement = Measurement)
                    GPIB_Read_2 = GPIB.read_mv(OS, long = Long, measurement = M2)
                    if GPIB_Read_Value > 100000:
                        GPIB_Read_Value = 0
                        print("Bad read from scope")
                    if GPIB_Read_2 > 100000:
                        GPIB_Read_2 = 0
                        print("Bad Read from Scope")
                    oscope_temp_list.append(GPIB_Read_Value)
                    oscope_temp_list_2.append(GPIB_Read_2)
                    time.sleep(0.2) #Correlate to frequency of pulsing
                oscope_list.append(sum(oscope_temp_list)/len(oscope_temp_list))
                o2.append(sum(oscope_temp_list_2)/len(oscope_temp_list_2))
                
        else:
            time.sleep(sleep_time)
                
#     print(write_value_list, collected_list)

    if Return == "N":
        return
    if Return == "Y":
        if Read_Tag != None:
            if Oscope:
                return write_value_list, collected_list, oscope_list, o2
            else:
                return write_value_list, collected_list
        else:
            return write_value_list

        
def Ramp_Two_Way(Client, Tag_Number, End_Value = 0, Runs = 1, Max_Step = 0.010, Return = "N", Read_Tag = "00000", count = 25):
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


    for _ in range(Runs):
        
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

                collected_list.append(Read(Client,Read_Tag,Average = True,count = count))

        max_spot = write_value
        #Same loop as above, removed spacing
        for i in range(Steps + 1):
            
            if i != 0:
                
                temp_check = Read(Client,Tag_Number)
                
                if abs(temp_check - write_value) >= 0.001:
                    
                    exit()
                    
            write_value = max_spot - (Delta/Steps)*i #Only difference is the subtraction instead of addition
            
            write_value_list.append(write_value)
            
            Write(Client, Tag_Number, write_value)
            
            if Read_Tag != "00000":
                
                collected_list.append(Read(Client,Read_Tag,Average = True,count = count))
                
            

    if Return == "N":
        return
    if Return == "Y":
        if Read_Tag != "00000":
            return write_value_list, collected_list
        else:
            return write_value_list
        

        
def Plot(X_list, Y_list, X_axis, Y_axis, Title,Save = "N"):
    '''
        Plots the X_list and the Y_list
        Names on the X_axis and the Y_axis
    '''
    plt.figure(figsize = (9,6))
    plt.scatter(X_list, Y_list)
    plt.ylabel(Y_axis)
    plt.xlabel(Y_axis)
    plt.grid(True)
    plt.title(Title)

    if Save != "N":
        now = datetime.today().strftime('%y%m%d_%H%M')
        plt.savefig(now+".png")
    plt.show()
    

    
def Rapid_T_Scan(Client, WFH_Tag, WFV_Tag, Read_Tag, Horizontal_Delta = 0, Vertical_Delta = 0, Resolution = 25):
    '''
    Inputs: Client, see "Client" abov
        __ WFH_Tag: The tag for the horizontal controls for the window frame we are scanning
        __ WFV_Tag: The tag for the horizontal controls for the window frame we are scanning
        __ Read_Tag: This is the modbus tag for the data output tag we are reading, generally a beam dump outputting current
        __ Horizontal_Delta (Amps): How far we want to scan in the magnet frame space with the horizontal tag
        __ Vertical_Delta (Amps): How far we want to scan in the vertical magnet space
        __ Resolution: For each leg of the scan from the center, how many points do we want to collect
    Outputs: A window frame scan in which a quick sweep is performed with no regard to data collection. This is done for data gathering.
    Starting at the center. The scan is done in the following order:
        -- Move Upward, taking *Resolution* number of data points
        -- Quickly scan to the left center, gathering no data
        -- Move to the right, through the center, and to the rightmost point we are gathering, taking *Resolution* x 2 data points
        -- Quickly scan to the bottom center, gathering no data
        -- Move upward back to the center, taking *Resolution* data points
        
        Total data taken: Resolution * 4 data points
        
        Data: An array containing three columns of data. The first column is the horizontal window frame value,
            The second column is the vertical window frame value
            The third column contains the data taken from *Read_Tag* at the two values listed above
            
    Common changes to be made:
        -- Averaging number: Default is 25, this is how many points will be averaged over for the data collection, this number may
            want to be reduced to speed up the scanning
        -- Sleep_Time: (S) this is the amount of time between reads that we rest before making another request from the PLC
            The minimum value on the system as of 01/01/2020 is a 7 ms delay (0.007) to avoid repeat values
        -- Chunk_Size: This is the amount of chunky steps taken in the quick walking to the corner values, these are necessary to 
            Avoid magnetizing our magnets in the system.
        -- Chunk_rest_factor: This is a multiple from the sleep time on the averaging loop, we typically want a longer rest here
            to fully allow the PLC to catch up.
   
    '''
    WFH_Start = Read(Client, WFH_Tag) #Taking the start value for the window frames
    WFV_Start = Read(Client, WFV_Tag)

    Delta_H = Horizontal_Delta/Resolution #The step size for each step along the data taking routes
    Delta_V = Vertical_Delta/Resolution
    
    Averaging_Number = 25 #Number of times we read the Read tags for averaging, recommended about 25 if pulsing, 10 if CW
    Sleep_Time = .010 #Sleep time between reads
    Chunks = 4 #Inverse number of chunks, we use Resolution/Chunks, thus, the maximum value allowable is Resolution
    Chunk_rest_factor = 10 #Multiple of Sleep_Time to allow PLC to catch up.
    
    Data = np.zeros([(Resolution * 4),3]) #Initializing our data into an empty array to write over later
    
    #################################################################################
    
    #####
    #Moving upward first
    #####
    
    Loop_Number = 0 #Repeat variable, used to calculate where to write to, this iterates up to 3
    for i in range(Resolution):
        WFV_Write_Value = WFV_Start + ((i+1) * Delta_V) #Moving in the vertical direction
        
        Write(Client, WFV_Tag, WFV_Write_Value) #Writing the value to the PLC
        
        Data[i + Resolution * Loop_Number, 0] = Read(Client, WFH_Tag) #Storing the Horizontal Value
        Data[i + Resolution * Loop_Number, 1] = Read(Client, WFV_Tag) #Storing the Vertical Value
        Data[i + Resolution * Loop_Number, 2] = Read(Client, Read_Tag, Average = True, count = Averaging_Number, sleep_time = Sleep_Time) #Storing the Read_Tag averaged value
        
        #This loop is being repeated with some minor changes being made in the Write_values sections these
            #Are to reflect the changes in direction. Otherwise, refer to documentation in this loop for help.
    
        
    #####
    #Now moving to the left center
    #####
    
    for i in range(int(Resolution/Chunks)): #We still don't want huge steps so we simply reduce the steps taken by chunks
        WFH_Write_Value = WFH_Start - (i * (Horizontal_Delta/int(Resolution/Chunks))) #Chunking horizontally
        WFV_Write_Value = (WFV_Start + Vertical_Delta) - ((i+1) * (Horizontal_Delta/int(Resolution/Chunks))) #Chunking Vertically
        
        Write(Client, WFH_Tag, WFH_Write_Value) #Writing the values, notice no data is being collected here
        Write(Client, WFV_Tag, WFV_Write_Value)
        
        time.sleep(Sleep_Time*Chunk_rest_factor)
    
    #####
    #Now moving right to center center
    #####
    
    Loop_Number = 1
    for i in range(Resolution):
        WFH_Write_Value = (WFH_Start - Horizontal_Delta) + (i * Delta_H) 
        
        Write(Client, WFH_Tag, WFH_Write_Value)
        
        Data[i + Resolution * Loop_Number, 0] = Read(Client, WFH_Tag)
        Data[i + Resolution * Loop_Number, 1] = Read(Client, WFV_Tag) 
        Data[i + Resolution * Loop_Number, 2] = Read(Client, Read_Tag, Average = True, count = Averaging_Number, sleep_time = Sleep_Time)
        
        
    #####
    #Now moving center center to center right
    #####
    
    Loop_Number = 2
    for i in range(Resolution):
        WFH_Write_Value = WFH_Start + (i * Delta_H)
        
        Write(Client, WFH_Tag, WFH_Write_Value)
        
        Data[i + Resolution * Loop_Number, 0] = Read(Client, WFH_Tag)
        Data[i + Resolution * Loop_Number, 1] = Read(Client, WFV_Tag)
        Data[i + Resolution * Loop_Number, 2] = Read(Client, Read_Tag, Average = True, count = Averaging_Number, sleep_time = Sleep_Time)
        
    #####
    #Now moving Center Bottom
    #####
    
    for i in range(int(Resolution/Chunks)):
        WFH_Write_Value = (WFH_Start + Horizontal_Delta) - ((i+1) * (Horizontal_Delta/int(Resolution/Chunks)))
        WFV_Write_Value = (WFV_Start) - ((i+1) * (Vertical_Delta/int(Resolution/Chunks)))

        Write(Client, WFH_Tag, WFH_Write_Value)
        Write(Client, WFV_Tag, WFV_Write_Value)

        time.sleep(Sleep_Time*Chunk_rest_factor)
    
    #####
    #Now Moving Center Bottom to Center Center again
    #####
    
    Loop_Number = 3
    for i in range(Resolution):
        WFV_Write_Value = (WFV_Start - Vertical_Delta) + ((i+1) * Delta_V)
        
        Write(Client, WFV_Tag, WFV_Write_Value)
        
        Data[i + Resolution * Loop_Number, 0] = Read(Client, WFH_Tag)
        Data[i + Resolution * Loop_Number, 1] = Read(Client, WFV_Tag)
        Data[i + Resolution * Loop_Number, 2] = Read(Client, Read_Tag, Average = True, count = Averaging_Number, sleep_time = Sleep_Time)
        
            
    
    return Data

def Ramp_Two(Client, Magnet_1_Tag, Magnet_2_Tag, Magnet_1_Stop = 0, Magnet_2_Stop = 0, Resolution = 25, sleep_time = .050):
    '''
    Inputs: Client, see "Client" abov
        __ Magnet_1_Tag: The tag for the horizontal controls for the window frame we are scanning
        __ Magnet_2_Tag: The tag for the horizontal controls for the window frame we are scanning
        __ Magent_1_Stop: This is the modbus tag for the data output tag we are reading, generally a beam dump outputting current
        __ Magnet_2_Stop (Amps): How far we want to scan in the magnet frame space with the horizontal tag
        __ Resolution: For each leg of the scan from the center, how many points do we want to collect
        
    Outputs: Moves two magnets to their "stop" value in "Resolution" steps
    
    !Returns nothing!
    
    Logic:
        -- Check to see if there has been human intervention, if so, break
        -- Write to the magnets the next step value towards the goal
        -- Sleep for a small amount of time to avoid crowding the PLC
   
    '''
    
    Magnet_1_Start =  Read(Client,Magnet_1_Tag)
    Magnet_2_Start =  Read(Client,Magnet_2_Tag)
    
    Delta_1 = Magnet_1_Stop - Magnet_1_Start
    Delta_2 = Magnet_2_Stop - Magnet_2_Start
    
    for a__ in range(1,Resolution+1):
    
        if a__ != 1: #Don't check on the first run due to absence of write values
        
            temp_check_1 = Read(Client,Magnet_1_Tag) #Take the current value of Magnet 1
            temp_check_2 = Read(Client,Magnet_2_Tag) #Take the current value of Magnet 2
        
            #Comparing the current value to the last write value, if it is different, this updates the break loop for both Horizontal and Vertical
            if abs(temp_check_1 - Magnet_1_Write_Value) >= 0.001: #Magnet 1 Check
                print("Loop Broken")
                break
            if abs(temp_check_2 - Magnet_2_Write_Value) >= 0.001: #Magnet 2 Check
                print("Loop Broken")
                break
            
        Magnet_1_Write_Value = Magnet_1_Start + (Delta_1/Resolution)*a__
        Magnet_2_Write_Value = Magnet_2_Start + (Delta_2/Resolution)*a__
    
        Write(Client, Magnet_1_Tag, Magnet_1_Write_Value)
        Write(Client, Magnet_2_Tag, Magnet_2_Write_Value)

        time.sleep(sleep_time)
        
    return

def Save_and_Plot(Data, Save = True, Plot = True):
    '''
    Inputs: A 3 column array as produced by Rapid_T_Scan above
    
    Outputs: A txt file with the data in it and a 3D plot
    '''

    now = datetime.today().strftime('%y%m%d_%H%M') #Taking the current time in YYMMDD_HHmm format to save the plot and the txt file
    
    if Save == True:
        with open(now +'.txt', 'w') as f: #Open a new file by writing to it named the date as created above + .txt
    
            for i in Total_Data:
                f.write(str(i) + '\n')
            
            f.close()

    
    ######
    #Plotting
    ######
    x = Data[:,0]
    x = x.astype(np.float)

    y = Data[:,1]
    y = y.astype(np.float)

    z = Data[:,2]
    z = z.astype(np.float)

    fig = plt.figure(figsize = (12,8))
    ax = Axes3D(fig)
    ax.scatter(x, y, z, c=z, cmap='viridis', linewidth=0.5)

    ax.set_xlabel("Window Frame Horizontal Amperage")
    ax.set_ylabel("Window Frame Vertical Amperage")
    ax.set_zlabel("Collected Current")
    ax.set_title("Rapid Dog Leg Results")
    
    if Save == True:
        plt.savefig(now + '_graph.svg')


    plt.show()

def FWHM(x,y,extras = False):
    all_above = [abs(x) if abs(x) >= (abs(y).max())/2 else None for x in y]
    all_below = [abs(x) if abs(x) < (abs(y).max())/2 else None for x in y]
    
    good_x = []
    for i in range(len(x)):
        if all_above[i] != None:
            good_x.append(x[i])
            
    width = max(good_x)-min(good_x)

    if extras == False:
        return all_above, all_below, width
    else:
        good_sum = sum([abs(i) if i != None else 0 for i in all_above])
        bad_sum = sum([abs(i) if i != None else 0 for i in all_below])
        center = np.median(np.array([i for i in good_x if i != None]))
        return all_above, all_below, width, center, good_sum, bad_sum

def convert_to_mms(locs, Delta_1): #Converting the xlabels to mm
    new_list = []
    for i in locs:
        new_list.append(round(i/Delta_1*12,2)) #Our conversion formula
    return new_list

def Delta1_2(locs, Delta_1, Delta_2): #Converting the 1 values to the same displacement in 2
    new_list = []
    for i in locs:
        new_list.append(round(i/Delta_1*Delta_2,2))
    return new_list
    
def Delta2_1(locs, Delta_1, Delta_2): #Converting the 1 values to the same displacement in 2
    new_list = []
    for i in locs:
        new_list.append(round(-1*i/Delta_1*Delta_2,2))
    return new_list


def Dog_Leg(Client, WF1H_Tag, WF2H_Tag, WF1V_Tag, WF2V_Tag, Target_1_Tag, \
            Target_2_Tag, Tag_List, WF1H_Start = None, WF2H_Start = None, \
            WF1V_Start = None, WF2V_Start = None, Read_Steps = 40, \
            Delta_1 = 0.384, Delta_2 = 0.228, Threshold_Percent = 20, count = 20, sleep_time = 0.010, \
            Deviation_Check = 0.001, Zoom_In_Factor = 1, Scale_Factor = 0.91, iteration = None, move_to_center = False, Tunnel = None):

    '''
    Inputs:
        __ Client: Modbus TCP client that hosts PLCs
        __ WF1H_Tag: The modbus start address for the first horizontal window frame we are controlling
        __ WF2H_Tag, WF1V_Tag, WF2V_Tag: Horizontal and vertical window frame modbus address
        __ Target_1_Tag, Target_2_Tag: The modbus address for the beam target current dumps
        __ Tag_List: See Gather above, list of lists with tag values and wether or not they are
            averaged. These will be the tags grabbed at each step
        __ WF1H_Start, WF2H_Start, WF1V_Start, WF2V_Start: Our starting value for each of these magnets
            If default of None remains, then the dog leg is taken from the starting point
        __ Read_Steps: The amount of steps, in each direction, that we will attempt to take the Dog Leg
            This values divides the delta by this number, so step size will change as this value changes.
        __ Delta_1, Delta_2: The amount that the first window frame and second window frames will move
            the ratio of these is determined by the distance and relative strength of the two window 
            frames; float: 0 < Delta
        __ Threshold_Percent: This is the percent of the starting collection required to keep the dog leg
            moving in the current direction that it is. Once the dog leg falls below this threshold, the 
            dog leg will break out of a loop and go back to the starting point; 
            float:  0 <= Threshold_Percent <= 1
        __ count: This is the number of points that will be averaged at each Dog Leg iteration;
            integer: 1 <= count
        __ sleep_time: time, in seconds, to wait between each averaged point in count;
            float: 0 <= sleep_time
        __ Deviation_Check: Threshold, in Amps, that the magnet value setpoint must deviate from the
            last written point for the program to go back to the start and end. This is to ensure
            that if there is any human intervention, the dog leg will go back to the start and return
            control to the operator; float: 0 < Deviation_Check
        __ Zoom_In_Factor: This exists to adjust scaling on the output graph. This is primarily used when
            changing the magnets that are being Dog Legged
        __ Scale_Factor: Similar to Zoom_In_Factor, truly a relic
    
    Outputs:
        A graph named (current time)_graph.svg that contains a graph and table of the dog leg data taken
        A txt file containing a snapshot of the system at the end of the dog leg named 
            (current time)_snapshot.txt containing all of the read values for each magnet we have listed 
            in our tag database (Tag_Database.py)
        A txt file containing all of the Dog Leg data gathered from the Tag List throughout the run
            named (current time).txt
        
        returns a figure of merit for dog leg optimization. This is the FWHM for each axis squared and flipped
            in sign (to make minimization problems more intuitive)
            
    Requirements:
        Tag_Database must be in the same directory folder as this Master file.
        This function must be contained within the Master file (do not copy and paste out of this file)
        
        imports:
            from pymodbus.client.sync import ModbusTcpClient
            from pymodbus.payload import BinaryPayloadDecoder
            from pymodbus.payload import BinaryPayloadBuilder
            from pymodbus.constants import Endian
            numpy
            matplotlib.pyplot
            from datetime import datetime
            time
            concurrent.futures
    
    Logic:
        Ramp to our starting point
        Take data Read_Steps to the right by moving mag 1 to the right and mag 2 to the left
        Move to start
        Take data Read_Steps to the left, upward, and downward
        Move to start between each
        Take the Full width half max of the horizontal and vertically produced lines
        Output files
    '''
    
    
    if Tunnel.lower() == 'west':
        import Tag_Database_West as Tags
    elif Tunnel.lower() == 'east':
        import Tag_Database_East as Tags
    else:
        import Tag_Database as Tags

    start_time = time.time()

    Pulsing_Status = bool(Read(Client, Tags.Pulsing_Output, Bool = True))

    EC = Read(Client, Tags.Emitted_Current, Average = True, count = count)
    
    #Move to our starting point
    
    #If no starting values are provided, we take a dog leg from the current position
    
    if WF1H_Start == None:
        WF1H_Start = Read(Client, WF1H_Tag)
    if WF2H_Start == None:
        WF2H_Start = Read(Client, WF2H_Tag)
    if WF1V_Start == None:
        WF1V_Start = Read(Client, WF1V_Tag)
    if WF2V_Start == None:
        WF2V_Start = Read(Client, WF2V_Tag)
    
    Ramp_Two(Client, WF1H_Tag, WF2H_Tag, Magnet_1_Stop = WF1H_Start, Magnet_2_Stop = WF2H_Start, Resolution = Read_Steps, sleep_time = sleep_time)
    Ramp_Two(Client, WF1V_Tag, WF2V_Tag, Magnet_1_Stop = WF1V_Start, Magnet_2_Stop = WF2V_Start, Resolution = Read_Steps, sleep_time = sleep_time)
    
    Full_Data_Set = list()
    H_Broken = V_Broken = False #Creating the check tag for the dog leg, starting out as false as no errors could have been raised yet
    Start_Current = (Read(Client, Target_1_Tag, Average = True, count = count,sleep_time = sleep_time) + \
                 Read(Client, Target_2_Tag, Average = True, count = count,sleep_time = sleep_time))
    
    print("Right Displacement")

    ## Each of these are adding our data to a list as instantiated above. These will appear at each data gathering point
    Full_Data_Set.append(Gather(Client, Tag_List, count = count, sleep_time = sleep_time))

    for Right_Steps in range(1, Read_Steps + 1):
        if Right_Steps != 1: #Don't check on the first run due to absence of Window Frame write values
            #Comparing the current value to the last write value, if it is different, this updates the break loop for both Horizontal and Vertical
            if abs(Read(Client,WF1H_Tag) - WF1H_Write_Value) >= Deviation_Check or abs(Read(Client,WF2H_Tag) - WF2H_Write_Value) >= Deviation_Check: #WF1H Check
                H_Broken = V_Broken = True
                print("Loop Broken")
                break   

        WF1H_Write_Value = WF1H_Start + (Delta_1/Read_Steps)*Right_Steps #Calculated value to walk 1 to the right
        WF2H_Write_Value = WF2H_Start - (Delta_2/Read_Steps)*Right_Steps #Calculated value to walk 2 to the left

        Write(Client, WF1H_Tag, WF1H_Write_Value) #Writing to 1h
        Write(Client, WF2H_Tag, WF2H_Write_Value) #Writing to 2h
        #print(WF1H_Write_Value)
        #print(WF2H_Write_Value)

        Full_Data_Set.append(Gather(Client, Tag_List, count = count, sleep_time = sleep_time))
        if abs(Full_Data_Set[-1][5] + Full_Data_Set[-1][6]) < abs(Threshold_Percent*Start_Current*.01): #Checking our threshold
            break
    print("Moving to center")
    
    Ramp_Two(Client, WF1H_Tag, WF2H_Tag, Magnet_1_Stop = WF1H_Start, Magnet_2_Stop = WF2H_Start, Resolution = Right_Steps//2, sleep_time = sleep_time) #Moves back to the start in half of the same # of steps taken

    print("Left Displacement")

    Full_Data_Set.append(Gather(Client, Tag_List, count = count, sleep_time = sleep_time))

    for Left_Steps in range(1, Read_Steps + 1):
        if H_Broken or V_Broken == True:
            break
        if Left_Steps != 1: #Don't check on the first run due to absence of Window Frame write values
            #Comparing the current value to the last write value, if it is different, this updates the break loop for both Horizontal and Vertical
            if abs(Read(Client,WF1H_Tag) - WF1H_Write_Value) >= Deviation_Check or abs(Read(Client,WF2H_Tag) - WF2H_Write_Value) >= Deviation_Check: #WF1H Check
                H_Broken = V_Broken = True
                print("Loop Broken")
                break

        WF1H_Write_Value = WF1H_Start - (Delta_1/Read_Steps)*Left_Steps
        WF2H_Write_Value = WF2H_Start + (Delta_2/Read_Steps)*Left_Steps

        Write(Client, WF1H_Tag, WF1H_Write_Value) #Writing to 1h
        Write(Client, WF2H_Tag, WF2H_Write_Value) #Writing to 2h
        #print(WF1H_Write_Value)
        #print(WF2H_Write_Value)

        Full_Data_Set.append(Gather(Client, Tag_List, count = count, sleep_time = sleep_time))

        if abs(Full_Data_Set[-1][5] + Full_Data_Set[-1][6]) < abs(Threshold_Percent*Start_Current*.01): #Checking our threshold
            break

    print("Moving to center")

    Ramp_Two(Client, WF1H_Tag, WF2H_Tag, Magnet_1_Stop = WF1H_Start, Magnet_2_Stop = WF2H_Start, Resolution = Left_Steps//2, sleep_time = sleep_time)

    print("Upward Displacement")

    Full_Data_Set.append(Gather(Client, Tag_List, count = count, sleep_time = sleep_time))

    for Upward_Steps in range(1, Read_Steps + 1):
        if H_Broken or V_Broken == True:
            break
        if Upward_Steps != 1: #Don't check on the first run due to absence of Window Frame write values
            #Comparing the current value to the last write value, if it is different, this updates the break loop for both Horizontal and Vertical
            if abs(Read(Client,WF1V_Tag) - WF1V_Write_Value) >= Deviation_Check or abs(Read(Client,WF2V_Tag) - WF2V_Write_Value) >= Deviation_Check: #WF1H Check
                H_Broken = V_Broken = True
                print("Loop Broken")
                break

        WF1V_Write_Value = WF1V_Start + (Delta_1/Read_Steps)*Upward_Steps
        WF2V_Write_Value = WF2V_Start - (Delta_2/Read_Steps)*Upward_Steps

        Write(Client, WF1V_Tag, WF1V_Write_Value) #Writing to 1h
        Write(Client, WF2V_Tag, WF2V_Write_Value) #Writing to 2h
        #print(WF1V_Write_Value)
        #print(WF2V_Write_Value)

        Full_Data_Set.append(Gather(Client, Tag_List, count = count, sleep_time = sleep_time))

        if abs(Full_Data_Set[-1][5] + Full_Data_Set[-1][6]) < abs(Threshold_Percent*Start_Current*.01): #Checking our threshold
            break

    print("Moving to center")

    Ramp_Two(Client, WF1V_Tag, WF2V_Tag, Magnet_1_Stop = WF1V_Start, Magnet_2_Stop = WF2V_Start, Resolution = Upward_Steps//2, sleep_time = sleep_time)

    print("Downward Displacement")

    Full_Data_Set.append(Gather(Client, Tag_List, count = count, sleep_time = sleep_time))

    for Downward_Steps in range(1, Read_Steps + 1):
        if H_Broken or V_Broken == True:
            break
        if Downward_Steps != 1: #Don't check on the first run due to absence of Window Frame write values
            #Comparing the current value to the last write value, if it is different, this updates the break loop for both Horizontal and Vertical
            if abs(Read(Client,WF1V_Tag) - WF1V_Write_Value) >= Deviation_Check or abs(Read(Client,WF2V_Tag) - WF2V_Write_Value) >= Deviation_Check: #WF1H Check
                H_Broken = V_Broken = True
                print("Loop Broken")
                break

        WF1V_Write_Value = WF1V_Start - (Delta_1/Read_Steps)*Downward_Steps
        WF2V_Write_Value = WF2V_Start + (Delta_2/Read_Steps)*Downward_Steps

        Write(Client, WF1V_Tag, WF1V_Write_Value) #Writing to 1h
        Write(Client, WF2V_Tag, WF2V_Write_Value) #Writing to 2h
        #print(WF1V_Write_Value)
        #print(WF2V_Write_Value)

        Full_Data_Set.append(Gather(Client, Tag_List, count = count, sleep_time = sleep_time))

        if abs(Full_Data_Set[-1][5] + Full_Data_Set[-1][6]) < abs(Threshold_Percent*Start_Current*.01): #Checking our threshold
            break

    print("Moving to center")
    
    
    if iteration == None:
        now = datetime.today().strftime('%y%m%d_%H%M%S') #Taking the current time in YYMMDD_HHmm format to save the plot and the txt file
    else:
        now = datetime.today().strftime('%y%m%d_%H%M%S__') #Taking the current time in YYMMDD_HHmm format to save the plot and the txt file
        now += str(iteration)
        
    Controlled_Magnets = []
    
    Moved_Magnets = [WF1H_Tag, WF2H_Tag, WF1V_Tag, WF2V_Tag]
    variables = vars(Tags)
    for Mag_Tag in Moved_Magnets:
        for item in variables.items():
            if item[1] == Mag_Tag:
                Controlled_Magnets.append(item[0])

    Snapshot(Client, Tunnel, filename = now + "_snapshot.txt")
    
    with open(f'.\Output Data\{Tunnel}\Dog Legs\{now}_Dog_Leg.txt','w') as f: #Opening a file with the current date and time
        f.write("{}(A), {}(A), {}(A), {}(A), Avg'd Emitted Current(mA), Avg'd Loop Mid(mA), Avg'd Loop Bypass(mA), Cu Gun (V), SRF Pt (dBm)\n"\
                .format(Controlled_Magnets[0], Controlled_Magnets[1], Controlled_Magnets[2], Controlled_Magnets[3]))
        for line in Full_Data_Set:
            f.write(str(line).strip("([])")+'\n') #Writing each line in that file
        f.close() #Closing the file to save it

    Full_Data_Array = np.array(Full_Data_Set) #Converting from a list to an array

    Horizontal_1 = Full_Data_Array[:(Right_Steps + 2 + Left_Steps),0] #Defining the steps on in the horizontal
    Horizontal_2 = Full_Data_Array[:(Right_Steps + 2 + Left_Steps),1]

    Vertical_1 = Full_Data_Array[(Right_Steps + 2 + Left_Steps):,2] #Defining the steps only in the Vertical
    Vertical_2 = Full_Data_Array[(Right_Steps + 2 + Left_Steps):,3]
    Dump_1 = Full_Data_Array[:,5] #Dump 1 all values
    Dump_2 = Full_Data_Array[:,6] #Dump 2 all values
    Emitted_Current = Full_Data_Array[:,4] #Emitted current all values
    Dump_Sum = Dump_1 + Dump_2 #All dump values

    #Dump Sum into percent from start
    Horizontal_Percent = Dump_Sum[:(Right_Steps + 2 + Left_Steps)]/Emitted_Current[:(Right_Steps + 2 + Left_Steps)]*100 #Defining the percents
    Vertical_Percent = Dump_Sum[(Right_Steps + 2 + Left_Steps):]/Emitted_Current[(Right_Steps + 2 + Left_Steps):]*100

    #FWHM of all of our data
    Horizontal_Above, Horizontal_Below, H_Width, Center_Value_1H, H_Goodsum, H_Badsum = FWHM(Horizontal_1, Horizontal_Percent, extras = True) #FWHM Calclations
    Vertical_Above, Vertical_Below, V_Width, Center_Value_1V, V_Goodsum, V_Badsum = FWHM(Vertical_1, Vertical_Percent, extras = True)
    _,_1,_2,Center_Value_2H,_3, _4 = FWHM(Horizontal_2, Horizontal_Percent, extras = True)
    _,_1,_2,Center_Value_2V,_3, _4 = FWHM(Vertical_2, Vertical_Percent, extras = True)

    if move_to_center:
        print('Moving to center of FWHM')
        
        Ramp_Two(Client, WF1H_Tag, WF1V_Tag, Magnet_1_Stop = Center_Value_1H, Magnet_2_Stop = Center_Value_1V, Resolution = Read_Steps, sleep_time = sleep_time)
        Ramp_Two(Client, WF2H_Tag, WF2V_Tag, Magnet_1_Stop = Center_Value_2H, Magnet_2_Stop = Center_Value_2V, Resolution = Read_Steps, sleep_time = sleep_time)
    else:
        Ramp_Two(Client, WF1V_Tag, WF2V_Tag, Magnet_1_Stop = WF1V_Start, Magnet_2_Stop = WF2V_Start, Resolution = Downward_Steps//2, sleep_time = sleep_time)
        
    #Plotting
    plt.figure(figsize = (9,9)) #Changing the figure to be larger

    ax1 = plt.subplot(1,1,1)
    ax1.scatter(Horizontal_1 - Horizontal_1[0], Horizontal_Above, label = 'Horizontal above FWHM',color = 'C0', alpha = 0.75) #Plotting 1H Above FWHM
    ax1.scatter(Horizontal_1 - Horizontal_1[0], Horizontal_Below, label = 'Horizontal below FWHM', color = 'C0', alpha = 0.5, marker = '.') #Plotting 1H below FWHM
    ax1.scatter(Vertical_1 - Vertical_1[0], Vertical_Above, label = 'Vertical above FWHM', color = 'C1', alpha = 0.75) #Plotting 1V above FWHM
    ax1.scatter(Vertical_1 - Vertical_1[0], Vertical_Below, label = 'Vertical below FWHM', color = 'C1', alpha = 0.5, marker = '.') #plotting 1V Below FWHM
    ax1.set_xlabel("Displacement WF6 (Amps)", fontsize = 12) #Setting xlabel
    ax1.set_ylabel("Collection from start (%); ({0:.2f}\u03BCA) collected at start".format(1000*abs(min(Dump_Sum))), fontsize = 12) #Making the y axis label
    ax1.set_title("Dog Leg Taken at " + now, fontsize = 16) #Making the title 
    ax1.set_xlim(-0.4,0.4)
    ax1.legend(bbox_to_anchor = (0.5,0.27), loc = 'upper center') #Adding the legend and placing it in the bottom center of the plot

    ax1.minorticks_on() #Turning on the minor axis
    ax1.grid(True,alpha = 0.25,which = 'both',color = 'gray') #Making the grid (and making it more in the background)

    locs = ax1.get_xticks() #Grabbing the xticks from that axis

    ax2 = ax1.twiny() #Copying axis

    ax2.set_xticks(locs) #Setting xticks to same position
    ax2.set_xticklabels(convert_to_mms(locs, Delta_1)) #Converting to mm
    ax2.xaxis.set_ticks_position('top') # set the position of the second x-axis to top
    ax2.xaxis.set_label_position('top') # set the position of the second x-axis to top
    ax2.spines['top'].set_position(('outward', 0)) #Setting the ticks to go out of graph area
    ax2.set_xlabel('Displacement (mm)', fontsize = 12) #Label
    ax2.set_xlim(ax1.get_xlim()) #Setting to the same limit as prior axis

    ax3 = ax1.twiny() #Repeat for axis 3

    ax3.set_xticks(locs)
    ax3.set_xticklabels(Delta2_1(locs, Delta_1, Delta_2))
    ax3.xaxis.set_ticks_position('bottom') # set the position of the second x-axis to bottom
    ax3.xaxis.set_label_position('bottom') # set the position of the second x-axis to bottom
    ax3.spines['bottom'].set_position(('outward', 40))
    ax3.set_xlabel('Displacement WF7(Amps)', fontsize = 12)
    ax3.set_xlim(ax1.get_xlim())

    col_labels = ['WF6  Start (A)','WF7 Start (A)','FWHM', 'Center (6,7) (A)', 'Sum Above', 'Sum Below'] #Making the table column names
    row_labels = ['Horizontal','Vertical','Params'] #making the table row names
    table_vals = [[round(WF1H_Start,3), round(WF2H_Start,3), round(H_Width,3), "{:.3f}; {:.3f}".format(Center_Value_1H, Center_Value_2H), round(H_Goodsum,1), round(H_Badsum,1)],
                  [round(WF1V_Start,3) , round(WF2V_Start,3), round(V_Width,3), "{:.3f}; {:.3f}".format(Center_Value_1V, Center_Value_2V) , round(V_Goodsum,1), round(V_Badsum,1)],
                  ["Threshold %: {:.0f}".format(Threshold_Percent),"Zoom: {:.2f}".format(Zoom_In_Factor),"Scale: {:.2f}".format(Scale_Factor),
                   "# H Steps: {:.0f}".format(Right_Steps + 2 + Left_Steps),"# V Steps: {:.0f}".format(Upward_Steps + 2 + Downward_Steps), "EC (mA): {:.3f}".format(EC)]] #Setting values

    the_table = plt.table(cellText=table_vals, #Putting the table onto the plot
                      colWidths = [0.13]*6,
                      rowLabels=row_labels,
                      colLabels=col_labels,
                      loc='lower center', zorder = 1) #Putting in the center and in front of all else

    plt.gca().set_ylim(bottom=-2) #Making sure the plot always goes below 0 in the y axis

    plt.tight_layout() #configuring plot to not cut off extraneous objects like title and x axes
    
    plt.savefig(f'.\Output Data\{Tunnel}\Dog Legs\{now}_Dog_Leg_graph.png',transparent = True) #Saving the figure to a plot

    plt.show()
    
    print("This DogLeg took {0:.1f} Seconds to run".format(time.time() - start_time)) #Printing the amount of time the dog leg took
    
    return -1 * ((H_Width)**2 + (V_Width)**2)



def config_reader(file, config_type):
    '''
    LOI: Lines of interest, these are the lines with the data. In them.
    '''
    Lines = []
    try:
        with open(file, 'r') as f:
            for line in f:
                Lines.append(line)
    except:
        print("Error in the filename, please check the file name and make sure it is in the current directory")
        return 
            
    if config_type == "Dipole Scan":
        LOI = Lines[2:10]
        Parameters = []
        for param in LOI:
            if param == "\n":
                continue
#             current_param = param.strip("\n").replace(" ","").split(": ")
            current_param = re.split(":\s{1}", param)
            try:
                if ('Runs' in current_param[0]) or ('count' in current_param[0]):
                    Parameters.append(int(current_param[1].strip("\n")))
                else:
                    Parameters.append(float(current_param[1].strip("\n")))
            except:
                Parameters.append(current_param[1].strip("\n"))
        return Parameters
    
    if config_type == "Dog Leg":
        LOI = Lines[2:10]
        Parameters = []
        for param in LOI:
            if param == "\n":
                continue
            current_param = param.strip("\n").replace(" ","").split(":")
            try:
                if ('Steps' in current_param[0]) or ('count' in current_param[0]):
                    Parameters.append(int(current_param[1]))   
                else:
                    Parameters.append(float(current_param[1]))
            except:
                if (current_param[1].lower() == "false") or (current_param[1].lower() == "true"):
                    Parameters.append('true' in current_param[1].lower())
                else:
                    Parameters.append(current_param[1])
        return Parameters
    
    if config_type == "IF Regulation":
        LOI = Lines[2:20]
        Parameters = []
        for param in LOI:
            if param == "\n":
                continue
            current_param = param.strip("\n").replace(" ","").split(":")
            try:
                if ('Channel' in current_param[0]) or ('Measurement' in current_param[0])\
                or ('size' in current_param[0]) or ('Debounce' in current_param[0]):
                    Parameters.append(int(current_param[1]))   
                else:
                    Parameters.append(float(current_param[1]))
            except:
                if (current_param[1].lower() == "false") or (current_param[1].lower() == "true"):
                    Parameters.append('true' in current_param[1].lower())
                else:
                    Parameters.append(current_param[1])
        return Parameters
    
    if config_type == "Cutoffs":
        LOI = Lines[2:8]
        Parameters = []
        for param in LOI:
            if param == "\n":
                continue
            current_param = param.strip("\n").replace(" ","").split(":")
            try:
                if ('V0' in current_param[0]) or ('sawtooths' in current_param[0]):
                    Parameters.append(int(current_param[1]))   
                else:
                    Parameters.append(float(current_param[1]))
            except:
                if (current_param[1].lower() == "false") or (current_param[1].lower() == "true"):
                    Parameters.append('true' in current_param[1].lower())
                else:
                    Parameters.append(current_param[1])
        return Parameters
    
    if config_type == "Gun Walker":
        LOI = Lines[2:16]
        Parameters = []
        for param in LOI:
            if param == "\n":
                continue
            current_param = param.strip("\n").replace(" ","").split(":")
            try:
                if ('GPIB' in current_param[0]):
                    Parameters.append(int(current_param[1]))   
                else:
                    Parameters.append(float(current_param[1]))
            except:
                if (current_param[1].lower() == "false") or (current_param[1].lower() == "true"):
                    Parameters.append('true' in current_param[1].lower())
                else:
                    Parameters.append(current_param[1])
        return Parameters
    
    if config_type == "Snapshot":
        LOI = Lines[2:4]
        Parameters = []
        for param in LOI:
            if param == "\n":
                continue
            current_param = param.strip("\n").replace(" ","").split(":")
            
            Parameters.append(current_param[1])

        return Parameters
    
    print("Error in the type of config file. \n\
Please use one of the following verbose:\n------------\nDipole Scan\nDog Leg\n\
IF Regulation\nCutoffs\nGun Walker\n------------")
    return ""

