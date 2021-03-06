'''
Cutoff_Tester.py
Author: Austin Czyzewski
Org date: 10/06/2020

Purpose: This script is meant to automate taking the V0 cutoffs 1 and 2
    using the method proposed by Andrew Schnepp and Sam Baurac. 
    In this method the gating field is fluctuated linearly with the 
    bias harmonic field both on and off to help compensate for change in
    position of the cathode. This data is used to determine the strength 
    of our accelerating fields and to help determine running parameters.
    
Example of how to use it:
    - Run it
'''


import Master as M
import Tag_Database as Tags
import numpy as np
import matplotlib.pyplot as plt
import time


time_1 = time.time()
Client = M.Make_Client("10.50.0.10")
M.Read(Client, Tags.WF1H) #Arbitrary read to establish trust (I think this part is weird to me)

################################################################
### Initialize #################################################
################################################################

V0_resolution = 50 #Resolution of steps taken in both cutoff measurements
Num_sawtooths_1 = 1 #number of points taken in the first cutoff
Num_sawtooths_2 = 1 #second cutoff


################################################################
### Grab the operator input of V0 ranges #######################
################################################################

##V0_1 = float(input("V0 Setpoint 1  "))
##V0_2 = float(input("V0 Setpoint 2  "))
##V0_3 = float(input("V0 Setpoint 3  "))
##V0_4 = float(input("V0 Setpoint 4  "))

V0_1 = 3.5
V0_2 = 4
V0_3 = 3.6
V0_4 = 4.1

################################################################
### List of tags to read at every step #########################
################################################################

#(Sorry for the stupid double list format. I wrote Gather() before I knew how often I'd use it)

Tag_List = [[Tags.CU_Pt, False], [Tags.CU_V, False],[Tags.BH_Pt, False], \
            [Tags.V0_Read, False], [Tags.Emitted_Current, False], \
            [Tags.Cu_Gun_Temp, False], [Tags.Power_Read, False],\
            [Tags.BH_OC_Temp, False], [Tags.CU_Gun_CHWR_Ave, False]]

Full_Data_Set = list()

################################################################
### Set up the lists to run and then run the loop ##############
################################################################

# V0_List_1 = np.arange(V0_1, V0_2 + V0_resolution, V0_resolution)
# V0_List_2 = np.arange(V0_3, V0_4 + V0_resolution, V0_resolution)

V0_List_1 = np.linspace(V0_1, V0_2, number_of_points)
V0_List_2 = np.linspace(V0_3, V0_4, number_of_points)


#sleep_time = 0 #Don't take plateau data first run through

for index in range(Num_sawtooths_1): #First loop with V0_1 and V0_2
    
    #Taking the plateau data
    runtime = time.time()
    if index:
        while time.time() - runtime < sleep_time:
            Full_Data_Set.append(M.Gather(Client, Tag_List))
        
    #Start setting the sleep time if on the first pass in this loop
    if not index:
        start_time = time.time()
        
    #Ramp one way in V0 while collecting data
    for value in V0_List_1:
        M.Write(Client, Tags.V0_SP, value)
        Full_Data_Set.append(M.Gather(Client, Tag_List))
    
    #Finish setting the sleep time to what it took to ramp one way
    if not index:
        sleep_time = (time.time() - start_time)/3
        print(sleep_time*3)
    #Taking the trough data
    runtime = time.time()
    while time.time() - runtime < sleep_time:
        Full_Data_Set.append(M.Gather(Client, Tag_List))
    
    #Reverse! Reverse!
    for value in V0_List_1[::-1]:
        M.Write(Client, Tags.V0_SP, value)
        Full_Data_Set.append(M.Gather(Client, Tag_List))
        
################################################################
### Cutoff 1 done. Now turning off BH and taking cutoff 2 ######
################################################################

M.Write(Client, Tags.BH_VVA_Reg_SW, False, Bool = True)
M.Write(Client, Tags.BH_VVA_SP, 0)

for index in range(Num_sawtooths_2):
    
    #Plateau (on first run it will match time of first loop)
    runtime = time.time()
    if index:
        while time.time() - runtime < sleep_time:
            Full_Data_Set.append(M.Gather(Client, Tag_List))
        
    #Begin setting new sleep time
    if not index:
        start_time = time.time()
        
    #Ramp it
    for value in V0_List_2:
        M.Write(Client, Tags.V0_SP, value)
        Full_Data_Set.append(M.Gather(Client, Tag_List))
    
    #Sleep time pt.II
    if not index:
        sleep_time = (time.time() - start_time)/3
        print(sleep_time*3)
        
    #Trough
    runtime = time.time()
    while time.time() - runtime < sleep_time:
        Full_Data_Set.append(M.Gather(Client, Tag_List))
    
    #Bring it back now, y'all
    for value in V0_List_2[::-1]:
        M.Write(Client, Tags.V0_SP, value)
        Full_Data_Set.append(M.Gather(Client, Tag_List))

        
################################################################
### All measurements done. Now it's just storing the data
################################################################

with open("Testing_Cutoffs.txt",'w') as f: 
    for line in Full_Data_Set:
        f.write(str(line).strip("([])")+'\n')
    f.close() #Close file to make sure it saves!
    
Full_Data_Array = np.array(Full_Data_Set) #Put data analysis after this line!

print(time.time() - time_1)

time.sleep(120)