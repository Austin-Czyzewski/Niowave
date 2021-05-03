import GPIB_FUNCS as GPIB #Importing our GPIB communication functions for easier comprehension and use
import pyvisa #import GPIB communication module
import time #imports time to sleep program temporarily
import Master as M
import sys
config_file_path = str(sys.argv[-1])

Tunnel, PLC_IP, End_Freq, Big_Step_Size, Small_Step_Size, Small_Sleep_Time, \
    Big_Sleep_Time, Pr_Small_Step_Threshold, Pr_Absolute_Threshold, \
    SG_GPIB_Add, OS_GPIB_Add = M.config_reader(config_file_path, "Gun Walker")

print(Tunnel)
if Tunnel.lower() == 'west':
    import Tag_Database_West as Tags
elif Tunnel.lower() == 'east':
    import Tag_Database_East as Tags
else:
    import Tag_Database as Tags

Client = M.Make_Client(PLC_IP) #Connecting to PLC


print(M.Read(Client, Tags.Oscope_Reset, Bool = True))
print(M.Read(Client, Tags.Regulation_Setpoint_Reset, Bool = True))
print(M.Read(Client, Tags.Error_Signal_Regulation, Bool = True))
print(M.Read(Client, Tags.Pulsing_Output, Bool = True))


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
               
