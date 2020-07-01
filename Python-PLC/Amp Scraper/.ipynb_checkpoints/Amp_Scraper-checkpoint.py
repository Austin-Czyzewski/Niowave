###############################################################################
###############################################################################
# Author: Austin Czyzewski

# Date: 06/25/2020; Version Date: 07/01/2020
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

import time 
import os
import numpy as np
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
        
#Convert amp forward power from percent to Watts        
Conversion_Rate = 50 

#modbus addresses
Tag_List = np.arange(50001,50100,2)
           
#############################
## Runtime loop
#############################

while True:
    start_time = time.time()
                            

    ######################################################################
    ## Note:
    ## This is where things get slowed down the most. 
    ## Unfortunately, web scraping is not the quickest
    ######################################################################
    
    try:
        Amp_Response = os.popen("curl -u admin:admin http://{}/status.xml".format(Amp_IP))
        #Above grabs data from amp output xml file
    except:
        print("Failed to connect to the amplifier")
    #print(len())
    Amp_Readout = list()
    
    for line in Amp_Response:
        
        Amp_Readout.append(line.split('>')) #Splits <Name>Value<Name> into <Name, Value<Name

    Names = list()
    Values = list() 
    
    for num, i in enumerate(Amp_Readout):  
                                   
            
        Amp_Readout[num][0] = Amp_Readout[num][0].strip('<') #<Name to Name ##aesthetic##
        
        Names.append(Amp_Readout[num][0]) 
            
        try: #This try-except is to handle the non-data lines of our html
                                
            Amp_Readout[num][1] = i[1].split('<') #Value<Name to [Value, <Name]
            
            if "!DEF" in Amp_Readout[num][1]: #!DEF is bad, we like NaNs
                Values.append("NaN")
                
            else:
                Values.append(Amp_Readout[num][1][0]) #who cares about <Name anymore?
                
        except: 
            
            Values.append('NaN') 
    
    try: #This try-except is to add a converted value and to act as a check that we are 
            #actually getting data
            
        Values[-1] = str(round(float(Values[8]) * Conversion_Rate,3)) #Adding the converted
                                                        # FWD Power value
        Names[-1] = "MeasuredFWDWatts"
        
    except:
        print("Error grabbing data from {}".format(Amp_IP))
        print("Detected Names: {} Detected Values: {}".format(len(Values), len(Names)))
        
        continue
            

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
        
        try: #Try again with fresh connection
            M.Make_Client(PLC_IP)
            M.Write_Multiple(Client, Tag_List[0], Values)
            
        except:
            print("Write to PLC failed after {:.2f} second wait".format(Sleep_Check_Time/10))
        
        
    os.system('cls') #clear print screen
        
    for Name, Value in zip(Names[1:], Values): 
        print(Name, Value)
        
    print("{:.1f} ms pull-push".format(1000* (time.time() - start_time))) 
    
    #time.sleep(1) #This is already slow enough. We don't need to waste any more time
