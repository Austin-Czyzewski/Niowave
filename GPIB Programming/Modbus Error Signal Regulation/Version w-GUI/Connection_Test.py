import GPIB_FUNCS as GPIB #Importing our GPIB communication functions for easier comprehension and use
import pyvisa #import GPIB communication module
import time #imports time to sleep program temporarily
from tkinter import * #importing GUI library
import tkinter

RM = pyvisa.ResourceManager() #pyVISA device manager
print(RM.list_resources()) #Printing out all detected device IDs
resources = RM.list_resources()
##SG = RM.open_resource('GPIB0::10::INSTR') #Opening the Signal generator as an object
#OS = RM.open_resource('GPIB0::16::INSTR') #Opening the oscilloscope as an object
#OS.control_ren(6)
#a = OS.query('*IDN?')
#print(a)
#OS.control_ren(6)
#OS.write("*RST")
for resource in resources:
    device = RM.open_resource(resource)
    print(resource)
    print(device.query("*IDN?"))
    device.control_ren(6)
print("All Done")
