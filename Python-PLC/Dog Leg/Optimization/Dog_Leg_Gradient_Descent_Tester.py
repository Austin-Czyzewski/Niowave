import Dog_Leg_Master as M
import time
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import Tag_Database as Tags
from plot_functions import plot_traj, plot_scatter, linear_fit
from read_dogleg import read_dogleg, gen_perturb_scan
start_time = time.time() #Grabbing the time at start to time process

Client = M.Make_Client('10.50.0.10')

Pulsing_Status = bool(M.Read(Client, Tags.Pulsing_Output, Bool = True)) #Detects whether pulsing or not

if Pulsing_Status:
    count = 25 #Integer. How many points will be recorded at each step and averaged over if pulsing
    sleep_time = 0.010 #Float.(ms)Sleep for 20 ms, this is tested to not overload PLC or give redundant data
else:
    count = 10 #Non-pulsing count of steps to take
    sleep_time = 0.010 #Non-pulsing sleep time
    
Tag_List = [[Tags.WF6H, False], [Tags.WF7H, False], [Tags.WF6V, False], [Tags.WF7V, False], \
            [Tags.Emitted_Current, True], [Tags.Recirculator_Halfway, True], \
            [Tags.Recirculator_Bypass, True], [Tags.CU_V, False], [Tags.SRF_Pt, False]]

WF6H_Start = M.Read(Client, Tags.WF6H) #Taking the start values of all of the Window Frame values
WF7H_Start = M.Read(Client, Tags.WF7H)
WF6V_Start = M.Read(Client, Tags.WF6V)
WF7V_Start = M.Read(Client, Tags.WF7V)

Perturbation_Step = 0.025 #Amps, once upward and once downward
def peturb(blah):
    WF6H_Dog_Legs = [WF6H_Start, WF6H_Start, WF6H_Start + Perturbation_Step]
    WF7H_Dog_Legs = [WF7H_Start, WF7H_Start, WF7H_Start]
    WF6V_Dog_Legs = [WF6V_Start, WF6V_Start + Perturbation_Step, WF6V_Start]
    WF7V_Dog_Legs = [WF7V_Start, WF7V_Start, WF7V_Start]

for iteration in range(len(WF6H_Dog_Legs)):
    M.Dog_Leg(Client, Tags.WF6H, Tags.WF6V, Tags.WF7H, Tags.WF7V, \
              Tags.Recirculator_Halfway, Tags.Recirculator_Bypass, \
              Tag_List, \
              WF6H_Dog_Legs[iteration], WF6V_Dog_Legs[iteration], \
              WF7H_Dog_Legs[iteration], WF7V_Dog_Legs[iteration], \
              count = count, sleep_time = sleep_time, \
              Theshold_Percent = 0)
