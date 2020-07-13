import Dog_Leg_Master as M
import Tag_Database as Tags
import time


Client = M.Make_Client('10.50.0.10')

Tag_List = [[WF6H_Tag, False], [WF7H_Tag, False], [WF6V_Tag, False], [WF7V_Tag, False], \
                [Tags.Emitted_Current, True], [Tags.Recirculator_Halfway, True], \
                [Tags.Recirculator_Bypass, True], [Tags.CU_V, False], [Tags.SRF_Pt, False]]

Pulsing_Status = bool(M.Read(Client, Tags.Pulsing_Output, Bool = True)) #Detects whether pulsing or not

if Pulsing_Status:
    count = 25 #Integer. How many points will be recorded at each step and averaged over if pulsing
    sleep_time = 0.010 #Float.(S)
else:
    count = 10 #Non-pulsing count of avg
    sleep_time = 0.010 #Non-pulsing sleep

WF6H_Tag, WF7H_Tag, WF6V_Tag, WF7V_Tag = Tags.WF6H, Tags.WF7H, Tags.WF6V, Tags.WF7V

WF6H_Start = M.Read(Client, WF6H_Tag)
WF7H_Start = M.Read(Client, WF7H_Tag)
WF6V_Start = M.Read(Client, WF6V_Tag)
WF7V_Start = M.Read(Client, WF7V_Tag)


FOM = M.Dog_Leg(Client, WF6H_Tag, WF7H_Tag, WF6V_Tag, WF7V_Tag, \
              Tags.Recirculator_Bypass, Tags.Recirculator_Halfway, \
              Tag_List, \
              WF6H_Start, M.Read(Client, Tags.WF7H), \
              WF6V_Start, M.Read(Client, Tags.WF7V), \
              count = count, sleep_time = sleep_time, \
              Threshold_Percent = 0, Read_Steps = 40)

print(FOM)

for _ in range(10):
    print('holup')
    time.sleep(1)
    
FOM_pert = M.Dog_Leg(Client, WF6H_Tag, WF7H_Tag, WF6V_Tag, WF7V_Tag, \
              Tags.Recirculator_Bypass, Tags.Recirculator_Halfway, \
              Tag_List, \
              WF6H_Start + 0.100, M.Read(Client, Tags.WF7H), \
              WF6V_Start + 0.100, M.Read(Client, Tags.WF7V), \
              count = count, sleep_time = sleep_time, \
              Threshold_Percent = 0, Read_Steps = 40, iteration = 20)

print(FOM_pert)