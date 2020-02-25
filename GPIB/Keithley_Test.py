import pyvisa as pv
import numpy as np
import matplotlib.pyplot as plt
import seaborn
seaborn.set()

RM = pyvisa.ResourceManager()
keithley = rm.open_resource("GPIB::0")
keithley.write("*rst; status:preset; *cls")

interval_in_ms = 500
number_of_readings = 10

for i in range(10):
    
    keithley.write("status:measurement:enable 512; *sre 1")
    keithley.write("sample:count %d" % number_of_readings)
    keithley.write("trigger:source bus")
    keithley.write("trigger:delay %f" % (interval_in_ms / 1000.0))
    keithley.write("trace:points %d" % number_of_readings)
    keithley.write("trace:feed sense1; trace:feed:control next")

    keithley.write("initiate")
    keithley.assert_trigger()
    keithley.wait_for_srq()

    voltages = keithley.query_ascii_values("trace:data?")
    print("Average voltage: ", sum(voltages) / len(voltages))

    keithley.query("status:measurement?")
    keithley.write("trace:clear; trace:feed:control next")