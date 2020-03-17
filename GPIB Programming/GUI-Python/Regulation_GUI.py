import GPIB_FUNCS as GPIB
import pyvisa
import time
from tkinter import *

RM = pyvisa.ResourceManager()
print(RM.list_resources())
SG = RM.open_resource('GPIB0::10::INSTR')
OS = RM.open_resource('GPIB0::16::INSTR')

running = False # Global flag
reset = False # Global flag
pulsing = False # Global flag

IF_Channel = 2
Trigger_Channel = 4
Trigger_Level = 20   /1000 #mv

Measurement = 3
Step_size = 40 #(Hz)
Pulse_Step_Size = 10 #(Hz)
Max_Threshold = 10000 #(Hz)
Walk_Threshold = 2.5 #(mV)
Pulse_Walk_Threshold = 0.5 #(mV)
Wait_after_step = 0.0400 #Seconds
Wait_between_reads = 0.0100 #Seconds
Long = False

GPIB.measurement_setup(OS,IF_Channel, measurement = Measurement)
GPIB.channel_settings_check(OS, IF_Channel)
GPIB.trigger_settings_set(OS, Trigger_Channel, Trigger_Level)
GPIB.vertical_marker_pulsing(OS, IF_Channel)

interlock_color = 'Yellow'

global Ups
global Downs
global i
Ups = 0
Downs = 0
i = 0
Start_Freq = GPIB.freq(SG)

try:
    short_test = float(OS.query("MEASU:MEAS1:VAL?"))
    pass
except:
    long_test = float(OS.query("MEASU:MEAS{}:VAL?".format(1)).split(' ')[1].strip("\n"))
    Long = True
    pass


print("\n\n\n")
print("-" * 60)
print("Beginning modulation")
print("-" * 60)
print("\n\n\n")

def scanning():
    
    global reset
    global pulsing
    global running
    global Ups
    global Downs
    global i
    if reset:
        print("-"*60, "\n\n\nResetting Oscilloscope\n\n\n", "-"*60)
        
        GPIB.measurement_setup(OS,IF_Channel, measurement = Measurement)
        GPIB.channel_settings_check(OS, IF_Channel)
        GPIB.trigger_settings_set(OS, Trigger_Channel, Trigger_Level)
        GPIB.vertical_marker_pulsing(OS, IF_Channel)
       
        reset = False
    if running:  # Only do this if the Stop button has not been clicked
        root.configure(bg = 'SpringGreen2')
        
        if pulsing:
            
            read_value = GPIB.cursor_vbar_read_mv(OS)
        
            if read_value > Pulse_Walk_Threshold:
                Ups += 1
                Downs = 0
                if Ups > 3:
                    temp_freq = GPIB.freq(SG)
                    if (temp_freq + Pulse_Step_Size) > (Start_Freq + Max_Threshold):
                        print("Broken on too many steps upward")
                        root.configure(bg = interlock_color)
                        running = False
                    if OS.query("MEASU:Meas{}:State?".format(Measurement))[-2] != str(1):
                        print("Measurement Off")
                        root.configure(bg = interlock_color)
                        running = False
                    GPIB.write_frequency(SG, (temp_freq + Pulse_Step_Size),"HZ")
                    print("Raised Frequency ", i)
                    time.sleep(Wait_after_step)

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
            
        else:
            read_value = GPIB.read_mv(OS, long = Long, measurement = Measurement)
        
            if read_value > Walk_Threshold:
                Ups += 1
                Downs = 0
                if Ups > 3:
                    temp_freq = GPIB.freq(SG)
                    if (temp_freq + Step_size) > (Start_Freq + Max_Threshold):
                        print("Broken on too many steps upward")
                        #global running
                        running = False
                    if OS.query("MEASU:Meas{}:State?".format(Measurement))[-2] != str(1):
                        print("Measurement Off")
                        root.configure(bg = interlock_color)
                        running = False
                    GPIB.write_frequency(SG, (temp_freq + Step_size),"HZ")
                    print("Raised Frequency ", i)
                    time.sleep(Wait_after_step)

            if read_value < -Walk_Threshold:
                Downs += 1
                Ups = 0
                if Downs > 3:
                    temp_freq = GPIB.freq(SG)
                    if (temp_freq - Step_size) < (Start_Freq - Max_Threshold):
                        print("Broken on too many steps downward")
                        #global running
                        running = False
                    if OS.query("MEASU:Meas{}:State?".format(Measurement))[-2] != str(1):
                        print("Measurement Off")
                        root.configure(bg = interlock_color)
                        running = False
                    GPIB.write_frequency(SG, (temp_freq - Step_size),"HZ")
                    print("Lowered Frequency ", i)
                    time.sleep(Wait_after_step)

            #time.sleep(Wait_between_reads)
            i += 1

    # After .1 seconds, call scanning again (create a recursive loop)
    root.after(100, scanning)


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
    root.configure(bg = 'sky blue')
    global reset
    reset = True
    
def pulsing_toggle():
    global pulsing
    if pulsing:
        pulsing = False
    else:
        pulsing = True
    


root = Tk()
root.title("Regulation Window")
root.geometry("1000x1000")
#root.attributes('-fullscreen', True)

app = Frame(root)
app.grid()
size = 10
start = Button(app, text="Start Regulation", command=start, activebackground="SpringGreen2", height = size, width = size*5, bg = 'Pale Green', font=('Helvetica', '20'), bd = size)
stop = Button(app, text="Stop Regulation", command=stop, activebackground="firebrick1", height = size, width = size*5, bg = 'tomato', font=('Helvetica', '20'), bd = size)
reset_button = Button(app, text="Reset Oscilloscope", command=reset_measurement, activebackground="light sky blue", height = int(size/3), width = size*5, bg = 'sky blue', font=('Helvetica', '20'), bd = size)
Pulsing_button = Checkbutton(app, text="Pulsing", command=pulsing_toggle, activebackground="white", height = int(size/3), width = size*5, bg = 'gray', font=('Helvetica', '20'), bd = size,indicatoron=False,selectcolor='orange')
start.grid()
stop.grid()
reset_button.grid()
Pulsing_button.grid()

root.after(1000, scanning)  # After 1 second, call scanning
root.mainloop()
