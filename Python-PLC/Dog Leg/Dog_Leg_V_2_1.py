#Created by: Austin Czyzewski
#    Date Tested: 02/24/2020
#         Date last updated: 02/24/2020

############
### Notes:
# There is a suspected offset in the magntude of the Bypass dump and loop mid, this may cause a minor discrepancy from visually observed data
# and the data collected here.
############

import Master as M
import time
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import Tag_Database as Tags



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
    - Analyze the data and output the middle of the FWHM
    - Give the user the option to ramp to the optimal values
'''

#Establish a connection to the PLC

Client = M.Make_Client('10.50.0.20')

start_time = time.time()
#Dog Leg

Move_To_Optimum = False

Target_Tag = Tags.Recirculator_Halfway #Int or Str. Which Tag we are reading, 11109 is Loop bypass dump as of 01/01/2020
Target_Tag_2 = Tags.Recirculator_Bypass
Threshold_Percent = 35 #Float. The percentage of beam that we want to collect in order to turn the Dog Leg around

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

EC_Tag = Tags.Emitted_Current

###################################################################################################

### End of User Defined Variables

###################################################################################################

WF6H_Start = M.Read(Client,WF6H_Tag) #Starting value for Window Frame 6 Horizontal
WF7H_Start = M.Read(Client,WF7H_Tag) #Starting value for Window Frame 7 Horizontal

WF6V_Start = M.Read(Client,WF6V_Tag) #Starting value for Window Frame 6 Horizontal
WF7V_Start = M.Read(Client,WF7V_Tag) #Starting value for Window Frame 7 Horizontal

EC = M.Read(Client, EC_Tag)

start_time = time.time()

#Summing the start current of the two dumps
Start_Current = (M.Read(Client, Target_Tag, Average = True, count = count,sleep_time = sleep) + M.Read(Client, Target_Tag_2, Average = True, count = count,sleep_time = sleep))
    
H_Broken = False #Creating the check tag for the Horizontal dog leg, starting out as false as no errors could have been raised yet
V_Broken = False #Creating the check tag for the Vertical dog leg, starting out as false as no errors could have been raised yet

###################################################################################################

### #Creating the data structure

###################################################################################################

# 6 Columns, unknown rows
# WF6H | WF6V | WF7H | WF7V | Dump 1 | Dump 2 | Emitted Current |
#  0   |  1   |  2   |  3   |   4    |   5    |        6        |

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

print("Right Displacement")

Full_Data_Set.append([M.Read(Client, WF6H_Tag), #Adding the value of the current WF6H request point
                     M.Read(Client, WF7H_Tag), #Adding the value of the current WF7H request point
                     M.Read(Client, WF6V_Tag), #Adding the value of the current WF6V request point
                     M.Read(Client, WF7V_Tag), #Adding the value of the current WF7V request point
                     M.Read(Client, Target_Tag, Average = True, count = count, sleep_time = sleep), #Averaging and then adding the target 1 value
                     M.Read(Client, Target_Tag_2, Average = True, count = count, sleep_time = sleep), #Averaging and adding target 2 value
                     M.Read(Client, EC_Tag)]) #Adding the current emitted current

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
            
    WF6H_Write_Value = WF6H_Start + (Delta_6/Read_Steps)*Right_Steps #Calculated value to walk 6 to the right
    WF7H_Write_Value = WF7H_Start - (Delta_7/Read_Steps)*Right_Steps #Calculated value to walk 7 to the left
    
    M.Write(Client, WF6H_Tag, WF6H_Write_Value) #Writing to 6h
    M.Write(Client, WF7H_Tag, WF7H_Write_Value) #Writing to 7h
    
    Target_1_Collection = M.Read(Client, Target_Tag, Average = True, count = count, sleep_time = sleep) #Averaging the collection at these points for each dump
    Target_2_Collection = M.Read(Client, Target_Tag_2, Average = True, count = count, sleep_time = sleep) 
    
    Full_Data_Set.append([M.Read(Client, WF6H_Tag), M.Read(Client, WF7H_Tag), M.Read(Client, WF6V_Tag), M.Read(Client, WF7V_Tag), Target_1_Collection, Target_2_Collection, M.Read(Client, EC_Tag)]) #Adding all the data from this point to the array
    
    if abs(Target_1_Collection + Target_2_Collection) < abs(Threshold_Percent*Start_Current*.01): #Checking our threshold
        break

#############################
### Back to Center
#############################

print("Moving to center")

M.Ramp_Two(Client, WF6H_Tag, WF7H_Tag, Magnet_1_Stop = WF6H_Start, Magnet_2_Stop = WF7H_Start, Resolution = Right_Steps) #Moves back to the start in the same # of steps taken

#############################
### To the left
#############################

#####
# --------------- This is the same loop as above with flipped signs for the calculations
#####
print("Left Displacement")

Full_Data_Set.append([M.Read(Client, WF6H_Tag),
                     M.Read(Client, WF7H_Tag),
                     M.Read(Client, WF6V_Tag),
                     M.Read(Client, WF7V_Tag),
                     M.Read(Client, Target_Tag, Average = True, count = count, sleep_time = sleep),
                     M.Read(Client, Target_Tag_2, Average = True, count = count, sleep_time = sleep),
                     M.Read(Client, EC_Tag)])

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
    
    Full_Data_Set.append([M.Read(Client, WF6H_Tag), M.Read(Client, WF7H_Tag), M.Read(Client, WF6V_Tag), M.Read(Client, WF7V_Tag), Target_1_Collection, Target_2_Collection, M.Read(Client, EC_Tag)])
    
    if abs(Target_1_Collection + Target_2_Collection) < abs(Threshold_Percent*Start_Current*.01):
        break

#############################
### Back to Center
#############################

print("Moving to center")

M.Ramp_Two(Client, WF6H_Tag, WF7H_Tag, Magnet_1_Stop = WF6H_Start, Magnet_2_Stop = WF7H_Start, Resolution = Left_Steps)

###################################################################################################

### Starting the Vertical walk

###################################################################################################

#############################
### Upward
#############################

#####
# --------------- These are the same as the horizontal loops above
#####

print("Upward Displacement")

Full_Data_Set.append([M.Read(Client, WF6H_Tag),
                     M.Read(Client, WF7H_Tag),
                     M.Read(Client, WF6V_Tag),
                     M.Read(Client, WF7V_Tag),
                     M.Read(Client, Target_Tag, Average = True, count = count, sleep_time = sleep),
                     M.Read(Client, Target_Tag_2, Average = True, count = count, sleep_time = sleep),
                     M.Read(Client, EC_Tag)])

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
    
    Full_Data_Set.append([M.Read(Client, WF6H_Tag), M.Read(Client, WF7H_Tag), M.Read(Client, WF6V_Tag), M.Read(Client, WF7V_Tag), Target_1_Collection, Target_2_Collection, M.Read(Client, EC_Tag)])
    
    if abs(Target_1_Collection + Target_2_Collection) < abs(Threshold_Percent*Start_Current*.01):
        break

#############################
### Back to Center
#############################

print("Moving to center")

M.Ramp_Two(Client, WF6V_Tag, WF7V_Tag, Magnet_1_Stop = WF6V_Start, Magnet_2_Stop = WF7V_Start, Resolution = Upward_Steps, sleep_time = .100)

#############################
### Downward
#############################
print("Downward Displacement")

Full_Data_Set.append([M.Read(Client, WF6H_Tag),
                     M.Read(Client, WF7H_Tag),
                     M.Read(Client, WF6V_Tag),
                     M.Read(Client, WF7V_Tag),
                     M.Read(Client, Target_Tag, Average = True, count = count, sleep_time = sleep),
                     M.Read(Client, Target_Tag_2, Average = True, count = count, sleep_time = sleep),
                     M.Read(Client, EC_Tag)])

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
    
    Full_Data_Set.append([M.Read(Client, WF6H_Tag), M.Read(Client, WF7H_Tag), M.Read(Client, WF6V_Tag), M.Read(Client, WF7V_Tag), Target_1_Collection, Target_2_Collection, M.Read(Client, EC_Tag)])
    
    if abs(Target_1_Collection + Target_2_Collection) < abs(Threshold_Percent*Start_Current*.01):
        break

#############################
### Back to Center
#############################

print("Moving to center")

M.Ramp_Two(Client, WF6V_Tag, WF7V_Tag, Magnet_1_Stop = WF6V_Start, Magnet_2_Stop = WF7V_Start, Resolution = Downward_Steps, sleep_time = .100)

###################################################################################################

### Saving and Plotting

###################################################################################################

#############################
### Saving
#############################

#Saving To a Txt File with the format mentioned in the data structure above
now = datetime.today().strftime('%y%m%d_%H%M') #Taking the current time in YYMMDD_HHmm format to save the plot and the txt file

with open(now + ".txt",'w') as f: #Opening a file with the current date and time
    for line in Full_Data_Set:
        f.write(str(line).strip("([])")+'\n') #Writing each line in that file
    f.close() #Closing the file to save it
    
#############################
### Plotting
#############################

### Putting data into a more usable format

Full_Data_Array = np.array(Full_Data_Set) #Converting from a list to an array

Horizontal_6 = Full_Data_Array[:(Right_Steps + 2 + Left_Steps),0] #Defining the steps on in the horizontal
Horizontal_7 = Full_Data_Array[:(Right_Steps + 2 + Left_Steps),1]

Vertical_6 = Full_Data_Array[(Right_Steps + 2 + Left_Steps):,2] #Defining the steps only in the Vertical
Vertical_7 = Full_Data_Array[(Right_Steps + 2 + Left_Steps):,3]
Dump_1 = Full_Data_Array[:,4] #Dump 1 all values
Dump_2 = Full_Data_Array[:,5] #Dump 2 all values
Emitted_Current = Full_Data_Array[:,6] #Emitted current all values
Dump_Sum = Dump_1 + Dump_2 #All dump values

### Plotting

def convert_to_mms(locs): #Converting the xlabels to mm
    new_list = []
    for i in locs:
        new_list.append(round(i/.384*12,2)) #Our conversion formula
    return new_list

def Delta6_7(locs): #Converting the 6 values to the same displacement in 7
    new_list = []
    for i in locs:
        new_list.append(round(i/.384*.228,2))
    return new_list

#Dump Sum into percent from start
Horizontal_Percent = Dump_Sum[:(Right_Steps + 2 + Left_Steps)]/Emitted_Current[:(Right_Steps + 2 + Left_Steps)]*100 #Defining the percents
Vertical_Percent = Dump_Sum[(Right_Steps + 2 + Left_Steps):]/Emitted_Current[(Right_Steps + 2 + Left_Steps):]*100

#FWHM of all of our data
Horizontal_Above, Horizontal_Below, H_Width, Center_Value_6H, H_Goodsum, H_Badsum = M.FWHM(Horizontal_6, Horizontal_Percent, extras = True) #FWHM Calclations
Vertical_Above, Vertical_Below, V_Width, Center_Value_6V, V_Goodsum, V_Badsum = M.FWHM(Vertical_6, Vertical_Percent, extras = True)
_,_1,_2,Center_Value_7H,_3, _4 = M.FWHM(Horizontal_7, Horizontal_Percent, extras = True)
_,_1,_2,Center_Value_7V,_3, _4 = M.FWHM(Vertical_7, Vertical_Percent, extras = True)


#Plotting
plt.figure(figsize = (9,9)) #Changing the figure to be larger

ax1 = plt.subplot(1,1,1)
ax1.scatter(Horizontal_6 - Horizontal_6[0], Horizontal_Above, label = 'Horizontal above FWHM',color = 'C0', alpha = 0.75) #Plotting 6H Above FWHM
ax1.scatter(Horizontal_6 - Horizontal_6[0], Horizontal_Below, label = 'Horizontal below FWHM', color = 'C0', alpha = 0.5, marker = '.') #Plotting 6H below FWHM
ax1.scatter(Vertical_6 - Vertical_6[0], Vertical_Above, label = 'Vertical above FWHM', color = 'C1', alpha = 0.75) #Plotting 6V above FWHM
ax1.scatter(Vertical_6 - Vertical_6[0], Vertical_Below, label = 'Vertical below FWHM', color = 'C1', alpha = 0.5, marker = '.') #plotting 6V Below FWHM
ax1.set_xlabel("Displacement WF6 (Amps)", fontsize = 12) #Setting xlabel
ax1.set_ylabel("Collection from start (%); ({0:.2f}\u03BCA) collected at start".format(1000*abs(min(Dump_Sum))), fontsize = 12) #Making the y axis label
ax1.set_title("Dog Leg Taken at " + now, fontsize = 16) #Making the title 
ax1.legend(bbox_to_anchor = (0.5,0.27), loc = 'upper center') #Adding the legend and placing it in the bottom center of the plot

ax1.minorticks_on() #Turning on the minor axis
ax1.grid(True,alpha = 0.25,which = 'both',color = 'gray') #Making the grid (and making it more in the background)

locs = ax1.get_xticks() #Grabbing the xticks from that axis

ax2 = ax1.twiny() #Copying axis

ax2.set_xticks(locs) #Setting xticks to same position
ax2.set_xticklabels(convert_to_mms(locs)) #Converting to mm
ax2.xaxis.set_ticks_position('top') # set the position of the second x-axis to top
ax2.xaxis.set_label_position('top') # set the position of the second x-axis to top
ax2.spines['top'].set_position(('outward', 0)) #Setting the ticks to go out of graph area
ax2.set_xlabel('Displacement (mm)', fontsize = 12) #Label
ax2.set_xlim(ax1.get_xlim()) #Setting to the same limit as prior axis

ax3 = ax1.twiny() #Repeat for axis 3

ax3.set_xticks(locs)
ax3.set_xticklabels(Delta6_7(locs))
ax3.xaxis.set_ticks_position('bottom') # set the position of the second x-axis to bottom
ax3.xaxis.set_label_position('bottom') # set the position of the second x-axis to bottom
ax3.spines['bottom'].set_position(('outward', 40))
ax3.set_xlabel('Displacement WF7(Amps)', fontsize = 12)
ax3.set_xlim(ax1.get_xlim())

col_labels = ['WF6 Start (A)','WF7 Start (A)','FWHM', 'Center (6,7) (A)', 'Sum Above', 'Sum Below'] #Making the table column names
row_labels = ['Horizontal','Vertical','Params'] #making the table row names
table_vals = [[round(WF6H_Start,3), round(WF7H_Start,3), round(H_Width,3), "{:.3f}; {:.3f}".format(Center_Value_6H, Center_Value_7H), round(H_Goodsum,1), round(H_Badsum,1)],
              [round(WF6V_Start,3) , round(WF7V_Start,3), round(V_Width,3), "{:.3f}; {:.3f}".format(Center_Value_6V, Center_Value_7V) , round(V_Goodsum,1), round(V_Badsum,1)],
              ["Threshold %: {:.0f}".format(Threshold_Percent),"Zoom: {:.2f}".format(Zoom_In_Factor),"Scale: {:.2f}".format(Scale_Factor),
               "# H Steps: {:.0f}".format(Right_Steps + 2 + Left_Steps),"# V Steps: {:.0f}".format(Upward_Steps + 2 + Downward_Steps), "EC (mA): {:.3f}".format(EC)]] #Setting values

the_table = plt.table(cellText=table_vals, #Putting the table onto the plot
                  colWidths = [0.13]*6,
                  rowLabels=row_labels,
                  colLabels=col_labels,
                  loc='lower center', zorder = 1) #Putting in the center and in front of all else

plt.gca().set_ylim(bottom=-2) #Making sure the plot always goes below 0 in the y axis

plt.tight_layout() #configuring plot to not cut off extraneous objects like title and x axes

plt.savefig(now + "_graph.svg",transparent = True) #Saving the figure to a plot

if Move_To_Optimum == True: #If the option to move to the optimum is true, then move the magnets there
    print("Moving to optimum for 6 and 7")
    M.Ramp_Two(Client, WF6H_Tag, WF6V_Tag, Magnet_1_Stop = Center_Value_6H, Magnet_2_Stop = Center_Value_6V, Resolution = Read_Steps, sleep_time = .100)
    M.Ramp_Two(Client, WF7H_Tag, WF7V_Tag, Magnet_1_Stop = Center_Value_7H, Magnet_2_Stop = Center_Value_7V, Resolution = Read_Steps, sleep_time = .100)


print("This took {0:.1f} Seconds to run".format(time.time() - start_time)) #Printing the amount of time the dog leg took

plt.show()
