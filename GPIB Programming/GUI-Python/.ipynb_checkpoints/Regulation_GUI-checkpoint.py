import GPIB_FUNCS as GPIB #Importing our GPIB communication functions for easier comprehension and use
import pyvisa #import GPIB communication module
import time #imports time to sleep program temporarily
from tkinter import * #importing GUI library
import tkinter

RM = pyvisa.ResourceManager() #pyVISA device manager
print(RM.list_resources()) #Printing out all detected device IDs
SG = RM.open_resource('GPIB0::10::INSTR') #Opening the Signal generator as an object
OS = RM.open_resource('GPIB0::16::INSTR') #Opening the oscilloscope as an object

running = False # Global flag, used for run status of GUI
reset = False # Global flag, used to pause modulation and reset the oscilloscope
pulsing = False # Global flag, used to change the modulation parameters for CW to pulsing

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
reset_on_start = False

GPIB.measurement_setup(OS,IF_Channel, measurement = Measurement) #Setting up the required measurement for regulation

# These reset the oscilloscope on startup, only the one above is needed.
#GPIB.channel_settings_check(OS, IF_Channel) #Setting up the vertical and horizontal settings for the error signal
#GPIB.trigger_settings_set(OS, Trigger_Channel, Trigger_Level) #Sets up the vertical settings for trigger channel and trigger parameters
#GPIB.vertical_marker_pulsing(OS, IF_Channel) #Sets up vertical cursor bars to read edge of pulse

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

def scanning(): #Defining what is happening when scanning our GUI
    
    global reset #Global variables, these first three are necessary but again, leave them all.
    global pulsing
    global running
    global Ups
    global Downs
    global i
    global Error_signal_offset
    
    #########################################
    # Reset button loop
    #########################################
    
    if reset: #Checks the reset parameter and runs if True
        print("-"*60 + "\n\n\nResetting Oscilloscope\n\n\n" + "-"*60) #print visual break to indicate reset
        
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
        
            if read_value > (Error_signal_offset + Pulse_Walk_Threshold): #Checks to see if that value is outside of threshold
                Ups += 1
                Downs = 0
                if Ups > Loops_Debounce: #Effective debounce
                    temp_freq = GPIB.freq(SG) #Gathers the current frequency
                    GPIB.write_frequency(SG, (temp_freq + Pulse_Step_Size),"HZ") #Writes calculated frequency to the signal generator
                    print("Raised Frequency ", i) #Shows that we took a step in frequency
                    if (temp_freq + Pulse_Step_Size) > (Start_Freq + Max_Threshold): #Sees if the new frequency is outside of bounds
                        print("Error: Broken on too many steps upward")
                        root.configure(bg = interlock_color) #Sets to the interlock color
                        running = False #Breaks loop if true
                    if OS.query("MEASU:Meas{}:State?".format(Measurement))[-2] != str(1): #Sees if the measurement is still active
                        print("Error: Measurement Off")
                        root.configure(bg = interlock_color) #Sets to the interlock color
                        running = False #Breaks loop if true
                    if read_value > (Error_signal_offset + Interlock_Threshold_mv):
                        print("Error: Deviation too far")
                        root.configure(bg = interlock_color) #Sets to the interlock color
                        running = False
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
                        root.configure(bg = interlock_color)
                        running = False
                    if OS.query("MEASU:Meas{}:State?".format(Measurement))[-2] != str(1):
                        print("Measurement Off")
                        root.configure(bg = interlock_color)
                        running = False
                    if read_value < (Error_signal_offset - Interlock_Threshold_mv):
                        print("Error: Deviation too far")
                        root.configure(bg = interlock_color) #Sets to the interlock color
                        running = False
                    time.sleep(Wait_after_step)

            time.sleep(Wait_between_reads)
            i += 1
            
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
                        root.configure(bg = interlock_color)
                        running = False
                    if OS.query("MEASU:Meas{}:State?".format(Measurement))[-2] != str(1):
                        print("Measurement Off")
                        root.configure(bg = interlock_color)
                        running = False
                    if read_value > (Error_signal_offset + Interlock_Threshold_mv):
                        print("Error: Deviation too far")
                        root.configure(bg = interlock_color) #Sets to the interlock color
                        running = False
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
                        root.configure(bg = interlock_color)
                        running = False
                    if OS.query("MEASU:Meas{}:State?".format(Measurement))[-2] != str(1):
                        print("Measurement Off")
                        root.configure(bg = interlock_color)
                        running = False
                    if read_value < (Error_signal_offset - Interlock_Threshold_mv):
                        print("Error: Deviation too far")
                        root.configure(bg = interlock_color) #Sets to the interlock color
                        running = False
                    time.sleep(Wait_after_step)

            #time.sleep(Wait_between_reads)
            i += 1 #Update iterator

    # After .1 seconds, call scanning again (create a recursive loop)
    root.after(100, scanning) #Wait the first number of ms, then continue scanning


def start():
    """Enable scanning by setting the global flag to True."""
    global running
    global Error_signal_offset
    if reset_on_start == True:
        Error_signal_offset = GPIB.read_mv(OS, long = Long, measurement = Measurement)
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

def regulation_setpoint_set():
    global Error_signal_offset
    global pulsing
    if pulsing:
        Error_signal_offset = GPIB.cursor_vbar_read_mv(OS)
    else:
        Error_signal_offset = GPIB.read_mv(OS, long = Long, measurement = Measurement)

def pass_value():
    """Passes the value into the label, checks for proper value"""
    global Error_signal_offset
    newtext = textvar.get() #Grabs the updated value
    
    try:
        Error_signal_offset = float(newtext)
        print(Error_signal_offset)
        label['bg'] = 'green'
        
    except:
        print("Value must be a number")
        newtext = "Warning: Value must be a integer or float in"
        label['bg'] = 'red'
        
    label['text'] = newtext + ' (mv)'
    
    textvar.set("") # Delete the entry text

def entry():
    """Creates entry and label boxes"""
    entry = tkinter.Entry(root, textvariable=textvar, width = size * 5)
    entry['font'] = "Arial 12"
    entry.focus()
    entry.grid(row = 0, column = 2, pady = size*1, ipady = size*5, sticky = "N")
    entry.bind("<Return>", lambda x: pass_value())
    label = tkinter.Label(root, width = size * 5)
    label.grid(row = 0, column = 2, pady = size*10+size*5, ipady = size*5, sticky = "N")
    return entry, label


root = Tk() #Beginning the GUI object
root.title("Regulation Window") #Title of the GUI
root.geometry("1000x1000") #Size of the GUI
app = Frame(root) #Application window
app.grid() #Making this visible

#root.attributes('-fullscreen', True) #Swap the comments on this line and the previous to determine if the GUI is fullscreen or resizable

textvar = tkinter.StringVar()

entry, label = entry()

#app = Frame(root) #Application window
#app.grid() #Making this visible
start = Button(app, text="Start Regulation", command=start, activebackground="SpringGreen2", height = size, width = size*5, bg = 'Pale Green', font=('Helvetica', '20'), bd = size) #Start button configuration, same for next lines
stop = Button(app, text="Stop Regulation", command=stop, activebackground="firebrick1", height = size, width = size*5, bg = 'tomato', font=('Helvetica', '20'), bd = size)
reset_button = Button(app, text="Reset Oscilloscope", command=reset_measurement, activebackground="light sky blue", height = int(size/3), width = size*5, bg = 'sky blue', font=('Helvetica', '20'), bd = size)
Pulsing_button = Checkbutton(app, text="Pulsing", command=pulsing_toggle, activebackground="white", height = int(size/3), width = size*5, bg = 'gray', font=('Helvetica', '20'), bd = size,indicatoron=False,selectcolor='orange')
Regulation_setpoint_button = Button(app, text="Set regulation setpoint here", command=regulation_setpoint_set, activebackground="gray", height = int(size/3), width = size*5, bg = 'lightgray', font=('Helvetica', '20'), bd = size)

start.grid(row = 1, column = 1) #put the start button on the GUI, same for next three lines
stop.grid(row = 2, column = 1)
reset_button.grid(row = 3, column = 1)
Pulsing_button.grid(row = 4, column = 1)
Regulation_setpoint_button.grid(row = 5, column = 1)

root.after(1000, scanning)  # After 1 second, call scanning
root.mainloop()