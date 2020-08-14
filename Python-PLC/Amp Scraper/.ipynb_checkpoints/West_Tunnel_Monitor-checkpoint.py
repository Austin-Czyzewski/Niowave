###############################################################################
###############################################################################
# Author: Austin Czyzewski

# Date: 07/13/2020
#
# Purpose: Take amplifier status data and write to a csv. Store so we can watch interlocks tripped and amp status

#
###############################################################################
###############################################################################


#############################
## imports
#############################

import time 
import os
import numpy as np
from datetime import datetime


def append_to_file(filename, additions, newline = True):
    with open(filename, 'a') as file:
        if newline:
            file.write(str(additions) + '\n')
        else:
            file.write(str(additions))
    file.close()
    
def raise_alarm(disturbance):
    print_list = ['Carrier off', 'Overdrive off', 'VSWR', 'Voltage Error', 'RF Input level', 'Temperature','AGC Mode']
    print(print_list[disturbance])
    
#############################
## Connect to PLC, define Modbus addresses
#############################
datadir = 'ampdata'

try:
    os.mkdir(datadir)
except:
    pass

filename = '{}/Amp_CSV_{}.csv'.format(datadir, datetime.today().strftime('%y%m%d_%H%M'))

#PLC_IP = "10.1.2.100"
Amp_IP = '10.50.0.21'
Sleep_Check_Time = 10 #Seconds
point_time = 1 #seconds
        
#Convert amp forward power from percent to Watts        
Conversion_Rate = 50 

#modbus addresses
Tag_List = np.arange(50001,50100,2)
           
#############################
## Runtime loop
#############################
Name_it = True
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
    
    if Name_it:
        with open(filename,'w') as file:
            file.write("YYMMDD_HHMMSS.ssssss, ")
            for Name in Names[1:]:
                file.write(str(Name) + ', ')
            file.write('\n')
            file.close()
    
    
    try:
        append_to_file(filename, datetime.today().strftime('%y%m%d_%H%M%S.%f') + ', ', newline = False)
        for Value in Values:            
            append_to_file(filename, "{}, ".format(Value), newline = False)
        append_to_file(filename, "{:.1f} ms".format(1000* (time.time() - start_time)))
    except:
        
        print("Write to PLC failed...")
        print("Waiting...")
        time.sleep(Sleep_Check_Time/10)
            
    pull_push = time.time()-start_time
    print("{:.1f} ms pull-push".format(1000* (pull_push))) 
    
    if pull_push > 1:
        pull_push = 0
    
    time.sleep(point_time-pull_push) #This is already slow enough. We don't need to waste any more time
    Name_it = False
    break