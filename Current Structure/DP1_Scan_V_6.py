''' Creator: Austin Czyzewski

Date Created: 11/20/2020
Date Last Updated: 04/27/2021
Tested and Approved: 

Purpose: Move the first dipole up and down while taking data of collected current

Route: Gather user input for changes to dipole 1 to be made
    - Take a system snapshot before the scan
    - Define the parameters of data gathering
    - Read the value, perform safety checks
    - Write new Dipole one setting
    - Read Collected current
    - Repeat in ascending order
    - Repeat in descending order until reaching starting value
    - Plot
    - Save plot and txt file w/ snapshot as header

Changes from V3:
    Adding a config file for easier version control
    Adding config file confirmations
    Adding a system snapshot
'''

import matplotlib.pyplot as plt
from datetime import datetime
import time
import numpy as np
import matplotlib as mpl
import xlsxwriter
import glob
import os
import pandas as pd
import sys
import Master as M

config_file_path = str(sys.argv[-1])

Tunnel, PLC_IP, os_address, Runs, Step_Size, count, use_oscope = M.config_reader(config_file_path, "Dipole Scan")

print(Tunnel)
if Tunnel.lower() == 'west':
    import Tag_Database_West as Tags
elif Tunnel.lower() == 'east':
    import Tag_Database_East as Tags
else:
    import Tag_Database as Tags

plot_type = 'png' #Acceptable formats include: svg, png, jpeg, jpg, eps, pdf, tiff, tif, etc.
flip_graph = True


# print(Tunnel, PLC_IP, os_address, Runs, Step_Size, count, Oscope)
# print(type(Tunnel), type(PLC_IP), type(os_address), type(Runs), type(Step_Size), type(count), type(Oscope))

Client = M.Make_Client(PLC_IP)


End_Value = float(input("What is the ending amperage that you want to ramp the magnet to? (Amps)   "))

now = datetime.today().strftime('%y%m%d_%H%M%S') #Taking the current time in YYMMDD_HHmm format to save the plot and the txt file

#Grabbing all of our data for the system snapshot
#################################################
Pulsing_Status = bool(M.Read(Client, Tags.Pulsing_Output, Bool = True))

Emission_Setpoint = M.Read(Client, Tags.Emission_Set)

if Pulsing_Status:
    Emission_Actual = M.Read(Client, Tags.Emitted_Current, Average = True, count = pulsing_count, sleep_time = 0.010)
else:
    Emission_Actual = M.Read(Client, Tags.Emitted_Current, Average = True, count = count, sleep_time = 0.010)

Dipole_Tag = Tags.DP1
Read = Tags.DBA_Bypass

Start_Value = M.Read(Client, Dipole_Tag) #Recording the starting value of the Dipole
print("Started at {0:.3f} Amps".format(Start_Value))

DP1_Values = list()
DBA_Collection = list()
colors = list()
Oscope_Data = list()
Oscope_Data_2 = list()

print("Beginning dipole scans")
for i in range(Runs):
    #print("Going to target value")

    if use_oscope.lower() == 'true':
        DP1_Vals, DBA_Col, Oscope, O2 = M.Ramp_One_Way(Client, Dipole_Tag, End_Value, Max_Step = Step_Size, Return = "Y", \
                                                       Read_Tag = Read, count = count, Oscope = use_oscope, os_address = os_address)
        DP1_Values += DP1_Vals #Adding the recorded data to the lists
        DBA_Collection += DBA_Col
        Oscope_Data += Oscope
        Oscope_Data_2 += O2
    else:
        DP1_Vals, DBA_Col = M.Ramp_One_Way(Client, Dipole_Tag, End_Value, Max_Step = Step_Size, Return = "Y", Read_Tag = Read, count = count)
        DP1_Values += DP1_Vals #Adding the recorded data to the lists
        DBA_Collection += DBA_Col 

    
    colors += ['chocolate' for i in list(range(len(DP1_Vals)))] #Appending 'chocolate' as the color for this data set
    
    #print("Going to start")
    
    if use_oscope.lower() == 'true':
        DP1_Vals, DBA_Col, Oscope, O2 = M.Ramp_One_Way(Client, Dipole_Tag, Start_Value, Max_Step = Step_Size, Return = "Y", \
                                                       Read_Tag = Read, count = count, Oscope = use_oscope, os_address = os_address)
        DP1_Values += DP1_Vals #Adding the recorded data to the lists
        DBA_Collection += DBA_Col
        Oscope_Data += Oscope
        Oscope_Data_2 += O2
    else:
        DP1_Vals, DBA_Col = M.Ramp_One_Way(Client, Dipole_Tag, Start_Value, Max_Step = Step_Size, Return = "Y", Read_Tag = Read, count = count)
        DP1_Values += DP1_Vals #Adding the recorded data to the lists
        DBA_Collection += DBA_Col 

    colors += ['firebrick' for i in list(range(len(DP1_Vals)))] #Appending 'firebrick' as the color for this data set
    
DP1_Values = np.array(DP1_Values)
DBA_Collection = np.array(DBA_Collection)
Oscope_List = np.array(Oscope_Data)
Oscope_List_2 = np.array(Oscope_Data_2)

print("Dipole scans finished. Saving to .xlsx and plotting.")

fig, ax = plt.subplots(figsize = (12,8))

if use_oscope.lower() == 'true':
    ax.scatter(DP1_Values, Oscope_List, color = colors, alpha = 0.5)
    ax.set_ylabel("DBA Current Collected (mV)")
else:
    ax.scatter(DP1_Values, DBA_Collection, color = colors, alpha = 0.5)
    ax.set_ylabel("DBA Current Collected (mA)")

ax.grid(axis = 'both',alpha = 0.25,which = 'both',color = 'gray')
ax.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator(5))
ax.yaxis.set_minor_locator(mpl.ticker.AutoMinorLocator(5))

if flip_graph:
    ax.invert_xaxis()
    ax.invert_yaxis()

ax.set_xlabel('Dipole 1 Setting (Amps)')
ax.set_title("Dipole 1 current collected over walk from {0:.3f} to {1:.3f}".format(Start_Value, End_Value))
fig.suptitle("Orange = Ascending, Red = Descending",fontsize = 8, alpha = 0.65)
fig.savefig(f'.\Output Data\{Tunnel}\Dipole Scans\{now}_DP1_scan_graph.{plot_type}', dpi = 450, transparent = True)

print(f'.\\Output Data\\{Tunnel}\\Dipole Scans\\{now}_DP1_scan_graph.{plot_type} saved. Writing excel file. ')

if use_oscope.lower() == 'true':
    percent_collection_excel_formulas = [f"=(C{num+2}/D{num+2})*25" for num in range(len(DP1_Values))]
    data_frame = pd.DataFrame([DP1_Values, DBA_Collection, Oscope_List, Oscope_List_2, percent_collection_excel_formulas])
    data_frame = data_frame.transpose()
    data_frame.columns =  ['Dipole 1 (Amps)', 'Collection (Amps -- PLC)', 'Collection (mV -- Oscope)', 'Emitted Current (mV -- Oscope)', "Percent Collection"]

else:
    data_frame = pd.DataFrame([DP1_Values, DBA_Collection])
    data_frame = data_frame.transpose()
    data_frame.columns =  ['Dipole 1 (Amps)', 'Collection (Amps -- PLC)']

# data_frame.transpose()
print(data_frame.head())

workbook = xlsxwriter.Workbook(f'.\Output Data\{Tunnel}\Dipole Scans\{now}_DP1_scan.xlsx',  {'nan_inf_to_errors': True})
dpscan = workbook.add_worksheet('Dipole Scan Data')
snapshot = workbook.add_worksheet("Snapshot")

data_list = [list(data_frame.columns)] + data_frame.values.tolist()
for x, i in enumerate(data_list):
    for y, _ in enumerate(i):
        dpscan.write(x,y,data_list[x][y])
dpscan.freeze_panes(1,0)

var, data  = M.Snapshot(Client, Tunnel = 'west', filename = 'junk', save = False, feedback=True)
snapshot_df = pd.DataFrame(var, data[0])
snapshot_df.reset_index(inplace=True)
snapshot_df.columns = ['Values','Tag','Modbus Address']

snapshot_data_list = [list(snapshot_df.columns)] + snapshot_df.values.tolist()
for x, i in enumerate(snapshot_data_list):
    for y, _ in enumerate(i):
        snapshot.write(x,y,snapshot_data_list[x][y])
snapshot.freeze_panes(1,0)


chart1 = workbook.add_chart({'type': 'scatter'})

chart1.add_series({
    'name':       'PLC Data',
    'categories': "='Dipole Scan Data'!$A$2:$A${}".format(len(data_frame['Dipole 1 (Amps)'])+1),
    'values':     "='Dipole Scan Data'!$B$2:$B${}".format(len(data_frame['Dipole 1 (Amps)'])+1),
})

if use_oscope.lower() == 'true':
    chart1.add_series({
        'name':       'Oscilloscope data',
        'categories': "='Dipole Scan Data'!$A$2:$A${}".format(len(data_frame['Dipole 1 (Amps)'])+1),
        'values':     "='Dipole Scan Data'!$C$2:$C${}".format(len(data_frame['Dipole 1 (Amps)'])+1),
    })

chart1.set_title({'name': 'Dipole Scan'})

chart1.set_x_axis({'name': 'Dipole 1 Amps',# 'min': min(df.One), 'max': max(df.One)
                   'num_format': '#,##0.00', 'minor_unit': 0.005 , 'major_unit': .01,
                   'name_font': {'bold': True, 'italic': True}, 'reverse': True,
                   'interval_tick': int(len(data_frame['Dipole 1 (Amps)'])/10)})

chart1.set_y_axis({'name': 'Emitted Current', 'reverse': True})

dpscan.insert_chart('F2', chart1, {'x_offset': 25, 'y_offset': 10})

workbook.close()

print(f'.\Output Data\{Tunnel}\Dipole Scans\{now}_DP1_scan.xlsx saved. Program finished. Displaying plot.')

plt.show()

exit()
