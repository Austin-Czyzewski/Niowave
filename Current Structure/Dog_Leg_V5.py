import Master as M
import sys
import time

config_file_path = str(sys.argv[-1])

Tunnel, PLC_IP, Threshold_Percent, Read_Steps, Center, count, pulsing_count = M.config_reader(config_file_path, "Dog Leg")

print(Tunnel)
if Tunnel.lower() == 'west':
    import Tag_Database_West as Tags
elif Tunnel.lower() == 'east':
    import Tag_Database_East as Tags
else:
    import Tag_Database as Tags
    
    
#####################################################################
# Connect to PLC & gather start values
#####################################################################
Client = M.Make_Client(PLC_IP)

Pulsing_Status = bool(M.Read(Client, Tags.Pulsing_Output, Bool = True)) #Detects whether pulsing or not

if Pulsing_Status:
    count = pulsing_count #Integer. How many points will be recorded at each step and averaged over if pulsing
    sleep_time = 0.010 #Float.(S) time between averaged reads
else:
    count = count #Non-pulsing count of avg
    sleep_time = 0.010 #Non-pulsing sleep

#WF6H_Tag, WF7H_Tag, WF6V_Tag, WF7V_Tag = Tags.WF6H, Tags.WF7H, Tags.WF6V, Tags.WF7V #6 and 7 dog leg
WF6H_Tag, WF7H_Tag, WF6V_Tag, WF7V_Tag = Tags.WF6H, Tags.WF7H, Tags.WF6V, Tags.WF7V #16 and 17 dog leg

WF6H_Start = M.Read(Client, WF6H_Tag)
WF7H_Start = M.Read(Client, WF7H_Tag)
WF6V_Start = M.Read(Client, WF6V_Tag)
WF7V_Start = M.Read(Client, WF7V_Tag)

######################################
# Establish list of actively tracked parameters
######################################

Tag_List = [[WF6H_Tag, False], [WF7H_Tag, False], [WF6V_Tag, False], [WF7V_Tag, False], \
                [Tags.Emitted_Current, True], [Tags.Recirculator_Halfway, True], \
                [Tags.Recirculator_Bypass, True], [Tags.CU_V, False], [Tags.SRF_Pt, False]]

######################################
# Run dog leg
######################################

FOM = M.Dog_Leg(Client, WF6H_Tag, WF7H_Tag, WF6V_Tag, WF7V_Tag, \
              Tags.Recirculator_Bypass, Tags.Recirculator_Halfway, \
              Tag_List, \
              count = count, sleep_time = sleep_time, \
              #Delta_1 = 0.5, Delta_2 = 0.5, \
              Threshold_Percent = Threshold_Percent, Read_Steps = Read_Steps, move_to_center = Center, Tunnel = Tunnel)

input("Press enter to close finish this script")