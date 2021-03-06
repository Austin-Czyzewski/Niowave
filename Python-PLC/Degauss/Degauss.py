import Master as M
import numpy as np
import matplotlib.pyplot as plt
import time
import Tag_Database as Tags

'''
Purpose:
    - Produce more reliable magnet saves for more consistent operation
    - Save labor-hours on finding low and high energy drift
    - More consistent operation for production of isotopes

Method:
    - Produce a Guassian Curve.
    - Assign the curve to a scaled magnet value
    - Run the program to degauss the magnets

'''

##### Turn to False if no plot output is desired
plot = True

##### Turn to False when fully running, true stops from actual writing
testing = True

######################################
#Adjustable Key Parameters
######################################

#If adjusting ANY of these, 

Time = 4 #Artbitrary scaling, defualt value
Amplitude = .05
Decay_Constant = .75 #Lower values = more peaks, longer decay time
                #higher values = more decay between each peak, recommended range
                # of 0.4 < x < 0.75
Points = 3000

Dipole_Amplitude = 5 #(Amps) The value we want Dipoles to reach in the peak
                        #This can also be set to the start value if need be

Frequency = 5 #Increase this value for more oscillations

WF_Amplitude = 3 #(Amps)

Sol_Amplitude = 4 #(Amps)

######################################
#PLC Parameters
######################################

Client = M.Make_Client("192.168.1.2")

Dipole_Start_Tag = Tags.DP1 #First Dipole we are controlling

Window_Frame_Start_Tag = Tags.WF1V #First Window Frame we are controlling

Solenoid_Start_Tag = Tags.Sol1 #First Solenoid we are controlling

Dipole_Count = 2 #Number of Dipoles 

Window_Frame_Count = 7 #Number of Window Frames

Solenoid_Count = 3 #Number of Solenoids (Not used currently)

Start_Time = time.time()

###################
#Uncomment the following to have amplitude start at the current setpoint
###################
#Dipole_Amplitude = M.Read(Client, Dipole_Start_Tag)

#WF_Amplitude = M.Read(Client, Window_Frame_Start_Tag)

#Sol_Amplitude = M.Read(Client, Solenoid_Start_Tag)

#######################################
#Producing the Gaussian
#######################################

x = np.linspace(0,Time*3/4*np.pi, Points) #Defining the number of points that we'll take

y = (Amplitude) * np.exp(Decay_Constant * -x) * np.cos((Frequency * np.pi * x)) #Producing the Guassian

x = np.linspace(0,len(x)*.1,len(x)) #Overwriting x to convert to seconds

y[-1] = 0 #Setting the last point in y to 0 so all magnets are at 0

#######################################
#Writing the y values to the magnets, scaled
#######################################

for pre_scaled_value in y:
    
    Dipoles = [] #Creating Dipole list (and emptying every loop)
    WFs = [] #Creating and emptying the list of WF values for the next write
    Sols = [] #Creating the list and the functionality just not using for now
    
    #Creating the correct sized list to input into the write_multiple function
    for _ in range(Dipole_Count):
        Dipoles.append(pre_scaled_value * Dipole_Amplitude)
        
    for _ in range(Window_Frame_Count * 2): #Multiplied by two because we have 
                                            #Horizontal and Vertical
        WFs.append(pre_scaled_value * WF_Amplitude)
    
    for _ in range(Solenoid_Count):
        Sols.append(pre_scaled_value * Sol_Amplitude)

    if testing == False:
        M.Write_Multiple(Client, Dipole_Start_Tag, Dipoles)
        M.Write_Multiple(Client, Window_Frame_Start_Tag, WFs)

        ##################################################
        #DO NOT UNCOMMENT UNTIL WE HAVE SOLENOID TOGGLING FUNCTIONALITY
        #M.Write_Multiple(Client, Solenoid_Start_Tag, Sols)
        ##################################################

        time.sleep(.05)

    else:
        continue
    
    

print("{0:.1f} Seconds to run".format(time.time() - Start_Time))

if plot == True:
    plt.plot(x,y* Dipole_Amplitude, label = 'Dipoles', alpha = 0.5)
    plt.plot(x,y* WF_Amplitude, label = 'Window Frames', alpha = 0.5)
    plt.plot(x,y * Sol_Amplitude, label = 'Solenoids', alpha = 0.5)
    plt.legend()
    plt.title("DeGaussing Path Taken")
    plt.xlabel("Seconds")
    plt.ylabel("Amps")
    plt.show()