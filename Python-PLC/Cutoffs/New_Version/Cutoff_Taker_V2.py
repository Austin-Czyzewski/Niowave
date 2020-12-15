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

******* Changes to Master File -- Gather() added inital_values for speed
******* Changes to Tag Database -- Added BH Pf slider bar params (bottom)

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

number_of_points = 50 #Resolution of steps taken in both cutoff measurements
Num_sawtooths_1 = 6 #number of points taken in the first cutoff
Num_sawtooths_2 = 6 #second cutoff
Ratio_From_Start = 0.8 #The amount to move the slider bar back up after running

################################################################
### Grab the operator input of V0 ranges #######################
################################################################

V0_1 = float(input("V0 Low Cutoff 2  "))
V0_2 = float(input("V0 High Cutoff  2  "))
V0_3 = float(input("V0 Low Cutoff 1  "))
V0_4 = float(input("V0 High Cutoff 1  "))

##V0_1 = 3.5
##V0_2 = 4
##V0_3 = 3.6
##V0_4 = 4.1

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

V0_Start_Value = M.Read(Client, Tags.V0_SP)
sleep_time = 10 #Don't take plateau data first run through

for index in range(Num_sawtooths_1): #First loop with V0_1 and V0_2
    
    #Taking the plateau data
    runtime = time.time()
    if index:
        while time.time() - runtime < sleep_time:
            Full_Data_Set.append(M.Gather(Client, Tag_List, \
                      initial_values = [\
                          time.time(), \
                          value]))
        
    #Start setting the sleep time if on the first pass in this loop
    start_time = time.time()
        
    #Ramp one way in V0 while collecting data
    for value in V0_List_1:
        M.Write(Client, Tags.V0_SP, value)
        Full_Data_Set.append(M.Gather(Client, Tag_List, \
                      initial_values = [\
                          time.time(), \
                          value]))
    
    #Finish setting the sleep time to what it took to ramp one way
    print(time.time()-start_time)
    
    #Taking the trough data
    runtime = time.time()
    while time.time() - runtime < sleep_time:
        Full_Data_Set.append(M.Gather(Client, Tag_List, \
                      initial_values = [\
                          time.time(), \
                          value]))
    
    #Reverse! Reverse!
    for value in V0_List_1[::-1]:
        M.Write(Client, Tags.V0_SP, value)
        Full_Data_Set.append(M.Gather(Client, Tag_List, \
                      initial_values = [\
                          time.time(), \
                          value]))
        
################################################################
### Cutoff 1 done. Now turning off BH and taking cutoff 2 ######
################################################################
Slider_Bar_Setpoint = M.Read(Client, Tags.BH_VVA_SP)

print(Slider_Bar_Setpoint)
M.Write(Client, Tags.BH_VVA_Reg_SW, False, Bool = True)
M.Write(Client, Tags.BH_VVA_SP, 0)

for index in range(Num_sawtooths_2):
    
    #Plateau (on first run it will match time of first loop)
    runtime = time.time()
    if index:
        while time.time() - runtime < sleep_time:
            Full_Data_Set.append(M.Gather(Client, Tag_List, \
                      initial_values = [\
                          time.time(), \
                          value]))
        
    #Begin setting new sleep time
    start_time = time.time()
        
    #Ramp it
    for value in V0_List_2:
        M.Write(Client, Tags.V0_SP, value)
        Full_Data_Set.append(M.Gather(Client, Tag_List, \
                      initial_values = [\
                          time.time(), \
                          value]))
    
    print(time.time() - start_time)
        
    #Trough
    runtime = time.time()
    while time.time() - runtime < sleep_time:
        Full_Data_Set.append(M.Gather(Client, Tag_List, \
                      initial_values = [\
                          time.time(), \
                          value]))
    
    #Bring it back now, y'all
    for value in V0_List_2[::-1]:
        M.Write(Client, Tags.V0_SP, value)
        Full_Data_Set.append(M.Gather(Client, Tag_List, \
                      initial_values = [\
                          time.time(), \
                          value]))

        
################################################################
### All measurements done. Now it's just storing the data
################################################################

with open("Real_Cutoffs.txt",'w') as f: 
    for line in Full_Data_Set:
        f.write(str(line).strip("([])")+'\n')
    f.close() #Close file to make sure it saves!
    
Full_Data_Array = np.array(Full_Data_Set) #Put data analysis after this line!

print(time.time() - time_1)
M.Write(Client, Tags.V0_SP, V0_Start_Value)
M.Write(Client, Tags.VO_VVA_SP, Slider_Bar_Setpoint * Ratio_From_Start)