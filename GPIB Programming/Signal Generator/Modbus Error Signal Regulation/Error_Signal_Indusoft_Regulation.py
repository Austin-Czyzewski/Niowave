import GPIB_FUNCS as GPIB #Importing our GPIB communication functions for easier comprehension and use
import pyvisa #import GPIB communication module
import time #imports time to sleep program temporarily
import Master as M
import numpy as np
import Tag_Database as Tags
from datetime import datetime

Client = M.Make_Client('192.168.1.2')

Pulsing_Tag = Tags.Pulsing_Output #Assign Modbus address here
Running_Tag = Tags.Error_Signal_Regulation #Assign Modbus address here
Reset_Tag = Tags.Error_Signal_Reset #Assign Modbus address here
Regulation_Setpoint_Tag = Tags.Regulation_Setpoint_Reset #Assign Modbus address here

RM = pyvisa.ResourceManager() #pyVISA device manager
Resources = RM.list_resources() #Printing out all detected device IDs

try:
    SG = RM.open_resource(Resources[0]) #Opening the Signal generator as an object
    OS = RM.open_resource(Resources[1]) #Opening the oscilloscope as an object
    
    Start_Freq = SG.query("FREQ:CW?")
    print("Starting Frequency of Signal Generator: {} Hz".format(Start_Freq))
else:
    SG = RM.open_resource(Resources[1]) #Opening the Signal generator as an object
    OS = RM.open_resource(Resources[0]) #Opening the oscilloscope as an object
    
    Start_Freq = SG.query("FREQ:CW?")
    print("Starting Frequency of Signal Generator: {} Hz".format(Start_Freq))
    
IF_Channel = 3 #The channel that the error signal is on
Trigger_Channel = 4 #The channel which shows the SRF pulse
Trigger_Level = 20   /1000 #mv #The level of the pulse trigger
Read_Start_Voltage = True

Measurement = 3 #Measurement channel
Step_size = 20 #(Hz) Change in frequency with each regulation step
Pulse_Step_Size = 10 #(Hz) Change in frequency with each regulation step when pulsing
Max_Threshold = 100000 #(Hz) Total amount of frequency change before automatically tripping off program
Walk_Threshold = 0.5 #(mV) Deviation from 0 the error signal needs to be before CW regulation kicks in
Pulse_Walk_Threshold = 0.5 #(mV) Deviation from 0 the error signal needs before pulsing regulation kicks in
Wait_after_step = 0.0400 #Seconds, the time waited after a step is taken, necessary to allow oscope measurements to change
Wait_between_reads = 0.0100 #Seconds, currently not used, supplemented by GUI time between reads
Interlock_Threshold_mv = 30 #mv, this is the amount of deviation before regulation trips off


size = 8 #Size marker used universally between buttons

Loops_Debounce = 1
Long = False #The form that our measurement is output from the o-scope, depending on the way it is set up this can be in either a short or long form
## additional tweak in testing 200417

Error_signal_offset = 0 # (mV) want to pulse off zero
reset_on_start = False #This tag is in case we want to reset the entire oscilloscope on startup

GPIB.measurement_setup(OS,IF_Channel, measurement = Measurement) #Setting up the required measurement for regulation

# These reset the oscilloscope on startup, only the one above is needed.
#GPIB.channel_settings_check(OS, IF_Channel) #Setting up the vertical and horizontal settings for the error signal
#GPIB.trigger_settings_set(OS, Trigger_Channel, Trigger_Level) #Sets up the vertical settings for trigger channel and trigger parameters
#GPIB.vertical_marker_pulsing(OS, IF_Channel) #Sets up vertical cursor bars to read edge of pulse

Ups = 0 #number of steps taken up before taking one down
Downs = 0 #visa versa
i = 0 #total number of iterative loops gone through, only present to show differences in command line readouts

try: #Quick test to determine short or long form oscilloscope output
    short_test = float(OS.query("MEASU:MEAS{}:VAL?".format(Measurement)))
    if Read_Start_Voltage == True:
        Error_signal_offset = short_test
    pass
except:
    long_test = float(OS.query("MEASU:MEAS{}:VAL?".format(Measurement)).split(' ')[1].strip("\n"))
    Long = True
    if Read_Start_Voltage == True:
        Error_signal_offset = long_test
    pass

#print statement
print("\n\n\n")
print("-" * 60)
print("Beginning modulation")
print("-" * 60)
print("\n\n\n")


#########################################
# Reset button loop
#########################################
while True:
    
    reset = M.read(Client, Reset_Tag)
    running = M.read(Client, Running_Tag)
    pulsing = M.read(Client, Pulsing_Tag)
    regulation_setpoint_change = M.read(Client, Regulation_Setpoint_Tag)
    
    if reset: #Checks the reset parameter and runs if True
        print("-"*60 + "\n\n\nResetting Oscilloscope\n\n\n" + "-"*60) #print visual break to indicate reset

        GPIB.measurement_setup(OS,IF_Channel, measurement = Measurement) #Same as beginning parameters above
        GPIB.channel_settings_check(OS, IF_Channel)
        GPIB.trigger_settings_set(OS, Trigger_Channel, Trigger_Level)
        GPIB.vertical_marker_pulsing(OS, IF_Channel)

        M.write(Client, Reset_Tag, 0)
        
    
    #########################################
    # Checking to see if we want to update regulation setpoint
    #########################################
    if regulation_setpoint_change:
        if pulsing:
            Error_signal_offset = GPIB.cursor_vbar_read_mv(OS)
        else:
            Error_signal_offset = GPIB.read_mv(OS, long = Long, measurement = Measurement)
            
        M.write(Client, Regulation_Setpoint_Tag, 0)
    #########################################
    # Checking for the regulation loop if on
    #########################################

    if running:  # running parameter, if True, runs this loop

        #########################################
        # Loop for pulsing operation
        #########################################

        if pulsing: #Checks pulsing tag and runs this loop if true

            read_value = GPIB.cursor_vbar_read_mv(OS) #Takes the current value of oscilloscope vbar

            if read_value > (Error_signal_offset + Pulse_Walk_Threshold): #Checks to see if that value is outside of threshold
                Ups += 1
                Downs = 0
                if Ups > Loops_Debounce: #Effective debounce
                    temp_freq = GPIB.freq(SG) #Gathers the current frequency
                    GPIB.write_frequency(SG, (temp_freq + Pulse_Step_Size),"HZ") #Writes calculated frequency to the signal generator
                    print("Raised Frequency ", i) #Shows that we took a step in frequency
                    if (temp_freq + Pulse_Step_Size) > (Start_Freq + Max_Threshold): #Sees if the new frequency is outside of bounds
                        print("Error: Broken on too many steps upward")
                        M.write(Client, Running_Tag, 0) #Breaks running loop on interlock
                    if OS.query("MEASU:Meas{}:State?".format(Measurement))[-2] != str(1): #Sees if the measurement is still active
                        print("Error: Measurement Off")
                        M.write(Client, Running_Tag, 0) #Breaks running loop on interlock
                    if read_value > (Error_signal_offset + Interlock_Threshold_mv):
                        print("Error: Deviation too far")
                        M.write(Client, Running_Tag, 0) #Breaks running loop on interlock
                    time.sleep(Wait_after_step) #Sleep for after step debounce time

            #########################################
            # Repeat above loop but below the threshold instead of above
            #########################################


            if read_value < (Error_signal_offset - Pulse_Walk_Threshold): 
                Downs += 1
                Ups = 0
                if Downs > Loops_Debounce:
                    temp_freq = GPIB.freq(SG)
                    GPIB.write_frequency(SG, (temp_freq - Pulse_Step_Size),"HZ")
                    print("Lowered Frequency ", i)
                    if (temp_freq - Pulse_Step_Size) < (Start_Freq - Max_Threshold):
                        print("Broken on too many steps downward")
                        M.write(Client, Running_Tag, 0) #Breaks running loop on interlock
                    if OS.query("MEASU:Meas{}:State?".format(Measurement))[-2] != str(1):
                        print("Measurement Off")
                        M.write(Client, Running_Tag, 0) #Breaks running loop on interlock
                    if read_value < (Error_signal_offset - Interlock_Threshold_mv):
                        print("Error: Deviation too far")
                        M.write(Client, Running_Tag, 0) #Breaks running loop on interlock
                    time.sleep(Wait_after_step)

            #time.sleep(Wait_between_reads)

        #########################################
        # Loop for CW operation, use same logic
        #########################################

        else:
            read_value = GPIB.read_mv(OS, long = Long, measurement = Measurement)

            if read_value > (Error_signal_offset + Walk_Threshold):
                Ups += 1
                Downs = 0
                if Ups > Loops_Debounce:
                    temp_freq = GPIB.freq(SG)
                    GPIB.write_frequency(SG, (temp_freq + Step_size),"HZ")
                    print("Raised Frequency ", i)
                    if (temp_freq + Step_size) > (Start_Freq + Max_Threshold):
                        print("Broken on too many steps upward")
                        M.write(Client, Running_Tag, 0) #Breaks running loop on interlock
                    if OS.query("MEASU:Meas{}:State?".format(Measurement))[-2] != str(1):
                        print("Measurement Off")
                        M.write(Client, Running_Tag, 0) #Breaks running loop on interlock
                    if read_value > (Error_signal_offset + Interlock_Threshold_mv):
                        print("Error: Deviation too far")
                        M.write(Client, Running_Tag, 0) #Breaks running loop on interlock
                    time.sleep(Wait_after_step)

            #########################################
            # Repeat above loop but below the threshold instead of above
            #########################################

            if read_value < (Error_signal_offset - Walk_Threshold):
                Downs += 1
                Ups = 0
                if Downs > Loops_Debounce:
                    temp_freq = GPIB.freq(SG)
                    GPIB.write_frequency(SG, (temp_freq - Step_size),"HZ")
                    print("Lowered Frequency ", i)
                    if (temp_freq - Step_size) < (Start_Freq - Max_Threshold):
                        print("Broken on too many steps downward")
                        M.write(Client, Running_Tag, 0) #Breaks running loop on interlock
                    if OS.query("MEASU:Meas{}:State?".format(Measurement))[-2] != str(1):
                        print("Measurement Off")
                        M.write(Client, Running_Tag, 0) #Breaks running loop on interlock
                    if read_value < (Error_signal_offset - Interlock_Threshold_mv):
                        print("Error: Deviation too far")
                        M.write(Client, Running_Tag, 0) #Breaks running loop on interlock
                    time.sleep(Wait_after_step)

        time.sleep(Wait_between_reads)
        i += 1 #Update iterator