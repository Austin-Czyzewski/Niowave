import GPIB_FUNCS as GPIB #Importing our GPIB communication functions for easier comprehension and use
import pyvisa #import GPIB communication module
import time #imports time to sleep program temporarily
import Master as M
import Tag_Database as Tags

Client = M.Make_Client('10.50.0.10') #Connecting to PLC


print(M.Read(Client, Tags.Oscope_Reset, Bool = True))
print(M.Read(Client, Tags.Regulation_Setpoint_Reset, Bool = True))
print(M.Read(Client, Tags.Error_Signal_Regulation, Bool = True))
print(M.Read(Client, Tags.Pulsing_Output, Bool = True))
#for i in range(100):
#    M.Write(Client,55555, i)
#    print(i)
#    time.sleep(0.1)


#Pulsing_Tag = Tags.Pulsing_Output #Assign Modbus address here
Running_Tag = Tags.Error_Signal_Regulation #Assign Modbus address here
#Reset_Tag = Tags.Error_Signal_Reset #Assign Modbus address here
#Regulation_Setpoint_Tag = Tags.Regulation_Setpoint_Reset #Assign Modbus address here

RM = pyvisa.ResourceManager() #pyVISA device manager
Resources = RM.list_resources() #Printing out all detected device IDs
print(Resources)
SG = RM.open_resource("GPIB0::10::INSTR")
OS = RM.open_resource("GPIB0::16::INSTR")
time.sleep(2)


print("SG \n",SG.query("*IDN?"))
print("OS \n",OS.query("*IDN?"))

SG.control_ren(6)


freq = float(SG.query("Freq:CW?"))
while float(SG.query("Freq:CW?")) > 350.09* 10 ** 6:
    Pr = M.Read(Client, Tags.CU_Pr)
    if Pr > 325:
        if Pr > 900:
            freq -= 1000
            time.sleep(0.1)
        else:
            freq -= 100
        SG.write("freq:cw {} Hz".format(freq))
        print(freq)
        time.sleep(.025)
    else:
        time.sleep(0.250)

print("All done here you go")
SG.control_ren(6)
               
