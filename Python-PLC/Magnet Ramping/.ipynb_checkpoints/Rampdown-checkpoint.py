"""
Created on Mon Dec 16 09:55 2019

@author: aczyzewski

Goal: Load in a prior magnet save and walk the magnets to a new value

Route:
    - Create variables to store mag settings
    - Write to the magnets to 0
"""
import Master as M
import ctypes  # An included library with Python install.

Acknowledgment = 7
Acknowledgment = ctypes.windll.user32.MessageBoxW(0, "Are you sure that you want to ramp all of the magnets to 0? Please make sure that you do not operate with the Cathode on during this process", "Ramp All Magnets to 0", 4)

if Acknowledgment != 6:
    exit()
    


WFHnum = 21 #The number of horizontal window frames to control
Hnums = []

WFVnum = 21 #The number of vertical window frames to control
Vnums = []

DPnum = 8 #The number of Dipoles
Dpnums = []

Solnum = 9 #Number of solenoids
Solnums = []

for i in range(100):
    if i < WFHnum:
        Hnums.append(20203 + 4*i)
    if i < WFVnum:
        Vnums.append(20201 + 4*i)
    if i < DPnum:
        Dpnums.append(22201 + 2*i)
    if i < Solnum:
        Solnums.append(21201 + 2*i)


Client = M.Make_Client('192.168.1.2')

for i in range(len(Hnums)):
    print("Window Frame {} H".format(i+1))
    M.Ramp_One_Way(Client, Hnums[i],0,Max_Step = 0.010)

for i in range(len(Vnums)):
    print("Window Frame {} V".format(i+1))
    M.Ramp_One_Way(Client, Vnums[i],0,Max_Step = 0.010)

for i in range(len(Solnums)):
    print("Solenoid {}".format(i+1))
    M.Ramp_One_Way(Client, Solnums[i],0,Max_Step = 0.010)
    
for i in range(len(Dpnums)):
    print("Dipole {}".format(i+1))
    M.Ramp_One_Way(Client, Dpnums[i],0,Max_Step = 0.005)


