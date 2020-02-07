#Created by: Austin Czyzewski
#    Date Tested: 01/14/2020
#         Date last updated: 01/15/2020

############
### Notes:
# Known bug if the beam dump is shorted out/ we have unstable emission where the magnets may not return to the start. Always take a magnet save
#         when obtaining good collection or starting a leg of dog legs.
############

import Master as M
import time
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime



'''
Purpose: To scissor window frames 6 and 7 in the horizontal and vertical directions while collecting data on the current collected.
    We are doing this to collect better data on the dog leg process, save man hours, and produce a quantification for when a good
    'dog leg' is acheived. This program will spit out a familiar plot while also storing the data for future analysis to be done.


Logic walkthrough:
    - Read the Starting current of the Dump
    - At the beginning of each write, check to insure no human intervention has occurred with the write, if it has, kill the loop, continue to produce graphs and txt file
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

start_time = time.time()
#Dog Leg

Target_Tag = Tags.Recirculator_Halfway #Int or Str. Which Tag we are reading, 11109 is Loop bypass dump as of 01/01/2020
Target_Tag_2 = Tags.Recirculator_Bypass
Threshold_Percent = 20 #Float. The percentage of beam that we want to collect in order to turn the Dog Leg around

Zoom_In_Factor = 1 #This is how much we want to zoomn in if we are interested in an artifact at the center of the dog leg or want higher precision in the center

Scale_Factor = 0.91 #This is how much we want to scale off of the excel documents used prior to Dog Legs
#Starting the loop to read the current collected

#Take the starting value of the Target Tag, use for the threshold

Read_Steps = 40 #Integer. Number of steps to be taken in the Dog Leg. Must be an integer
count = 20 #Integer. How many points will be recorded at each step and averaged over.
sleep_time = 10 #Float.(ms)Sleep for 20 ms, this is tested to not overload PLC or give redundant data
sleep = sleep_time/1000 #Setting the sleep time to ms


Delta_6 = 0.384*Scale_Factor/Zoom_In_Factor #Change in Window Frame 6 Values throughout the test, standard is 0.384 from Dog Leg Excel sheets (01/01/2020)
Delta_7 = 0.228*Scale_Factor/Zoom_In_Factor #Change in Window Frame 7 Values throughout the test, standard is 0.228 from Dog Leg Excel sheets (01/01/2020)

#Window Frames Horizontal

WF6H_Tag = Tags.WF6H #The tag for Window Frame 6 Horizontal
WF7H_Tag = Tags.WF7H #The tag for Window Frame 7 Horizontal

WF6V_Tag = Tags.WF6V #Window Frame 6 Vertical Tag
WF7V_Tag = Tags.WF7V #Window Frame 7 Vertical Tag

###################################################################################################

### End of User Defined Variables

###################################################################################################

WF6H_Start = M.Read(Client,WF6H_Tag) #Starting value for Window Frame 6 Horizontal
WF7H_Start = M.Read(Client,WF7H_Tag) #Starting value for Window Frame 7 Horizontal

WF6V_Start = M.Read(Client,WF6V_Tag) #Starting value for Window Frame 6 Horizontal
WF7V_Start = M.Read(Client,WF7V_Tag) #Starting value for Window Frame 7 Horizontal

start_time = time.time()

#Summing the start current of the two dumps
Start_Current = (M.Read(Client, Target_Tag, Average = True, count = count,sleep_time = sleep) + M.Read(Client, Target_Tag_2, Average = True, count = count,sleep_time = sleep))
    
H_Broken = False #Creating the check tag for the Horizontal dog leg, starting out as false as no errors could have been raised yet
V_Broken = False #Creating the check tag for the Vertical dog leg, starting out as false as no errors could have been raised yet

###################################################################################################

### #Creating the data structure

###################################################################################################

# 6 Columns, unknown rows
# WF6H | WF6V | WF7H | WF7V | Dump 1 | Dump 2 |
#  0   |  1   |  2   |  3   |   4    |   5    |

Full_Data_Set = []

# & 
#Convert to an array and then access the rows like this:
#  Full_Data_Set[x,y][z]
# x: this is the row
# y: this is the column
# z: (optional) value within that column (like row, but in a format that can be used to select multiple numbers instead of a range or single number)

#Example:
# plt.plot(Full_Data_Set[:iterator_1,0],Full_Data_Set[:iterator_1,4])
# The above example would plot WF6H vs Dump_1

###################################################################################################

### Starting the Horizontal walk

###################################################################################################

#############################
### To the right
#############################

Full_Data_Set.append([M.Read(Client, WF6H_Tag),
                     M.Read(Client, WF7H_Tag),
                     M.Read(Client, WF6V_Tag),
                     M.Read(Client, WF7V_Tag),
                     M.Read(Client, Target_Tag, Average = True, count = count, sleep_time = sleep),
                     M.Read(Client, Target_Tag_2, Average = True, count = count, sleep_time = sleep)])

for Right_Steps in range(1, Read_Steps + 1):
    
    if Right_Steps != 1: #Don't check on the first run due to absence of Window Frame write values
        
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
            
    WF6H_Write_Value = WF6H_Start + (Delta_6/Read_Steps)*Right_Steps
    WF7H_Write_Value = WF7H_Start - (Delta_7/Read_Steps)*Right_Steps
    
    M.Write(Client, WF6H_Tag, WF6H_Write_Value)
    M.Write(Client, WF7H_Tag, WF7H_Write_Value)
    
    Target_1_Collection = M.Read(Client, Target_Tag, Average = True, count = count, sleep_time = sleep)
    Target_2_Collection = M.Read(Client, Target_Tag_2, Average = True, count = count, sleep_time = sleep)
    
    Full_Data_Set.append([M.Read(Client, WF6H_Tag), M.Read(Client, WF7H_Tag), M.Read(Client, WF6V_Tag), M.Read(Client, WF7V_Tag), Target_1_Collection, Target_2_Collection])
    
    if abs(Target_1_Collection + Target_2_Collection) < abs(Threshold_Percent*Start_Current*.01):
        break

#############################
### Back to Center
#############################

M.Ramp_Two(Client, WF6H_Tag, WF7H_Tag, Magnet_1_Stop = WF6H_Start, Magnet_2_Stop = WF7H_Start, Resolution = Right_Steps)

#############################
### To the left
#############################

Full_Data_Set.append([M.Read(Client, WF6H_Tag),
                     M.Read(Client, WF7H_Tag),
                     M.Read(Client, WF6V_Tag),
                     M.Read(Client, WF7V_Tag),
                     M.Read(Client, Target_Tag, Average = True, count = count, sleep_time = sleep),
                     M.Read(Client, Target_Tag_2, Average = True, count = count, sleep_time = sleep)])

for Left_Steps in range(1, Read_Steps + 1):
    if H_Broken == True:
        break
    if V_Broken == True:
        break
    if Left_Steps != 1: #Don't check on the first run due to absence of Window Frame write values
        
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
            
    WF6H_Write_Value = WF6H_Start - (Delta_6/Read_Steps)*Left_Steps
    WF7H_Write_Value = WF7H_Start + (Delta_7/Read_Steps)*Left_Steps
    
    M.Write(Client, WF6H_Tag, WF6H_Write_Value)
    M.Write(Client, WF7H_Tag, WF7H_Write_Value)
    
    Target_1_Collection = M.Read(Client, Target_Tag, Average = True, count = count, sleep_time = sleep)
    Target_2_Collection = M.Read(Client, Target_Tag_2, Average = True, count = count, sleep_time = sleep)
    
    Full_Data_Set.append([M.Read(Client, WF6H_Tag), M.Read(Client, WF7H_Tag), M.Read(Client, WF6V_Tag), M.Read(Client, WF7V_Tag), Target_1_Collection, Target_2_Collection])
    
    if abs(Target_1_Collection + Target_2_Collection) < abs(Threshold_Percent*Start_Current*.01):
        break

#############################
### Back to Center
#############################

M.Ramp_Two(Client, WF6H_Tag, WF7H_Tag, Magnet_1_Stop = WF6H_Start, Magnet_2_Stop = WF7H_Start, Resolution = Left_Steps)

###################################################################################################

### Starting the Vertical walk

###################################################################################################

#############################
### Upward
#############################

Full_Data_Set.append([M.Read(Client, WF6H_Tag),
                     M.Read(Client, WF7H_Tag),
                     M.Read(Client, WF6V_Tag),
                     M.Read(Client, WF7V_Tag),
                     M.Read(Client, Target_Tag, Average = True, count = count, sleep_time = sleep),
                     M.Read(Client, Target_Tag_2, Average = True, count = count, sleep_time = sleep)])

for Upward_Steps in range(1, Read_Steps + 1):
    if H_Broken == True:
        break
    if V_Broken == True:
        break
    if Upward_Steps != 1: #Don't check on the first run due to absence of Window Frame write values
        
        temp_check_6 = M.Read(Client,WF6V_Tag) #Take the current value of WF6H
        temp_check_7 = M.Read(Client,WF7V_Tag) #Take the current value of WF7H
        
        #Comparing the current value to the last write value, if it is different, this updates the break loop for both Horizontal and Vertical
        if abs(temp_check_6 - WF6V_Write_Value) >= 0.001: #WF6H Check
            H_Broken = True
            V_Broken = True
            print("Loop Broken")
            break
        if abs(temp_check_7 - WF7V_Write_Value) >= 0.001: #WF7H Check
            H_Broken = True
            V_Broken = True
            print("Loop Broken")
            break
            
    WF6V_Write_Value = WF6V_Start + (Delta_6/Read_Steps)*Upward_Steps
    WF7V_Write_Value = WF7V_Start - (Delta_7/Read_Steps)*Upward_Steps
    
    M.Write(Client, WF6V_Tag, WF6V_Write_Value)
    M.Write(Client, WF7V_Tag, WF7V_Write_Value)
    
    Target_1_Collection = M.Read(Client, Target_Tag, Average = True, count = count, sleep_time = sleep)
    Target_2_Collection = M.Read(Client, Target_Tag_2, Average = True, count = count, sleep_time = sleep)
    
    Full_Data_Set.append([M.Read(Client, WF6H_Tag), M.Read(Client, WF7H_Tag), M.Read(Client, WF6V_Tag), M.Read(Client, WF7V_Tag), Target_1_Collection, Target_2_Collection])
    
    if abs(Target_1_Collection + Target_2_Collection) < abs(Threshold_Percent*Start_Current*.01):
        break

#############################
### Back to Center
#############################

M.Ramp_Two(Client, WF6V_Tag, WF7V_Tag, Magnet_1_Stop = WF6V_Start, Magnet_2_Stop = WF7V_Start, Resolution = Upward_Steps, sleep_time = .100)

#############################
### Downward
#############################

Full_Data_Set.append([M.Read(Client, WF6H_Tag),
                     M.Read(Client, WF7H_Tag),
                     M.Read(Client, WF6V_Tag),
                     M.Read(Client, WF7V_Tag),
                     M.Read(Client, Target_Tag, Average = True, count = count, sleep_time = sleep),
                     M.Read(Client, Target_Tag_2, Average = True, count = count, sleep_time = sleep)])

for Downward_Steps in range(1, Read_Steps + 1):
    if H_Broken == True:
        break
    if V_Broken == True:
        break
    if Downward_Steps != 1: #Don't check on the first run due to absence of Window Frame write values
        
        temp_check_6 = M.Read(Client,WF6V_Tag) #Take the current value of WF6H
        temp_check_7 = M.Read(Client,WF7V_Tag) #Take the current value of WF7H
        
        #Comparing the current value to the last write value, if it is different, this updates the break loop for both Horizontal and Vertical
        if abs(temp_check_6 - WF6V_Write_Value) >= 0.001: #WF6H Check
            H_Broken = True
            V_Broken = True
            print("Loop Broken")
            break
        if abs(temp_check_7 - WF7V_Write_Value) >= 0.001: #WF7H Check
            H_Broken = True
            V_Broken = True
            print("Loop Broken")
            break
            
    WF6V_Write_Value = WF6V_Start - (Delta_6/Read_Steps)*Downward_Steps
    WF7V_Write_Value = WF7V_Start + (Delta_7/Read_Steps)*Downward_Steps
    
    M.Write(Client, WF6V_Tag, WF6V_Write_Value)
    M.Write(Client, WF7V_Tag, WF7V_Write_Value)
    
    Target_1_Collection = M.Read(Client, Target_Tag, Average = True, count = count, sleep_time = sleep)
    Target_2_Collection = M.Read(Client, Target_Tag_2, Average = True, count = count, sleep_time = sleep)
    
    Full_Data_Set.append([M.Read(Client, WF6H_Tag), M.Read(Client, WF7H_Tag), M.Read(Client, WF6V_Tag), M.Read(Client, WF7V_Tag), Target_1_Collection, Target_2_Collection])
    
    if abs(Target_1_Collection + Target_2_Collection) < abs(Threshold_Percent*Start_Current*.01):
        break

#############################
### Back to Center
#############################

M.Ramp_Two(Client, WF6V_Tag, WF7V_Tag, Magnet_1_Stop = WF6V_Start, Magnet_2_Stop = WF7V_Start, Resolution = Downward_Steps, sleep_time = .100)

###################################################################################################

### Saving and Plotting

###################################################################################################

#############################
### Saving
#############################

#Saving To a Txt File with the format mentioned in the data structure above
now = datetime.today().strftime('%y%m%d_%H%M') #Taking the current time in YYMMDD_HHmm format to save the plot and the txt file

with open(now + ".txt",'w') as f:
    for line in Full_Data_Set:
        f.write(str(line).strip("([])")+'\n')
    f.close()
    
#############################
### Plotting
#############################

### Putting data into a more usable format

Full_Data_Array = np.array(Full_Data_Set)

Horizontal_6 = Full_Data_Array[:(Right_Steps + 2 + Left_Steps),0]
Horizontal_7 = Full_Data_Array[:(Right_Steps + 2 + Left_Steps),1]

Vertical_6 = Full_Data_Array[(Right_Steps + 2 + Left_Steps):,2]
Vertical_7 = Full_Data_Array[(Right_Steps + 2 + Left_Steps):,3]
Dump_1 = Full_Data_Array[:,4]
Dump_2 = Full_Data_Array[:,5]
Dump_Sum = Dump_1 + Dump_2

### Plotting

#Converting to mms of displacement
Horizontal_In_mms = (Horizontal_6 - WF6H_Start)/Delta_6*15/Zoom_In_Factor #Our max displacement is 15 mms
Vertical_In_mms = (Vertical_6 - WF6V_Start)/Delta_6*15/Zoom_In_Factor

#Dump Sum into percent from start
Horizontal_Percent = Dump_Sum[:(Right_Steps + 2 + Left_Steps)]/Start_Current*100
Vertical_Percent = Dump_Sum[(Right_Steps + 2 + Left_Steps):]/Start_Current*100

#Plotting
plt.figure(figsize = (9,6)) #Changing the figure to be larger
plt.minorticks_on() #Turning on the minor axis
plt.grid(True,alpha = 0.25,which = 'both',color = 'gray') #Making the grid (and making it more in the background)

plt.scatter(x = Horizontal_In_mms,y = Horizontal_Percent,label = 'Horizontal',alpha = 0.5) #plotting horizontal
plt.scatter(x = Vertical_In_mms,y = Vertical_Percent,label = 'Vertical', alpha = 0.5) #plotting vertical

plt.gca().set_ylim(bottom=-2)
#plt.gca().invert_yaxis()

plt.legend() #Making the legend for the plot

plt.xlabel("Displacement (mm)") #Making the x axis label
plt.ylabel("Collection from start (%); ({0:.3f}\u03BCA) collected at start".format(1000*abs(Start_Current))) #Making the y axis label
plt.title("Dog Leg Taken at " + now) #Making the title
plt.suptitle("WF6H:{0:.3f}; WF6V:{1:.3f}; WF7H:{2:.3f}; WF8H:{3:.3f} (Amps)".format(WF6H_Start,WF6V_Start,WF7H_Start,WF7V_Start)) #Creating the label below the title

plt.savefig(now + "_graph.svg",transparent = True, dpi = 600) #Saving the figure to a plot
#plt.savefig(now + "_graph.png",dpi = 600,transparent = True) #This would save to a high resolution png (For easy printing of multiple graphs on one sheet of paper or whatever you want a png for)

print("This took {0:.1f} Seconds to run".format(time.time() - start_time))

plt.show()
