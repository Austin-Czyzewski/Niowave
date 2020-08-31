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

import GPIB_FUNCS as GPIB #Importing our GPIB communication functions for easier comprehension and use
import pyvisa #import GPIB communication module
import time #imports time to sleep program temporarily
import Master as M
import Tag_Database as Tags

Client = M.Make_Client('192.168.1.2')

#Pulsing_Tag = Tags.Pulsing_Output #Assign Modbus address here
Running_Tag = Tags.Error_Signal_Regulation #Assign Modbus address here
#Reset_Tag = Tags.Error_Signal_Reset #Assign Modbus address here
#Regulation_Setpoint_Tag = Tags.Regulation_Setpoint_Reset #Assign Modbus address here

RM = pyvisa.ResourceManager() #pyVISA device manager
Resources = RM.list_resources() #Printing out all detected device IDs
print(Resources)
SG = RM.open_resource("GPIB0::10::INSTR")

time.sleep(2)


print(SG.query("*IDN?"))


SG.control_ren(6)


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
Reset_Tag = Tags.Oscope_Reset #Assign Modbus address here
Regulation_Setpoint_Tag = Tags.Regulation_Setpoint_Reset #Assign Modbus address here
Regulation_Entry_Tag = Tags.Regulation_Float #The input tag for this guy

RM = pyvisa.ResourceManager() #pyVISA device manager
Resources = RM.list_resources() #Printing out all detected device IDs
print(Resources)
try:
    SG = RM.open_resource(Resources[1]) #Opening the Signal generator as an object
    OS = RM.open_resource(Resources[2]) #Opening the oscilloscope as an object
    
    Start_Freq = float(SG.query("FREQ:CW?"))
    print("Starting Frequency of Signal Generator: {} Hz".format(Start_Freq))
except:
    SG = RM.open_resource(Resources[2]) #Opening the Signal generator as an object
    OS = RM.open_resource(Resources[1]) #Opening the oscilloscope as an object
    
    Start_Freq = float(SG.query("FREQ:CW?"))
    print("Starting Frequency of Signal Generator: {} Hz".format(Start_Freq))

IF_Channel = 1 #The channel that the error signal is on
Trigger_Channel = 4 #The channel which shows the SRF pulse
Trigger_Level = 20   /1000 #mv #The level of the pulse trigger
Read_Start_Voltage = True

Measurement = 1 #Measurement channel
Step_size = 0 #(Hz) Change in frequency with each regulation step
Pulse_Step_Size = 10 #(Hz) Change in frequency with each regulation step when pulsing
Max_Threshold = 100000 #(Hz) Total amount of frequency change before automatically tripping off program
Walk_Threshold = 0.5 #(mV) Deviation from 0 the error signal needs to be before CW regulation kicks in
Pulse_Walk_Threshold = 0.5 #(mV) Deviation from 0 the error signal needs before pulsing regulation kicks in
Wait_after_step = 0.0400 #Seconds, the time waited after a step is taken, necessary to allow oscope measurements to change
Wait_between_reads = 0.0100 #Seconds, currently not used, supplemented by GUI time between reads
Interlock_Threshold_mv = 10 #mv, this is the amount of deviation before regulation trips off

Loops_Debounce = 1
Long = False #The form that our measurement is output from the o-scope, depending on the way it is set up this can be in either a short or long form
## additional tweak in testing 200417

Error_signal_offset = 0 # (mV) want to pulse off zero
M.Write(Client, Regulation_Entry_Tag, Error_signal_offset)
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

reset = False
regulation_setpoint_change = False
pulsing = False

#########################################
# Reset button loop
#########################################
while True:

    reset = M.Read(Client, Reset_Tag, Bool = True)
    running = M.Read(Client, Running_Tag, Bool = True)
    pulsing = M.Read(Client, Pulsing_Tag, Bool = True)
    regulation_setpoint_change = M.Read(Client, Regulation_Setpoint_Tag, Bool = True)
    Error_signal_offset = M.Read(Client, Regulation_Entry_Tag)
    #print(Error_signal_offset)
    
    if reset: #Checks the reset parameter and runs if True
        print("-"*60 + "\n\n\nResetting Oscilloscope\n\n\n" + "-"*60) #print visual break to indicate reset

        GPIB.measurement_setup(OS,IF_Channel, measurement = Measurement) #Same as beginning parameters above
        GPIB.channel_settings_check(OS, IF_Channel)
        GPIB.trigger_settings_set(OS, Trigger_Channel, Trigger_Level)
        GPIB.vertical_marker_pulsing(OS, IF_Channel)

        M.Write(Client, Reset_Tag, False, Bool = True)
        
    
    #########################################
    # Checking to see if we want to update regulation setpoint
    #########################################
    if regulation_setpoint_change:
        if pulsing:
            Error_signal_offset = GPIB.cursor_vbar_read_mv(OS)
        else:
            Error_signal_offset = GPIB.read_mv(OS, long = Long, measurement = Measurement)
            
        M.Write(Client, Regulation_Setpoint_Tag, False, Bool = True)
        M.Write(Client, Regulation_Entry_Tag, Error_signal_offset)
    #########################################
    # Checking for the regulation loop if on
    #########################################
    time.sleep(0.1)
    if running:  # running parameter, if True, runs this loop
        #print("Step 3")
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
                        M.Write(Client, Running_Tag, False, Bool = True) #Breaks running loop on interlock
                        SG.control_ren(6) #Returns to local control
                    if OS.query("MEASU:Meas{}:State?".format(Measurement))[-2] != str(1): #Sees if the measurement is still active
                        print("Error: Measurement Off")
                        M.Write(Client, Running_Tag, False, Bool = True) #Breaks running loop on interlock
                        SG.control_ren(6)
                    if read_value > (Error_signal_offset + Interlock_Threshold_mv):
                        print("Error: Deviation too far")
                        M.Write(Client, Running_Tag, False, Bool = True) #Breaks running loop on interlock
                        SG.control_ren(6)
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
                        M.Write(Client, Running_Tag, False, Bool = True) #Breaks running loop on interlock
                        SG.control_ren(6)
                    if OS.query("MEASU:Meas{}:State?".format(Measurement))[-2] != str(1):
                        print("Measurement Off")
                        M.Write(Client, Running_Tag, False, Bool = True) #Breaks running loop on interlock
                        SG.control_ren(6)
                    if read_value < (Error_signal_offset - Interlock_Threshold_mv):
                        print("Error: Deviation too far")
                        M.Write(Client, Running_Tag, False, Bool = True) #Breaks running loop on interlock
                        SG.control_ren(6)
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
                        M.Write(Client, Running_Tag, False, Bool = True) #Breaks running loop on interlock
                        SG.control_ren(6)
                    if OS.query("MEASU:Meas{}:State?".format(Measurement))[-2] != str(1):
                        print("Measurement Off")
                        M.Write(Client, Running_Tag, False, Bool = True) #Breaks running loop on interlock
                        SG.control_ren(6)
                    if read_value > (Error_signal_offset + Interlock_Threshold_mv):
                        print("Error: Deviation too far")
                        M.Write(Client, Running_Tag, False, Bool = True) #Breaks running loop on interlock
                        SG.control_ren(6)
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
                        M.Write(Client, Running_Tag, False, Bool = True) #Breaks running loop on interlock
                        SG.control_ren(6)
                    if OS.query("MEASU:Meas{}:State?".format(Measurement))[-2] != str(1):
                        print("Measurement Off")
                        M.Write(Client, Running_Tag, False, Bool = True) #Breaks running loop on interlock
                        SG.control_ren(6)
                    if read_value < (Error_signal_offset - Interlock_Threshold_mv):
                        print("Error: Deviation too far")
                        M.Write(Client, Running_Tag, False, Bool = True) #Breaks running loop on interlock
                        SG.control_ren(6)
                    time.sleep(Wait_after_step)
        

        time.sleep(Wait_between_reads)
        i += 1 #Update iterator


#### Creator: Austin Czyzewski
## Date: 02/03/2020

#This is an importable tag database designed to make writing code for automation direct interaction a little bit
#    more intuitive. The intention here is to get rid of the need to look into the modbus excel file for a new tag
#    as most of the legwork is done here. Simply reference this program for what I've named each item. This program
#    is currently in its early stages so it is best to remember that these names may change and so may the tags.


########################################
### Window Frame Request
########################################

WF1V = 20201
WF2V = 20203
WF3V = 20205
WF4V = 20207
WF5V = 20209
WF6V = 20211
WF7V = 20213
WF8V = 20215
WF9V = 20217
WF10V = 20219
WF11V = 20221
WF12V = 20223
WF13V = 20225
WF14V = 20227
WF15V = 20229
WF16V = 20231
WF17V = 20233
WF18V = 20235
WF19V = 20237
WF20V = 20239
WF21V = 20241
WF22V = 20243
WF23V = 20245
WF24V = 20247
WF25V = 20249


WF1H = 20251
WF2H = 20253
WF3H = 20255
WF4H = 20257
WF5H = 20259
WF6H = 20261
WF7H = 20263
WF8H = 20265
WF9H = 20267
WF10H = 20269
WF11H = 20271
WF12H = 20273
WF13H = 20275
WF14H = 20277
WF15H = 20279
WF16H = 20281
WF17H = 20283
WF18H = 20285
WF19H = 20287
WF20H = 20289
WF21H = 20291
WF22H = 20293
WF23H = 20295
WF24H = 20297
WF25H = 20299

########################################
### Dipole Request
########################################

DP1 = 22201
DP2 = 22203
DP3 = 22205
DP4 = 22207
DP5 = 22209
DP6 = 22211
DP7 = 22213
DP8 = 22215

########################################
### Solenoid Request
########################################

Sol1 = 21201
Sol2 = 21203
Sol3 = 21205
Sol4 = 21207
Sol5 = 21209
Sol6 = 21211
Sol7 = 21213
Sol8 = 21215
Sol9 = 21217

########################################
### Window Frame Readback
########################################

WF1V_Read = 20101
WF1H_Read = 20103
WF2V_Read = 20105
WF2H_Read = 20107
WF3V_Read = 20109
WF3H_Read = 20111
WF4V_Read = 20113
WF4H_Read = 20115
WF5V_Read = 20117
WF5H_Read = 20119
WF6V_Read = 20121
WF6H_Read = 20123
WF7V_Read = 20125
WF7H_Read = 20127
WF8V_Read = 20129
WF8H_Read = 20131
WF9V_Read = 20133
WF9H_Read = 20135
WF10V_Read = 20137
WF10H_Read = 20139
WF11V_Read = 20141
WF11H_Read = 20143
WF12V_Read = 20145
WF12H_Read = 20147
WF13V_Read = 20149
WF13H_Read = 20151
WF14V_Read = 20153
WF14H_Read = 20155
WF15V_Read = 20157
WF15H_Read = 20159
WF16V_Read = 20161
WF16H_Read = 20163
WF17V_Read = 20165
WF17H_Read = 20167
WF18V_Read = 20169
WF18H_Read = 20171
WF19V_Read = 20173
WF19H_Read = 20175
WF20V_Read = 20177
WF20H_Read = 20179
WF21V_Read = 20181
WF21H_Read = 20183

########################################
### Dipole Readback
########################################

DP1_Read = 22101
DP2_Read = 22103
DP3_Read = 22105
DP4_Read = 22107
DP5_Read = 22109
DP6_Read = 22111
DP7_Read = 22113
DP8_Read = 22115

########################################
### Solenoid Readback
########################################

Sol1_Read = 21101
Sol2_Read = 21103
Sol3_Read = 21105
Sol4_Read = 21107
Sol5_Read = 21109
Sol6_Read = 21111
Sol7_Read = 21113
Sol8_Read = 21115
Sol9_Read = 21117

########################################
### Cathode Controls
########################################

IR_Temp = 10101
VA_Temp = 10111
Heater_Amps_Set = 10107
Temperature_Set = 10303
Emission_Set = 10305
Voltage_Read = 10103
Current_Read = 10105
Impedance_Read = 10121
Power_Read = 10123

########################################
### Current Readbacks
########################################

Emitted_Current = 11103
DBA_Bypass = 11109
Recirculator_Halfway = 11111
Recirculator_Bypass = 11113
RF_Beam_Mon = 11117

########################################
### Pulse Controls
########################################

Pulse_Frequency = 10309
Pulse_Duty = 10311
Pulse_Delay = 13013

########################################
### Cu Gun, BH Coupler, SRF Pf, Pr, Pt
########################################

CU_Pf = '01101'
CU_Pr = '01103'
CU_Pt = '01105'
CU_V = '01115'
BH_Pf = 21225
BH_Pr = 21227
BH_Pt = 21229
SRF_Pf = '02101'
SRF_Pr = '02103'
SRF_Pt = '02105'

########################################
### HV Bias Paremeters
########################################

HV_Bias =  11101
HV_Off_Setpoint = 11301
HV_On_Setpoint = 11303
Trek_V = 11501
Trek_I = 11503
V0_SP = 11311
V0_Read = 11101

########################################
### Error Signal Regulation Tags
########################################

Pulsing_Output = '11014' 
Error_Signal_Regulation = '00012' 
Oscope_Reset = '00013' 
Regulation_Setpoint_Reset = '00014'
Regulation_Float = '01001'

def freq(Device):
    '''
    Inputs the signal generator device as already opened by
    resource manager.
    
    Outputs: The frequency of the system in Hz
    
    '''
    
    frequency = Device.query("freq:cw?")
    
    return float(frequency)

def write_frequency(Device, Value, Units = "MHZ"):
    '''
    Inputs: (Device, Value, Units)
        - Device: Signal generator that we have defined by resource manager
        - Value: The frequency of the new signal, units determined by units (Default is MHz)
        - Units: Must be string, can either be (in any case) Mhz, Khz, or Hz
        
    Outputs: Just writes the new frequency
    '''
    
    Device.write("freq:cw {} {}".format(Vaslue,Units))
    
You have traveled far. Please stay at this Inn and read about what we are all about.

This is the GPIB Programming area, where we write mostly python scripts to mostly automate mostly simple tasks.

Currently, there a few folders here with names that represent scientific equipment. What is contained within them is
  python scripts testing functions, communications, and overall interactions with them. The most successful of which is the
  GUI-python folder which contains the culminations of the work for error signal regulation. This is a large bright GUI that
  contains four buttons that are clearly labeled (Except reset oscilloscope, which instead of resetting the oscilloscope only
  resets the options for it).

There will be more to come. Thank you for visiting the GPIBinn


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
    
import Master_All_Versions as M
import Tag_Database as Tags
from datetime import datetime
from time import sleep

IP = '10.50.0.10'

Client = M.Make_Client(IP)

while True:
    sleep(0.5)
    now = datetime.today().strftime('%y%m%d_%H%M%S.%f') + '.txt'
    try:
        M.Snapshot(Client, now)
    except:
        print("Failed connection to PLC at {}".format(now))
        continue
        
''' Creator: Austin Czyzewski

Date: 12/04/2019
Last Updated: 06/25/2020

Purpose: Define functions to make code more modular and add functionality
    - Set up the code in a way that we have functions that can be used with imports and make easy code to write

Functions to be found:
    - Establish client (Make_Client)
        - Set an IP address and save to act for functions
        
    - Read from client
        - Read the output from a modbus tag
        
    - Write to client
        - Similar to read, however, give a new value to write to. Be careful, there is no safety in magnet step size here
        
    - Ramp one way
        - Select the magnet, set an end value, and define a step size and this will walk the magnet to that value

    - Ramp two way
        - Select the magnet, set an end value, define a step size, and this will walk the magnet to and from that value
        
    - Plot
        - Currently not very useful, don't use this
    
    - Rapid_T_Scan
        - This takes a 2 axis magnet and rapidly scans in a t shape, this can prove to be useful for taking large datasets


Example Code to Write a script that reads the value of dipole 1 and then writes a new value. Then it checks that it actually wrote:

from Master import *
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.payload import BinaryPayloadBuilder
from pymodbus.constants import Endian

Client = Make_Client('192.186.10.2') #Establish Client
Dipole_1_Before = Read(Client,22201) #Read DP1

New_Dipole_1 = 0.123 #Amps, Set new value to be set

Dipole_1 = Write(Client,22201,New_Dipole_1) #Write to DP1 
Dipole_1_After = Read(Client,22201) #Read DP1



if Dipole_1_After == Dipole_1_Before:
    print("True")
else:
    print("False")

'''

from pymodbus.client.sync import ModbusTcpClient
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.payload import BinaryPayloadBuilder
from pymodbus.constants import Endian
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import time
import concurrent.futures
#import tisgrabber as IC
#import cv2

sleep_time = 0.020 #time in seconds before grabbing a consecutive data point

UseCamera = False

if UseCamera:
    resolution = '1920x1080'
    def_exp, def_gain = 0.01, 480  # exp in units of sec, gain in units of 1/10 dB

    # Access CCD data and grab initial frame
    Camera = IC.TIS_CAM()
    Camera.ShowDeviceSelectionDialog() #Brings up camera catalog for selection

    if Camera.IsDevValid() == 1:

        # Set a video format
        temp = "RGB32 (" + resolution + ")"
        Camera.SetVideoFormat(temp); del temp
        Camera.SetPropertyAbsoluteValue("Exposure","Value", def_exp)
        Camera.SetPropertyValue("Gain","Value", def_gain)

        # Communicate with camera
        Camera.StartLive(1)

        # Initial image snap
        Camera.SnapImage() #Take an image

        # Get image
        init_img = Camera.GetImage()
        init_img = cv2.flip(init_img, 0)
        init_img = cv2.cvtColor(init_img, cv2.COLOR_BGR2RGB)

    else:
        Camera.StopLive()
        exit()

    # At this point we have successfully communicated with the camera. Camera is 
    # now actively in standby mode and can take image snapshot upon request.

def snap(Camera, def_exp = 0.01, def_gain = 480):
    '''
    Inputs:
        __ Camera: The camera that we are connected to through TIS
        __ def_exp: The exposure time of the image that we want
        __ def_gain: Gain of the image that we want
    
    Outputs:
        A .bmp file with the name that contains the time at which the image is taken
        
    Required imports:
        - datetime
        - cv2
        - tisgrabber
        
    Example: 
        Camera = IC.TIS_CAM()
        snap(Camera, def_exp = 1/3, def_gain = 0)
        
    '''
    def_exp = def_exp #exposure (seconds)
    def_gain = def_gain  # gain in units of 1/10 dB
    
    Camera.SnapImage()
    image = Camera.GetImage()
    image = cv2.flip(image, 0) # note image is saved in BGR color code

                # we will save image sequences in the imgs directory
    timestamp = datetime.now() # data acquisition time stamp. need to be moved?
    fname = './imgs/' +  timestamp.strftime("%y%m%d_%H-%M-%S.%f") + \
        'exp' + str(def_exp) + '-gain' + str(def_gain) + '-dipolescan.bmp'
    cv2.imwrite(fname, image)

def merge(list1, list2): 
    '''
    Inputs:
        Two lists of equal length
    
    Outputs:
        One list that contains a list of the zipped values from the
        two lists
    
    '''
    merged_list = [(list1[i], list2[i]) for i in range(0, len(list1))] 
    return merged_list

def Make_Client(IP):
    '''
        -Inputs: IP Address of modbus to communicate with. Input as a string.
        
        -Outputs: A client to be used by pymodbus for reading and writing
        
        -Required imports
        from pymodbus.client.sync import ModbusTcpClient

        -Example:
        Client = Make_Client('192.168.1.2')

    '''

    #Using pymodbus to establish the client we are reaching
    Client = ModbusTcpClient(str(IP))
    return Client



def Read(Client, Tag_Number, Average = False, count = 20,sleep_time = .010, Bool = False):
    '''
        -Inputs: Client, see "Client" Above
            __ Tag_Number: which modbus to read, convention is this: input the modbus start tag number. Must have a modbus tag.
            __ Average: Tells us wether or not to average these data points
            __ Count: The number of points that we will average over if Average == True
            __ sleep_time: Time (ms) that we will rest before grabbing the next piece of data

        -Must have established client before attempting to read from the client
        
        -Outputs: The value of that Moodbus tag

        Method: Grab holding register value
                - Decode that value into a 32 bit float
                - Convert from 32 bit float to regular float
        
        -Required imports
        from pymodbus.client.sync import ModbusTcpClient
        from pymodbus.payload import BinaryPayloadDecoder
        from pymodbus.constants import Endian

        -example:
        Client = Make_Client('192.168.1.2')
        Dipole_1_Current = Read(Client,22201)

    '''
    Tag_Number = int(Tag_Number)-1


    if Bool == False:
        
        if Average == True:
            
            temp_list = []
            for i in range(count):
                Payload = Client.read_holding_registers(Tag_Number,2,unit=1)
                Tag_Value_Bit = BinaryPayloadDecoder.fromRegisters(Payload.registers, byteorder=Endian.Big, wordorder=Endian.Big)
                Tag_Value = Tag_Value_Bit.decode_32bit_float()
                temp_list.append(Tag_Value)

                time.sleep(sleep_time)

            return (sum(temp_list)/count)
        else:
            Payload = Client.read_holding_registers(Tag_Number,2,unit=1)
            Tag_Value_Bit = BinaryPayloadDecoder.fromRegisters(Payload.registers, byteorder=Endian.Big, wordorder=Endian.Big)
            Tag_Value = Tag_Value_Bit.decode_32bit_float()
            return Tag_Value
        
    if Bool == True:
        Tag_Value = Client.read_coils(Tag_Number,unit=1).bits[0]

    return Tag_Value


def Gather(Client, tag_list, count = 20, sleep_time = 0.010):
    """
    Inputs: Client, see "Client" Above
        __ tag_list: a list of tags and whether or not to average them. The list must be in the following format: [[Tag#, True],[Tag#, False],[Tag#, True]]
                    where True and False indicate whether you want the Read to be averaged.
        __ count: how many reads to average over, see "Read" above
        __ sleep_time: how long to sleep between each averaged read, see "Read" above
        
    Method:
        - Build an empty list we will add to later
        - Import the threading tool, start up a threaded executor
        - Build workers, have them work. Store values in order as executed
        - When all are finished, add the results to the list
        - Output list
    """
    
    temp_list = [] #initialize temporary list
    with concurrent.futures.ThreadPoolExecutor() as executor:
        
        results = [executor.submit(Read, Client = Client, Tag_Number = tag, Average = avg, count = count, sleep_time=sleep_time) for tag,avg in tag_list]
        
        for f in results:
            temp_list.append(f.result())
            
    return temp_list



def Write(Client, Tag_Number, New_Value, Bool = False):
    '''  -Future: input a safety method to make sure we aren't drastically changing values

        Inputs: Client, see "Client" Above
            __ Tag_Number: which modbus to read, convention is this: input the modbus start tag number. Must have a modbus tag.
            __ New_Value: New value which you want the modbus to output to

        -Must have established client before attempting to write to the client
        
        -Outputs: The value of that Moodbus tag

        Method:
                - Build a payload to send to register
                - Add float value to that payload
                - Build payload path (path to register)
                - Build the payload
                - Write the new value
        
        -Required imports
        from pymodbus.client.sync import ModbusTcpClient
        from pymodbus.payload import BinaryPayloadDecoder
        from pymodbus.constants import Endian

        -example:
        Client = Make_Client('192.168.1.2')
        Dipole_1_Current = Write(Client,22201,0.450)


    '''

    Tag_Number = int(Tag_Number)-1

    if Bool == False:
        
        Builder = BinaryPayloadBuilder(byteorder=Endian.Big, wordorder=Endian.Big)
        Builder.add_32bit_float(New_Value)
        Payload = Builder.to_registers()
        Payload = Builder.build()
        Client.write_registers(Tag_Number, Payload, skip_encode=True, unit=1)

    if Bool == True:
        Client.write_coils(Tag_Number, [New_Value], skip_encode=False, unit=1)

    return


def Write_Multiple(Client, Start_Tag_Number, New_Value_List):
    
    '''
    Inputs:
        __ Client: See client
        __ Start_Tag_Number: This is the starting tag value, this will increment
            by two for each of the items in the New_Values_List
        __ New_Values_List: This is a list of new values that you want to write, this
            is typically the same number repeated once for each time that you want
            to write to each magnet. This is done this way so that you can write
            different values to each magnet if you want to. (Typically by a scaled
            amount if you are doing that.)
        
        - Must have an established Client before running this function.
        
        - Outputs:
            __ Writes to a number of user defined magnets, may, in the future,
                allow one value to be written to a specified number of magnets.
                
        - Method:
                - Set up the Client
                - Define the start tag value, 22201 for dipole 1 for example
                - For each dipole you want to step, you define the new value 
                    you want written to it.
        - Example (Writing to 8 Dipoles starting with DP1)
        
        List = [0.100,0.100,0.100,0.100,0.100,0.100,0.100,0.100]
        DP1_Tag = 22201
        
        Client = M.Make_Client('192.168.1.2')
        
        M.Write_Multiple(Client, DP1_Tag, List)
        
            - Result: All of the Dipoles (Assuming there are 8 will be written to 0.100) 
    
    '''
    
    Tag_Number = int(Start_Tag_Number)-1
    
    Builder = BinaryPayloadBuilder(byteorder=Endian.Big, wordorder=Endian.Big)
    
    for value in New_Value_List:
        Builder.add_32bit_float(value)
        
    Payload = Builder.to_registers()
    Payload = Builder.build()
    
    Client.write_registers(Tag_Number, Payload, skip_encode=True, unit=1)
    
    return


def Snapshot(Client, filename, start = 8):
    '''
    Inputs:
        __ Client: See Make_Client
        __ filename: What you want the filename to be
        __ start: the starting value of the indexing from the Tag_Database
        the defualt is 8 since that is the first defined variable 
        in the tag database. This will change if you do not want any magnets
        
    Outputs:
        A .txt file with the filename and the Read value of each magnet in 
        the Tag_Database. A quick and easy way to get and store a system snapshot
        
    Requirements:
        Tag_Database to be in the same folder as the file that this call is made in
        
    '''
    
    import Tag_Database as Tags
    
    Read(Client,Tags.CU_V)
    
    variables = vars(Tags)
    variables = np.array(list(variables.items()))
    variables = variables[start:]
    #variables[:,1] = variables[:,1].astype(int)
    #variables = variables[variables[:,1].argsort()]
    Tag_List = []
    for item in variables:
        Tag_List.append([item[1], False])
            
    temp_list = []
    temp_list.append(Gather(Client, Tag_List, count = 20, sleep_time = 0.010))
    
    with open(filename,'w') as f: #Opening a file with the current date and time
        for num, line in enumerate(temp_list[0]):
            f.write(variables[num,0] + ": " + str(line).strip("([])")+'\n') #Writing each line in that file
        f.close() #Closing the file to save it


def Ramp_One_Way(Client, Tag_Number, End_Value = 0, Max_Step = 0.010, Return = "N", Read_Tag = None, \
                 count = 25, sleep_time = 0.020, step_time = 0.25, Image = False):
    '''  -Future: input a safety method to make sure we aren't drastically changing values

        Inputs: Client, see "Client" Above
            __ Tag_Number: which modbus to read, convention is this: input the modbus start tag number. Must have a modbus tag.
            __ End_Value: End value which you want the modbus to ramp the magnet to
            __ Max_Step: The maximum change in amerage you want the magnet to be able to move, default 10 mA
            __ Return: "N" if you don't want the data in a list, "Y" if you do want the data in a list. Default "N"
            __ Read_Tag: Which value do you want to be recording, if "00000" no value is recorded, otherwise it reads that tag. Default "00000"
            __ count: how many datapoints do you want to average over for the Read_Tag function. Default is 25

        -Must have established client before attempting to write to the client
        
        -Outputs: Writes to the specified magnet, outputs either a list of the written values,
            or a list of the written values with a list of the collected Read_Tag values merged with written mag values.

        Method:
                - Define the start and end value, take the difference between the two
                - Define the number of steps needed to safely walk to that value
                - Check that there hasn't been any human intervention
                - Write a new value to PLC (see Write())
                - Record both written value and the value of a selected tag
                - Check if there is a requested save
                - Save, or exit
        
        -Required imports
        from pymodbus.client.sync import ModbusTcpClient
        from pymodbus.payload import BinaryPayloadDecoder
        from pymodbus.constants import Endian

        -example:
        Client = Make_Client('192.168.1.2')
        DBA_Collection_Through_Aperture = Ramp_One_Way(Client, 22201, .450,.010,"Y","11109")

        #User plotting choice:
        plot(DBA_Collection_Through_Aperture[0],DBA_Collection_Through_Aperture[1])


    '''
    
    Start_Value = Read(Client,Tag_Number)
    
    Delta = End_Value-Start_Value

    if np.isclose(0,Delta) == True:
        #print("skip")
        return


    Steps = 10

    #Insures that we are making step sizes with the appropriate scaling
    while abs(Delta/Steps) >= Max_Step:
        Steps += 1

    #print("Difference between start and end value: {0:.3f} Amps".format(Delta))

    write_value_list = []
    collected_list = []

    for i in range(Steps + 1):

        #This is to enforce that any human intervention will break the program and prevent it from running further
        #Note that we are using the write value from the last run in the loop to check that the value is the same as the loop left it
        if i != 0:
            temp_check = Read(Client,Tag_Number)

            if abs(temp_check - write_value) >= 0.001:
                break
        
            
        write_value = Start_Value + (Delta/Steps)*i

        write_value_list.append(write_value)

        Write(Client, Tag_Number, write_value)

        if Read_Tag != None:

            collected_list.append(Read(Client,Read_Tag,Average = True,count = count))
            
            if Image:
                time.sleep(step_time/2)
                
                snap(Camera)
                
        
        else:
            time.sleep(sleep_time * 10)
                
            

    if Return == "N":
        return
    if Return == "Y":
        if Read_Tag != "00000":
            return write_value_list, collected_list
        else:
            return write_value_list
        

        
def Ramp_Two_Way(Client, Tag_Number, End_Value = 0, Runs = 1, Max_Step = 0.010, Return = "N", Read_Tag = "00000", count = 25):
    '''  -Future: input a safety method to make sure we aren't drastically changing values

        Inputs: Client, see "Client" Above
            __ Tag_Number: which modbus to read, convention is this: input the modbus start tag number. Must have a modbus tag.
            __ End_Value: End value which you want the modbus to ramp the magnet to
            __ Max_Step: The maximum change in amerage you want the magnet to be able to move, default 10 mA
            __ Return: "N" if you don't want the data in a list, "Y" if you do want the data in a list. Default "N"
            __ Read_Tag: Which value do you want to be recording, if "00000" no value is recorded, otherwise it reads that tag. Default "00000"
            __ count: how many datapoints do you want to average over for the Read_Tag function. Default is 25

        -Must have established client before attempting to write to the client
        
        -Outputs: Writes to the specified magnet, outputs either a list of the written values,
            or a list of the written values with a list of the collected Read_Tag values merged with written mag values.

        Method:
                - Define the start and end value, take the difference between the two
                - Define the number of steps needed to safely walk to that value
                - Check that there hasn't been any human intervention
                - Write a new value to PLC (see Write())
                - Record both written value and the value of a selected tag
                - Check if there is a requested save
                - Save, or exit
        
        -Required imports
        from pymodbus.client.sync import ModbusTcpClient
        from pymodbus.payload import BinaryPayloadDecoder
        from pymodbus.constants import Endian

        -example:
        Client = Make_Client('192.168.1.2')
        DBA_Collection_Through_Aperture = Ramp_One_Way(Client, 22201, .450,.010,"Y","11109")

        #User plotting choice:
        plot(DBA_Collection_Through_Aperture[0],DBA_Collection_Through_Aperture[1])


    '''
    
    Start_Value = Read(Client,Tag_Number)
    
    Delta = End_Value-Start_Value

    Steps = 10

    #Insures that we are making step sizes with the appropriate scaling
    while abs(Delta/Steps) >= Max_Step:
        Steps += 1

    #print("Difference between start and end value: {0:.3f} Amps".format(Delta))

    write_value_list = []
    collected_list = []


    for _ in range(Runs):
        
        for i in range(Steps + 1):

            #This is to enforce that any human intervention will break the program and prevent it from running further
            #Note that we are using the write value from the last run in the loop to check that the value is the same as the loop left it
            if i != 0:
                temp_check = Read(Client,Tag_Number)

                if abs(temp_check - write_value) >= 0.001:
                    exit()
            
                
            write_value = Start_Value + (Delta/Steps)*i

            write_value_list.append(write_value)

            Write(Client, Tag_Number, write_value)

            if Read_Tag != "00000":

                collected_list.append(Read(Client,Read_Tag,Average = True,count = count))

        max_spot = write_value
        #Same loop as above, removed spacing
        for i in range(Steps + 1):
            
            if i != 0:
                
                temp_check = Read(Client,Tag_Number)
                
                if abs(temp_check - write_value) >= 0.001:
                    
                    exit()
                    
            write_value = max_spot - (Delta/Steps)*i #Only difference is the subtraction instead of addition
            
            write_value_list.append(write_value)
            
            Write(Client, Tag_Number, write_value)
            
            if Read_Tag != "00000":
                
                collected_list.append(Read(Client,Read_Tag,Average = True,count = count))
                
            

    if Return == "N":
        return
    if Return == "Y":
        if Read_Tag != "00000":
            return write_value_list, collected_list
        else:
            return write_value_list
    
def Rapid_T_Scan(Client, WFH_Tag, WFV_Tag, Read_Tag, Horizontal_Delta = 0, Vertical_Delta = 0, Resolution = 25):
    '''
    Inputs: Client, see "Client" abov
        __ WFH_Tag: The tag for the horizontal controls for the window frame we are scanning
        __ WFV_Tag: The tag for the horizontal controls for the window frame we are scanning
        __ Read_Tag: This is the modbus tag for the data output tag we are reading, generally a beam dump outputting current
        __ Horizontal_Delta (Amps): How far we want to scan in the magnet frame space with the horizontal tag
        __ Vertical_Delta (Amps): How far we want to scan in the vertical magnet space
        __ Resolution: For each leg of the scan from the center, how many points do we want to collect
        
    Outputs: A window frame scan in which a quick sweep is performed with no regard to data collection. This is done for data gathering.
    Starting at the center. The scan is done in the following order:
        -- Move Upward, taking *Resolution* number of data points
        -- Quickly scan to the left center, gathering no data
        -- Move to the right, through the center, and to the rightmost point we are gathering, taking *Resolution* x 2 data points
        -- Quickly scan to the bottom center, gathering no data
        -- Move upward back to the center, taking *Resolution* data points
        
        Total data taken: Resolution * 4 data points
        
        Data: An array containing three columns of data. The first column is the horizontal window frame value,
            The second column is the vertical window frame value
            The third column contains the data taken from *Read_Tag* at the two values listed above
            
    Common changes to be made:
        -- Averaging number: Default is 25, this is how many points will be averaged over for the data collection, this number may
            want to be reduced to speed up the scanning
        -- Sleep_Time: (S) this is the amount of time between reads that we rest before making another request from the PLC
            The minimum value on the system as of 01/01/2020 is a 7 ms delay (0.007) to avoid repeat values
        -- Chunk_Size: This is the amount of chunky steps taken in the quick walking to the corner values, these are necessary to 
            Avoid magnetizing our magnets in the system.
        -- Chunk_rest_factor: This is a multiple from the sleep time on the averaging loop, we typically want a longer rest here
            to fully allow the PLC to catch up.
   
    '''
    WFH_Start = Read(Client, WFH_Tag) #Taking the start value for the window frames
    WFV_Start = Read(Client, WFV_Tag)

    Delta_H = Horizontal_Delta/Resolution #The step size for each step along the data taking routes
    Delta_V = Vertical_Delta/Resolution
    
    Averaging_Number = 25 #Number of times we read the Read tags for averaging, recommended about 25 if pulsing, 10 if CW
    Sleep_Time = .010 #Sleep time between reads
    Chunks = 4 #Inverse number of chunks, we use Resolution/Chunks, thus, the maximum value allowable is Resolution
    Chunk_rest_factor = 10 #Multiple of Sleep_Time to allow PLC to catch up.
    
    Data = np.zeros([(Resolution * 4),3]) #Initializing our data into an empty array to write over later
    
    #################################################################################
    
    #####
    #Moving upward first
    #####
    
    Loop_Number = 0 #Repeat variable, used to calculate where to write to, this iterates up to 3
    for i in range(Resolution):
        WFV_Write_Value = WFV_Start + ((i+1) * Delta_V) #Moving in the vertical direction
        
        Write(Client, WFV_Tag, WFV_Write_Value) #Writing the value to the PLC
        
        Data[i + Resolution * Loop_Number, 0] = Read(Client, WFH_Tag) #Storing the Horizontal Value
        Data[i + Resolution * Loop_Number, 1] = Read(Client, WFV_Tag) #Storing the Vertical Value
        Data[i + Resolution * Loop_Number, 2] = Read(Client, Read_Tag, Average = True, count = Averaging_Number, sleep_time = Sleep_Time) #Storing the Read_Tag averaged value
        
        #This loop is being repeated with some minor changes being made in the Write_values sections these
            #Are to reflect the changes in direction. Otherwise, refer to documentation in this loop for help.
    
        
    #####
    #Now moving to the left center
    #####
    
    for i in range(int(Resolution/Chunks)): #We still don't want huge steps so we simply reduce the steps taken by chunks
        WFH_Write_Value = WFH_Start - (i * (Horizontal_Delta/int(Resolution/Chunks))) #Chunking horizontally
        WFV_Write_Value = (WFV_Start + Vertical_Delta) - ((i+1) * (Horizontal_Delta/int(Resolution/Chunks))) #Chunking Vertically
        
        Write(Client, WFH_Tag, WFH_Write_Value) #Writing the values, notice no data is being collected here
        Write(Client, WFV_Tag, WFV_Write_Value)
        
        time.sleep(Sleep_Time*Chunk_rest_factor)
    
    #####
    #Now moving right to center center
    #####
    
    Loop_Number = 1
    for i in range(Resolution):
        WFH_Write_Value = (WFH_Start - Horizontal_Delta) + (i * Delta_H) 
        
        Write(Client, WFH_Tag, WFH_Write_Value)
        
        Data[i + Resolution * Loop_Number, 0] = Read(Client, WFH_Tag)
        Data[i + Resolution * Loop_Number, 1] = Read(Client, WFV_Tag) 
        Data[i + Resolution * Loop_Number, 2] = Read(Client, Read_Tag, Average = True, count = Averaging_Number, sleep_time = Sleep_Time)
        
        
    #####
    #Now moving center center to center right
    #####
    
    Loop_Number = 2
    for i in range(Resolution):
        WFH_Write_Value = WFH_Start + (i * Delta_H)
        
        Write(Client, WFH_Tag, WFH_Write_Value)
        
        Data[i + Resolution * Loop_Number, 0] = Read(Client, WFH_Tag)
        Data[i + Resolution * Loop_Number, 1] = Read(Client, WFV_Tag)
        Data[i + Resolution * Loop_Number, 2] = Read(Client, Read_Tag, Average = True, count = Averaging_Number, sleep_time = Sleep_Time)
        
    #####
    #Now moving Center Bottom
    #####
    
    for i in range(int(Resolution/Chunks)):
        WFH_Write_Value = (WFH_Start + Horizontal_Delta) - ((i+1) * (Horizontal_Delta/int(Resolution/Chunks)))
        WFV_Write_Value = (WFV_Start) - ((i+1) * (Vertical_Delta/int(Resolution/Chunks)))

        Write(Client, WFH_Tag, WFH_Write_Value)
        Write(Client, WFV_Tag, WFV_Write_Value)

        time.sleep(Sleep_Time*Chunk_rest_factor)
    
    #####
    #Now Moving Center Bottom to Center Center again
    #####
    
    Loop_Number = 3
    for i in range(Resolution):
        WFV_Write_Value = (WFV_Start - Vertical_Delta) + ((i+1) * Delta_V)
        
        Write(Client, WFV_Tag, WFV_Write_Value)
        
        Data[i + Resolution * Loop_Number, 0] = Read(Client, WFH_Tag)
        Data[i + Resolution * Loop_Number, 1] = Read(Client, WFV_Tag)
        Data[i + Resolution * Loop_Number, 2] = Read(Client, Read_Tag, Average = True, count = Averaging_Number, sleep_time = Sleep_Time)
        
            
    
    return Data

def Ramp_Two(Client, Magnet_1_Tag, Magnet_2_Tag, Magnet_1_Stop = 0, Magnet_2_Stop = 0, Resolution = 25, sleep_time = .050):
    '''
    Inputs: Client, see "Client" abov
        __ Magnet_1_Tag: The tag for the horizontal controls for the window frame we are scanning
        __ Magnet_2_Tag: The tag for the horizontal controls for the window frame we are scanning
        __ Magent_1_Stop: This is the modbus tag for the data output tag we are reading, generally a beam dump outputting current
        __ Magnet_2_Stop (Amps): How far we want to scan in the magnet frame space with the horizontal tag
        __ Resolution: For each leg of the scan from the center, how many points do we want to collect
        
    Outputs: Moves two magnets to their "stop" value in "Resolution" steps
    
    !Returns nothing!
    
    Logic:
        -- Check to see if there has been human intervention, if so, break
        -- Write to the magnets the next step value towards the goal
        -- Sleep for a small amount of time to avoid crowding the PLC
   
    '''
    
    Magnet_1_Start =  Read(Client,Magnet_1_Tag)
    Magnet_2_Start =  Read(Client,Magnet_2_Tag)
    
    Delta_1 = Magnet_1_Stop - Magnet_1_Start
    Delta_2 = Magnet_2_Stop - Magnet_2_Start
    
    for a__ in range(1,Resolution+1):
    
        if a__ != 1: #Don't check on the first run due to absence of write values
        
            temp_check_1 = Read(Client,Magnet_1_Tag) #Take the current value of Magnet 1
            temp_check_2 = Read(Client,Magnet_2_Tag) #Take the current value of Magnet 2
        
            #Comparing the current value to the last write value, if it is different, this updates the break loop for both Horizontal and Vertical
            if abs(temp_check_1 - Magnet_1_Write_Value) >= 0.001: #Magnet 1 Check
                print("Loop Broken")
                break
            if abs(temp_check_2 - Magnet_2_Write_Value) >= 0.001: #Magnet 2 Check
                print("Loop Broken")
                break
            
        Magnet_1_Write_Value = Magnet_1_Start + (Delta_1/Resolution)*a__
        Magnet_2_Write_Value = Magnet_2_Start + (Delta_2/Resolution)*a__
    
        Write(Client, Magnet_1_Tag, Magnet_1_Write_Value)
        Write(Client, Magnet_2_Tag, Magnet_2_Write_Value)

        time.sleep(sleep_time)
        
    return

def Save_and_Plot(Data, Save = True, Plot = True):
    '''
    Inputs: A 3 column array as produced by Rapid_T_Scan above
    
    Outputs: A txt file with the data in it and a 3D plot
    '''

    now = datetime.today().strftime('%y%m%d_%H%M') #Taking the current time in YYMMDD_HHmm format to save the plot and the txt file
    
    if Save == True:
        with open(now +'.txt', 'w') as f: #Open a new file by writing to it named the date as created above + .txt
    
            for i in Total_Data:
                f.write(str(i) + '\n')
            
            f.close()

    
    ######
    #Plotting
    ######
    x = Data[:,0]
    x = x.astype(np.float)

    y = Data[:,1]
    y = y.astype(np.float)

    z = Data[:,2]
    z = z.astype(np.float)

    fig = plt.figure(figsize = (12,8))
    ax = Axes3D(fig)
    ax.scatter(x, y, z, c=z, cmap='viridis', linewidth=0.5)

    ax.set_xlabel("Window Frame Horizontal Amperage")
    ax.set_ylabel("Window Frame Vertical Amperage")
    ax.set_zlabel("Collected Current")
    ax.set_title("Rapid Dog Leg Results")
    
    if Save == True:
        plt.savefig(now + '_graph.svg')


    plt.show()


def FWHM(x,y,extras = False):
    all_above = [abs(x) if abs(x) >= (abs(y).max())/2 else None for x in y]
    all_below = [abs(x) if abs(x) < (abs(y).max())/2 else None for x in y]
    
    good_x = []
    for i in range(len(x)):
        if all_above[i] != None:
            good_x.append(x[i])
            
    width = max(good_x)-min(good_x)

    if extras == False:
        return all_above, all_below, width
    else:
        good_sum = sum([abs(i) if i != None else 0 for i in all_above])
        bad_sum = sum([abs(i) if i != None else 0 for i in all_below])
        center = np.median(np.array([i for i in good_x if i != None]))
        return all_above, all_below, width, center, good_sum, bad_sum

    
def convert_to_mms(locs, Delta_1): #Converting the xlabels to mm
    new_list = []
    for i in locs:
        new_list.append(round(i/Delta_1*12,2)) #Our conversion formula
    return new_list

def Delta1_2(locs, Delta_1, Delta_2): #Converting the 1 values to the same displacement in 2
    new_list = []
    for i in locs:
        new_list.append(round(i/Delta_1*Delta_2,2))
    return new_list

def Dog_Leg(Client, WF1H_Tag, WF2H_Tag, WF1V_Tag, WF2V_Tag, Target_1_Tag, \
            Target_2_Tag, Tag_List, WF1H_Start = None, WF2H_Start = None, \
            WF1V_Start = None, WF2V_Start = None, Read_Steps = 40, \
            Delta_1 = 0.384, Delta_2 = 0.228, Threshold_Percent = 20, count = 20, sleep_time = 0.010, \
            Deviation_Check = 0.001, Zoom_In_Factor = 1, Scale_Factor = 0.91, iterator = None):

    '''
    Inputs:
        __ Client: Modbus TCP client that hosts PLCs
        __ WF1H_Tag: The modbus start address for the first horizontal window frame we are controlling
        __ WF2H_Tag, WF1V_Tag, WF2V_Tag: Horizontal and vertical window frame modbus address
        __ Target_1_Tag, Target_2_Tag: The modbus address for the beam target current dumps
        __ Tag_List: See Gather above, list of lists with tag values and wether or not they are
            averaged. These will be the tags grabbed at each step
        __ WF1H_Start, WF2H_Start, WF1V_Start, WF2V_Start: Our starting value for each of these magnets
            If default of None remains, then the dog leg is taken from the starting point
        __ Read_Steps: The amount of steps, in each direction, that we will attempt to take the Dog Leg
            This values divides the delta by this number, so step size will change as this value changes.
        __ Delta_1, Delta_2: The amount that the first window frame and second window frames will move
            the ratio of these is determined by the distance and relative strength of the two window 
            frames; float: 0 < Delta
        __ Threshold_Percent: This is the percent of the starting collection required to keep the dog leg
            moving in the current direction that it is. Once the dog leg falls below this threshold, the 
            dog leg will break out of a loop and go back to the starting point; 
            float:  0 <= Threshold_Percent <= 1
        __ count: This is the number of points that will be averaged at each Dog Leg iteration;
            integer: 1 <= count
        __ sleep_time: time, in seconds, to wait between each averaged point in count;
            float: 0 <= sleep_time
        __ Deviation_Check: Threshold, in Amps, that the magnet value setpoint must deviate from the
            last written point for the program to go back to the start and end. This is to ensure
            that if there is any human intervention, the dog leg will go back to the start and return
            control to the operator; float: 0 < Deviation_Check
        __ Zoom_In_Factor: This exists to adjust scaling on the output graph. This is primarily used when
            changing the magnets that are being Dog Legged
        __ Scale_Factor: Similar to Zoom_In_Factor, truly a relic
    
    Outputs:
        A graph named (current time)_graph.svg that contains a graph and table of the dog leg data taken
        A txt file containing a snapshot of the system at the end of the dog leg named 
            (current time)_snapshot.txt containing all of the read values for each magnet we have listed 
            in our tag database (Tag_Database.py)
        A txt file containing all of the Dog Leg data gathered from the Tag List throughout the run
            named (current time).txt
        
        returns a figure of merit for dog leg optimization. This is the FWHM for each axis squared and flipped
            in sign (to make minimization problems more intuitive)
            
    Requirements:
        Tag_Database must be in the same directory folder as this Master file.
        This function must be contained within the Master file (do not copy and paste out of this file)
        
        imports:
            from pymodbus.client.sync import ModbusTcpClient
            from pymodbus.payload import BinaryPayloadDecoder
            from pymodbus.payload import BinaryPayloadBuilder
            from pymodbus.constants import Endian
            numpy
            matplotlib.pyplot
            from datetime import datetime
            time
            concurrent.futures
    
    Logic:
        Ramp to our starting point
        Take data Read_Steps to the right by moving mag 1 to the right and mag 2 to the left
        Move to start
        Take data Read_Steps to the left, upward, and downward
        Move to start between each
        Take the Full width half max of the horizontal and vertically produced lines
        Output files
    '''
    
    
    import Tag_Database as Tags

    start_time = time.time()

    Pulsing_Status = bool(Read(Client, Tags.Pulsing_Output, Bool = True))

    EC = Read(Client, Tags.Emitted_Current, Average = True, count = count)
    
    #Move to our starting point
    
    #If no starting values are provided, we take a dog leg from the current position
    
    if WF1H_Start == None:
        WF1H_Start = Read(Client, WF1H_Tag)
    if WF2H_Start == None:
        WF2H_Start = Read(Client, WF2H_Tag)
    if WF1V_Start == None:
        WF1V_Start = Read(Client, WF1V_Tag)
    if WF2V_Start == None:
        WF2V_Start = Read(Client, WF2V_Tag)
    
    Ramp_Two(Client, WF1H_Tag, WF2H_Tag, Magnet_1_Stop = WF1H_Start, Magnet_2_Stop = WF2H_Start, Resolution = Read_Steps, sleep_time = sleep_time)
    Ramp_Two(Client, WF1V_Tag, WF2V_Tag, Magnet_1_Stop = WF1V_Start, Magnet_2_Stop = WF2V_Start, Resolution = Read_Steps, sleep_time = sleep_time)
    
    Full_Data_Set = list()
    H_Broken = V_Broken = False #Creating the check tag for the dog leg, starting out as false as no errors could have been raised yet
    Start_Current = (Read(Client, Target_1_Tag, Average = True, count = count,sleep_time = sleep_time) + \
                 Read(Client, Target_2_Tag, Average = True, count = count,sleep_time = sleep_time))
    
    print("Right Displacement")

    ## Each of these are adding our data to a list as instantiated above. These will appear at each data gathering point
    Full_Data_Set.append(Gather(Client, Tag_List, count = count, sleep_time = sleep_time))

    for Right_Steps in range(1, Read_Steps + 1):
        if Right_Steps != 1: #Don't check on the first run due to absence of Window Frame write values
            #Comparing the current value to the last write value, if it is different, this updates the break loop for both Horizontal and Vertical
            if abs(Read(Client,WF1H_Tag) - WF1H_Write_Value) >= Deviation_Check or abs(Read(Client,WF2H_Tag) - WF2H_Write_Value) >= Deviation_Check: #WF1H Check
                H_Broken = V_Broken = True
                print("Loop Broken")
                break   

        WF1H_Write_Value = WF1H_Start + (Delta_1/Read_Steps)*Right_Steps #Calculated value to walk 1 to the right
        WF2H_Write_Value = WF2H_Start - (Delta_2/Read_Steps)*Right_Steps #Calculated value to walk 2 to the left

        Write(Client, WF1H_Tag, WF1H_Write_Value) #Writing to 1h
        Write(Client, WF2H_Tag, WF2H_Write_Value) #Writing to 2h
        #print(WF1H_Write_Value)
        #print(WF2H_Write_Value)

        Full_Data_Set.append(Gather(Client, Tag_List, count = count, sleep_time = sleep_time))
        if abs(Full_Data_Set[-1][5] + Full_Data_Set[-1][6]) < abs(Threshold_Percent*Start_Current*.01): #Checking our threshold
            break
    print("Moving to center")
    
    Ramp_Two(Client, WF1H_Tag, WF2H_Tag, Magnet_1_Stop = WF1H_Start, Magnet_2_Stop = WF2H_Start, Resolution = Right_Steps//2, sleep_time = sleep_time) #Moves back to the start in half of the same # of steps taken

    print("Left Displacement")

    Full_Data_Set.append(Gather(Client, Tag_List, count = count, sleep_time = sleep_time))

    for Left_Steps in range(1, Read_Steps + 1):
        if H_Broken or V_Broken == True:
            break
        if Left_Steps != 1: #Don't check on the first run due to absence of Window Frame write values
            #Comparing the current value to the last write value, if it is different, this updates the break loop for both Horizontal and Vertical
            if abs(Read(Client,WF1H_Tag) - WF1H_Write_Value) >= Deviation_Check or abs(Read(Client,WF2H_Tag) - WF2H_Write_Value) >= Deviation_Check: #WF1H Check
                H_Broken = V_Broken = True
                print("Loop Broken")
                break

        WF1H_Write_Value = WF1H_Start - (Delta_1/Read_Steps)*Left_Steps
        WF2H_Write_Value = WF2H_Start + (Delta_2/Read_Steps)*Left_Steps

        Write(Client, WF1H_Tag, WF1H_Write_Value) #Writing to 1h
        Write(Client, WF2H_Tag, WF2H_Write_Value) #Writing to 2h
        #print(WF1H_Write_Value)
        #print(WF2H_Write_Value)

        Full_Data_Set.append(Gather(Client, Tag_List, count = count, sleep_time = sleep_time))

        if abs(Full_Data_Set[-1][5] + Full_Data_Set[-1][6]) < abs(Threshold_Percent*Start_Current*.01): #Checking our threshold
            break

    print("Moving to center")

    Ramp_Two(Client, WF1H_Tag, WF2H_Tag, Magnet_1_Stop = WF1H_Start, Magnet_2_Stop = WF2H_Start, Resolution = Left_Steps//2, sleep_time = sleep_time)

    print("Upward Displacement")

    Full_Data_Set.append(Gather(Client, Tag_List, count = count, sleep_time = sleep_time))

    for Upward_Steps in range(1, Read_Steps + 1):
        if H_Broken or V_Broken == True:
            break
        if Upward_Steps != 1: #Don't check on the first run due to absence of Window Frame write values
            #Comparing the current value to the last write value, if it is different, this updates the break loop for both Horizontal and Vertical
            if abs(Read(Client,WF1V_Tag) - WF1V_Write_Value) >= Deviation_Check or abs(Read(Client,WF2V_Tag) - WF2V_Write_Value) >= Deviation_Check: #WF1H Check
                H_Broken = V_Broken = True
                print("Loop Broken")
                break

        WF1V_Write_Value = WF1V_Start + (Delta_1/Read_Steps)*Upward_Steps
        WF2V_Write_Value = WF2V_Start - (Delta_2/Read_Steps)*Upward_Steps

        Write(Client, WF1V_Tag, WF1V_Write_Value) #Writing to 1h
        Write(Client, WF2V_Tag, WF2V_Write_Value) #Writing to 2h
        #print(WF1V_Write_Value)
        #print(WF2V_Write_Value)

        Full_Data_Set.append(Gather(Client, Tag_List, count = count, sleep_time = sleep_time))

        if abs(Full_Data_Set[-1][5] + Full_Data_Set[-1][6]) < abs(Threshold_Percent*Start_Current*.01): #Checking our threshold
            break

    print("Moving to center")

    Ramp_Two(Client, WF1V_Tag, WF2V_Tag, Magnet_1_Stop = WF1V_Start, Magnet_2_Stop = WF2V_Start, Resolution = Upward_Steps//2, sleep_time = sleep_time)

    print("Downward Displacement")

    Full_Data_Set.append(Gather(Client, Tag_List, count = count, sleep_time = sleep_time))

    for Downward_Steps in range(1, Read_Steps + 1):
        if H_Broken or V_Broken == True:
            break
        if Downward_Steps != 1: #Don't check on the first run due to absence of Window Frame write values
            #Comparing the current value to the last write value, if it is different, this updates the break loop for both Horizontal and Vertical
            if abs(Read(Client,WF1V_Tag) - WF1V_Write_Value) >= Deviation_Check or abs(Read(Client,WF2V_Tag) - WF2V_Write_Value) >= Deviation_Check: #WF1H Check
                H_Broken = V_Broken = True
                print("Loop Broken")
                break

        WF1V_Write_Value = WF1V_Start - (Delta_1/Read_Steps)*Downward_Steps
        WF2V_Write_Value = WF2V_Start + (Delta_2/Read_Steps)*Downward_Steps

        Write(Client, WF1V_Tag, WF1V_Write_Value) #Writing to 1h
        Write(Client, WF2V_Tag, WF2V_Write_Value) #Writing to 2h
        #print(WF1V_Write_Value)
        #print(WF2V_Write_Value)

        Full_Data_Set.append(Gather(Client, Tag_List, count = count, sleep_time = sleep_time))

        if abs(Full_Data_Set[-1][5] + Full_Data_Set[-1][6]) < abs(Threshold_Percent*Start_Current*.01): #Checking our threshold
            break

    print("Moving to center")

    Ramp_Two(Client, WF1V_Tag, WF2V_Tag, Magnet_1_Stop = WF1V_Start, Magnet_2_Stop = WF2V_Start, Resolution = Downward_Steps//2, sleep_time = sleep_time)
    
    if iterator == None:
        now = datetime.today().strftime('%y%m%d_%H%M%S') #Taking the current time in YYMMDD_HHmm format to save the plot and the txt file
    else:
        now = datetime.today().strftime('%y%m%d_%H%M%S') #Taking the current time in YYMMDD_HHmm format to save the plot and the txt file
        now += str(iterator)
        
    Controlled_Magnets = []
    
    Moved_Magnets = [WF1H_Tag, WF2H_Tag, WF1V_Tag, WF2V_Tag]
    variables = vars(Tags)
    for Mag_Tag in Moved_Magnets:
        for item in variables.items():
            if item[1] == Mag_Tag:
                Controlled_Magnets.append(item[0])

    Snapshot(Client, filename = now + "_snapshot.txt")
    
    with open(now + ".txt",'w') as f: #Opening a file with the current date and time
        f.write("{}(A), {}(A), {}(A), {}(A), Avg'd Emitted Current(mA), Avg'd Loop Mid(mA), Avg'd Loop Bypass(mA), Cu Gun (V), SRF Pt (dBm)\n"\
                .format(Controlled_Magnets[0], Controlled_Magnets[1], Controlled_Magnets[2], Controlled_Magnets[3]))
        for line in Full_Data_Set:
            f.write(str(line).strip("([])")+'\n') #Writing each line in that file
        f.close() #Closing the file to save it

    Full_Data_Array = np.array(Full_Data_Set) #Converting from a list to an array

    Horizontal_1 = Full_Data_Array[:(Right_Steps + 2 + Left_Steps),0] #Defining the steps on in the horizontal
    Horizontal_2 = Full_Data_Array[:(Right_Steps + 2 + Left_Steps),1]

    Vertical_1 = Full_Data_Array[(Right_Steps + 2 + Left_Steps):,2] #Defining the steps only in the Vertical
    Vertical_2 = Full_Data_Array[(Right_Steps + 2 + Left_Steps):,3]
    Dump_1 = Full_Data_Array[:,5] #Dump 1 all values
    Dump_2 = Full_Data_Array[:,6] #Dump 2 all values
    Emitted_Current = Full_Data_Array[:,4] #Emitted current all values
    Dump_Sum = Dump_1 + Dump_2 #All dump values

    #Dump Sum into percent from start
    Horizontal_Percent = Dump_Sum[:(Right_Steps + 2 + Left_Steps)]/Emitted_Current[:(Right_Steps + 2 + Left_Steps)]*100 #Defining the percents
    Vertical_Percent = Dump_Sum[(Right_Steps + 2 + Left_Steps):]/Emitted_Current[(Right_Steps + 2 + Left_Steps):]*100

    #FWHM of all of our data
    Horizontal_Above, Horizontal_Below, H_Width, Center_Value_1H, H_Goodsum, H_Badsum = FWHM(Horizontal_1, Horizontal_Percent, extras = True) #FWHM Calclations
    Vertical_Above, Vertical_Below, V_Width, Center_Value_1V, V_Goodsum, V_Badsum = FWHM(Vertical_1, Vertical_Percent, extras = True)
    _,_1,_2,Center_Value_2H,_3, _4 = FWHM(Horizontal_2, Horizontal_Percent, extras = True)
    _,_1,_2,Center_Value_2V,_3, _4 = FWHM(Vertical_2, Vertical_Percent, extras = True)


    #Plotting
    plt.figure(figsize = (9,9)) #Changing the figure to be larger

    ax1 = plt.subplot(1,1,1)
    ax1.scatter(Horizontal_1 - Horizontal_1[0], Horizontal_Above, label = 'Horizontal above FWHM',color = 'C0', alpha = 0.75) #Plotting 1H Above FWHM
    ax1.scatter(Horizontal_1 - Horizontal_1[0], Horizontal_Below, label = 'Horizontal below FWHM', color = 'C0', alpha = 0.5, marker = '.') #Plotting 1H below FWHM
    ax1.scatter(Vertical_1 - Vertical_1[0], Vertical_Above, label = 'Vertical above FWHM', color = 'C1', alpha = 0.75) #Plotting 1V above FWHM
    ax1.scatter(Vertical_1 - Vertical_1[0], Vertical_Below, label = 'Vertical below FWHM', color = 'C1', alpha = 0.5, marker = '.') #plotting 1V Below FWHM
    ax1.set_xlabel("Displacement WF6 (Amps)", fontsize = 12) #Setting xlabel
    ax1.set_ylabel("Collection from start (%); ({0:.2f}\u03BCA) collected at start".format(1000*abs(min(Dump_Sum))), fontsize = 12) #Making the y axis label
    ax1.set_title("Dog Leg Taken at " + now, fontsize = 16) #Making the title 
    ax1.legend(bbox_to_anchor = (0.5,0.27), loc = 'upper center') #Adding the legend and placing it in the bottom center of the plot

    ax1.minorticks_on() #Turning on the minor axis
    ax1.grid(True,alpha = 0.25,which = 'both',color = 'gray') #Making the grid (and making it more in the background)

    locs = ax1.get_xticks() #Grabbing the xticks from that axis

    ax2 = ax1.twiny() #Copying axis

    ax2.set_xticks(locs) #Setting xticks to same position
    ax2.set_xticklabels(convert_to_mms(locs, Delta_1)) #Converting to mm
    ax2.xaxis.set_ticks_position('top') # set the position of the second x-axis to top
    ax2.xaxis.set_label_position('top') # set the position of the second x-axis to top
    ax2.spines['top'].set_position(('outward', 0)) #Setting the ticks to go out of graph area
    ax2.set_xlabel('Displacement (mm)', fontsize = 12) #Label
    ax2.set_xlim(ax1.get_xlim()) #Setting to the same limit as prior axis

    ax3 = ax1.twiny() #Repeat for axis 3

    ax3.set_xticks(locs)
    ax3.set_xticklabels(Delta1_2(locs, Delta_1, Delta_2))
    ax3.xaxis.set_ticks_position('bottom') # set the position of the second x-axis to bottom
    ax3.xaxis.set_label_position('bottom') # set the position of the second x-axis to bottom
    ax3.spines['bottom'].set_position(('outward', 40))
    ax3.set_xlabel('Displacement WF7(Amps)', fontsize = 12)
    ax3.set_xlim(ax1.get_xlim())

    col_labels = ['WF6 Start (A)','WF7 Start (A)','FWHM', 'Center (6,7) (A)', 'Sum Above', 'Sum Below'] #Making the table column names
    row_labels = ['Horizontal','Vertical','Params'] #making the table row names
    table_vals = [[round(WF1H_Start,3), round(WF2H_Start,3), round(H_Width,3), "{:.3f}; {:.3f}".format(Center_Value_1H, Center_Value_2H), round(H_Goodsum,1), round(H_Badsum,1)],
                  [round(WF1V_Start,3) , round(WF2V_Start,3), round(V_Width,3), "{:.3f}; {:.3f}".format(Center_Value_1V, Center_Value_2V) , round(V_Goodsum,1), round(V_Badsum,1)],
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

    print("This DogLeg took {0:.1f} Seconds to run".format(time.time() - start_time)) #Printing the amount of time the dog leg took
    
    return -1 * ((H_Width)**2 + (V_Width)**2)
    
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
    
No lollygagging!

This program is to degauss the magnets

Good job. You did it.

Have fun, be safe, and remember: Only YOU can prevent magnetfires.

If you want to change some things, I did not make this program quite as intuitive as the others.

First thing's first:

plot = True will produce a plot after we are done running, just for your own happiness. Or, more importantly, when you are
  trying to change or improve the decay time.
  
testing = True will deactivate the functionality that communicates with the PLCs. This can be useful for...idk... testing.

All of the Amplitudes can be scaled varying by the magnet type. Will be adding functionality to scale differently based on secition
 but, if you are taking the time to read this, you can also do this yourself (so I don't have to test and approve the new version)
 by simply adding a conditional statement in the Dipole Amplitude lists that may change by an additional factor. I don't care, do what
 you want.
 
Points will change the real world time that this takes to run, NOT the amount of peaks or any decay parameters.

This code can be pretty useful... If we use it. However, I would much rather use a version that is integrated into our
ladder logic for interlock reasons (I do not want to add the overhead to every single python script I run to check for broken interlocks)

Seriously, though, the 5 minute run time is fine. You can deal with it. Click the button to run this and go make sure your radiation signs
are posted correctly or something. Alternatively, you could clean the area around you and improve it. Up to you, no judgement,
I am not your boss. But remember, things run a lot better if you don't change any of the key parameters.

All the best, 

Your friendly neighborhood pythoner programmer accelerator engineer, 

Austin Czyzewski

:)


''' Creator: Austin Czyzewski

Date Created: 12/04/2019
Date Last Updated: 05/27/2020
Tested and Approved: 05/27/2020

Purpose: Move the first dipole up and down while taking data of collected current

Route: Gather user input for changes to dipole 1 to be made
    - Take a system snapshot before the scan
    - Define the parameters of data gathering
    - Read the value, perform safety checks
    - Write new Dipole one setting
    - Read Collected current
    - Repeat in ascending order
    - Repeat in descending order until reaching starting value
    - Plot
    - Save plot and txt file w/ snapshot as header

'''

import matplotlib.pyplot as plt
from datetime import datetime
import time
import numpy as np
import Master as M
import Tag_Database as Tags

Client = M.Make_Client('192.168.1.2')


End_Value = float(input("What is the ending amperage that you want to ramp the magnet to? (Amps)   "))

#Grabbing all of our data for the system snapshot
#################################################
Pulsing_Status = bool(M.Read(Client, Tags.Pulsing_Output, Bool = True))
Emission_Setpoint = M.Read(Client, Tags.Emission_Set)

if Pulsing_Status:
    Emission_Actual = M.Read(Client, Tags.Emitted_Current, Average = True, count = 50, sleep_time = 0.025)
else:
    Emission_Actual = M.Read(Client, Tags.Emitted_Current, Average = True, count = 20, sleep_time = 0.010)
    
IR_Temp = M.Read(Client, Tags.IR_Temp)
VA_Temp = M.Read(Client, Tags.VA_Temp)
V0_Setpoint = M.Read(Client, Tags.V0_SP)
V0_Read = M.Read(Client, Tags.V0_Read)
Cathode_V = M.Read(Client, Tags.Voltage_Read)
Cathode_I = M.Read(Client, Tags.Current_Read)
Cathode_Z = M.Read(Client, Tags.Impedance_Read)
Cathode_P = M.Read(Client, Tags.Power_Read)
CU_Gun_Pf = M.Read(Client, Tags.CU_Pf)
CU_Gun_Pr = M.Read(Client, Tags.CU_Pr)
CU_Gun_Pt = M.Read(Client, Tags.CU_Pt)
CU_Gun_V = M.Read(Client, Tags.CU_V)
BH_Gun_Pf = M.Read(Client, Tags.BH_Pf)
BH_Gun_Pr = M.Read(Client, Tags.BH_Pr)
BH_Gun_Pt = M.Read(Client, Tags.BH_Pt)
SRF_Pf = M.Read(Client, Tags.SRF_Pf)
SRF_Pr = M.Read(Client, Tags.SRF_Pr)
SRF_Pt = M.Read(Client, Tags.SRF_Pt)
Pulse_Freq = M.Read(Client, Tags.Pulse_Frequency)
Pulse_Duty = M.Read(Client, Tags.Pulse_Duty)

Threshold_Percent = 0.05

#Uncomment to make variable number of runs
#Runs = int(input("How many runs do you want the Dipole to make?   "))

Runs = 1 #Number of times you want to ramp to the input value and back to the start
Dipole_Tag = Tags.DP1 #Modbus address of the magnet we are writing to
Step_size = .001 #Step Size, in Amps, that we are taking to reach our goal
Read = Tags.DBA_Bypass #Modbus address of the value we want to Read while we scan the magnet
count = 20 #Number of times we want to average the Read Tag value
pulsing_count = 50 #number of times we want to average the Read Tag value if pulsing

Start_Value = M.Read(Client, Dipole_Tag) #Recording the starting value of the Dipole
print("Started at {0:.3f} Amps".format(Start_Value))

DP1_Values = []
DBA_Collection = []
colors = []

print("Beginning Scan")
for i in range(Runs):
    print("Going to target value")
    
    if Pulsing_Status:
        DP1_Vals, DBA_Col = M.Ramp_One_Way(Client, Dipole_Tag, End_Value, Max_Step = Step_size, Return = "Y", Read_Tag = Read, count = pulsing_count)
    else:
        DP1_Vals, DBA_Col = M.Ramp_One_Way(Client, Dipole_Tag, End_Value, Max_Step = Step_size, Return = "Y", Read_Tag = Read, count = count)
    #The above function walks the magnet to the endpoint ,and returns the data
    
    DP1_Values += DP1_Vals #Adding the recorded data to the lists
    DBA_Collection += DBA_Col 
    
    colors += ['chocolate' for i in list(range(len(DP1_Vals)))] #Appending 'chocolate' as the color for this data set
    
    print("Going to start")
    
    if Pulsing_Status:
        DP1_Vals, DBA_Col = M.Ramp_One_Way(Client, Dipole_Tag, Start_Value, Max_Step = Step_size, Return = "Y", Read_Tag = Read, count = pulsing_count)
    else:
        DP1_Vals, DBA_Col = M.Ramp_One_Way(Client, Dipole_Tag, Start_Value, Max_Step = Step_size, Return = "Y", Read_Tag = Read, count = count)
    #The above statement walks us back to the start, and returns the data
    
    DP1_Values += DP1_Vals
    DBA_Collection += DBA_Col

    colors += ['firebrick' for i in list(range(len(DP1_Vals)))] #Appending 'firebrick' as the color for this data set
    
    
DP1_Values = np.array(DP1_Values)
DBA_Collection = np.array(DBA_Collection)

#Converting into millimeters
x_mindex = np.where(DBA_Collection == min(DBA_Collection[:len(DBA_Collection//(Runs*2))]))[0][0] #Gathering the peak point
x_maxdex = np.argmin(abs(DBA_Collection) > Threshold_Percent * abs(min(DBA_Collection))) #First point higher than the threshold percent of collection

mms = (max(DP1_Values[x_maxdex:x_mindex]) - DP1_Values[x_maxdex:x_mindex])/\
    (max(DP1_Values[x_maxdex:x_mindex]) - min(DP1_Values[x_maxdex:x_mindex]))*10

Percent_Collection = abs(DBA_Collection/Emission_Setpoint)*100

for iteration in range(x_maxdex):
    mms = np.insert(mms, 0, None)

while len(DP1_Values) > len(mms):
    mms = np.append(mms, None)

now = datetime.today().strftime('%y%m%d_%H%M') #Grabbing the time and date in a common format to save the plot and txt file to
Emission_String = str(int(abs(Emission_Actual)*1000))
V0_String = str(round(V0_Setpoint,2)).replace('.', '_')

plt.figure(figsize = (12,8))
plt.scatter(DP1_Values,DBA_Collection,color = colors, alpha = 0.5)

plt.grid(True,alpha = 0.25,which = 'both',color = 'gray') #Making a grid
plt.minorticks_on() #Setting the minor ticks

#Naming
plt.ylabel("DBA current collected (mA)")
plt.xlabel("Magnet Setting (A)")
plt.title("Dipole 1 current collected over walk from {0:.3f} to {1:.3f}".format(Start_Value, End_Value))
plt.suptitle("Orange = Ascending, Red = Descending",fontsize = 8, alpha = 0.65)

plt.savefig(now + '_V0_' + V0_String + '_' +  Emission_String.zfill(4) + '_graph.png', dpi = 450, trasnparent = True) #Saving to the time and date as png

save_list = np.array([DP1_Values, DBA_Collection, Percent_Collection, mms])

with open(now + '_V0_' + V0_String + '_' +  Emission_String.zfill(4) + 'EC.txt', 'w') as f:
    f.write("EC_Setpoint: {:.4f}, EC_Read: {:.4f}, IR_Temp: {:.4f}, VA_Temp: {:.4f}".format(Emission_Setpoint, Emission_Actual, \
                                                    IR_Temp, VA_Temp) + '\n')
    f.write("V0_Set: {:.4f}, V0_Read {:.4f}, Pulse_Bool: {:.4f}, Rise_Threshold: {:.4f}".format(V0_Setpoint, V0_Read, \
                                                    Pulsing_Status, Threshold_Percent) + '\n')
    
    f.write("Cathode Voltage: {:.4f}, Cathode Current: {:.4f}, Cathode Impedance: {:.4f}, Cathode Power: {:.4f}".format(Cathode_V, Cathode_I, \
                                                    Cathode_Z, Cathode_P) + '\n')
    f.write("Cu Gun Pf: {:.4f}, Cu Gun Pr: {:.4f}, Cu Gun Pt: {:.4f}, Cu Gun V: {:.4f}".format(CU_Gun_Pf, CU_Gun_Pr, \
                                                    CU_Gun_Pt, CU_Gun_V) + '\n')
    f.write("BH Pf: {:.4f}, BH Pr: {:.4f}, BH Pt: {:.4f}, Pulse Frequency: {:.4f}".format(BH_Gun_Pf, BH_Gun_Pr, \
                                                    BH_Gun_Pt, Pulse_Freq) + '\n')
    f.write("SRF Pf: {:.4f}, SRF Pr: {:.4f}, SRF Pt: {:.4f}, Pulse Duty: {:.4f}".format(SRF_Pf, SRF_Pr, \
                                                    SRF_Pt, Pulse_Duty) + '\n')
    f.write("Raw DP1(Amps), Raw Collection(mA), Percent Collection , Conversion to mms" + '\n')
    for row in range(len(save_list[0,:])):
        for column in range(len(save_list[:,0])):
            f.write(str(save_list[column,row]) + ', ')
        f.write('\n')
    f.close()
plt.show()
exit()


import numpy as np
import matplotlib.pyplot as plt
import seaborn
seaborn.set()
import time
from IPython.display import display, clear_output
import glob
import os


Files = glob.glob("*EC.txt")
Open_Files = []
for file in range(len(Files)):
    Temp_file = open(Files[file],'r')
    for num, i in enumerate(Temp_file):
        if num > 6: #This could be our culprit here, we now have many more columns
            Open_Files.append(i.strip("())\n"))
    Temp_file.close()
#print(Open_Files[100])
for line in range(len(Open_Files)):
    Open_Files[line] = Open_Files[line].strip("None, None").split(',')
#print(Open_Files[100])
np.array(Open_Files[100], dtype = np.float)
#Open_Files = np.array(Open_Files, dtype = np.float)
#Open_Files = np.array([np.array(i).astype(float) for i in Open_Files])
Open_Files = np.array([i[:2] for i in Open_Files])
Open_Files

Emissions = []
for i in Files:
    Emissions.append(int(i[-10:-6].strip("_")))
print(Emissions)


Iterator = int(len(Open_Files)/len(Files))
#print(Iterator)
All_Emissions = np.zeros([len(Files),Iterator, 2])
for i in range(len(Files)):
    #print(Open_Files[Iterator*i:Iterator*(i+1)])
    All_Emissions[i] = Open_Files[Iterator*i:Iterator*(i+1)]
    
    
All_Emissions_Avg = np.zeros([len(Files),int([i-1 if i%2 != 0 else i for i in [Iterator]][0]/2),2])

for num,k in enumerate(All_Emissions):
    for i in range(int(len(k)/2)):
        for j in range(int(len(k)/2)):
            #if np.shape(All_Emissions)[1] %2 != 0:
            if k[i,0] == k[j,0]:
                All_Emissions_Avg[num,i] = (([k[i,0],(k[i,1]+k[j,1])/2]))
                

plt.figure(figsize = (11,8.5))
view_list = range(len(All_Emissions_Avg))

for run in view_list:
    plt.plot(All_Emissions_Avg[run,:,0],1e5*abs(All_Emissions_Avg[run,:,1]/Emissions[run]),label = "{} \u03BCA Emitted".format(Emissions[run]),alpha = 0.5)
plt.minorticks_on()
plt.grid(True,alpha = 0.25,which = 'both',color = 'gray')
plt.legend()
plt.title("Collected Current Through DBA Aperture at Various Emissions")
#plt.xlim(.410,.430)
#plt.ylim(30,60)
plt.xlabel("Current in Dipole 1 (A)")
plt.ylabel("Current Collected as percentage of Emitted Current")
plt.gca().invert_xaxis()
plt.savefig("DP1_Scan_Results.svg",transparent = True)


#Created by: Austin Czyzewski -- 06/01/2020
#    Date Tested: NA
#         Date last updated: NA

############
### Notes:
# There is a suspected offset in the magntude of the Bypass dump and loop mid, this may cause a minor discrepancy from visually observed data
# and the data collected here.
############

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
#All necessary imports, Master must be 06/01/2020 version or greater
import Master as M
import time
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import Tag_Database as Tags

Client = M.Make_Client('10.50.0.10') #Connect to PLC

start_time = time.time() #Grabbing start time to take time of Dog Leg

Pulsing_Status = bool(M.Read(Client, Tags.Pulsing_Output, Bool = True)) #Detects whether pulsing or not

Move_To_Optimum = False #True or false, move to calculated center point after dog leg is finished?

# The tag list below is structured as multiple lists. Each of these lists contain the tag and whether or not that tag should be averaged
Tag_List = [[Tags.WF6H, False], [Tags.WF7H, False], [Tags.WF6V, False], [Tags.WF7V, False], \
            [Tags.Emitted_Current, True], [Tags.Recirculator_Halfway, True], \
            [Tags.Recirculator_Bypass, True], [Tags.CU_V, False], [Tags.SRF_Pt, False]]

Threshold_Percent = 0 #Float. The percentage of beam that we want to collect in order to turn the Dog Leg around

Deviation_Check = 0.001

Zoom_In_Factor = 1 #This is how much we want to zoomn in if we are interested in an artifact at the center of the dog leg or want higher precision in the center

Scale_Factor = 0.91 #This is how much we want to scale off of the excel documents used prior to Dog Legs

Read_Steps = 40 #Integer. Number of steps to be taken in the Dog Leg. Must be an integer

if Pulsing_Status:
    count = 25 #Integer. How many points will be recorded at each step and averaged over if pulsing
    sleep_time = 0.010 #Float.(ms)Sleep for 20 ms, this is tested to not overload PLC or give redundant data
else:
    count = 10 #Non-pulsing count of steps to take
    sleep_time = 0.010 #Non-pulsing sleep time

Delta_6 = 0.384*Scale_Factor/Zoom_In_Factor #Change in Window Frame 6 Values throughout the test, standard is 0.384 from Dog Leg Excel sheets (01/01/2020)
Delta_7 = 0.228*Scale_Factor/Zoom_In_Factor #Change in Window Frame 7 Values throughout the test, standard is 0.228 from Dog Leg Excel sheets (01/01/2020)

# Taking a system snapshot before the dog leg begins
####################################################
Emission_Setpoint = M.Read(Client, Tags.Emission_Set)
Emission_Actual = M.Read(Client, Tags.Emitted_Current, Average = True, count = count, sleep_time = sleep_time)
WF1H = M.Read(Client, Tags.WF1H)
WF1V = M.Read(Client, Tags.WF1V)
WF2H = M.Read(Client, Tags.WF2H)
WF2V = M.Read(Client, Tags.WF2V)
WF3H = M.Read(Client, Tags.WF3H)
WF3V = M.Read(Client, Tags.WF3V)
WF4H = M.Read(Client, Tags.WF4H)
WF4V = M.Read(Client, Tags.WF4V)
WF5H = M.Read(Client, Tags.WF5H)
WF5V = M.Read(Client, Tags.WF5V)
DP1 = M.Read(Client, Tags.DP1)
DP2 = M.Read(Client, Tags.DP2)
Sol1 = M.Read(Client, Tags.Sol1)
Sol2 = M.Read(Client, Tags.Sol2)
Sol3 = M.Read(Client, Tags.Sol3)
WF6H_Start = M.Read(Client,Tags.WF6H)
WF7H_Start = M.Read(Client,Tags.WF7H)
WF6V_Start = M.Read(Client,Tags.WF6V)
WF7V_Start = M.Read(Client,Tags.WF7V)
IR_Temp = M.Read(Client, Tags.IR_Temp)
VA_Temp = M.Read(Client, Tags.VA_Temp)
V0_Setpoint = M.Read(Client, Tags.V0_SP)
V0_Read = M.Read(Client, Tags.V0_Read)
Cathode_V = M.Read(Client, Tags.Voltage_Read)
Cathode_I = M.Read(Client, Tags.Current_Read)
Cathode_Z = M.Read(Client, Tags.Impedance_Read)
Cathode_P = M.Read(Client, Tags.Power_Read)
CU_Gun_Pf = M.Read(Client, Tags.CU_Pf)
CU_Gun_Pr = M.Read(Client, Tags.CU_Pr)
CU_Gun_Pt = M.Read(Client, Tags.CU_Pt)
CU_Gun_V = M.Read(Client, Tags.CU_V)
BH_Gun_Pf = M.Read(Client, Tags.BH_Pf)
BH_Gun_Pr = M.Read(Client, Tags.BH_Pr)
BH_Gun_Pt = M.Read(Client, Tags.BH_Pt)
SRF_Pf = M.Read(Client, Tags.SRF_Pf)
SRF_Pr = M.Read(Client, Tags.SRF_Pr)
SRF_Pt = M.Read(Client, Tags.SRF_Pt)
Pulse_Freq = M.Read(Client, Tags.Pulse_Frequency)
Pulse_Duty = M.Read(Client, Tags.Pulse_Duty)
EC = M.Read(Client, Tags.Emitted_Current)
Cu_Gun_Temp = M.Read(Client, Tags.Cu_Gun_Temp)
BH_OC_Temp = M.Read(Client, Tags.BH_OC_Temp)
DBA_Dump_CHWS = M.Read(Client, Tags.DBA_Dump_CHWS)

#Summing the start current of the two dumps
Start_Current = (M.Read(Client, Tags.Recirculator_Halfway, Average = True, count = count,sleep_time = sleep_time) + \
                 M.Read(Client, Tags.Recirculator_Bypass, Average = True, count = count,sleep_time = sleep_time))

H_Broken = V_Broken = False #Creating the check tag for the dog leg, starting out as false as no errors could have been raised yet

Full_Data_Set = list()
WF6H_Tag = Tags.WF6H #Storing these tags since we use them frequently.
WF7H_Tag = Tags.WF7H
WF6V_Tag = Tags.WF6V
WF7V_Tag = Tags.WF7V

print("Right Displacement")

## Each of these are adding our data to a list as instantiated above. These will appear at each data gathering point
Full_Data_Set.append(M.Gather(Client, Tag_List, count = count, sleep_time = sleep_time))

for Right_Steps in range(1, Read_Steps + 1):
    if Right_Steps != 1: #Don't check on the first run due to absence of Window Frame write values
        #Comparing the current value to the last write value, if it is different, this updates the break loop for both Horizontal and Vertical
        if abs(M.Read(Client,WF6H_Tag) - WF6H_Write_Value) >= Deviation_Check or abs(M.Read(Client,WF7H_Tag) - WF7H_Write_Value) >= Deviation_Check: #WF6H Check
            H_Broken = V_Broken = True
            print("Loop Broken")
            break   
            
    WF6H_Write_Value = WF6H_Start + (Delta_6/Read_Steps)*Right_Steps #Calculated value to walk 6 to the right
    WF7H_Write_Value = WF7H_Start - (Delta_7/Read_Steps)*Right_Steps #Calculated value to walk 7 to the left
    
    M.Write(Client, WF6H_Tag, WF6H_Write_Value) #Writing to 6h
    M.Write(Client, WF7H_Tag, WF7H_Write_Value) #Writing to 7h
    
    Full_Data_Set.append(M.Gather(Client, Tag_List, count = count, sleep_time = sleep_time))
    if abs(Full_Data_Set[-1][5] + Full_Data_Set[-1][6]) < abs(Threshold_Percent*Start_Current*.01): #Checking our threshold
        break
print("Moving to center")

M.Ramp_Two(Client, WF6H_Tag, WF7H_Tag, Magnet_1_Stop = WF6H_Start, Magnet_2_Stop = WF7H_Start, Resolution = Right_Steps//2, sleep_time = sleep_time) #Moves back to the start in hald of the same # of steps taken

print("Left Displacement")

Full_Data_Set.append(M.Gather(Client, Tag_List, count = count, sleep_time = sleep_time))

for Left_Steps in range(1, Read_Steps + 1):
    if H_Broken or V_Broken == True:
        break
    if Left_Steps != 1: #Don't check on the first run due to absence of Window Frame write values
        #Comparing the current value to the last write value, if it is different, this updates the break loop for both Horizontal and Vertical
        if abs(M.Read(Client,WF6H_Tag) - WF6H_Write_Value) >= Deviation_Check or abs(M.Read(Client,WF7H_Tag) - WF7H_Write_Value) >= Deviation_Check: #WF6H Check
            H_Broken = V_Broken = True
            print("Loop Broken")
            break
            
    WF6H_Write_Value = WF6H_Start - (Delta_6/Read_Steps)*Left_Steps
    WF7H_Write_Value = WF7H_Start + (Delta_7/Read_Steps)*Left_Steps
    
    M.Write(Client, WF6H_Tag, WF6H_Write_Value)
    M.Write(Client, WF7H_Tag, WF7H_Write_Value)
    
    Full_Data_Set.append(M.Gather(Client, Tag_List, count = count, sleep_time = sleep_time))
    
    if abs(Full_Data_Set[-1][5] + Full_Data_Set[-1][6]) < abs(Threshold_Percent*Start_Current*.01): #Checking our threshold
        break
        
print("Moving to center")

M.Ramp_Two(Client, WF6H_Tag, WF7H_Tag, Magnet_1_Stop = WF6H_Start, Magnet_2_Stop = WF7H_Start, Resolution = Left_Steps//2, sleep_time = sleep_time)

print("Upward Displacement")

Full_Data_Set.append(M.Gather(Client, Tag_List, count = count, sleep_time = sleep_time))

for Upward_Steps in range(1, Read_Steps + 1):
    if H_Broken or V_Broken == True:
        break
    if Upward_Steps != 1: #Don't check on the first run due to absence of Window Frame write values
        #Comparing the current value to the last write value, if it is different, this updates the break loop for both Horizontal and Vertical
        if abs(M.Read(Client,WF6V_Tag) - WF6V_Write_Value) >= Deviation_Check or abs(M.Read(Client,WF7V_Tag) - WF7V_Write_Value) >= Deviation_Check: #WF6H Check
            H_Broken = V_Broken = True
            print("Loop Broken")
            break
            
    WF6V_Write_Value = WF6V_Start + (Delta_6/Read_Steps)*Upward_Steps
    WF7V_Write_Value = WF7V_Start - (Delta_7/Read_Steps)*Upward_Steps
    
    M.Write(Client, WF6V_Tag, WF6V_Write_Value)
    M.Write(Client, WF7V_Tag, WF7V_Write_Value)
    
    Full_Data_Set.append(M.Gather(Client, Tag_List, count = count, sleep_time = sleep_time))
    
    if abs(Full_Data_Set[-1][5] + Full_Data_Set[-1][6]) < abs(Threshold_Percent*Start_Current*.01): #Checking our threshold
        break

print("Moving to center")

M.Ramp_Two(Client, WF6V_Tag, WF7V_Tag, Magnet_1_Stop = WF6V_Start, Magnet_2_Stop = WF7V_Start, Resolution = Upward_Steps//2, sleep_time = sleep_time)

print("Downward Displacement")

Full_Data_Set.append(M.Gather(Client, Tag_List, count = count, sleep_time = sleep_time))

for Downward_Steps in range(1, Read_Steps + 1):
    if H_Broken or V_Broken == True:
        break
    if Downward_Steps != 1: #Don't check on the first run due to absence of Window Frame write values
        #Comparing the current value to the last write value, if it is different, this updates the break loop for both Horizontal and Vertical
        if abs(M.Read(Client,WF6V_Tag) - WF6V_Write_Value) >= Deviation_Check or abs(M.Read(Client,WF7V_Tag) - WF7V_Write_Value) >= Deviation_Check: #WF6H Check
            H_Broken = V_Broken = True
            print("Loop Broken")
            break
            
    WF6V_Write_Value = WF6V_Start - (Delta_6/Read_Steps)*Downward_Steps
    WF7V_Write_Value = WF7V_Start + (Delta_7/Read_Steps)*Downward_Steps
    
    M.Write(Client, WF6V_Tag, WF6V_Write_Value)
    M.Write(Client, WF7V_Tag, WF7V_Write_Value)
    
    Full_Data_Set.append(M.Gather(Client, Tag_List, count = count, sleep_time = sleep_time))
    
    if abs(Full_Data_Set[-1][5] + Full_Data_Set[-1][6]) < abs(Threshold_Percent*Start_Current*.01): #Checking our threshold
        break

print("Moving to center")

M.Ramp_Two(Client, WF6V_Tag, WF7V_Tag, Magnet_1_Stop = WF6V_Start, Magnet_2_Stop = WF7V_Start, Resolution = Downward_Steps//2, sleep_time = sleep_time)

now = datetime.today().strftime('%y%m%d_%H%M') #Taking the current time in YYMMDD_HHmm format to save the plot and the txt file


with open(now + ".txt",'w') as f: #Opening a file with the current date and time
    f.write("EC_Setpoint, EC_Read, IR_Temp, VA_Temp, WF1H, WF1V\n")
    f.write("V0_Set, V0_Read, Pulse_Bool, Rise_Threshold, WF2H, WF2V\n")
    f.write("Cathode Voltage, Cathode Current, Cathode Impedance, Cathode Power, WF3H, WF3V\n")
    f.write("Cu Gun Pf, Cu Gun Pr, Cu Gun Pt, Cu Gun V, WF4H, WF4V\n")
    f.write("BH Pf, BH Pr, BH Pt, Pulse Frequency, WF5H, WF5V\n")
    f.write("SRF Pf, SRF Pr, SRF Pt, Pulse Duty, DP1, DP2\n")
    f.write("Sol 1, Sol2, Sol3, Cu Gun T, BH OC T, DBA CHWS\n")
    f.write("WF6H (A), WF7H(A), WF6V(A), WF7V(A), Avg'd Emitted Current(mA), Avg'd Loop Mid(mA), Avg'd Loop Bypass(mA), Cu Gun (V), SRF Pt (dBm)\n")
    f.write("{:.4f}, {:.4f}, {:.4f}, {:.4f}, {:.3f}, {:.3f}\n".format(Emission_Setpoint, Emission_Actual, IR_Temp, VA_Temp, WF1H, WF1V))
    f.write("{:.4f}, {:.4f}, {:.4f}, {:.4f}, {:.3f}, {:.3f}\n".format(V0_Setpoint, V0_Read, Pulsing_Status, Threshold_Percent, WF2H, WF2V))
    f.write("{:.4f}, {:.4f}, {:.4f}, {:.4f}, {:.3f}, {:.3f}\n".format(Cathode_V, Cathode_I, Cathode_Z, Cathode_P, WF3H, WF3V))
    f.write("{:.4f}, {:.4f}, {:.4f}, {:.4f}, {:.3f}, {:.3f}\n".format(CU_Gun_Pf, CU_Gun_Pr, CU_Gun_Pt, CU_Gun_V, WF4H, WF4V))
    f.write("{:.4f}, {:.4f}, {:.4f}, {:.4f}, {:.3f}, {:.3f}\n".format(BH_Gun_Pf, BH_Gun_Pr, BH_Gun_Pt, Pulse_Freq, WF5H, WF5V))
    f.write("{:.4f}, {:.4f}, {:.4f}, {:.4f}, {:.3f}, {:.3f}\n".format(SRF_Pf, SRF_Pr, SRF_Pt, Pulse_Duty, DP1, DP2))
    f.write("{:.3f}, {:.3f}, {:.3f}, {:.4f}, {:.4f}, {:.4f}\n".format(Sol1, Sol2, Sol3, Cu_Gun_Temp, BH_OC_Temp, DBA_Dump_CHWS))
    for line in Full_Data_Set:
        f.write(str(line).strip("([])")+'\n') #Writing each line in that file
    f.close() #Closing the file to save it
    
    Full_Data_Array = np.array(Full_Data_Set) #Converting from a list to an array

Horizontal_6 = Full_Data_Array[:(Right_Steps + 2 + Left_Steps),0] #Defining the steps on in the horizontal
Horizontal_7 = Full_Data_Array[:(Right_Steps + 2 + Left_Steps),1]

Vertical_6 = Full_Data_Array[(Right_Steps + 2 + Left_Steps):,2] #Defining the steps only in the Vertical
Vertical_7 = Full_Data_Array[(Right_Steps + 2 + Left_Steps):,3]
Dump_1 = Full_Data_Array[:,5] #Dump 1 all values
Dump_2 = Full_Data_Array[:,6] #Dump 2 all values
Emitted_Current = Full_Data_Array[:,4] #Emitted current all values
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

import numpy as np
import matplotlib.pyplot as plt
import seaborn
import time
seaborn.set()


def function(x_cord, y_cord):
    return 0.5 * x_cord**2 - 4 * x_cord + 0.2 * y_cord**2 + 2.7 * y_cord + 17.8

def centroid(vertex1, vertex2, vertex3):
    '''Vertices in the format:
    vertex1 = [X,Y]
    vertex2 = [X,Y]
    vertex3 = [X,Y]
    '''
    Ox = (vertex1[0] + vertex2[0] + vertex3[0])/3
    Oy = (vertex1[1] + vertex2[1] + vertex3[1])/3
    plt.scatter(Ox, Oy, color = 'black', label = 'centroid')
    return np.array([Ox, Oy])


def reflection_coordinate(worst_vertex, centroid, alpha = 1):
    '''blah
    
    '''    
    Xr = centroid + alpha*(centroid - worst_vertex)
    plt.scatter(Xr[0], Xr[1], color = 'blue', label = 'reflected coordinate', alpha = 0.25)
    return Xr

def expansion_coordinate(reflected_coordinate, centroid, gamma = 2):
    Xe = centroid + gamma*(reflected_coordinate - centroid)
    plt.scatter(Xe[0], Xe[1], color = 'gray', label = 'expansion coordinate', alpha = 0.25)
    return Xe

def contraction_coordinate(worst_vertex, centroid, rho = 0.5):
    Xc = centroid + rho*(worst_vertex - centroid)
    plt.scatter(Xc[0], Xc[1], color = 'firebrick', label = 'contraction coordinate', alpha = 0.25)
    return Xc

def simplex_optimization_step(dog_legs, alpha = 1, gamma = 2, rho = 0.5):
    """Dog Legs in the format:
        [[WFH, WFV, FOM],
         [WFH, WFV, FOM],
         [WFH, WFV, FOM]]
    
    """
    
    v1 = dog_legs[0]
    v2 = dog_legs[1]
    v3 = dog_legs[2]
    
    plt.scatter(dog_legs[:,0], dog_legs[:,1], color = 'red')
    
    Xo = centroid(v1[:2], v2[:2], v3[:2])
    
    worst_index = np.where(dog_legs[:,2] == min(dog_legs[:,2]))[0][0]
    best_index = np.where(dog_legs[:,2] == max(dog_legs[:,2]))[0][0]
    middle_index = np.where([i not in [best_index,worst_index] for i in [0,1,2]])[0][0] #Getting the index not used in [0,1,2]
        
    Xr = reflection_coordinate(dog_legs[worst_index,:2], Xo)
    #Xe = expansion_coordinate(Xr, Xo)
    #Xc = contraction_coordinate(dog_legs[worst_index,:2], Xo)
    
    #print(Xr, Xe, Xc)
    
    ##############
    #Ramp_Two to Xr, perform a dog leg
    #perform dog leg at Xr, get the figure of merit and compare in the following way
    ##############
    
    reflected_FOM = function(Xr[0], Xr[1]) #fake dog leg results
    

    if reflected_FOM > dog_legs[middle_index,2] and reflected_FOM <= dog_legs[best_index,2]:
        #replace worst coordinates with Xr and end of simplex step
        print('reflection step')
        reflected_coords = list(Xr)
        reflected_coords.append(reflected_FOM)
        dog_legs[worst_index] = np.array(reflected_coords)
        return dog_legs
    
    if reflected_FOM > max(dog_legs[:,2]):
        # Run a dog leg at Xe
        #Ramp_Two
        print('expansion step')
        Xe = expansion_coordinate(Xr, Xo)
        expansion_FOM = function(Xe[0], Xe[1])
        if expansion_FOM > reflected_FOM:
            expansion_coords = list(Xe)
            expansion_coords.append(expansion_FOM)
            dog_legs[worst_index] = np.array(expansion_coords)
            return dog_legs
        else:
            reflected_coords = list(Xr)
            reflected_coords.append(reflected_FOM)
            dog_legs[worst_index] = np.array(reflected_coords)
            return dog_legs
            
    
    if reflected_FOM <= dog_legs[middle_index,2]:
        # Run a dog leg at Xc
        #Ramp_Two
        print('ccontraction step')
        Xc = contraction_coordinate(dog_legs[worst_index,:2], Xo)
        contraction_FOM = function(Xc[0], Xc[1])
        if contraction_FOM >= dog_legs[worst_index,2]:
            contraction_coords = list(Xc)
            contraction_coords.append(contraction_FOM)
            dog_legs[worst_index] = np.array(contraction_coords)
            return dog_legs
        else:
            print("Your function is too far from the maximum please choose a new set of starting points")
    else:
        print("You gotta be kidding me")
        print(reflected_FOM)
        
sample_data = [[1,0],
              [.3,.2],
              [.5,-.3]]

sample_data[0].append(function(sample_data[0][0], sample_data[0][1]))
sample_data[1].append(function(sample_data[1][0], sample_data[1][1]))
sample_data[2].append(function(sample_data[2][0], sample_data[2][1]))

sample_data = np.array(sample_data)

plt.figure(figsize = (12,8))
plt.show()
new_simplex = simplex_optimization_step(sample_data)
for _ in range(10):
    new_simplex = simplex_optimization_step(new_simplex)
    time.sleep(1)
    plt.draw()
#plt.legend();
print(new_simplex, 'aaaa')
#plt.plot(new_simplex[:,0], new_simplex[:,1], alpha = 0.25, linewidth = 10)

"""
Created on Mon Dec 16 09:55 2019

@author: Austin Czyzewski

Goal: Load in a prior magnet save and walk the magnets to a new value

Route:
    - Create the tags to read
    - Load in an old magnet save
    - Write to the magnet the new setting using the Master Python file
"""
#imports: Pandas is used to store the excel file as a dataframe, Master is all modbus communications
import pandas as pd
import Master as M


#User input to define which magnet save to load in
Notebook = str(input("Which Magnet save to load? (YYMMDD_HHMM) "))

WFHnum = 21 #The number of horizontal window frames
Hnums = []

WFVnum = 21 #The number of vertical window frames
Vnums = []

DPnum = 8 #The number of Dipoles
Dpnums = []

Solnum = 9 #Number of solenoids
Solnums = []

for i in range(100):
    if i < WFHnum:
        Hnums.append(20203 + 4*i) #Modbus tag numbering convention for all of these, these are the starts and steps between likewise magnets
    if i < WFVnum:
        Vnums.append(20201 + 4*i)
    if i < DPnum:
        Dpnums.append(22201 + 2*i)
    if i < Solnum:
        Solnums.append(21201 + 2*i)

#Reading in the excel file as a dataframe for easier access (abbreviated as df)
        
excel_as_df = pd.read_excel('..\Magnet Saves\{}.xlsx'.format(Notebook)) #Using windows command line controls to direct python to the directory

Client = M.Make_Client('192.168.1.2') #Establishing a connection with the PLC, see Master.Make_Client

for i in range(len(Hnums)): #Iterate through the list of Horizontal window frames
    print("Window Frame {} H".format(i+1),Hnums[i],excel_as_df['WF H'].iloc[i]) #Print which magnet it is ramping
    M.Ramp_One_Way(Client, Hnums[i],excel_as_df['WF H'].iloc[i],Max_Step = 0.010) #Ramp that magnet, see Master.Ramp_One_Way
#Repeat for all types of magnets
for i in range(len(Vnums)):
    print("Window Frame {} V".format(i+1),Vnums[i],excel_as_df['WF V'].iloc[i])
    M.Ramp_One_Way(Client, Vnums[i],excel_as_df['WF V'].iloc[i],Max_Step = 0.010)

for i in range(len(Solnums)):
    print("Solenoid {}".format(i+1),Solnums[i],excel_as_df['Sol'].iloc[i])
    M.Ramp_One_Way(Client, Solnums[i],excel_as_df['Sol'].iloc[i],Max_Step = 0.010)
    
for i in range(len(Dpnums)):
    print("Dipole {}".format(i+1),Dpnums[i],excel_as_df['DP'].iloc[i])
    M.Ramp_One_Way(Client, Dpnums[i],excel_as_df['DP'].iloc[i],Max_Step = 0.005)


"""
Created on Mon Dec 16 09:55 2019

@author: aczyzewski

Goal: Load in a prior magnet save and walk the magnets to a new value

Route:
    - Create variables to store mag settings
    - Write to the magnets to 0
"""
import Master as M
import ctypes  # An included library with Python install.

Acknowledgment = 7
Acknowledgment = ctypes.windll.user32.MessageBoxW(0, "Are you sure that you want to ramp all of the magnets to 0? Please make sure that you do not operate with the Cathode on during this process", "Ramp All Magnets to 0", 4)

if Acknowledgment != 6:
    exit()
    


WFHnum = 21 #The number of horizontal window frames to control
Hnums = []

WFVnum = 21 #The number of vertical window frames to control
Vnums = []

DPnum = 8 #The number of Dipoles
Dpnums = []

Solnum = 9 #Number of solenoids
Solnums = []

for i in range(100):
    if i < WFHnum:
        Hnums.append(20203 + 4*i)
    if i < WFVnum:
        Vnums.append(20201 + 4*i)
    if i < DPnum:
        Dpnums.append(22201 + 2*i)
    if i < Solnum:
        Solnums.append(21201 + 2*i)


Client = M.Make_Client('192.168.1.2')

for i in range(len(Hnums)):
    print("Window Frame {} H".format(i+1))
    M.Ramp_One_Way(Client, Hnums[i],0,Max_Step = 0.010)

for i in range(len(Vnums)):
    print("Window Frame {} V".format(i+1))
    M.Ramp_One_Way(Client, Vnums[i],0,Max_Step = 0.010)

for i in range(len(Solnums)):
    print("Solenoid {}".format(i+1))
    M.Ramp_One_Way(Client, Solnums[i],0,Max_Step = 0.010)
    
for i in range(len(Dpnums)):
    print("Dipole {}".format(i+1))
    M.Ramp_One_Way(Client, Dpnums[i],0,Max_Step = 0.005)



"""
Created on Mon Dec  2 15:50:56 2019

@author: aczyzewski

Goal: Read Values from the PLC into an excel file for the purpose of Magnet Saves

Route:
    -Create variables to write values to
    -Update values from the PLC
    -Write variables to DataFrame
    -Port DataFrame to Excel File (.xlsx)
"""
#imports, numpy and pandas for data manipulation modbus to communicate with PLC
import numpy as np
import pandas as pd
from datetime import datetime
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.payload import BinaryPayloadBuilder
from pymodbus.constants import Endian
import time



##Importing Values from the PLC 
###############################

#Scratch -- if we only use the magnets in a list this is one way to one line it
#WFH_1,WFH_2,WFH_3,WFH_4,WFH_5,WFH_6,WFH_7,WFH_8,WFH_9,WFH_10,WFH_11,WFH_12,WFH_13,WFH_14,WFH_15,WFH_16,WFH_17,WFH_18,WFH_19,WFH_20,WFH_21,WFH_22,WFH_23,WFH_24,WFH_25,WFH_26,WFH_27,WFH_28,WFV_1,WFV_2,WFV_3,WFV_4,WFV_5,WFV_6,WFV_7,WFV_8,WFV_9,WFV_10,WFV_11,WFV_12,WFV_13,WFV_14,WFV_15,WFV_16,WFV_17,WFV_18,WFV_19,WFV_20,WFV_21,WFV_22,WFV_23,WFV_24,WFV_25,WFV_26,WFV_27,WFV_28,DP_1,DP_2,DP_3,DP_4,DP_5,DP_6,DP_7,DP_8,Sol_1,Sol_2,Sol_3,Sol_4,Sol_5,Sol_6,Sol_7,Sol_8,Sol_9,Sol_10,Sol_11,Sol_12,Sol_13 = 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
#End Scratch

#Window Frames Vertical
WFV_1 = 0
WFV_2 = 0
WFV_3 = 0
WFV_4 = 0
WFV_5 = 0
WFV_6 = 0
WFV_7 = 0
WFV_8 = 0
WFV_9 = 0
WFV_10 = 0
WFV_11 = 0
WFV_12 = 0
WFV_13 = 0
WFV_14 = 0
WFV_15 = 0
WFV_16 = 0
WFV_17 = 0
WFV_18 = 0
WFV_19 = 0
WFV_20 = 0
WFV_21 = 0
WFV_22 = 0
WFV_23 = 0
WFV_24 = 0
WFV_25 = 0
WFV_26 = 0
WFV_27 = 0
WFV_28 = 0

#Window Frames Horizontal
WFH_1 = 0
WFH_2 = 0
WFH_3 = 0
WFH_4 = 0
WFH_5 = 0
WFH_6 = 0
WFH_7 = 0
WFH_8 = 0
WFH_9 = 0
WFH_10 = 0
WFH_11 = 0
WFH_12 = 0
WFH_13 = 0
WFH_14 = 0
WFH_15 = 0
WFH_16 = 0
WFH_17 = 0
WFH_18 = 0
WFH_19 = 0
WFH_20 = 0
WFH_21 = 0
WFH_22 = 0
WFH_23 = 0
WFH_24 = 0
WFH_25 = 0
WFH_26 = 0
WFH_27 = 0
WFH_28 = 0

#Solenoids
Sol_1 = 0
Sol_2 = 0
Sol_3 = 0
Sol_4 = 0
Sol_5 = 0
Sol_6 = 0
Sol_7 = 0
Sol_8 = 0
Sol_9 = 0
Sol_10 = 0
Sol_11 = 0
Sol_12 = 0
Sol_13 = 0  
Sol_R_4 = 0
Sol_R_5 = 0
Sol_R_6 = 0
Sol_R_7 = 0
Sol_R_9 = 0
Sol_R_10 = 0
Sol_R_11 = 0
Sol_R_12 = 0

#Dipoles
DP_1 = 0
DP_2 = 0
DP_3 = 0
DP_4 = 0
DP_5 = 0
DP_6 = 0
DP_7 = 0
DP_8 = 0
DP_R_3 = 0
DP_R_4 = 0
DP_R_5 = 0
DP_R_6 = 0
DP_R_7 = 0
DP_R_8 = 0
DP_R_9 = 0

#non magnets
#_________________________________________________________________________________________________

#Copper Gun PF,PR,PT
CU_Pf = 0
CU_Pr = 0
CU_Pt = 0
CU_V = 0
Cu_Vac = 0

#BH PF,PR,PT
BH_Pf = 0
BH_Pr = 0
BH_Pt = 0
BH_V = 0

#SRF PF,PR,PT
SRF_Pf = 0
SRF_Pr = 0
SRF_Pt = 0
SRF_V = 0
SRF_Gain = 0
SRF_Cavity_Vac = 0
SRF_I_Time = 0
SRF_D_Time = 0


#HV Bias
HV_Bias = 0

Pulse_Freq = 0
Pulse_Duty = 0
Pulse_Delay = 0

#Temps
IR_Temp = 0
CHWS = 0
T1_OC = 0
T2_OC = 0
HV_Off_Setpoint = 0
HV_On_Setpoint = 0
DBA_App = 0
Coupler = 0
SRF_Tuner = 0
Up_Gate = 0
Down_Gate = 0
Sol_4_Temp = 0
Sol_5_Temp = 0
WF_10_Temp = 0
Bellows_1 = 0
Bellows_2 = 0
Bellows_3 = 0
DP_3_Temp = 0
DP_4_Temp = 0
DP_5_Temp = 0
DP_6_Temp = 0
DP_7_Temp = 0
DP_8_Temp = 0
W_Up_Break = 0

#Beamline vacs + flow
Cross_Vac = 0
Insulating_Vac = 0
Estation_Vac = 0
Loop_Vac = 0
W_target = 0
Low_E = 0
Low_E_Dt = 0
Low_E_Heat = 0
Loop = 0
Loop_Dt = 0
Loop_Heat = 0
W_Flow = 0
W_Dt = 0
W_Heat = 0

#Current Collection and Emission
DBA_Dump = 0
Loop_Dump = 0
Loop_Half = 0
W_Collect = 0
IC = 0
IC_Range = 0
IC_Dose = 0
IC_Dose_Accum = 0
Current_Emitted = 0



#Putting magnets into lists so that we can update using loops
#############################################################

WFHs = [WFH_1,WFH_2,WFH_3,WFH_4,WFH_5,WFH_6,WFH_7,WFH_8,WFH_9,WFH_10,WFH_11,WFH_12,WFH_13,WFH_14,WFH_15,WFH_16,WFH_17,WFH_18,WFH_19,WFH_20,WFH_21,WFH_22,WFH_23,WFH_24,WFH_25,WFH_26,WFH_27,WFH_28]
#Window Frame Horizontal Modbus locations
WFHnum = 21 #The number of horizontal window frames to control
Hnums = []

WFVs = [WFV_1,WFV_2,WFV_3,WFV_4,WFV_5,WFV_6,WFV_7,WFV_8,WFV_9,WFV_10,WFV_11,WFV_12,WFV_13,WFV_14,WFV_15,WFV_16,WFV_17,WFV_18,WFV_19,WFV_20,WFV_21,WFV_22,WFV_23,WFV_24,WFV_25,WFV_26,WFV_27,WFV_28]
#Window Frame Vertical Modbus locations
WFVnum = 21 #The number of vertical window frames to control
Vnums = []

DPs = [DP_1,DP_2,DP_3,DP_4,DP_5,DP_6,DP_7,DP_8]
#Dipole Modbus locations
DPnum = 8 #The number of Dipoles
Dpnums = []

Sols = [Sol_1,Sol_2,Sol_3,Sol_4,Sol_5,Sol_6,Sol_7,Sol_8,Sol_9,Sol_10,Sol_11,Sol_12,Sol_13]
#Solenoid Modbus locations
Solnum = 9 #Number of solenoids
Solnums = []

for i in range(100):
    if i < WFHnum:
        Hnums.append(20202 + 4*i)
    if i < WFVnum:
        Vnums.append(20200 + 4*i)
    if i < DPnum:
        Dpnums.append(22200 + 2*i)
    if i < Solnum:
        Solnums.append(21200 + 2*i)
        
#for all numbers with leading 0s python will reject so must make a string. There is an integer conversion later.
CU_Tags = ['01100','01102','01104','01114']
BH_Tags = [21224,21226,21228]
HV_Tags = [11100,11300,11302]
SRF_Tags = ['02100','02102','02104']
Pulse_Tags = ['00014','00012','00010','10100','11102']
#Grabbing the values from each magnet, redacted is the write permissions
########################################################################

#Building a list to go into a function
DBA_Mag_Names = [WFH_1,WFH_2,WFH_3,WFH_4,WFH_5,WFH_6,WFH_7,WFH_8,WFH_9,WFH_10,WFH_11,WFH_12,WFH_13,WFH_14,WFH_15,WFH_16,WFH_17,WFH_18,WFH_19,WFH_20,WFH_21,
                 WFV_1,WFV_2,WFV_3,WFV_4,WFV_5,WFV_6,WFV_7,WFV_8,WFV_9,WFV_10,WFV_11,WFV_12,WFV_13,WFV_14,WFV_15,WFV_16,WFV_17,WFV_18,WFV_19,WFV_20,WFV_21,
                 DP_1,DP_2,DP_3,DP_4,DP_5,DP_6,DP_7,DP_8,
                 Sol_1,Sol_2,Sol_3,Sol_4,Sol_5,Sol_6,Sol_7,Sol_8,Sol_9,
                 CU_Pf,CU_Pr,CU_Pt,CU_V,
                 BH_Pf,BH_Pr,BH_Pt,
                 HV_Bias, HV_Off_Setpoint,HV_On_Setpoint,
                 SRF_Pf,SRF_Pr,SRF_Pt,
                 Pulse_Freq,Pulse_Duty,Pulse_Delay,IR_Temp,Current_Emitted]

#Building the list of tags to grab
DBA_Mag_Tags = Hnums + Vnums + Dpnums + Solnums + CU_Tags + BH_Tags + HV_Tags + SRF_Tags + Pulse_Tags

client = ModbusTcpClient('10.6.0.2')
p = 0
N = 1
temp_list = []
for j in range(len(DBA_Mag_Names)):
    result = client.read_holding_registers(int(DBA_Mag_Tags[j]),2,unit=1)
    number = BinaryPayloadDecoder.fromRegisters(result.registers, byteorder=Endian.Big, wordorder=Endian.Big)
    temp_list.append(round(number.decode_32bit_float(),3))

    time.sleep(.020)
client.close()

WFH_1,WFH_2,WFH_3,WFH_4,WFH_5,WFH_6,WFH_7,WFH_8,WFH_9,WFH_10,WFH_11,WFH_12,WFH_13,WFH_14,WFH_15,WFH_16,WFH_17,WFH_18,WFH_19,WFH_20,WFH_21,WFV_1,WFV_2,WFV_3,WFV_4,WFV_5,WFV_6,WFV_7,WFV_8,WFV_9,WFV_10,WFV_11,WFV_12,WFV_13,WFV_14,WFV_15,WFV_16,WFV_17,WFV_18,WFV_19,WFV_20,WFV_21,DP_1,DP_2,DP_3,DP_4,DP_5,DP_6,DP_7,DP_8,Sol_1,Sol_2,Sol_3,Sol_4,Sol_5,Sol_6,Sol_7,Sol_8,Sol_9,CU_Pf,CU_Pr,CU_Pt,CU_V,BH_Pf,BH_Pr,BH_Pt,HV_Bias,HV_Off_Setpoint,HV_On_Setpoint,SRF_Pf,SRF_Pr,SRF_Pt,Pulse_Freq,Pulse_Duty,Pulse_Delay,IR_Temp,Current_Emitted = temp_list

#Putting the dataframe into an excel file.
##########################################

#into the spreadsheet format
dftoexcel = pd.DataFrame([[WFV_1,WFH_1,Sol_1,DP_1,'','Cu Gun (1)',CU_Pf,CU_Pr,CU_Pt,CU_V,'','','','','','','','','',''],
                       [WFV_2,WFH_2,Sol_2,DP_2,'','BH (2)',BH_Pf,BH_Pr,BH_Pt,BH_V,'','','','','','','','','',''],
                       [WFV_3,WFH_3,Sol_3,DP_3,'','Bias (0)','--','--','--',HV_Bias,'','','','','','','','','',''],
                       [WFV_4,WFH_4,Sol_4,DP_4,'','SRF',SRF_Pf,SRF_Pr,SRF_Pt,'','','','','','','','','','',''],
                       [WFV_5,WFH_5,Sol_5,DP_5,'','','','','','','','','','','','','','','',''],
                       [WFV_6,WFH_6,Sol_6,DP_6,'','','IR_Temp',IR_Temp,'K','','','','','','','','','','',''],
                       [WFV_7,WFH_7,Sol_7,DP_7,'','','Emitted Current',Current_Emitted,'uA','','','','','','','','','','',''],
                       [WFV_8,WFH_8,Sol_8,DP_8,'','','','','','','','','','','','','','','',''],
                       [WFV_9,WFH_9,Sol_9,'','','','HV Off SP',HV_Off_Setpoint,'kV','','','','','','','','','','',''],
                       [WFV_10,WFH_10,Sol_10,'','','','HV On SP',HV_On_Setpoint,'kV','','','','','','','','','',''],
                       [WFV_11,WFH_11,Sol_11,'','','','','','','','','','','','','','','','',''],
                       [WFV_12,WFH_12,Sol_12,'','','','','','','','','','','','','','','','',''],
                       [WFV_13,WFH_13,Sol_13,'','','','','','','','','','','','','','','','',''],
                       [WFV_14,WFH_14,'','','','','','','','','','','','','','','','','',''],
                       [WFV_15,WFH_15,'','','','','','','','','','','','','','','','','',''],
                       [WFV_16,WFH_16,'','','','','','','','','','','','','','','','','',''],
                       [WFV_17,WFH_17,'','','','','','','','','','','','','','','','','',''],
                       [WFV_18,WFH_18,'','','','','','','','','','','','','','','','','',''],
                       [WFV_19,WFH_19,'','','','','','','','','','','','','','','','','',''],
                       [WFV_20,WFH_20,'','','','','','','','','','','','','','','','','',''],
                       [WFV_21,WFH_21,'','','','','','','','','','','','','','','','','',''],
                       [WFV_22,WFH_22,'','','','','','','','','','','','','','','','','',''],
                       [WFV_23,WFH_23,'','','','','Pulsing Params','','','','','','','','','','','','',''],
                       [WFV_24,WFH_24,'','','','','Freq (Hz)','Duty (%)','Delay (ms)','','','','','','','','','','',''],
                       [WFV_25,WFH_25,'','','','',Pulse_Freq,Pulse_Duty,Pulse_Delay,'','','','','','','','','','',''],
                       [WFV_26,WFH_26,'','','','','','','','','','','','','','','','','',''],
                       [WFV_27,WFH_27,'','','','','','','','','','','','','','','','','',''],
                       [WFV_28,WFH_28,'','','','','','','','','','','','','','','','','','']],
                      index=['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28',],
                      columns=['WF V','WF H','Sol','DP','','','Pf (W)','Pr (W)','Pt (dBm)','V (kV)','','','','','','','','','',''])



#Saving the file to an excel file. This syntax used as the date and time of now plus the file extension name
############################################################################################################

#Date and time so we don't have to specify manually
now = datetime.today().strftime('%y%m%d_%H%M')

#to save all values
dftoexcel.to_excel(str(now)+'.xlsx')

## Niowave

Hello Traveler,

You have come far and I can see that you are tired. Let me offer you some assistance.

In this directory you will find the following items as of 06/29/2020 (that's in mm/dd/yyyy):	
	
A folder titled: Amp Scraper
	This project is intended to do a simple web scrape of a GUI output of a technologix
	amplifier. This program reads the values from the XML file that the amplifier outputs
	and pushes them to a PLC where ladder logic takes over and controls interlocks and 
	reports relevant values

A folder titled: DeGuass
	This is a simple script to degauss magnets in the system. This is to offset inconsistancies
	caused by magnet hysteresis. This program walks all the magnets connected to the PLC through 
	a decaying sin function until reaching zero. 
	
A folder titled: Dipole Scan
	Dipole Scans are a useful diagnostic for our accelerator injector. This program takes 
	advantage of our system design that uses our injector as an energy filter. This script
	sweeps the current of a magnet down and back up and records the collected beam at the 
	end of our injector setup. This has become a daily tool for operation.

A folder titled: Dog Leg
	Dog Legs are another diagnostic created to take advantage of the Geometry of our system. 
	This script sweeps two magnets concurrently in opposite directions to move our electron
	beam parallel through the superconducting cavity. This gives us an idea of how parallel
	and centered our beam is through the cavity axis.
	
A folder titled: East Tunnel
	An adaption of most of the daily scripts to run on our second system that has some minor design variations.
	
A folder titled: In_Testing
	This folder contains various scripts that are in the testing phase. This is primarily used
	for troubleshooting and the beginnings of version improvements.
	
A folder titled: Magnet Ramping
	This folder contains a project that stood in only for a few weeks. This was a temporary fix
	for a problem that operators faced with new updates to the GUI or Logic of the PLC's where 
	all of our magnets would be turned off and it would waste time to ramp them up. This was created 
	to load in a magnet save and ramp the magnets to the new values, it still took some time but saved
	many man-hours.
	
A folder titled: Magnet Saves
	This folder holds a dear place in my heart, and this is where this whole project began. This 
	started with an impromptu way to save magnet settings as a quick fix and the potential grew.
	
	
A python file named Master:
	This is a python file and acts as a library for other programs
	listed in the files below. In this file you will find the functions called in other
	programs. The purpose of these functions is to make the code modular and easier to adapt.
	
A python file named Master_All_Versions:
	Similar to Master, this contains functions from different versions of testing and minor
	side projects. This file is here to act as a quick reference for the continuation of
	long forgotten work.

A pytho file named Tag_Database:
	This simple script contains the modbus address for all commonly used tags in our system.
	The introduction of this script is to make the code more modular, future-proof, and readable.
	This document is update with changes in the PLCs and additions of new functionality (see Amp_Scraper.py).
	
A word document titled: future projects
	This document contains ramblings and ideas about future ideas with python as a modbus communicator.

#####################
#bokeh serve --show bokeh_tester.py
#####################

##########################################################
##########################################################
# Temperature trends
##########################################################
##########################################################
import numpy as np
from bokeh.plotting import figure
from bokeh.io import show, output_notebook, curdoc
from bokeh.models import LinearAxis, Range1d, BoxSelectTool
from bokeh.models.formatters import DatetimeTickFormatter, BasicTickFormatter
from bokeh.models import Legend
from bokeh.models.ranges import DataRange1d
from bokeh.plotting import figure, curdoc
from bokeh.driving import linear, count
import numpy.random as random

from bokeh.layouts import column
from bokeh.models import Slider
#from bokeh.io import show

from datetime import datetime
import time
import os
from bokeh.models.widgets import CheckboxGroup
from Tag_Database import *

Vacuums = [Gun_Vac, Gun_Cross, SRF_Cavity_Vac, HE_Sraight_Vac, # All of the vacuum tags that we currently have, in order
           Insulating_Vac, E_Station_Vac]

Temps = [BH_OC_Temp, DBA_Pipe_Temp, Cu_Gun_Temp, HE_Straight_Col, 
         DBA_Dump_CHWR, DBA_Dump_CHWS, Tuner_Plate_Temp, 
         Gate_Valve_Downstream_Temp, Gate_Valve_Upstream_Temp, 
         Loop_Bypass_CHWS, Loop_Bypass_CHWR, DBA_Coupler, 
         Coupler_Shoulder, Solenoid_4_Temp, Solenoid_5_Temp]

DST_Conversion = 3
if time.localtime().tm_isdst == 1:
    DST_Conversion = 4

Start_Time = time.time()*10**3-DST_Conversion*60*60*1000

Update_time = 25

temp_roll_scale = 10000

ROLL = int(1000*60*60*24/Update_time)
ROLL = 1000

span = 10*60 #Seconds

line_width = 4

y_max = None
y_min = None
range_scale = 0.2
curdoc().theme = 'dark_minimal'
#DataRange1d(only_visible = True)

p = figure(plot_width=1000, plot_height=400,
           x_axis_label = 'Time', y_axis_label = 'Random Number', x_axis_type = 'datetime', 
           tools="pan,xwheel_zoom,ywheel_zoom,xbox_zoom,reset",
           y_range=DataRange1d(only_visible = True, max_interval = y_max, min_interval = y_min),
           sizing_mode='stretch_both',
           lod_timeout = 100,
           lod_threshold = 10,
           lod_factor = 2000,
#           output_backend = 'webgl',
           x_range = DataRange1d(only_visible = True,
                                 follow = "end", follow_interval = span*1000,
                                 max_interval = 60*1000*60*24, min_interval = 1000, 
                                 range_padding_units = 'absolute',range_padding = 1000,))
          #other_property = here)
p.yaxis.visible = False
p.xaxis.formatter = DatetimeTickFormatter(milliseconds = '%H:%M:%S.%2N',seconds = "%H:%M:%S",minsec = "%H:%M:%S",minutes = "%H:%M:%S",hourmin = "%H:%M:%S",hours = "%H:%M:%S",days = ['%m/%d', '%a%d'],months = ['%m/%Y', '%b %Y'],years = ['%Y'])
    
    
#slider = Slider(title = 'Follow Range', start= 2*1000 , end= 60*1000, step=1000, value=span*1000)
#slider.js_link('value', p.x_range, 'follow_interval')
#slider.on_change('value', p.x_range, 'follow_interval')
#Column = column(slider, width = 100, height = 100)
#p.add_layout(Column, 'below')

#r1 = p.line([], [], color="yellow", line_width=line_width, y_range_name = "pressures")
#r2 = p.line([], [], color="skyblue", line_width=line_width, y_range_name = "temps")
#r3 = p.line([], [], color="green", line_width=line_width, y_range_name = "temps")

import numpy as np
with open("Data.txt",'r') as file:
    lines = file.readlines()
for num,line in enumerate(lines[1:]):
    lines[num+1] = line.strip("\nr").split(",")
data = np.array(lines[1:]).astype(float)
data[:,0]

r1 = p.line([], [], color="yellow", line_width=line_width, y_range_name = "pressures")
r2 = p.line([], [], color="skyblue", line_width=line_width, y_range_name = "temps")
r3 = p.line([], [], color="green", line_width=line_width, y_range_name = "temps")

#print('\n'*5, r1.data_source.properties_with_values()['data']['x'], '\n'*5)

## For each new range add it here
p.extra_y_ranges = {"temps": DataRange1d(only_visible = True, renderers = [r2,r3],
                                         range_padding_units = 'percent',range_padding = range_scale), 
                   "pressures": DataRange1d(only_visible = True,  renderers = [r1],
                                            range_padding_units = 'percent',range_padding = range_scale)}

p.add_layout(LinearAxis(y_range_name="temps", axis_label = "Temps"), 'left')
p.add_layout(LinearAxis(y_range_name="pressures", axis_label = "Pressures"), 'left')

p.yaxis.formatter = BasicTickFormatter(precision = 1)

p.grid.grid_line_color = 'gray'
p.grid.minor_grid_line_alpha = 0.4
p.grid.grid_line_alpha = 0.4

#################################
#Add data here
#################################

#r1 = p.line([Start_Time], [0], color="yellow", line_width=2, y_range_name = "pressures")
#r2 = p.line([Start_Time], [0], color="skyblue", line_width=2, y_range_name = "temps")


legend = Legend(items=[("One" , [r1]),
                       ("Two" ,  [r2]), 
                       ("Three", [r3]), 
#                       ("Temps", [r2,r3]) 
                      ],
                location="center", click_policy = "hide")

p.add_layout(legend, 'right')
#p.legend.click_policy= "hide"

ds1 = r1.data_source
ds2 = r2.data_source
ds3 = r3.data_source

run = True

@count()
def update(step):
    
    global last_time
    run = True
    
    with open('Data.txt', 'rb') as file: #delete to f?
        file.seek(-2, os.SEEK_END)
        while file.read(1) != b'\n':
            file.seek(-2, os.SEEK_CUR) 
        last_line = file.readline().decode().split(",")
    temp_list = []
    for item in last_line:
        try:
            temp_list.append(float(item))
        except:
            temp_list.append(float(item.strip("\rn")))
            
    #currenttime = time.time()*10**3-DST_Conversion*60*60*1000
    try:
        #print("temp list",temp_list[0])
        #print("last time",last_time)
        temp_list[0] = time.time()*10**3-DST_Conversion*60*60*1000
        if temp_list[0] == last_time:
            run = False
    except:
        run = True
        
    
    if run:
        ds1.data['x'].append(temp_list[0])
        ds1.data['y'].append(random.normal(65,10)*1e-6)
        #ds1.data['y'].append(temp_list[1])

        ds2.data['x'].append(temp_list[0])
        ds2.data['y'].append(random.normal(47,5))
        #ds2.data['y'].append(temp_list[2])

        ds3.data['x'].append(temp_list[0])
        ds3.data['y'].append(random.normal(74,1))  
        #ds3.data['y'].append(temp_list[3])

        #ds1.trigger('data', ds1.data, ds1.data)
        ds1.stream({"x": ds1.data['x'], "y": ds1.data['y']}, rollover=ROLL) ##### THIS LINE IS ONLY IF TXT FILE IS NOT USED
        #ds2.trigger('data', ds2.data, ds2.data)
        ds2.stream({"x": ds2.data['x'], "y": ds2.data['y']}, rollover=ROLL) ##### THIS LINE IS ONLY IF TXT FILE IS NOT USED
        #ds3.trigger('data', ds3.data, ds3.data)
        ds3.stream({"x": ds3.data['x'], "y": ds3.data['y']}, rollover=ROLL) ##### THIS LINE IS ONLY IF TXT FILE IS NOT USED

        last_time = temp_list[0]

    
curdoc().add_root(p)

# Add a periodic callback to be run every 500 milliseconds
curdoc().add_periodic_callback(update, Update_time)

import time
import numpy as np
from Tag_Database import *
import Master as M

# Parameters
txt_file_length = 1800

#############################################
# Don't touch it
#############################################

Vacuums = [Gun_Vac, Gun_Cross, SRF_Cavity_Vac, HE_Sraight_Vac, 
           Insulating_Vac, E_Station_Vac]

Temps = [BH_OC_Temp, DBA_Pipe_Temp, Cu_Gun_Temp, HE_Straight_Col, 
         DBA_Dump_CHWR, DBA_Dump_CHWS, Tuner_Plate_Temp, 
         Gate_Valve_Downstream_Temp, Gate_Valve_Upstream_Temp, 
         Loop_Bypass_CHWS, Loop_Bypass_CHWR, DBA_Coupler, 
         Coupler_Shoulder, Solenoid_4_Temp, Solenoid_5_Temp]

DST_Conversion = 3
if time.localtime().tm_isdst == 1:
    DST_Conversion = 4
    
Client = M.Make_Client("10.50.0.10")

while True:
    start_time = time.time()

    temp_list = [time.time()*10**3-DST_Conversion*60*60*1000]
    
    for Tag in Vacuums:
        temp_list.append(M.Read(Client,Tag))
        
    file = open("Data.txt",'a')
    file.write(str(temp_list).strip("[]")+"\n")
    file.close()
    with open("Data.txt", "r+") as file:
        contents = file.readlines()
        if np.shape(contents)[0] > txt_file_length:
            file.seek(0)
            for num,j in enumerate(contents):
                if num != 1:
                    file.write(j)
            file.truncate()
    file.close()
    elapsed_time = time.time() - start_time
    print(elapsed_time)
    time.sleep(abs(1 - elapsed_time))
    
#####################
#bokeh serve --show Temp_Tester.py
#####################

##########################################################
##########################################################
# Temperature trends
##########################################################
##########################################################

import numpy as np
from bokeh.plotting import figure
from bokeh.io import show, output_notebook, curdoc
from bokeh.models import LinearAxis, Range1d, BoxSelectTool
from bokeh.models.formatters import DatetimeTickFormatter, BasicTickFormatter
from bokeh.models import Legend
from bokeh.models.ranges import DataRange1d
from bokeh.plotting import figure, curdoc
from bokeh.driving import linear
from bokeh.palettes import Category20, Turbo256
import numpy.random as random

from bokeh.layouts import column
from bokeh.models import Slider
#from bokeh.io import show

from datetime import datetime
import time
import os
from bokeh.models.widgets import CheckboxGroup
from Tag_Database import *

Vacuums = [Gun_Vac, Gun_Cross, SRF_Cavity_Vac, HE_Sraight_Vac, # All of the vacuum tags that we currently have, in order
           Insulating_Vac, E_Station_Vac]

DST_Conversion = 3
if time.localtime().tm_isdst == 1:
    DST_Conversion = 4

Start_Time = time.time()*10**3-DST_Conversion*60*60*1000

Update_time = 250

temp_roll_scale = 10000

ROLL = int(1000*60*60*24/Update_time)

span = 10       *60 #Minutes

line_width = 4

y_max = None
y_min = None
range_scale = 0.2
curdoc().theme = 'dark_minimal'

p = figure(plot_width=1000, plot_height=400,
           x_axis_label = 'Time', y_axis_label = 'Numbers', x_axis_type = 'datetime', 
           tools="pan,xwheel_zoom,ywheel_zoom,xbox_zoom,reset",
           y_range=DataRange1d(only_visible = True, max_interval = y_max, min_interval = y_min),
           sizing_mode='stretch_both',
#           output_backend="webgl",
           x_range = DataRange1d(only_visible = True,
                                 follow = "end", follow_interval = span*1000,
                                 max_interval = 60*1000*60*24, min_interval = 1000, 
                                 range_padding_units = 'absolute',range_padding = 1000,))
          #other_property = here)
p.yaxis.visible = False
p.xaxis.formatter = DatetimeTickFormatter(milliseconds = '%H:%M:%S.%2N',seconds = "%H:%M:%S",minsec = "%H:%M:%S",minutes = "%H:%M:%S",hourmin = "%H:%M:%S",hours = "%H:%M:%S",days = ['%m/%d', '%a%d'],months = ['%m/%Y', '%b %Y'],years = ['%Y'])
    

with open("Data.txt",'r') as file:
    lines = file.readlines()
for num,line in enumerate(lines[1:]):
    lines[num+1] = line.strip("\nr").split(",")
data = np.array(lines[1:]).astype(float)

r1 = p.line(list(data[:,0]), list(data[:,1]), color = 'white', line_width=line_width, y_range_name = "temps")
r2 = p.line(list(data[:,0]), list(data[:,2]), color = Turbo256[43], line_width=line_width, y_range_name = "temps")
r3 = p.line(list(data[:,0]), list(data[:,3]), color = Turbo256[86], line_width=line_width, y_range_name = "temps")
r4 = p.line(list(data[:,0]), list(data[:,4]), color = Turbo256[129], line_width=line_width, y_range_name = "temps")
r5 = p.line(list(data[:,0]), list(data[:,5]), color = Turbo256[172], line_width=line_width, y_range_name = "temps")
r6 = p.line(list(data[:,0]), list(data[:,6]), color = Turbo256[210], line_width=line_width, y_range_name = "temps")

#print('\n'*5, r1.data_source.properties_with_values()['data']['x'], '\n'*5)
data = False
## For each new range add it here
p.extra_y_ranges = {"temps": DataRange1d(only_visible = True, 
                                         renderers = [r1,r2,r3,r4,r5,r6],
                                         range_padding_units = 'percent',range_padding = range_scale)}

p.add_layout(LinearAxis(y_range_name="temps", axis_label = "Pressures"), 'left')

#p.yaxis.formatter = BasicTickFormatter(precision = 2)

p.grid.grid_line_color = 'gray'
p.grid.minor_grid_line_alpha = 0.4
p.grid.grid_line_alpha = 0.4

#################################
#Add data here
#################################

legend = Legend(items=[("Gun Vac" , [r1]),
                       ("Gun Cross Vac" ,  [r2]), 
                       ("SRF Cavity Vac", [r3]),
                       ("HE Straight Vac", [r4]),
                       ("Insulatin Vac", [r5]),
                       ("E-Station Vac", [r6]),
                      ],
                location="center", click_policy = "hide")

p.add_layout(legend, 'right')
#p.legend.click_policy= "hide"

ds1 = r1.data_source
ds2 = r2.data_source
ds3 = r3.data_source
ds4 = r4.data_source
ds5 = r5.data_source
ds6 = r6.data_source

run = True

@linear()
def update(step):
    
    global last_time
    run = True
    
    with open('Data.txt', 'rb') as file: #delete to f?
        file.seek(-2, os.SEEK_END)
        while file.read(1) != b'\n':
            file.seek(-2, os.SEEK_CUR) 
        last_line = file.readline().decode().split(",")
    temp_list = []
    for item in last_line:
        try:
            temp_list.append(float(item))
        except:
            temp_list.append(float(item.strip("\rn")))
            
    #currenttime = time.time()*10**3-DST_Conversion*60*60*1000
    try:
        print("temp list",temp_list[0])
        print("last time",last_time)
        print(len(temp_list))
        if temp_list[0] == last_time:
            run = False
    except:
        run = True
    
    if run:
        ds1.data['x'].append(temp_list[0])
        ds1.data['y'].append(temp_list[1])

        ds2.data['x'].append(temp_list[0])
        ds2.data['y'].append(temp_list[2])

        ds3.data['x'].append(temp_list[0])
        ds3.data['y'].append(temp_list[3])
        
        ds4.data['x'].append(temp_list[0])
        ds4.data['y'].append(temp_list[4])

        ds5.data['x'].append(temp_list[0])
        ds5.data['y'].append(temp_list[5])

        ds6.data['x'].append(temp_list[0])
        ds6.data['y'].append(temp_list[6])
        
        ds1.trigger('data', ds1.data, ds1.data)
        ds2.trigger('data', ds2.data, ds2.data)
        ds3.trigger('data', ds3.data, ds3.data)
        ds4.trigger('data', ds4.data, ds4.data)
        ds5.trigger('data', ds5.data, ds5.data)
        ds6.trigger('data', ds6.data, ds6.data)

        last_time = temp_list[0]

    
curdoc().add_root(p)

# Add a periodic callback to be run every 500 milliseconds
curdoc().add_periodic_callback(update, Update_time)

# This is not complete, and barely works. It was quickly killed here lie the remains.

import Master as M
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d, Axes3D
from datetime import datetime

class puck:
    
    WFH_Location = 0
    WFV_Location = 0
    
    Averaging_Number = 10
    
    Step_Size = .5
    max_grid = 7000
    
    Data = np.array([["X","Y","Z"]])
    
    def take_data(self):
        
        temp_list = []
        for i in range(self.Averaging_Number):
            temp_list.append(np.random.random())
                
        self.Data = np.append(self.Data,[[round(self.WFH_Location,3), round(self.WFV_Location,3), round(sum(temp_list)/self.Averaging_Number,3)]], axis = 0)
        
        return
    
    def walk_horizontal(self, distance, step_size = None):
        if step_size is None:
            step_size = self.Step_Size
            
        if step_size > abs(distance):
            while step_size >= abs(distance):
                step_size = step_size / 3
            print("Step size too large; cut to {0:.3f}".format(step_size))
        
        start_location = self.WFH_Location
        end_location = self.WFH_Location + distance
        
        for i in range(self.max_grid):
            
            if abs(end_location - self.WFH_Location) <= step_size:
                
                self.WFH_Location = end_location
                self.take_data()
                break
                
            else:
                if distance < 0:
                    self.WFH_Location -= step_size
                    self.take_data()
                else:
                    self.WFH_Location += step_size
                    self.take_data()
        return
    
    def walk_vertical(self, distance, step_size = None):
        if step_size is None:
            step_size = self.Step_Size
            
        if step_size > abs(distance):
            while step_size > abs(distance):
                step_size = step_size / 3
            print("Step size too large; cut to {0:.3f}".format(step_size))
        
        start_location = self.WFV_Location
        end_location = self.WFV_Location + distance
        
        for i in range(self.max_grid):
            
            if abs(end_location - self.WFV_Location) <= step_size:
                
                self.WFV_Location = end_location
                self.take_data()
                break
                
            else:
                if distance < 0:
                    self.WFV_Location -= step_size
                    self.take_data()
                else:
                    self.WFV_Location += step_size
                    self.take_data()
        return
            
            
            
    def walk_to(self, Horizontal, Vertical,step_size = None, chunks = 10):
        
        if step_size is None:
            step_size = self.Step_Size
        
        for i in range(chunks):
            self.walk_horizontal(Horizontal/chunks);
            self.walk_vertical(Vertical/chunks);
                
            
    def Plot(self, save = False):
        
        x = self.Data[1:,0]
        x = x.astype(np.float)

        y = self.Data[1:,1]
        y = y.astype(np.float)

        z = self.Data[1:,2]
        z = z.astype(np.float)
        
        fig = plt.figure(figsize = (12,8))
        
        ax = Axes3D(fig)
        ax.scatter(x, y, z, c=z, cmap='viridis', linewidth=0.5)

        ax.set_xlabel("Window Frame Horizontal Amperage")
        ax.set_ylabel("Window Frame Vertical Amperage")
        ax.set_zlabel("Collected Current")
        ax.set_title("Gathered Data")
        
        if save != False:
            if save == True:
                now = datetime.today().strftime('%y%m%d_%H%M')
                plt.savefig(now + '_graph' + '.svg')
            else:
                plt.savefig(save + '.svg')
    
    def save_data(self):
        now = datetime.today().strftime('%y%m%d_%H%M') #Taking the current time in YYMMDD_HHmm format to save the plot and the txt file

        with open(now +'.txt', 'w') as f: #Open a new file by writing to it named the date as created above + .txt
    
            for i in Total_Data:
                f.write(str(i) + '\n')
        
            f.close()
        

            
    
puck = puck()
print(puck.WFH_Location)
puck.walk_to(0.1, 3)
puck.Plot()


import Master as M
import numpy as np
import Matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d, Axes3D
from datetime import datetime

WFH_Tag = 20203
WFV_Tag = 20201
Read_Tag = 11109

Horizontal_Delta = .4
Vertical_Delta = .4

Grid_Resolution = 10
Resolution = 40

IP = '192.168.1.2'

Client = M.Make_Client(IP)

WFH_Start = M.Read(Client, WFH_Tag)
WFV_Start = M.Read(Client, WFV_Tag)

######
#Walking us down to the start of our diagonal
######

for i in range(1, Grid_Resolution + 1):
    WFH_Write_Value = WFH_Start - i * (Horizontal_Delta/Grid_Resolution)
    WFV_Write_Value = WFV_Start - i * (Vertical_Delta/Grid_Resolution)
    
    M.Write(Client, WFH_Tag, WFH_Write_Value)
    M.Write(Client, WFV_Tag, WFV_Write_Value)
    
WFH_Mid = M.Read(Client, WFH_Tag)
WFV_Mid = M.Read(Client, WFV_Tag)
    
#Header = np.array([["WFH_Value","WFV_Value","Collection"]])


######
#Walking diagonally and doing the rapid t scans
######
Total_Data = M.Rapid_T_Scan(Client, WFH_Tag, WFV_Tag, Read_Tag, Horizontal_Delta, Vertical_Delta, Resolution)
for i in range(1, 2*Grid_Resolution + 1):
    Data = M.Rapid_T_Scan(Client, WFH_Tag, WFV_Tag, Read_Tag, Horizontal_Delta, Vertical_Delta, Resolution)
    
    WFH_Write_Value = WFH_Mid + i * (Horizontal_Delta/Grid_Resolution)
    WFV_Write_Value = WFV_Mid + i * (Vertical_Delta/Grid_Resolution)
    
    M.Write(Client, WFH_Tag, WFH_Write_Value)
    M.Write(Client, WFV_Tag, WFV_Write_Value)
    
    #if i == 1:
        #Total_Data = np.append(Header, Data, axis = 0)
    
    #else:
    Total_Data = np.append(Total_Data, Data, axis = 0)
    
######
#Walking us back to the center again
######
WFH_End = M.Read(Client, WFH_Tag)
WFV_End = M.Read(Client, WFV_Tag)

for i in range(1, Grid_Resolution + 1):
    WFH_Write_Value = WFH_End - i * (Horizontal_Delta/Grid_Resolution)
    WFV_Write_Value = WFV_End - i * (Vertical_Delta/Grid_Resolution)
    
    M.Write(Client, WFH_Tag, WFH_Write_Value)
    M.Write(Client, WFV_Tag, WFV_Write_Value)
    
now = datetime.today().strftime('%y%m%d_%H%M') #Taking the current time in YYMMDD_HHmm format to save the plot and the txt file

with open(now +'.txt', 'w') as f: #Open a new file by writing to it named the date as created above + .txt
    
    for i in Total_Data:
        f.write(i + '\n')
        
    f.close()

    
######
#Plotting
######
x = Total_Data[1:,0]
x = x.astype(np.float)

y = Total_Data[1:,1]
y = y.astype(np.float)

z = Total_Data[1:,2]
z = z.astype(np.float)

fig = plt.figure(figsize = (12,8))
ax = Axes3D(fig)
ax.scatter(x, y, z, c=z, cmap='viridis', linewidth=0.5)

ax.set_xlabel("Window Frame Horizontal Amperage")
ax.set_ylabel("Window Frame Vertical Amperage")
ax.set_zlabel("Collected Current")
ax.set_title("Rapid Dog Leg Results")


plt.show()

To whom it may concern,

I have created this repository to hold my current projects that are being completed at Niowave Inc. 

There are currently four folders in this repository: GPIB Programming, Java-SCADA, Python-PLC, and Scripts. The descriptions to follow.

GPIB Programming: This folder contains the projects that involve SCPI communications through python and the National instruments VISA 
  driver. Currently there is a project that regulates the error signal output a signal generator has into an oscilloscope. Further
  testing and projects are also contained here.
  
Java-SCADA: Being a novice, this folder will contain beginner's projects that are being done here. This will hopefully contain the 
  beginnings of using Java to homebrew a SCADA
 
Python-PLC: This is the most developed of the repositories thus far. This contains many executables to help automate more time consuming
  tasks done here. This contains magnet controls of our systems and data taking scripts. Some of these projects have been phased out as
  they often start off as proof-of-concept and are designed to be simple enough to run entirely through a PLC if need be.
  
Scripts: These are primarily python scripts that I have discontinued work on for one reason or another.

Enjoy.

Warm regards,

Austin Czyzewski
