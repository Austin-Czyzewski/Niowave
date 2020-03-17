'''
Creator: Austin Czyzewski
Date: 02/12/2020

Purpose: To dog leg the second pass of the beam in the recirculating loop of our beam pass.

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

import Master as M
import time
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import Tag_Database as Tags


#Establish a connection to the PLC

Client = M.Make_Client('192.168.1.6')

start_time = time.time()
#Dog Leg

Target_Tag = Tags.RF_Beam_Mon #Int or Str. Which Tag we are reading, we are interested in the RF Beam monitor currently
Threshold_Percent = 0 #Float. The percentage of beam that we want to collect in order to turn the Dog Leg around

Zoom_In_Factor = 1 #This is how much we want to zoom in if we are interested in an artifact at the center of the dog leg or want higher precision in the center

Scale_Factor = 1 #This is how much we want to scale off of the excel documents used prior to Dog Legs
mm_factor = 1
#Starting the loop to read the current collected

#Take the starting value of the Target Tag, use for the threshold

Read_Steps = 40 #Integer. Number of steps to be taken in the Dog Leg. Must be an integer
count = 5 #Integer. How many points will be recorded at each step and averaged over.
sleep_time = 10 #Float.(ms)Sleep for 20 ms, this is tested to not overload PLC or give redundant data
sleep = sleep_time/1000 #Setting the sleep time to ms


Delta_12 = 0.500*Scale_Factor/Zoom_In_Factor #Change in Window Frame 12 Values throughout the test
Delta_13 = 0.500*Scale_Factor/Zoom_In_Factor #Change in Window Frame 13 Values throughout the test

#Window Frames Horizontal

WF12H_Tag = Tags.WF12H #The tag for Window Frame 12 Horizontal
WF13H_Tag = Tags.WF13H #The tag for Window Frame 13 Horizontal

WF12V_Tag = Tags.WF12V #Window Frame 12 Vertical Tag
WF13V_Tag = Tags.WF13V #Window Frame 13 Vertical Tag

###################################################################################################

### End of User Defined Variables

###################################################################################################

WF12H_Start = M.Read(Client,WF12H_Tag) #Starting value for Window Frame 12 Horizontal
WF13H_Start = M.Read(Client,WF13H_Tag) #Starting value for Window Frame 13 Horizontal

WF12V_Start = M.Read(Client,WF12V_Tag) #Starting value for Window Frame 12 Horizontal
WF13V_Start = M.Read(Client,WF13V_Tag) #Starting value for Window Frame 13 Horizontal

start_time = time.time()

#Summing the start current of the two dumps
Start_Current = M.Read(Client, Target_Tag, Average = True, count = count,sleep_time = sleep)
    
H_Broken = False #Creating the check tag for the Horizontal dog leg, starting out as false as no errors could have been raised yet
V_Broken = False #Creating the check tag for the Vertical dog leg, starting out as false as no errors could have been raised yet

###################################################################################################

### #Creating the data structure

###################################################################################################

# 6 Columns, unknown rows
# WF12H | WF13H | WF12V | WF13V | Target |
#  0   |  1   |  2   |  3   |   4    |

Full_Data_Set = []

# & 
#Convert to an array and then access the rows like this:
#  Full_Data_Set[x,y][z]
# x: this is the row
# y: this is the column
# z: (optional) value within that column (like row, but in a format that can be used to select multiple numbers instead of a range or single number)

#Example:
# plt.plot(Full_Data_Set[:iterator_1,0],Full_Data_Set[:iterator_1,4])
# The above example would plot WF12H vs Target_1_Collection

###################################################################################################

### Starting the Horizontal walk

###################################################################################################

#############################
### To the right
#############################

# First we are going to read the first value before we move at all
Full_Data_Set.append([M.Read(Client, WF12H_Tag),
                     M.Read(Client, WF13H_Tag),
                     M.Read(Client, WF12V_Tag),
                     M.Read(Client, WF13V_Tag),
                     M.Read(Client, Target_Tag, Average = True, count = count, sleep_time = sleep)])

#Now we are going to iterate up to the Read_Steps while making sure that we maintain our threshold collection
for Right_Steps in range(1, Read_Steps + 1):
    
    if Right_Steps != 1: #Don't check on the first run due to absence of Window Frame write values
        
        temp_check_12 = M.Read(Client,WF12H_Tag) #Take the current value of WF12H
        temp_check_13 = M.Read(Client,WF13H_Tag) #Take the current value of WF13H
        
        #Comparing the current value to the last write value, if it is different, this updates the break loop for both Horizontal and Vertical
        if abs(temp_check_12 - WF12H_Write_Value) >= 0.001: #WF12H Check
            H_Broken = True #Update the value of our loop breaker if there was human intervention so that further loops and this one don't run
            V_Broken = True
            print("Loop Broken")
            break
        if abs(temp_check_13 - WF13H_Write_Value) >= 0.001: #WF13H Check
            H_Broken = True
            V_Broken = True
            print("Loop Broken")
            break
            
    WF12H_Write_Value = WF12H_Start + (Delta_12/Read_Steps)*Right_Steps #Calculate the written value for each window frame
    WF13H_Write_Value = WF13H_Start - (Delta_13/Read_Steps)*Right_Steps
    
    M.Write(Client, WF12H_Tag, WF12H_Write_Value) #Write the calculated value to each window frame
    M.Write(Client, WF13H_Tag, WF13H_Write_Value)
    
    RFBM_Collection = M.Read(Client, Target_Tag, Average = True, count = count, sleep_time = sleep) #Read the Target tag count times and average
    
    Full_Data_Set.append([M.Read(Client, WF12H_Tag), M.Read(Client, WF13H_Tag), M.Read(Client, WF12V_Tag), M.Read(Client, WF13V_Tag), RFBM_Collection]) #Append all data to the current list
    
    if abs(RFBM_Collection) < abs(Threshold_Percent*Start_Current*.01): #Check to see that we are above our Threshold
        break

#############################
### Back to Center
#############################

#This function will walk us back to the start positions without taking data
M.Ramp_Two(Client, WF12H_Tag, WF13H_Tag, Magnet_1_Stop = WF12H_Start, Magnet_2_Stop = WF13H_Start, Resolution = Right_Steps)

#############################
### To the left
#############################

#Repeat the following loop with same logic with the difference being in the write value calculation
Full_Data_Set.append([M.Read(Client, WF12H_Tag),
                     M.Read(Client, WF13H_Tag),
                     M.Read(Client, WF12V_Tag),
                     M.Read(Client, WF13V_Tag),
                     M.Read(Client, Target_Tag, Average = True, count = count, sleep_time = sleep)])

for Left_Steps in range(1, Read_Steps + 1):
    if H_Broken == True:
        break
    if V_Broken == True:
        break
    if Left_Steps != 1: #Don't check on the first run due to absence of Window Frame write values
        
        temp_check_12 = M.Read(Client,WF12H_Tag) #Take the current value of WF12H
        temp_check_13 = M.Read(Client,WF13H_Tag) #Take the current value of WF13H
        
        #Comparing the current value to the last write value, if it is different, this updates the break loop for both Horizontal and Vertical
        if abs(temp_check_12 - WF12H_Write_Value) >= 0.001: #WF12H Check
            H_Broken = True
            V_Broken = True
            print("Loop Broken")
            break
        if abs(temp_check_13 - WF13H_Write_Value) >= 0.001: #WF13H Check
            H_Broken = True
            V_Broken = True
            print("Loop Broken")
            break
            
    WF12H_Write_Value = WF12H_Start - (Delta_12/Read_Steps)*Left_Steps
    WF13H_Write_Value = WF13H_Start + (Delta_13/Read_Steps)*Left_Steps
    
    M.Write(Client, WF12H_Tag, WF12H_Write_Value)
    M.Write(Client, WF13H_Tag, WF13H_Write_Value)
    
    RFBM_Collection = M.Read(Client, Target_Tag, Average = True, count = count, sleep_time = sleep)
    
    Full_Data_Set.append([M.Read(Client, WF12H_Tag), M.Read(Client, WF13H_Tag), M.Read(Client, WF12V_Tag), M.Read(Client, WF13V_Tag), RFBM_Collection])
    
    if abs(RFBM_Collection) < abs(Threshold_Percent*Start_Current*.01):
        break

#############################
### Back to Center
#############################

M.Ramp_Two(Client, WF12H_Tag, WF13H_Tag, Magnet_1_Stop = WF12H_Start, Magnet_2_Stop = WF13H_Start, Resolution = Left_Steps)

###################################################################################################

### Starting the Vertical walk

###################################################################################################

#############################
### Upward
#############################

Full_Data_Set.append([M.Read(Client, WF12H_Tag),
                     M.Read(Client, WF13H_Tag),
                     M.Read(Client, WF12V_Tag),
                     M.Read(Client, WF13V_Tag),
                     M.Read(Client, Target_Tag, Average = True, count = count, sleep_time = sleep)])

for Upward_Steps in range(1, Read_Steps + 1):
    if H_Broken == True:
        break
    if V_Broken == True:
        break
    if Upward_Steps != 1: #Don't check on the first run due to absence of Window Frame write values
        
        temp_check_12 = M.Read(Client,WF12V_Tag) #Take the current value of WF12H
        temp_check_13 = M.Read(Client,WF13V_Tag) #Take the current value of WF13H
        
        #Comparing the current value to the last write value, if it is different, this updates the break loop for both Horizontal and Vertical
        if abs(temp_check_12 - WF12V_Write_Value) >= 0.001: #WF12H Check
            H_Broken = True
            V_Broken = True
            print("Loop Broken")
            break
        if abs(temp_check_13 - WF13V_Write_Value) >= 0.001: #WF13H Check
            H_Broken = True
            V_Broken = True
            print("Loop Broken")
            break
            
    WF12V_Write_Value = WF12V_Start + (Delta_12/Read_Steps)*Upward_Steps
    WF13V_Write_Value = WF13V_Start - (Delta_13/Read_Steps)*Upward_Steps
    
    M.Write(Client, WF12V_Tag, WF12V_Write_Value)
    M.Write(Client, WF13V_Tag, WF13V_Write_Value)
    
    RFBM_Collection = M.Read(Client, Target_Tag, Average = True, count = count, sleep_time = sleep)
    
    Full_Data_Set.append([M.Read(Client, WF12H_Tag), M.Read(Client, WF13H_Tag), M.Read(Client, WF12V_Tag), M.Read(Client, WF13V_Tag), RFBM_Collection])
    
    if abs(RFBM_Collection) < abs(Threshold_Percent*Start_Current*.01):
        break

#############################
### Back to Center
#############################

M.Ramp_Two(Client, WF12V_Tag, WF13V_Tag, Magnet_1_Stop = WF12V_Start, Magnet_2_Stop = WF13V_Start, Resolution = Upward_Steps, sleep_time = .100)

#############################
### Downward
#############################

Full_Data_Set.append([M.Read(Client, WF12H_Tag),
                     M.Read(Client, WF13H_Tag),
                     M.Read(Client, WF12V_Tag),
                     M.Read(Client, WF13V_Tag),
                     M.Read(Client, Target_Tag, Average = True, count = count, sleep_time = sleep)])

for Downward_Steps in range(1, Read_Steps + 1):
    if H_Broken == True:
        break
    if V_Broken == True:
        break
    if Downward_Steps != 1: #Don't check on the first run due to absence of Window Frame write values
        
        temp_check_12 = M.Read(Client,WF12V_Tag) #Take the current value of WF12H
        temp_check_13 = M.Read(Client,WF13V_Tag) #Take the current value of WF13H
        
        #Comparing the current value to the last write value, if it is different, this updates the break loop for both Horizontal and Vertical
        if abs(temp_check_12 - WF12V_Write_Value) >= 0.001: #WF12H Check
            H_Broken = True
            V_Broken = True
            print("Loop Broken")
            break
        if abs(temp_check_13 - WF13V_Write_Value) >= 0.001: #WF13H Check
            H_Broken = True
            V_Broken = True
            print("Loop Broken")
            break
            
    WF12V_Write_Value = WF12V_Start - (Delta_12/Read_Steps)*Downward_Steps
    WF13V_Write_Value = WF13V_Start + (Delta_13/Read_Steps)*Downward_Steps
    
    M.Write(Client, WF12V_Tag, WF12V_Write_Value)
    M.Write(Client, WF13V_Tag, WF13V_Write_Value)
    
    RFBM_Collection = M.Read(Client, Target_Tag, Average = True, count = count, sleep_time = sleep)
    
    Full_Data_Set.append([M.Read(Client, WF12H_Tag), M.Read(Client, WF13H_Tag), M.Read(Client, WF12V_Tag), M.Read(Client, WF13V_Tag), RFBM_Collection])
    
    if abs(RFBM_Collection) < abs(Threshold_Percent*Start_Current*.01):
        break

#############################
### Back to Center
#############################

M.Ramp_Two(Client, WF12V_Tag, WF13V_Tag, Magnet_1_Stop = WF12V_Start, Magnet_2_Stop = WF13V_Start, Resolution = Downward_Steps, sleep_time = .100)

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

Horizontal_12 = Full_Data_Array[:(Right_Steps + 2 + Left_Steps),0]
Horizontal_13 = Full_Data_Array[:(Right_Steps + 2 + Left_Steps),1]

Vertical_12 = Full_Data_Array[(Right_Steps + 2 + Left_Steps):,2]
Vertical_13 = Full_Data_Array[(Right_Steps + 2 + Left_Steps):,3]
Target_1_Collection = Full_Data_Array[:,4]

### Plotting

#Converting to mms of displacement
Horizontal_In_mms = (Horizontal_12 - WF12H_Start)/Delta_12*mm_factor/Zoom_In_Factor #Our max displacement is 15 mms
Vertical_In_mms = (Vertical_12 - WF12V_Start)/Delta_12*mm_factor/Zoom_In_Factor

#Dump Sum into percent from start
Horizontal_Percent = Target_1_Collection[:(Right_Steps + 2 + Left_Steps)]/Start_Current*100
Vertical_Percent = Target_1_Collection[(Right_Steps + 2 + Left_Steps):]/Start_Current*100

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
plt.suptitle("WF12H:{0:.3f}; WF12V:{1:.3f}; WF13H:{2:.3f}; WF8H:{3:.3f} (Amps)".format(WF12H_Start,WF12V_Start,WF13H_Start,WF13V_Start)) #Creating the label below the title

plt.savefig(now + "_graph.svg",transparent = True, dpi = 600) #Saving the figure to a plot
#plt.savefig(now + "_graph.png",dpi = 600,transparent = True) #This would save to a high resolution png (For easy printing of multiple graphs on one sheet of paper or whatever you want a png for)

print("This took {0:.1f} Seconds to run".format(time.time() - start_time))

plt.show()
