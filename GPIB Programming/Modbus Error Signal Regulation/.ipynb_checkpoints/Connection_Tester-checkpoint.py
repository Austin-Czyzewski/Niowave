import GPIB_FUNCS as GPIB #Importing our GPIB communication functions for easier comprehension and use
import pyvisa #import GPIB communication module
import time #imports time to sleep program temporarily
import Master as M
import Tag_Database as Tags

Client = M.Make_Client('192.168.1.2')

#Pulsing_Tag = Tags.Pulsing_Output #Assign Modbus address here
Running_Tag = Tags.Error_Signal_Regulation #Assign Modbus address here
#Reset_Tag = Tags.Error_Signal_Reset #Assign Modbus address here
#Regulation_Setpoint_Tag = Tags.Regulation_Setpoint_Reset #Assign Modbus address here

RM = pyvisa.ResourceManager() #pyVISA device manager
Resources = RM.list_resources() #Printing out all detected device IDs
print(Resources)
SG = RM.open_resource("GPIB0::10::INSTR")

time.sleep(2)


print(SG.query("*IDN?"))


SG.control_ren(6)
