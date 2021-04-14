import numpy as np
import xlsxwriter
import glob
import re
import xml.etree.ElementTree as ET
import pandas as pd

list_of_files = glob.glob("*.xml")
print(list_of_files)

value_input = None
print("Please select a file below to view or type in filename")
for number, file in enumerate(list_of_files):
    print(f"{number}:    {file}")
temp_value = input("Which magnet save would you like to load? ")
try:
    value_input = list_of_files[int(temp_value)]
except:
    print(f"Assuming {temp_value} is the selected file")
    value_input = temp_value
print(f"The file that is being loaded is: {value_input}")


tree = ET.parse(value_input)
root = tree.getroot()

# # one specific item attribute
# print('Item #2 attribute:')
# print(root[0][1].attrib)

# # all item attributes
# print('\nAll attributes:')
# for elem in root:
#     for subelem in elem:
#         print(subelem.attrib)

# # one specific item's data
# print('\nItem #2 data:')
# print(root[0][1].text)

# all items data
# print('\nAll item data:')
names = list()
values = list()
for elem in root:
    for number, subelem in enumerate(elem):
#         print(subelem.text)
        if number == 0: 
            names.append(subelem.text)
        elif number == 1:
            values.append(float(subelem.text))
        else:
            print("Woah dude you got more than two values for this xml thingy")
            
# print(len(names), len(values))
# for item in names:
#     print(item)
        
magnames_dictionary = {
"UNUSED":"PLC.MAG__HOLD[0]",
"Window Frame 1V":"PLC.MAG__HOLD[1]",
"Window Frame 1H":"PLC.MAG__HOLD[2]",
"Window Frame 2V":"PLC.MAG__HOLD[3]",
"Window Frame 2H":"PLC.MAG__HOLD[4]",
"Window Frame 3V":"PLC.MAG__HOLD[5]",
"Window Frame 3H":"PLC.MAG__HOLD[6]",
"Window Frame 4V":"PLC.MAG__HOLD[7]",
"Window Frame 4H":"PLC.MAG__HOLD[8]",
"Window Frame 5V":"PLC.MAG__HOLD[9]",
"Window Frame 5H":"PLC.MAG__HOLD[10]",
"Window Frame 6V":"PLC.MAG__HOLD[11]",
"Window Frame 6H":"PLC.MAG__HOLD[12]",
"Window Frame 7V":"PLC.MAG__HOLD[13]",
"Window Frame 7H":"PLC.MAG__HOLD[14]",
"Window Frame 8V":"PLC.MAG__HOLD[15]",
"Window Frame 8H":"PLC.MAG__HOLD[16]",
"Window Frame 9V":"PLC.MAG__HOLD[17]",
"Window Frame 9H":"PLC.MAG__HOLD[18]",
"Window Frame 10V":"PLC.MAG__HOLD[19]",
"Window Frame 10H":"PLC.MAG__HOLD[20]",
"Window Frame 11V":"PLC.MAG__HOLD[21]",
"Window Frame 11H":"PLC.MAG__HOLD[22]",
"Window Frame 12V":"PLC.MAG__HOLD[23]",
"Window Frame 12H":"PLC.MAG__HOLD[24]",
"Window Frame 13V":"PLC.MAG__HOLD[25]",
"Window Frame 13H":"PLC.MAG__HOLD[26]",
"Window Frame 14V":"PLC.MAG__HOLD[27]",
"Window Frame 14H":"PLC.MAG__HOLD[28]",
"Window Frame 15V":"PLC.MAG__HOLD[29]",
"Window Frame 15H":"PLC.MAG__HOLD[30]",
"Window Frame 16V":"PLC.MAG__HOLD[31]",
"Window Frame 16H":"PLC.MAG__HOLD[32]",
"Window Frame 17V":"PLC.MAG__HOLD[33]",
"Window Frame 17H":"PLC.MAG__HOLD[34]",
"Window Frame 18V":"PLC.MAG__HOLD[35]",
"Window Frame 18H":"PLC.MAG__HOLD[36]",
"Window Frame 19V":"PLC.MAG__HOLD[37]",
"Window Frame 19H":"PLC.MAG__HOLD[38]",
"Window Frame 20V":"PLC.MAG__HOLD[39]",
"Window Frame 20H":"PLC.MAG__HOLD[40]",
"Window Frame 21V":"PLC.MAG__HOLD[41]",
"Window Frame 21H":"PLC.MAG__HOLD[42]",
"Dipole 1":"PLC.MAG__HOLD[43]",
"Dipole 2":"PLC.MAG__HOLD[44]",
"Dipole 3":"PLC.MAG__HOLD[45]",
"Dipole 4":"PLC.MAG__HOLD[46]",
"UNUSED 1":"PLC.MAG__HOLD[47]",
"UNUSED 2":"PLC.MAG__HOLD[48]",
"UNUSED 3":"PLC.MAG__HOLD[49]",
"Dipole 8":"PLC.MAG__HOLD[50]",
"Solenoid 1":"PLC.MAG__HOLD[51]",
"Solenoid 2":"PLC.MAG__HOLD[52]",
"Solenoid 3":"PLC.MAG__HOLD[53]",
"Solenoid 4":"PLC.MAG__HOLD[54]",
"Solenoid 5":"PLC.MAG__HOLD[55]",
"Solenoid 6":"PLC.MAG__HOLD[56]",
"Solenoid 7":"PLC.MAG__HOLD[57]",
"Solenoid 8":"PLC.MAG__HOLD[58]",
"Solenoid 9":"PLC.MAG__HOLD[59]",
"Window Frame 22V":"PLC.MAG__HOLD[60]",
"Window Frame 22H":"PLC.MAG__HOLD[61]",
"Window Frame 23V":"PLC.MAG__HOLD[62]",
"Window Frame 23H":"PLC.MAG__HOLD[63]",
"Window Frame 24V":"PLC.MAG__HOLD[64]",
"Window Frame 24H":"PLC.MAG__HOLD[65]",
"Window Frame 25V":"PLC.MAG__HOLD[66]",
"Window Frame 25H":"PLC.MAG__HOLD[67]",
"Window Frame 26V":"PLC.MAG__HOLD[68]",
"Window Frame 26H":"PLC.MAG__HOLD[69]",
"Window Frame 27V":"PLC.MAG__HOLD[70]",
"Window Frame 27H":"PLC.MAG__HOLD[71]",
"Window Frame 28V":"PLC.MAG__HOLD[72]",
"Window Frame 28H":"PLC.MAG__HOLD[73]",
"Dipole 9":"PLC.MAG__HOLD[74]",
"Solenoid 10":"PLC.MAG__HOLD[75]",
"Solenoid 11":"PLC.MAG__HOLD[76]",
"Solenoid 12":"PLC.MAG__HOLD[77]"}

def name_from_pos(pos):
    return str((list(magnames_dictionary.keys())[list(magnames_dictionary.values()).index(pos)]))
# magnet_name = name_from_pos("PLC.MAG__HOLD[23]")
# print(magnet_name)

magnet_names = [name_from_pos(x) for x in names]

# df = pd.DataFrame([magnet_names, values], index = ['Magnet', 'Value (Amps)'])
# df = df.transpose()

# df = df[~df.Magnet.str.contains("UNUSED")]

df = pd.DataFrame([magnet_names, values], index = ['Magnet', 'Value (Amps)'])
df = df.transpose()

df = df[~df.Magnet.str.contains("UNUSED")]
# b.head()
# df.index = df.Magnet.to_series.str.rsplit(' ').
# a = df.Magnet.str.rsplit(' ').str[-1].astype(int).sort_values()
df['index2'] = df.index
df['Groups'] = df['Magnet'].str.extract(r'^(?P<First>\S+).*?')
df = df.sort_values(by = ['Groups', 'index2'], ignore_index=False)
df = df.drop(labels = ['Groups','index2'], axis = 1)

# print(value_input[:-3] + "xlsx")
workbook = xlsxwriter.Workbook(value_input[:-3] + "xlsx", {'strings_to_numbers': True})
mags = workbook.add_worksheet("Magnet Save")
data_list = [list(df.columns)] + df.values.tolist()
hoz_trans = 0
ver_trans = 0
Sol_trig = False
WF_trig = False
for x, i in enumerate(data_list):
    for y, _ in enumerate(i):
        if 'Solenoid' in str(data_list[x][y]):
            if Sol_trig:
                pass
            else:
                hoz_trans = -x+1
                ver_trans = 3
                Sol_trig = True
        if 'Window' in str(data_list[x][y]):
            if WF_trig:
                pass
            else:
                hoz_trans = -x+1
                ver_trans = 6
                WF_trig = True
        if y > 2:
            mags.write_number(x+hoz_trans,y+ver_trans,float(data_list[x][y]))
        else:
            mags.write(x+hoz_trans,y+ver_trans,data_list[x][y])
workbook.close()