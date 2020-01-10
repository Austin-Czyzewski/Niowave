from pymodbus.client.sync import ModbusTcpClient
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.payload import BinaryPayloadBuilder
from pymodbus.constants import Endian
import matplotlib.pyplot as plt
from datetime import datetime
import time
import numpy as np
import Master as M

Client = M.Make_Client('10.50.0.10')


End_Value = float(input("What is the ending amperage that you want to ramp the magnet to? (Amps)   "))

#Uncomment to make variable number of runs
#Runs = int(input("How many runs do you want the Dipole to make?   "))

Runs = 1
Dipole_Tag = 22201
Step_size = .001
Read = "11109"
count = 20

Start_Value = M.Read(Client, Dipole_Tag)
print("Started at {0:.3f} Amps".format(Start_Value))

DP1_Values = []
DBA_Collection = []
colors = []
for i in range(Runs):
    
    DP1_Vals, DBA_Col = M.Ramp_One_Way(Client, Dipole_Tag, End_Value, Max_Step = Step_size, Return = "Y", Read_Tag = Read, count = count)

    DP1_Values += DP1_Vals
    DBA_Collection += DBA_Col

    temp_list = ['b' for i in list(range(len(DP1_Vals)))]

    colors += temp_list

    DP1_Vals, DBA_Col = M.Ramp_One_Way(Client, Dipole_Tag, Start_Value, Max_Step = Step_size, Return = "Y", Read_Tag = Read, count = count)

    DP1_Values += DP1_Vals
    DBA_Collection += DBA_Col

    temp_list = ['r' for i in list(range(len(DP1_Vals)))]

    colors += temp_list
    
    

now = datetime.today().strftime('%y%m%d_%H%M')
plt.figure(figsize = (12,8))
plt.scatter(DP1_Values,DBA_Collection,color = colors)

#Naming
plt.ylabel("DBA current collected")
plt.xlabel("Magnet Amperage")
plt.title("Dipole 1 current collected over walk from {0:.3f} to {1:.3f}".format(Start_Value, End_Value))
plt.suptitle("Blue = Ascending, Red = Descending",fontsize = 8)

plt.grid(True)
plt.savefig(now + '_graph.png',trasnparent = True)

Clean_DP1 = [round(i,3) for i in DP1_Values]
Clean_DBA = [round(i,4) for i in DBA_Collection]

save_list = M.merge(Clean_DP1,Clean_DBA)
with open(now+'.txt', 'w') as f:
    for item in save_list:
        f.write(str(item)+'\n')
    f.close()
plt.show()
exit()
