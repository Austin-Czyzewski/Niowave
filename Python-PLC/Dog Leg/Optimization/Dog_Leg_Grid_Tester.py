import Dog_Leg_Master as M
import time
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import Tag_Database as Tags

N = 5 #This will always be made an odd number by rounding up. This number needs to be an integer

Perturbation_Step = 0.035 #Amps, once upward and once downward


def grid(N, perturbation ,WFH_Start, WFV_Start):
    '''
    Take start value and output an N by N grid with new locations
    '''
    
    if N % 2 == 0: #Rounding up to get an even number of points on either side of the center
        N += 1
        
    WFH = [[0 for i in range(N)] for j in range(N)]
    WFV = [[0 for i in range(N)] for j in range(N)]
    for line in range(N):
        for point in range(N):
            WFH[line][point] = round(WFH_Start - (N//2 * perturbation) + point*perturbation, 3)
            WFV[line][point] = round(WFV_Start + (N//2 * perturbation) - line*perturbation, 3)
    WFH_list = list()
    WFV_list = list()
    for number, magnet in enumerate([WFH, WFV]):
        for line in magnet:
            for point in line:
                if number == 0:
                    WFH_list.append(point)
                else:
                    WFV_list.append(point)
    
    return WFH_list, WFV_list


start_time = time.time() #Grabbing the time at start to time process

Client = M.Make_Client('10.50.0.10')

Pulsing_Status = bool(M.Read(Client, Tags.Pulsing_Output, Bool = True)) #Detects whether pulsing or not

if Pulsing_Status:
    count = 25 #Integer. How many points will be recorded at each step and averaged over if pulsing
    sleep_time = 0.010 #Float.(S)
else:
    count = 10 #Non-pulsing count of steps to take
    sleep_time = 0.010 #Non-pulsing sleep

WF6H_Tag = Tags.WF6H
WF6V_Tag = Tags.WF6V
WF7H_Tag = Tags.WF7H
WF7V_Tag = Tags.WF7V

    
Tag_List = [[WF6H_Tag, False], [WF7H_Tag, False], [WF6V_Tag, False], [WF7V_Tag, False], \
            [Tags.Emitted_Current, True], [Tags.Recirculator_Halfway, True], \
            [Tags.Recirculator_Bypass, True], [Tags.CU_V, False], [Tags.SRF_Pt, False]]

WF1H_Start = M.Read(Client, WF6H_Tag) #Taking the start values of all of the Window Frame values
WF2H_Start = M.Read(Client, WF7H_Tag)
WF1V_Start = M.Read(Client, WF6V_Tag)
WF2V_Start = M.Read(Client, WF7V_Tag)

WF1_Vals = grid(N, Perturbation_Step, WF1H_Start, WF1V_Start) #Creating the grid we want to run over

for iteration in range(len(WF1_Vals[0])):
    #####################################
    ## This loop runs a dog leg at each point in the grid as created above
    #####################################
    
    print("WF6H Start: {}A, WF6V Start: {}A".format(WF1_Vals[0][iteration], WF1_Vals[1][iteration]))
    print("{} dog legs left in grid".format(len(WF1_Vals[0]) - iteration))
    M.Dog_Leg(Client, WF6H_Tag, WF7H_Tag, WF6V_Tag, WF7V_Tag, \
              Tags.Recirculator_Bypass, Tags.Recirculator_Halfway, \
              Tag_List, \
              WF1_Vals[0][iteration], WF2H_Start, \
              WF1_Vals[1][iteration], WF2V_Start, \
              count = count, sleep_time = sleep_time, \
              Threshold_Percent = 0, Read_Steps = 40)
    
    
################################
# A good place to do calculations with the data. All of the data is stored in .txt files in the folder with this data
################################


M.Ramp_Two(Client, WF6H_Tag, WF6V_Tag, WF1H_Start, WF1V_Start) #Moves the dog leg back to the center point (WF6H_Start and WF6V_Start). This would be a good chance to
                                                                # move the dog legs to our calculated optimum

print("This {0} x {0} grid took {1:.3f} seconds to run".format(N, time.time() - start_time))
