import pyvisa
import time

RM = pyvisa.ResourceManager()
print(RM.list_resources())
Devices = RM.list_resources()

try:
    SG = RM.open_resource(Devices[1])
except ExplicitException:
    print("No devices found")
try:
    OS = RM.open_resource(Devices[0])
except:
    print("Only one device found")
    
try:
    print(SG.query("freq:cw?"))
except:
    print("Devices flopped; either change order of listed resources or manually change addresses.")
    