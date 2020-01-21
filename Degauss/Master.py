''' Creator: Austin Czyzewski

Date: 12/04/2019

Purpose: Define functions to make code more modular and add functionality
    - Set up the code in a way that we have functions that can be used with imports and make easy code to write

Functions to be found:
    - Read from client
    - Write to client
    - Establish client
    - Ramp to value
'''

from pymodbus.client.sync import ModbusTcpClient
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.payload import BinaryPayloadBuilder
from pymodbus.constants import Endian
import matplotlib.pyplot as plt
from datetime import datetime
import time

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
                
                temp_list = []
                for i in range(count):
                    temp_list.append(Read(Client,Read_Tag))

                    time.sleep(sleep_time) #Sleep for 33 ms, this is tested to not overload PLC or give redundant data

                collected_list.append(sum(temp_list)/count)

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
                temp_list = []
                for i in range(count):
                    temp_list.append(Read(Client,Read_Tag))
                    time.sleep(sleep_time)
                collected_list.append(sum(temp_list)/count)
                
            

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
    plt.xlabel(X_axis)
    plt.grid(True)
    plt.title(Title)

    if Save != "N":
        now = datetime.today().strftime('%y%m%d_%H%M')
        plt.savefig(now+".png")
    plt.show()
    



'''
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
