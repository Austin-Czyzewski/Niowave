import GPIB_FUNCS as GPIB #Importing our GPIB communication functions for easier comprehension and use
import pyvisa #import GPIB communication module
import time #imports time to sleep program temporarily
import Master as M
import Tag_Database as Tags

Current_Tunnel = 'West'
PLC_IP = '10.50.0.10'

End_Freq = 350.11* 10 ** 6

Big_Step_Size = 3000
Small_Step_Size = 350
Small_Sleep_Time = 0.025
Big_Sleep_Time = 0.250
Pr_Small_Step_Threshold = 500
Pr_Absolute_Threshold = 290

SG_GPIB_Add = 10
OS_GPIB_Add = 16

Client = M.Make_Client(PLC_IP) #Connecting to PLC


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
SG = RM.open_resource("GPIB0::{}::INSTR".format(SG_GPIB_Add))
OS = RM.open_resource("GPIB0::{}::INSTR".format(OS_GPIB_Add))
time.sleep(2)


print("SG \n",SG.query("*IDN?"))
print("OS \n",OS.query("*IDN?"))

SG.control_ren(6)



freq = float(SG.query("Freq:CW?"))

while float(SG.query("Freq:CW?")) > End_Freq:
    Pr = M.Read(Client, Tags.CU_Pr)
    if Pr > Pr_Absolute_Threshold:
        if Pr > Pr_Small_Step_Threshold:
            freq -= Big_Step_Size
            time.sleep(Big_Sleep_Time)
        else:
            freq -= Small_Step_Size
        SG.write("freq:cw {} Hz".format(freq))
        print(freq)
        time.sleep(Small_Sleep_Time)
    else:
        time.sleep(Big_Sleep_Time)
        
SG.write("freq:cw {} Hz".format(End_Freq))

print("All done here's your controls back")
SG.control_ren(6)
               
