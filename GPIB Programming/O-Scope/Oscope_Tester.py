"""
Author: Austin Czyzewski
Date: 03/05/2020

Purpose: Save many...many man-hours and brain melting days and free up operators for more technical tasks
"""

import pyvisa
import time

RM = pyvisa.ResourceManager()
print(RM.list_resources())
#SG = RM.open_resource('GPIB0::1::INSTR')
#OS = RM.open_resource('GPIB0::10::INSTR')