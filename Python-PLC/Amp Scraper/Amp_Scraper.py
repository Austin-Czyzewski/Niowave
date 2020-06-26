###############################################################################
###############################################################################
# Author: Austin Czyzewski
# Date: 06/25/2020; Date Tested: 06/25/2020
#
# Purpose: Take amplifier status data and push into PLC. Reduce need for 
#           conversions, have more readily accessible data, etc.
#
# Method:
#       1- Connect to PLC, Connect to Amplifier
#       2- Read XML file from Amplifier, import as list
#       3- String format to get rid of HTML + XML overhead
#       4- Store Names and Values
#       5- Write Values to the PLC with pre-defined modbus addresses
#       6- Go back to step 2
#
###############################################################################
###############################################################################


#############################
## imports
#############################

import time #import our time module to allow us to wait
import os #allow us to interface with command line prompts like curl
import numpy as np #math functions
import Master as M #importing the PLC communications library

#############################
## Connect to PLC, define Modbus addresses
#############################
PLC_IP = "10.1.2.100"
Amp_IP = '10.1.2.125'
Sleep_Check_Time = 10 #Seconds

try:
    Client = M.Make_Client(PLC_IP) #Connecting to PLC
except:
    print("Connection to PLC Failed")
    print("Waiting...")
    time.sleep(Sleep_Check_Time)
    try:
        Client = M.Make_Client(PLC_IP)
    except:
        print("Connection after {} seconds failed. Ending script...".format(Sleep_Check_Time))
        time.sleep(10)
        exit()
        
Conversion_Rate = 50 #Convert amp forward power from percent to Watts

filler = 1001 #Temporary puppy
Tag_List = np.arange(50001,50100,2) #List of tags in order of writing
                                    #Only one really needed
           
#############################
## Begin reading loop
#############################
while True:
    start_time = time.time() #taking the time to evaluate how long the process 
                                #takes to run
                                
    #############################
    ## Grab the data from the amplifier; make more usable
    #############################

    #Amp_Response = os.popen("curl -u admin:admin http://169.254.1.1/status.xml") #5KW off network
    
    #Amp_Response = os.popen("curl -u admin:admin http://10.50.0.21/status.xml") #West Tunnel
    try:
        Amp_Response = os.popen("curl -u admin:admin http://{}/status.xml".format(Amp_IP))
        #Above grabs data from xml file
    except:
        print("Failed to connect to the amplifier")
        
    amp = list() #Create an empty list 
    
    for line in Amp_Response: #iterate over each value of the Amp Response
        
        amp.append(line.split('>')) #Split into two lines at the '>' in 
                                #<Name>Value<Name> format, creates 2 pieces

    Names = list() #Create empty lists of the names and values of each tag as 
    Values = list() #defined above
    
    for num, i in enumerate(amp): #For the index and each value in the list 
                                    #of responses
            
        amp[num][0] = amp[num][0].strip('<') #Get rid of the '<' in the Name 
                                                #value for aesthetic
            
        Names.append(amp[num][0]) #Add the now beautified name to the list 
                                    #of Names
            
        try: #Here we are going to try to do the following function but 
                #since some lines contain incorrect format, we have 
                #error handling in this form
                
            temp = i[1].split('<') #Split the second part of the string going 
                                    #from Value<Name to [Value, <Name]
                
            amp[num][1] = temp #Replace the Value<Name with list of 
                                #value and name
            if "!DEF" in amp[num][1]:
                Values.append("NaN")
            else:
                Values.append(amp[num][1][0]) #Only append the first value in the 
                                            #list [Value, <Name] to get Value
                
        except: #If our format is not in Value<Name then we add 
            Values.append('NaN') #this arbitrary string as filler
            
    Values[-1] = str(round(float(Values[8]) * Conversion_Rate,3)) #Adding the converted
                                                        # FWD Power value
    Names[-1] = "MeasuredFWDWatts"
    
#     for it in range(len(Names)):
#         print(Names[it], Values[it])
#         if "!DEF" in Values[it]:
#             Values[it] = 'Nan'
            
        
    os.system('cls') #Clears the print screen to save on memory 
                        #(Not needed if only writing to PLCs)

    #############################
    ## Write to the PLC
    #############################
    
    Values = np.array([float(Value) for Value in Values[1:]])
    
    
    try:
        M.Write_Multiple(Client, Tag_List[0], Values) #Writing all of the values to the PLC
    except:
        print("Write to PLC failed...")
        print("Waiting...")
        time.sleep(Sleep_Check_Time/10)
        try:
            M.Make_Client(PLC_IP)
            M.Write_Multiple(Client, Tag_List[0], Values)
        except:
            print("Write to PLC failed after {} second wait".format(Sleep_Check_Time/10))
        
    for Name, Value in zip(Names[1:], Values): #Here is filler for when we want 
                                            #to write these values to the PLC
            
    #    M.Write(Client, Tag_Num, float(Value)) #Writes to the Tag in Tag_List
        print(Name, Value)
        continue #Avoid parsing error with empty function for testing
        
    print("{:.3f} ms to run".format(1000* (time.time() - start_time))) 
    #Taking the current time and comparing to the start time. 
        #Printing the difference in ms
    
    #time.sleep(1) #sleep for designated amount of time in seconds
    