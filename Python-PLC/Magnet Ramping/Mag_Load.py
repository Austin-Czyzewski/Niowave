"""
Created on Mon Dec 16 09:55 2019

@author: Austin Czyzewski

Goal: Load in a prior magnet save and walk the magnets to a new value

Route:
    - Create the tags to read
    - Load in an old magnet save
    - Write to the magnet the new setting using the Master Python file
"""
#imports: Pandas is used to store the excel file as a dataframe, Master is all modbus communications
import pandas as pd
import Master as M


#User input to define which magnet save to load in
Notebook = str(input("Which Magnet save to load? (YYMMDD_HHMM) "))

WFHnum = 21 #The number of horizontal window frames
Hnums = []

WFVnum = 21 #The number of vertical window frames
Vnums = []

DPnum = 8 #The number of Dipoles
Dpnums = []

Solnum = 9 #Number of solenoids
Solnums = []

for i in range(100):
    if i < WFHnum:
        Hnums.append(20203 + 4*i) #Modbus tag numbering convention for all of these, these are the starts and steps between likewise magnets
    if i < WFVnum:
        Vnums.append(20201 + 4*i)
    if i < DPnum:
        Dpnums.append(22201 + 2*i)
    if i < Solnum:
        Solnums.append(21201 + 2*i)

#Reading in the excel file as a dataframe for easier access (abbreviated as df)
        
excel_as_df = pd.read_excel('..\Magnet Saves\{}.xlsx'.format(Notebook)) #Using windows command line controls to direct python to the directory

Client = M.Make_Client('192.168.1.2') #Establishing a connection with the PLC, see Master.Make_Client

for i in range(len(Hnums)): #Iterate through the list of Horizontal window frames
    print("Window Frame {} H".format(i+1),Hnums[i],excel_as_df['WF H'].iloc[i]) #Print which magnet it is ramping
    M.Ramp_One_Way(Client, Hnums[i],excel_as_df['WF H'].iloc[i],Max_Step = 0.010) #Ramp that magnet, see Master.Ramp_One_Way
#Repeat for all types of magnets
for i in range(len(Vnums)):
    print("Window Frame {} V".format(i+1),Vnums[i],excel_as_df['WF V'].iloc[i])
    M.Ramp_One_Way(Client, Vnums[i],excel_as_df['WF V'].iloc[i],Max_Step = 0.010)

for i in range(len(Solnums)):
    print("Solenoid {}".format(i+1),Solnums[i],excel_as_df['Sol'].iloc[i])
    M.Ramp_One_Way(Client, Solnums[i],excel_as_df['Sol'].iloc[i],Max_Step = 0.010)
    
for i in range(len(Dpnums)):
    print("Dipole {}".format(i+1),Dpnums[i],excel_as_df['DP'].iloc[i])
    M.Ramp_One_Way(Client, Dpnums[i],excel_as_df['DP'].iloc[i],Max_Step = 0.005)


