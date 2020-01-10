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