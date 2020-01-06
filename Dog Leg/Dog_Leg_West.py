#Created by: Austin Czyzewski
#    Date Tested: 12/13/2019
#         Date last updated: 01/03/2020


import Master as M
import time
import matplotlib.pyplot as plt
from datetime import datetime



'''
Purpose: To scissor window frames 6 and 7 in the horizontal and vertical directions while collecting data on the current collected.
    We are doing this to collect better data on the dog leg process, save man hours, and produce a quantification for when a good
    'dog leg' is acheived. This program will spit out a familiar plot while also storing the data for future analysis to be done.


Logic walkthrough:
    - Read the Starting current of the Dump
    - At the beginning of each run, check to insure no human intervention has occurred with the write, if it has, kill the loop, continue to produce graphs and txt file
    - Add the appropriate step to each magnet
    - Read the current many times and then take the average of that current and store it alongside the written values for the magnets
    - Every step of the way check if the current has dropped below a specified threshold, if it has, then walk the magnets backs where they came from by the steps taken,
         plus the same amount of read steps going the other way.
    - Repeat the same safety checks, always check each step that the current hasn't reached a lowpoint beyond the threshold
    - When it has, or it reaches the end, turn the magnets back around to walk back to where they started.
    - Repeat for the other set of magnets (Vertical)
    - Plot and produce txt file with Magnet settings in the left column and current readbacks in the right

'''

#Establish a connection to the PLC

Client = M.Make_Client('10.50.0.10')

#Dog Leg

Target_Tag = 11111 #Int or Str. Which Tag we are reading, 11109 is Loop bypass dump as of 01/01/2020
Target_Tag_2 = 11113
Threshold_Percent = 0 #Float. The percentage of beam that we want to collect in order to turn the Dog Leg around

Zoom_In_Factor = 1 #This is how much we want to zoomn in if we are interested in an artifact at the center of the dog leg or want higher precision in the center

#Starting the loop to read the current collected

#Take the starting value of the Target Tag, use for the threshold

read_steps = 40 #Integer. Number of steps to be taken in the Dog Leg. Must be an integer
count = 10 #Integer. How many points will be recorded at each step and averaged over.
sleep_time = 10 #Float.(ms)Sleep for 20 ms, this is tested to not overload PLC or give redundant data
sleep = sleep_time/1000 #Setting the sleep time to ms


Delta_6 = 0.384/Zoom_In_Factor #Change in Window Frame 6 Values throughout the test, standard is 0.384 from Dog Leg Excel sheets (01/01/2020)
Delta_7 = 0.228/Zoom_In_Factor #Change in Window Frame 7 Values throughout the test, standard is 0.228 from Dog Leg Excel sheets (01/01/2020)

collected_list_H = [] #Storing values for the magnets throughout the Horizontal Dog Leg
collected_list_V = [] #Storing values for the magnets throughout the Vertical Dog Leg

#Window Frames Horizontal

WF6H_Tag = 20223 #The tag for Window Frame 6 Horizontal
WF7H_Tag = 20227 #The tag for Window Frame 7 Horizontal

WF6H_Start = M.Read(Client,WF6H_Tag) #Starting value for Window Frame 6 Horizontal
WF7H_Start = M.Read(Client,WF7H_Tag) #Starting value for Window Frame 7 Horizontal

WF6H_list = [] #Storing the values for the horizontal run for Window Frame 6
WF7H_list = [] #Storing the values for the horizontal run for Window Frame 7

start_time = time.time()

temp_list = []
    
for _ in range(count):
    temp_list.append(M.Read(Client,Target_Tag)) #Appending to the temporary list to average over later
    temp_list.append(M.Read(Client,Target_Tag_2))

    time.sleep(sleep) #Sleep for the time defined in start values

Start_Current = sum(temp_list)/(count*2) #Summing the values collected

H_Broken = False #Creating the check tag for the Horizontal dog leg, starting out as false as no errors could have been raised yet
V_Broken = False #Creating the check tag for the Vertical dog leg, starting out as false as no errors could have been raised yet

#######################################################################################################################

#Loop for the Horizontal Dog Leg

#######################################################################################################################

#for i in range(read_steps + 1):
for i in range(read_steps+1):
    
    #Checking if the Horizontal Dog Leg is broken, if it is, then we break the loop, this is repeated for all if statements
    #        containing if H_Broken == True:
    
    if H_Broken == True: 
        break
    
    #Checking to see if there has been any human intervention since the last run, this is to act as a safety feature to
    #         alternatively kill the program if the run window is hidden
    
    if i != 0: #Don't check on the first run due to absence of Window Frame write values
        
        temp_check_6 = M.Read(Client,WF6H_Tag) #Take the current value of WF6H
        temp_check_7 = M.Read(Client,WF7H_Tag) #Take the current value of WF7H
        
        #Comparing the current value to the last write value, if it is different, this updates the break loop for both Horizontal and Vertical
        if abs(temp_check_6 - WF6H_Write_Value) >= 0.001: #WF6H Check
            H_Broken = True
            V_Broken = True
            print("Loop Broken")
            break
        if abs(temp_check_7 - WF7H_Write_Value) >= 0.001: #WF7H Check
            H_Broken = True
            V_Broken = True
            print("Loop Broken")
            break

    #Calculate the new write values from the step being taken 
    WF6H_Write_Value = WF6H_Start + (Delta_6/read_steps)*i
    WF7H_Write_Value = WF7H_Start - (Delta_7/read_steps)*i
    
    #Append the new write value to the Window Frame lists
    WF6H_list.append(WF6H_Write_Value)
    WF7H_list.append(WF7H_Write_Value)

    #Update a temporary value to be used when walking the loop back
    WF6H_max = WF6H_Write_Value
    WF7H_max = WF7H_Write_Value

    #Write to the PLC
    M.Write(Client, WF6H_Tag, WF6H_Write_Value)
    M.Write(Client, WF7H_Tag, WF7H_Write_Value)

    #Taking the value of the current collected and averaging, the list is temporary because it is updated each run
    temp_list = []

    for _ in range(count):
    	temp_list.append(M.Read(Client,Target_Tag)) #Appending to the temporary list to average over later
    	temp_list.append(M.Read(Client,Target_Tag_2))

    	time.sleep(sleep) #Sleep for the time defined in start values

    collection = sum(temp_list)/(count*2)
    collected_list_H.append(collection) #Storing the values in the collection list

    i_max = i #storing the maximum i value to be used to walk the loop back

    #This is to start the walk backward from the max horizontal value reached
    #    where we are checking to see that we
    #        1: haven't fallen below our threshold colletion and
    #        2: Haven't reached our maximum walking value
    #    When either of these conditions are satisfied, we start our walk in the other direction
    if abs(collection) < abs(Start_Current) * Threshold_Percent/100 or i == read_steps:
        #print('Start Horizontal Descent')
        for j in range(read_steps + i_max + 1): #Take the maximum value reached to go back to 0 (i_max) and then adding our read_steps (read_steps)
                                            #         to get us to our minimum for the Horizontal run
            #Same check as above to break the loop
            if H_Broken == True:
                break
                
            #Same check as above for human intervention
            if i != 0:
                
                temp_check_6 = M.Read(Client,WF6H_Tag)
                temp_check_7 = M.Read(Client,WF7H_Tag)
                

                if abs(temp_check_6 - WF6H_Write_Value) >= 0.001:
                    H_Broken = True
                    V_Broken = True
                    print("Loop Broken")
                    break
                if abs(temp_check_7 - WF7H_Write_Value) >= 0.001:
                    H_Broken = True
                    V_Broken = True
                    print("Loop Broken")
                    break

            #Same process as above to calculate the write values, only we are using the max value achieved and walking from there
            WF6H_Write_Value = WF6H_max - (Delta_6/read_steps)*j
            WF7H_Write_Value = WF7H_max + (Delta_7/read_steps)*j
            
            #Appending to our lists
            WF6H_list.append(WF6H_Write_Value)
            WF7H_list.append(WF7H_Write_Value)
            
            #Writing the new values
            M.Write(Client, WF6H_Tag, WF6H_Write_Value)
            M.Write(Client, WF7H_Tag, WF7H_Write_Value)

            #Storing the max achieved by this loop, in which case it is the minimum value acheived for window frame 6
            WF6H_min = WF6H_Write_Value
            WF7H_min = WF7H_Write_Value

            #Same loop as above for the current collected
            temp_list = []

            for _ in range(count):
    	        temp_list.append(M.Read(Client,Target_Tag)) #Appending to the temporary list to average over later
    	        temp_list.append(M.Read(Client,Target_Tag_2))

    	        time.sleep(sleep) #Sleep for the time defined in start values

            collection = sum(temp_list)/(count*2)
            collected_list_H.append(collection) #Storing the values in the collection list
                
            #We are storing j_max as the j-read_steps because this will tell us how far past 0 we walked
            j_max = j - read_steps

            #This is the same check as we used to enter this loop; however, this time we are checking that we don't
            #    walk past our minimum value. We are always looking for the threshold percent to be reached
            
            #This is creating a debounce that ensures that we at least walk back to zero before we check if we need to turn around
            if j < i: 
                collection = Start_Current #Setting to the start value to ensure that our check doesn't trip
                
            if abs(collection) < abs(Start_Current) * Threshold_Percent/100 or j == read_steps + i_max:
                #print('Start Horizontal Ascent')
                
                #Starting our loop for the walk back, j_max is used as it tells us how far past 0 we walked. An error
                #    will be produced if we didn't make it back to 0. Human intervention required at that point
                for k in range(j_max+1):

                    if H_Broken == True: #Same check to see if we need to break the loop, this runs at the beginning of the loop as to not
                                         #    not write any values to the magnets after we intended to break
                        break
                
                    if i != 0: #Same human intervention check as above
                        
                        temp_check_6 = M.Read(Client,WF6H_Tag)
                        temp_check_7 = M.Read(Client,WF7H_Tag)
                        

                        if abs(temp_check_6 - WF6H_Write_Value) >= 0.001:
                            H_Broken = True
                            V_Broken = True
                            print("Loop Broken")
                            break
                        if abs(temp_check_7 - WF7H_Write_Value) >= 0.001:
                            H_Broken = True
                            V_Broken = True
                            print("Loop Broken")
                            break

                    #Using the minimum value acheived and walking from there
                    WF6H_Write_Value = WF6H_min + (Delta_6/read_steps)*k
                    WF7H_Write_Value = WF7H_min - (Delta_7/read_steps)*k
                    
                    #Storing the values
                    WF6H_list.append(WF6H_Write_Value)
                    WF7H_list.append(WF7H_Write_Value)
                    
                    #Writing
                    M.Write(Client, WF6H_Tag, WF6H_Write_Value)
                    M.Write(Client, WF7H_Tag, WF7H_Write_Value)

                    #Same current collection loop as above
                    temp_list = []
                    for _ in range(count):
    	                temp_list.append(M.Read(Client,Target_Tag)) #Appending to the temporary list to average over later
    	                temp_list.append(M.Read(Client,Target_Tag_2))

    	                time.sleep(sleep) #Sleep for the time defined in start values

                    collection = sum(temp_list)/(count*2)
                    collected_list_H.append(collection) #Storing the values in the collection list
                #print("End Ascent")
                
                #When we are all the way done, we update the broken value to be True, this is so 
                #    we don't run through the list one more time and write any new values to the window frames
                H_Broken = True
                break
            
        
#print("Moving on to Vertical")
    



#Window Frames Vertical
    
WF6V_Tag = 20221 #Window Frame 6 Vertical Tag
WF7V_Tag = 20225 #Window Frame 7 Vertical Tag

WF6V_Start = M.Read(Client,WF6V_Tag) #Start value for Window Frame 6 Vertical
WF7V_Start = M.Read(Client,WF7V_Tag) #Start value for Window Frame 7 Vertical

WF6V_list = [] #Creating an empty list to store the vertical values to, this just makes it easier to manage for troubleshooting
WF7V_list = []

#print('Starting Vertical Ascent')
#######################################################################################################################

#Note: This is the same loop as above, all of the same logic is applied, the difference being in the human intervention loop
#    in the prior checks we would break both loops, but horizontal already ran so we only need to break vertical
#    Note the above loop for any concerns with this loop

#######################################################################################################################

for i in range(read_steps + 1):

    if V_Broken == True:
        break
    
    
    if i != 0:
        
        temp_check_6 = M.Read(Client,WF6V_Tag)
        temp_check_7 = M.Read(Client,WF7V_Tag)
        

        if abs(temp_check_6 - WF6V_Write_Value) >= 0.001:
            V_Broken = True
            print("Loop Broken")
            break
        if abs(temp_check_7 - WF7V_Write_Value) >= 0.001:
            V_Broken = True
            print("Loop Broken")
            break


    WF6V_Write_Value = WF6V_Start + (Delta_6/read_steps)*i
    WF7V_Write_Value = WF7V_Start - (Delta_7/read_steps)*i

    WF6V_list.append(WF6V_Write_Value)
    WF7V_list.append(WF7V_Write_Value)

    WF6V_max = WF6V_Write_Value
    WF7V_max = WF7V_Write_Value

    M.Write(Client, WF6V_Tag, WF6V_Write_Value)
    M.Write(Client, WF7V_Tag, WF7V_Write_Value)

    
    temp_list = []
    for _ in range(count):
    	temp_list.append(M.Read(Client,Target_Tag)) #Appending to the temporary list to average over later
    	temp_list.append(M.Read(Client,Target_Tag_2))

    	time.sleep(sleep) #Sleep for the time defined in start values

    collection = sum(temp_list)/(count*2)
    collected_list_V.append(collection) #Storing the values in the collection list

    i_max = i

    if abs(collection) < abs(Start_Current) * Threshold_Percent/100 or i == read_steps:
        #print("Starting Vertical Descent")
        for j in range(read_steps + i_max + 1):

            if V_Broken == True:
                break
        
            if i != 0:
                
                temp_check_6 = M.Read(Client,WF6V_Tag)
                temp_check_7 = M.Read(Client,WF7V_Tag)
                

                if abs(temp_check_6 - WF6V_Write_Value) >= 0.001:
                    V_Broken = True
                    print("Loop Broken")
                    break
                if abs(temp_check_7 - WF7V_Write_Value) >= 0.001:
                    V_Broken = True
                    print("Loop Broken")
                    break


            WF6V_Write_Value = WF6V_max - (Delta_6/read_steps)*j
            WF7V_Write_Value = WF7V_max + (Delta_7/read_steps)*j

            WF6V_list.append(WF6V_Write_Value)
            WF7V_list.append(WF7V_Write_Value)

            M.Write(Client, WF6V_Tag, WF6V_Write_Value)
            M.Write(Client, WF7V_Tag, WF7V_Write_Value)

            WF6V_min = WF6V_Write_Value
            WF7V_min = WF7V_Write_Value

            
            temp_list = []

            for _ in range(count):
    	        temp_list.append(M.Read(Client,Target_Tag)) #Appending to the temporary list to average over later
    	        temp_list.append(M.Read(Client,Target_Tag_2))

    	        time.sleep(sleep) #Sleep for the time defined in start values

            collection = sum(temp_list)/(count*2)
            collected_list_V.append(collection) #Storing the values in the collection list

            j_max = j - read_steps
            
            if j < i: 
                collection = Start_Current

            if abs(collection) < abs(Start_Current) * Threshold_Percent/100 or j == i_max + read_steps:
                #print("Starting Vertical Ascent")
        
                for k in range(j_max+1):

                    if V_Broken == True:
                        print("Loop Broken")
                        break
                
                    if i != 0:
                        
                        temp_check_6 = M.Read(Client,WF6V_Tag)
                        temp_check_7 = M.Read(Client,WF7V_Tag)
                        

                        if abs(temp_check_6 - WF6V_Write_Value) >= 0.001:
                            V_Broken = True
                            print("Loop Broken")
                            break
                        if abs(temp_check_7 - WF7V_Write_Value) >= 0.001:
                            V_Broken = True
                            print("Loop Broken")
                            break


                    WF6V_Write_Value = WF6V_min + (Delta_6/read_steps)*k
                    WF7V_Write_Value = WF7V_min - (Delta_7/read_steps)*k

                    WF6V_list.append(WF6V_Write_Value)
                    WF7V_list.append(WF7V_Write_Value)

                    M.Write(Client, WF6V_Tag, WF6V_Write_Value)
                    M.Write(Client, WF7V_Tag, WF7V_Write_Value)

                    
                    temp_list = []
                    for _ in range(count):
    	                temp_list.append(M.Read(Client,Target_Tag)) #Appending to the temporary list to average over later
    	                temp_list.append(M.Read(Client,Target_Tag_2))

    	                time.sleep(sleep) #Sleep for the time defined in start values

                    collection = sum(temp_list)/(count*2)
                    collected_list_V.append(collection) #Storing the values in the collection list
                #print("Done with Vertical Ascent")

                V_Broken = True
                break

            
        
#print("Loops Broken")

#######################################################################################################################

#End The repeat loop, moving on to data storage and plotting

#######################################################################################################################

##We are managing our lists and turning them into more usable versions for plotting and storing
WF6H_mm = [(i-WF6H_Start)/Delta_6*12/Zoom_In_Factor for i in WF6H_list] #This is using the conversion from excel file to convert magnet differences to mm
collected_perc_H = [100*(i/Start_Current) for i in collected_list_H] #Converting to percent
Horizontal = M.merge(WF6H_mm,collected_list_H) #This is merging the two lists above into one for easier writing to a text file


WF6V_mm = [(i-WF6V_Start)/Delta_6*12/Zoom_In_Factor for i in WF6V_list] #This is using the conversion from excel file to convert magnet differences to mm
collected_perc_V = [100*(i/Start_Current) for i in collected_list_V] #Converting to percent
Vertical = M.merge(WF6V_mm,collected_list_V) #This is merging the two lists above into one for easier writing to a text file

    
now = datetime.today().strftime('%y%m%d_%H%M') #Taking the current time in YYMMDD_HHmm format to save the plot and the txt file


#######################################################################################################################

#Starting saving the data to a txt file

#######################################################################################################################

with open(now +'.txt', 'w') as f: #Open a new file by writing to it named the date as created above + .txt
    f.write('WF6 (A) ,' + 'WF7 (A) ,' + 'Collected Current (mA)' + '\n' + '\n') #Creating the legend at the top of the txt file
    f.write('Horizontal' + '\n') #Write to that file start for the horizontal which will be one line "Horizontal"
    
    #Start a loop to write each value from the horizontal list to the file
    for i in range(len(WF6H_list)):
        f.write(str(WF6H_list[i]) + ',' + str(WF7H_list[i]) + ',' + str(collected_list_H[i]) +'\n') #Write the value of that line in the list to the file
        
    f.write('\n' + 'Vertical' + '\n') #Write to that file start for the vertical which will be one line "Vertical"
    
    #Start a loop to write each value from the vertical list to the file
    for j in range(len(WF6V_list)):
        f.write(str(WF6V_list[j]) + ',' + str(WF7V_list[j]) + ',' + str(collected_list_V[j]) +'\n') #Write the value of that line in the list to the file
    f.close() #Close the file, this ensures that it is saved and can be accessed later
#exit()

plt.figure(figsize = (9,6)) #Setting the figure size to be larger than default
plt.scatter(WF6H_mm, collected_perc_H,color = 'blue',label = 'Horizontal') #Plotting the horizontal dog leg as blue
plt.scatter(WF6V_mm, collected_perc_V,color = 'red',label = 'Vertical') #Plotting the verical dog leg as red
plt.xlabel('Displacement (mm)') #X axis label
plt.title("Dog Leg taken at {}".format(now))
plt.ylabel('Collected Current (% from Start)') #Y axis label
plt.legend()
if max(collected_perc_H) >= max(collected_perc_V):
    plt.ylim(-0.05,1.1*max(collected_perc_H))
else:
    plt.ylim(-0.05,1.1*max(collected_perc_V))
plt.grid(True)
#plt.gca().invert_yaxis() #Inverting the axis to produce a more familiar graph with max values as max and not min
plt.savefig(now + "_graph" + ".png") #Save the plot

end_time = time.time()

print("This Dog Leg took {0:.1f} seconds to run.".format(end_time - start_time))
plt.show() #Display a pop-up window with the plot this also clears the plot so do this last, stops the program from running until the plot is acknowledged
