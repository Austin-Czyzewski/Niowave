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
