"""
Author: Austin Czyzewski
Date: 03/05/2020

Purpose: Save many...many man-hours and brain melting days and free up operators for more technical tasks
"""

import pyvisa
import time

RM = pyvisa.ResourceManager()
print(RM.list_resources())
SG = RM.open_resource('GPIB0::11::INSTR')
OS = RM.open_resource('GPIB0::7::INSTR')

Measurement = 1
Channel = 3
Step_size = 20 #(Hz)
Max_Threshold = 10000 #(Hz)
Max_one_way_walk = 5000 #(Hz)
Walk_Threshold = 2.5 #(mV)
Wait_after_step = 0.0500 #Seconds
Wait_between_reads = 0.0100 #Seconds

def freq(Device):
    
    frequency = Device.query("freq:cw?")
    Device.write("*wai")
    
    return float(frequency)

def write_frequency(Device, Value, Units = "MHZ"):
    
    Device.write("freq:cw {} {}".format(Value,Units))
    Device.write("*wai")
    
    return

def read_mv(OSCOPE, MEASUREMENT):
    value = 1000*float(OS.query("MEASU:MEAS{}:VAL?".format(MEASUREMENT)).split(' ')[1].strip("\n"))
    OSCOPE.write("*wai")
    return value

def read_v(OSCOPE, MEASUREMENT):
    value = float(OS.query("MEASU:MEAS{}:VAL?".format(MEASUREMENT)).split(' ')[1].strip("\n"))
    OSCOPE.write("*wai")
    return value

def mean_meas(OSCOPE, CHANNEL, MEASUREMENT, SCALE = False):
    
    if type(CHANNEL) and type(MEASUREMENT) != int:
        print("Must be integers!")
    
    if not SCALE == False:
        OS.write("CH3:SCA {:.1E}".format())
        
    OS.write("MEASU:MEAS{}:SOURCE1 CH{}".format(MEASUREMENT, CHANNEL))
    OS.write("MEASU:MEAS{}:UNI v".format(MEASUREMENT))
    OS.write("MEASU:MEAS{}:STATE ON".format(MEASUREMENT))
    time.sleep(1)
    return OS.query("MEASU:meas{}:val?".format(MEASUREMENT))

mean_meas(OS, Channel, Measurement)

print("Beginning reading (mV): ", read_mv(OS,Measurement))

Start_Freq = float(SG.query("freq:cw?"))

print("\n\n\n")
print("-" * 60)
print("Beginning modulation")
print("-" * 60)
print("\n\n\n")

Ups = 0
Downs = 0
while True:
    
    read_value = read_mv(OS, Measurement)
    
    if read_value > Walk_Threshold:
        Ups += 1
        Downs = 0
        if Ups > 3:
            temp_freq = freq(SG)
            if (temp_freq + Step_size) > (Start_Freq + Max_Threshold):
                break
            write_frequency(SG, (temp_freq + Step_size),"HZ")
            print("Raised Frequency")
            time.sleep(Wait_after_step)
            
    if read_value < -Walk_Threshold:
        Downs += 1
        Ups = 0
        if Downs > 3:
            temp_freq = freq(SG)
            if (temp_freq - Step_size) < (Start_Freq - Max_Threshold):
                break
            write_frequency(SG, (temp_freq - Step_size),"HZ")
            print("Lowered Frequency")
            time.sleep(Wait_after_step)

    if Ups > Max_one_way_walk/Step_size:
        print("\n\n\nWalked up frequency for too long")
        break
    if Downs > Max_one_way_walk/Step_size:
        print("\n\n\nWalked down frequency for too long")
        break
    time.sleep(Wait_between_reads)

print("\n\n\n")
print("-" * 60)
print("Modulation Over\n")
print("\n\n\n")
print("Walked too many Hz")
print("-" * 60)
print("\n\n\n")

exit()