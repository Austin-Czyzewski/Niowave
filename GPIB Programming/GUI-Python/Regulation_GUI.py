import GPIB_FUNCS as GPIB #Importing our GPIB communication functions for easier comprehension and use
import pyvisa #import GPIB communication module
import time #imports time to sleep program temporarily
from tkinter import * #importing GUI library

RM = pyvisa.ResourceManager() #pyVISA device manager
print(RM.list_resources()) #Printing out all detected device IDs
SG = RM.open_resource('GPIB0::10::INSTR') #Opening the Signal generator as an object
OS = RM.open_resource('GPIB0::16::INSTR') #Opening the oscilloscope as an object

running = False # Global flag, used for run status of GUI
reset = False # Global flag, used to pause modulation and reset the oscilloscope
pulsing = False # Global flag, used to change the modulation parameters for CW to pulsing

IF_Channel = 2 #The channel that the error signal is on
Trigger_Channel = 4 #The channel which shows the SRF pulse
Trigger_Level = 20   /1000 #mv #The level of the pulse trigger

Measurement = 3 #Measurement channel
Step_size = 40 #(Hz) Change in frequency with each regulation step
Pulse_Step_Size = 10 #(Hz) Change in frequency with each regulation step when pulsing
Max_Threshold = 10000 #(Hz) Total amount of frequency change before automatically tripping off program
Walk_Threshold = 2.5 #(mV) Deviation from 0 the error signal needs to be before CW regulation kicks in
Pulse_Walk_Threshold = 0.5 #(mV) Deviation from 0 the error signal needs before pulsing regulation kicks in
Wait_after_step = 0.0400 #Seconds, the time waited after a step is taken, necessary to allow oscope measurements to change
Wait_between_reads = 0.0100 #Seconds, currently not used, supplemented by GUI time between reads
Long = False #The form that our measurement is output from the o-scope, depending on the way it is set up this can be in either a short or long form

GPIB.measurement_setup(OS,IF_Channel, measurement = Measurement) #Setting up the required measurement
GPIB.channel_settings_check(OS, IF_Channel) #Setting up the vertical and horizontal settings for the error signal
GPIB.trigger_settings_set(OS, Trigger_Channel, Trigger_Level) #Sets up the vertical settings for trigger channel and trigger parameters
GPIB.vertical_marker_pulsing(OS, IF_Channel) #Sets up vertical cursor bars to read edge of pulse

interlock_color = "Yellow"

global Ups #Defining global parameters, these ones are not actually necessary but leave them be
global Downs
global i
Ups = 0 #number of steps taken up before taking one down
Downs = 0 #visa versa
i = 0 #total number of iterative loops gone through, only present to show differences in command line readouts
Start_Freq = GPIB.freq(SG) #taking the start frequency of the signal generator

try: #Quick test to determine short or long form oscilloscope output
    short_test = float(OS.query("MEASU:MEAS{}:VAL?".format(Measurement)))
    pass
except:
    long_test = float(OS.query("MEASU:MEAS{}:VAL?".format(Measurement)).split(' ')[1].strip("\n"))
    Long = True
    pass

#print statement
print("\n\n\n")
print("-" * 60)
print("Beginning modulation")
print("-" * 60)
print("\n\n\n")

def scanning(): #Defining what is happening when scanning our GUI
    
    global reset #Global variables, these first three are necessary but again, leave them all.
    global pulsing
    global running
    global Ups
    global Downs
    global i
    
    #########################################
    # Reset button loop
    #########################################
    
    if reset: #Checks the reset parameter and runs if True
        print("-"*60 + "\n\n\nResetting Oscilloscope\n\n\n" + "-"*60) #print statement
        
        GPIB.measurement_setup(OS,IF_Channel, measurement = Measurement) #Same as beginning parameters above
        GPIB.channel_settings_check(OS, IF_Channel)
        GPIB.trigger_settings_set(OS, Trigger_Channel, Trigger_Level)
        GPIB.vertical_marker_pulsing(OS, IF_Channel)
       
        reset = False #Sets the reset parameter to false so not looping
        
    #########################################
    # Checking for the regulation loop if on
    #########################################

    if running:  # running parameter, if True, runs this loop
        root.configure(bg = 'SpringGreen2') #Sets the background of the GUI to be green
        
        #########################################
        # Loop for pulsing operation
        #########################################
        
        if pulsing: #Checks pulsing tag and runs this loop if true
            
            read_value = GPIB.cursor_vbar_read_mv(OS) #Takes the current value of oscilloscope vbar
        
            if read_value > Pulse_Walk_Threshold: #Checks to see if that value is outside of threshold
                Ups += 1
                Downs = 0
                if Ups > 3: #Effective debounce
                    temp_freq = GPIB.freq(SG) #Gathers the current frequency
                    if (temp_freq + Pulse_Step_Size) > (Start_Freq + Max_Threshold): #Sees if the new frequency is outside of bounds
                        print("Broken on too many steps upward")
                        root.configure(bg = interlock_color) #Sets to the interlock color
                        running = False #Breaks loop if true
                    if OS.query("MEASU:Meas{}:State?".format(Measurement))[-2] != str(1): #Sees if the measurement is still active
                        print("Measurement Off")
                        root.configure(bg = interlock_color) #Sets to the interlock color
                        running = False #Breaks loop if true
                    GPIB.write_frequency(SG, (temp_freq + Pulse_Step_Size),"HZ") #Writes calculated frequency to the signal generator
                    print("Raised Frequency ", i) #Shows that we took a step in frequency
                    time.sleep(Wait_after_step) #Sleep for after step debounce time
            
            #########################################
            # Repeat above loop but below the threshold instead of above
            #########################################
            
            
            if read_value < -Pulse_Walk_Threshold: 
                Downs += 1
                Ups = 0
                if Downs > 3:
                    temp_freq = GPIB.freq(SG)
                    if (temp_freq - Pulse_Step_Size) < (Start_Freq - Max_Threshold):
                        print("Broken on too many steps downward")
                        root.configure(bg = interlock_color)
                        running = False
                    if OS.query("MEASU:Meas{}:State?".format(Measurement))[-2] != str(1):
                        print("Measurement Off")
                        root.configure(bg = interlock_color)
                        running = False
                    GPIB.write_frequency(SG, (temp_freq - Pulse_Step_Size),"HZ")
                    print("Lowered Frequency ", i)
                    time.sleep(Wait_after_step)

            time.sleep(Wait_between_reads)
            i += 1
            
        #########################################
        # Loop for CW operation, use same logic
        #########################################
            
        else:
            read_value = GPIB.read_mv(OS, long = Long, measurement = Measurement)
        
            if read_value > Walk_Threshold:
                Ups += 1
                Downs = 0
                if Ups > 3:
                    temp_freq = GPIB.freq(SG)
                    if (temp_freq + Step_size) > (Start_Freq + Max_Threshold):
                        print("Broken on too many steps upward")
                        root.configure(bg = interlock_color)
                        running = False
                    if OS.query("MEASU:Meas{}:State?".format(Measurement))[-2] != str(1):
                        print("Measurement Off")
                        root.configure(bg = interlock_color)
                        running = False
                    GPIB.write_frequency(SG, (temp_freq + Step_size),"HZ")
                    print("Raised Frequency ", i)
                    time.sleep(Wait_after_step)
                    
            #########################################
            # Repeat above loop but below the threshold instead of above
            #########################################

            if read_value < -Walk_Threshold:
                Downs += 1
                Ups = 0
                if Downs > 3:
                    temp_freq = GPIB.freq(SG)
                    if (temp_freq - Step_size) < (Start_Freq - Max_Threshold):
                        print("Broken on too many steps downward")
                        root.configure(bg = interlock_color)
                        running = False
                    if OS.query("MEASU:Meas{}:State?".format(Measurement))[-2] != str(1):
                        print("Measurement Off")
                        root.configure(bg = interlock_color)
                        running = False
                    GPIB.write_frequency(SG, (temp_freq - Step_size),"HZ")
                    print("Lowered Frequency ", i)
                    time.sleep(Wait_after_step)

            #time.sleep(Wait_between_reads)
            i += 1 #Update iterator

    # After .1 seconds, call scanning again (create a recursive loop)
    root.after(100, scanning) #Wait the first number of ms, then continue scanning


def start():
    """Enable scanning by setting the global flag to True."""
    global running
    running = True

def stop():
    """Stop scanning by setting the global flag to False."""
    global running
    running = False
    root.configure(bg = 'firebrick1')

def reset_measurement():
    """Temporarily stops the scan to reset the oscilloscope settings to default used in regulation"""
    root.configure(bg = 'sky blue')
    global reset
    reset = True
    
def pulsing_toggle():
    """Toggles the pulsing parameter within the global running flag, detects if true or not currently"""
    global pulsing
    if pulsing: #If pulsing is true, toggle to false, if false, toggle to true, done so there is no need for two buttons with pulsing
        pulsing = False
    else:
        pulsing = True
    


root = Tk() #Beginning the GUI object
root.title("Regulation Window") #Title of the GUI
root.geometry("1000x1000") #Size of the GUI
#root.attributes('-fullscreen', True) #Swap the comments on this line and the previous to determine if the GUI is fullscreen or resizable

app = Frame(root) #Application window
app.grid() #Making this visible
size = 10 #Size marker used universally between buttons
start = Button(app, text="Start Regulation", command=start, activebackground="SpringGreen2", height = size, width = size*5, bg = 'Pale Green', font=('Helvetica', '20'), bd = size) #Start button configuration, same for next three lines
stop = Button(app, text="Stop Regulation", command=stop, activebackground="firebrick1", height = size, width = size*5, bg = 'tomato', font=('Helvetica', '20'), bd = size)
reset_button = Button(app, text="Reset Oscilloscope", command=reset_measurement, activebackground="light sky blue", height = int(size/3), width = size*5, bg = 'sky blue', font=('Helvetica', '20'), bd = size)
Pulsing_button = Checkbutton(app, text="Pulsing", command=pulsing_toggle, activebackground="white", height = int(size/3), width = size*5, bg = 'gray', font=('Helvetica', '20'), bd = size,indicatoron=False,selectcolor='orange')
start.grid() #put the start button on the GUI, same for next three lines
stop.grid()
reset_button.grid()
Pulsing_button.grid()

root.after(1000, scanning)  # After 1 second, call scanning
root.mainloop()