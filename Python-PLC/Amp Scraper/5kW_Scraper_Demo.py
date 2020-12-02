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
    print("{} raised as an error in the amplifier".format(print_list[disturbance]))

def communication_tester(Amp_IP, PLC_IP):
    amp_response = os.popen("ping {}".format(Amp_IP))
    PLC_response = os.popen("ping {}".format(PLC_IP))
    
def Writes(Client,Tags,Values):
    for Tag, Value in Tags, Values:
        M.Write(Client, Tag, Value)
    
#############################
## Connect to PLC, define Modbus addresses
#############################
import os
now = datetime.today().strftime('%y%m%d_%H%M%S.%f')
year = now[:2]
month = now[2:4]
day = now[4:6]
datadir = "AmpData/" + year + '/' + month + '/' + day

try:
    os.makedirs(datadir)
except:
    pass

filename = '{}/Amp_data_{}.csv'.format(datadir, datetime.today().strftime('%y%m%d_%H%M'))

PLC_IP = "10.1.2.100"
Amp_IP = '10.40.0.125'
Sleep_Check_Time = 10 #Seconds
point_time = 1 #seconds

try:
    #Client = M.Make_Client(PLC_IP) #Connecting to PLC
    pass
except:
    print("Connection to PLC Failed")
    print("Waiting...")
    time.sleep(Sleep_Check_Time)
    try:
        #Client = M.Make_Client(PLC_IP)
        pass
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
Name_it = True
_ = 0
while True:
    _ += 1
    Client = M.Make_Client(PLC_IP)
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
    for num,j in enumerate(zip(Names,Values)):
        print(num,j)
        
    LOI = [8,32,33,38,39,40,41,42,43,36,37]
    Modbus = [50015,50063,50065,50075,50077,50079,50081,50083,50085,50087,50089]
    
    Values = np.array([float(Value) for Value in Values[1:]])
    try:
        if Name_it:
            with open(filename,'w') as file:
                file.write("YYMMDD_HHMMSS.ssssss, ")
                for Name in Names[1:]:
                    file.write(str(Name) + ', ')
                file.write('\n')
                file.close()
    except:
        now = datetime.today().strftime('%y%m%d_%H%M%S.%f')
        # filename = '{}/Amp_data_{}.csv'.format(datadir, datetime.today().strftime('%y%m%d_%H%M'))
        year = now[:2]
        month = now[2:4]
        day = now[4:6]
        datadir =  "AmpData/" + year + '/' + month + '/' + day
        print(filename[-11:-9])
        if now[4:6] == filename[-11:-9]:
            filename = '{}/Amp_data_{}.csv'.format(datadir, datetime.today().strftime('%y%m%d_%H%M'))
            try:
                os.makedirs(datadir)
            except:
                print('Directory structure already exists')
                pass
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
        print("Write to Excel failed")
        filename = '{}/Amp_data_{}.csv'.format(datadir, datetime.today().strftime('%y%m%d_%H%M'))
            
#         M.Write_Multiple(Client, Tag_List[0], Values) #Writing all of the values to the PLC
#         Writes(Client, [],[])

    try:
        for Value_Index, Mod in zip(LOI, Modbus):
            print(Mod, Values[Value_Index-1])
            M.Write(Client, Mod, Values[Value_Index-1])
        pass
    except:
        
        print("Write to PLC failed...")
        print("Waiting...")
        time.sleep(Sleep_Check_Time/10)
        
        try: #Try again with fresh connection
            #M.Make_Client(PLC_IP)
            #M.Write_Multiple(Client, Tag_List[0], Values)
            pass
        except:
            print("Write to PLC failed after {:.2f} second wait".format(Sleep_Check_Time/10))
        
            
    pull_push = time.time()-start_time
    print("{:.1f} ms pull-push".format(1000* (pull_push))) 
    
    if pull_push > 1:
        pull_push = 0
    
    time.sleep(point_time-pull_push) #This is already slow enough. We don't need to waste any more time
    Name_it = False
    #os.system('cls')
    if _ > 45:
        break