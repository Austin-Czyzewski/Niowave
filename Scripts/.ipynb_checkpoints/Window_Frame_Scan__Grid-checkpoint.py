import Master as M
import numpy as np
import Matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d, Axes3D
from datetime import datetime

#Magnet and read tags
WFH_Tag = 20203
WFV_Tag = 20201
Read_Tag = 11109


#Adjust T scan Parameters
Horizontal_Delta = .1
Vertical_Delta = .1
Resolution = 40


#Adjust Grid Parameters
Grid_Resolution_Horizontal = 4
Grid_Resolution_Vertical = 5

#For the client
IP = '192.168.1.2'

Client = M.Make_Client(IP)

WFH_Start = M.Read(Client, WFH_Tag)
WFV_Start = M.Read(Client, WFV_Tag)

######
#Walking us to our starting point
######

for i in range(1, Grid_Resolution + 1):
    WFH_Write_Value = WFH_Start - i/2 * (Horizontal_Delta/Grid_Resolution)
    WFV_Write_Value = WFV_Start + i/2 * (Vertical_Delta/Grid_Resolution)
    
    M.Write(Client, WFH_Tag, WFH_Write_Value)
    M.Write(Client, WFV_Tag, WFV_Write_Value)
    
WFH_Corner = M.Read(Client, WFH_Tag)
WFV_Corner = M.Read(Client, WFV_Tag)

#Total_Data = M.Rapid_T_Scan(Client, WFH_Tag, WFV_Tag, Read_Tag, Horizontal_Delta, Vertical_Delta, Resolution)

for i in range(Grid_Resolution_Vertical):
    
    WFV_Write_Value = WFV_Corner - i * (Vertical_Delta/Grid_Resolution_Vertical)
    
    M.write(Client,WFV_Tag,WFV_Write_Value)
    
    if i == 0:
        
        Total_Data = M.Rapid_T_Scan(Client, WFH_Tag, WFV_Tag, Read_Tag, Horizontal_Delta, Vertical_Delta, Resolution)
        
    else:
    
        Data =  M.Rapid_T_Scan(Client, WFH_Tag, WFV_Tag, Read_Tag, Horizontal_Delta, Vertical_Delta, Resolution)
    
        Total_Data = np.append(Total_Data, Data, axis = 0)
    
    for j in range(1, Grid_Resolution_Horizontal):
        
        if i % 2 == 0:
            
            WFH_Write_Value = WFH_Corner + j * (Horizontal_Delta/Grid_Resolution_Horizontal)
    
            M.write(Client,WFH_Tag,WFH_Write_Value)
    
            Data =  M.Rapid_T_Scan(Client, WFH_Tag, WFV_Tag, Read_Tag, Horizontal_Delta, Vertical_Delta, Resolution)
    
            Total_Data = np.append(Total_Data, Data, axis = 0)
        
        else:
            
            WFH_Write_Value = WFH_Corner - j * (Horizontal_Delta/Grid_Resolution_Horizontal)
    
            M.write(Client,WFH_Tag,WFH_Write_Value)
    
            Data =  M.Rapid_T_Scan(Client, WFH_Tag, WFV_Tag, Read_Tag, Horizontal_Delta, Vertical_Delta, Resolution)
    
            Total_Data = np.append(Total_Data, Data, axis = 0)
        
WFH_End = M.Read(Client, WFH_Tag)
WFV_End = M.Read(Client, WFV_Tag)
        
if i % 2 == 0:
    for i in range(1, Grid_Resolution + 1):
    WFH_Write_Value = WFH_End - i/2 * (Horizontal_Delta/Grid_Resolution)
    WFV_Write_Value = WFV_End + i/2 * (Vertical_Delta/Grid_Resolution)
    
    M.Write(Client, WFH_Tag, WFH_Write_Value)
    M.Write(Client, WFV_Tag, WFV_Write_Value)
    
else:
    
    for i in range(1, Grid_Resolution + 1):
    WFH_Write_Value = WFH_End + i/2 * (Horizontal_Delta/Grid_Resolution)
    WFV_Write_Value = WFV_End + i/2 * (Vertical_Delta/Grid_Resolution)
    
    M.Write(Client, WFH_Tag, WFH_Write_Value)
    M.Write(Client, WFV_Tag, WFV_Write_Value)
    

#M.Write(Client, WFH_Tag, WFH_Start)
#M.Write(Client, WFV_Tag, WFV_Start)
######
#Saving to a file
######
    
now = datetime.today().strftime('%y%m%d_%H%M') #Taking the current time in YYMMDD_HHmm format to save the plot and the txt file

with open(now +'.txt', 'w') as f: #Open a new file by writing to it named the date as created above + .txt
    
    for i in Total_Data:
        f.write(str(i) + '\n')
        
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
ax.set_title("Collection in Window Frame Space")


plt.show()
