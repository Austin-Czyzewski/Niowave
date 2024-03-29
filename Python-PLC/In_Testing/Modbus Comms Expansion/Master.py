''' Creator: Austin Czyzewski

Date: 12/04/2019
Last Updated: 06/01/2020

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

sleep_time = 0.020 #time in seconds before grabbing a consecutive data point

def merge(list1, list2): 
      
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
    Client = ModbusTcpClient(str(IP), strict = False)
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
        import time

        -example:
        Client = Make_Client('192.168.1.2')
        Dipole_1_Current = Read(Client,22201)
        Collection = Read(Client, 11109, Average = True, count = 20, sleep_time = 0.010)
        Pulsing_Status = Read(Client, 11014, Bool = True)

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
        
    Required imports:
        from pymodbus.client.sync import ModbusTcpClient
        from pymodbus.payload import BinaryPayloadDecoder
        from pymodbus.constants import Endian
        import concurrent.futures
    
    Example:
        Client = Make_Client('192.168.1.2')
        Dipole_1_Current = Read(Client,22201)
        Tag_List = [[22201, False],[22203, True],[22205, False]]
        Data = list()
        Data.append(Gather(Client, Tag_List, count = 20, sleep_time = 0.010))
        
    ***********
    Note: You must do a simple read on the same Client before you Gather. This is a 
        bug with unknown origin. I'll chock it up to the PLC probably doesn't want
        the first communication to be a barrage and shuts things down.
    ***********
    """
    
    temp_list = [] #initialize temporary list
    with concurrent.futures.ThreadPoolExecutor() as executor:
        
        results = [executor.submit(Read, Client = Client, Tag_Number = tag, Average = avg, count = count, sleep_time=sleep_time) for tag,avg in tag_list]
        
        for f in results:
            temp_list.append(f.result())
            
    return temp_list



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



def Ramp_One_Way(Client, Tag_Number, End_Value = 0, Max_Step = 0.010, Return = "N", Read_Tag = "00000", count = 25):
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

    if np.isclose(0,Delta) == True:
        #print("skip")
        return


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

            collected_list.append(Read(Client,Read_Tag,Average = True,count = count))
        
        else:
            time.sleep(sleep_time * 10)
                
            

    if Return == "N":
        return
    if Return == "Y":
        if Read_Tag != "00000":
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
