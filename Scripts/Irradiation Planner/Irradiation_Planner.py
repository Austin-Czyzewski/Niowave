import numpy as np
import matplotlib.pyplot as plt
import seaborn
import datetime
import xlsxwriter
import pandas as pd
import math
# seaborn.set()

target_size = 1 #mL 1 or 10

Energy = np.arange(10,21,1)

if target_size == 1:
    Power = np.array([4128, 2200, 1279, 824, 598, 481, 412, 363, 332, 310, 290]) #Data from the green curve graphs 1 mL target

if target_size == 10:
    Power = np.array([12061, 6768, 4095, 2699, 1980, 1594, 1369, 1216, 1119, 1049, 990]) #Data from the green curve graphs 10 mL target
    
fudge_factor = 1.5 #Accelerator Watts/Iso Watts conversion (We think 1000 they say 500 = ff:2)

needed_amount = 300 #uCi

Power = Power*(needed_amount/1000)*fudge_factor #Adding in fudge factor and converting to Ac amount needed off of Green Curve

Us = [13.2,400]

radium_targets = [31, 40, 50, 75, 100] #Whatever target sizes you want to see
Beam_Powers = [200, 280, 300, 354, 400, 500, 600, 700, 800, 900, 1000] #Whatever powers you want to see

shipping_date = datetime.date(2022,7,30) #For the print statements below
from_prep_to_ship = 1

powers_offset = 2 #Spaces away from the edge (for excel file) (Minimum = 2)
radiums_offset = 3 #Spaces away from the top (Minimum = 3)

#######################################
# Begin no change zone
#######################################

filename = f'{target_size}mL Target.xlsx'

def days_with_losses(days):
    '''
    Somewhat factors in decay without doing all of the complicated math behind it (only works with continuous irradiation)
    '''
    return (-0.006*days + 1.0707)

def decay_eq(days_irradiated):
    '''
    Calculates optimal time to pull target based on days of continuous irradiation
    '''
    return 18.583*np.exp(-0.036*(days_irradiated))

list_of_powers = list()
list_of_radiums = list()
list_of_days = list()

Energy_Integer = math.trunc(Us[0])
Energy_Index = np.where(Energy == Energy_Integer)[0][0]

for power in Beam_Powers:
#     print("#"*60)
#     print(f"########## {power} Us-Watts ##########")
#     print("#"*60)
    for target in radium_targets:
        try:
            Scaled_Power = Power*100/target #Scales power needed to Ra in target amount
            Required_Power = Scaled_Power[Energy_Index] - (Scaled_Power[Energy_Index] - Scaled_Power[Energy_Index + 1])*(Us[0]-Energy_Integer) #Find required power and apprx. based on our energy
            Weeks_Running = Required_Power/power
            Days_Running = Weeks_Running*7
            Days_Running_Scaled = Days_Running / days_with_losses(Days_Running)
#             print(f'{target} mg Ra-226 target: {Days_Running_Scaled*24:.1f} Hours of Running // {Days_Running_Scaled/7:.1f} weeks')
            irradiation_end = shipping_date - datetime.timedelta(from_prep_to_ship) - datetime.timedelta(decay_eq(Days_Running_Scaled))
            target_install_deadline = irradiation_end - datetime.timedelta(Days_Running_Scaled)
#             print(f"{target} mg target must be installed by {target_install_deadline} with {Days_Running_Scaled:.1f} days of irradiation and {decay_eq(Days_Running_Scaled):.1f} days of decay\n")
            list_of_powers.append(power)
            list_of_radiums.append(target)
            list_of_days.append(Days_Running_Scaled)
        except:
            print("Not achievable\n")

wb = xlsxwriter.Workbook(filename)
ws = wb.add_worksheet()
bold = wb.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True})

if (len(list_of_powers) != len(list_of_radiums)) or (len(list_of_powers) != len(list_of_days)):
    print("I don't know how but this shit's messed up yo")
    
ra_length = len(radium_targets)
power_length = len(Beam_Powers)
# for i in range(len(list_of_powers)):
powers_array = np.array(list_of_powers)
radiums_array = np.array(list_of_radiums)
days_array = np.array(list_of_days)

print(powers_array[::ra_length])
print(radiums_array[::power_length])

ws.write('A1', f'Time Running (Days) to make {needed_amount} uCi Ac-225 with {target_size} mL target', bold)
ws.merge_range(xlsxwriter.utility.xl_col_to_name(powers_offset)+'1:'+xlsxwriter.utility.xl_col_to_name(powers_offset + power_length - 1)+'1', "Accelerator Dept Power (W)", bold)
ws.merge_range('A' + str(radiums_offset) + ':' + 'A' + str(radiums_offset + ra_length - 1), "Ra Target Size (mg)", bold)
ws.write(xlsxwriter.utility.xl_col_to_name(powers_offset + power_length)+'1', 'Assuming a 10 mL target at the NERD facility')

for number, power in enumerate(powers_array[::ra_length]):
    ws.write(xlsxwriter.utility.xl_col_to_name(number + powers_offset) + str(radiums_offset-1), power, bold)

for number, radium in enumerate(radiums_array[::power_length]):
    ws.write(xlsxwriter.utility.xl_col_to_name(powers_offset-1) + str(number + radiums_offset), radium, bold)

i = 0
for power_index, power in enumerate(powers_array[::ra_length]):
    for radium_index, radium in enumerate(radiums_array[::power_length]):
        ws.write(xlsxwriter.utility.xl_col_to_name(power_index + powers_offset) + str(radium_index + radiums_offset), round(days_array[i], 1))
        i += 1

wb.close()
