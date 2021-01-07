################################################################################
# Chad Denbrock
# Niowave Inc.
# Produced: 03.04.2020
# Last updated: 08.06.2020
################################################################################

import matplotlib.pyplot as plt
from openpyxl import Workbook
from openpyxl import load_workbook
import matplotlib as mpl
import re
import numpy as np
import time
import pandas as pd
import os
mpl.rcParams['savefig.dpi']  = 500
mpl.rcParams['font.size']    = 12
mpl.rcParams['mathtext.fontset'] = 'stix'
mpl.rcParams['font.family'] = 'STIXGeneral'


################################################################################
# Goal: Plot a fission product/actinide inventory from UTA-2 for a given
#           irradiation/decay cycle.
#
#
# Requirements:
#       Two excel (.xlsx) files. One for each the NU and LEU portions of UTA-2.
#           They must be named with 'NU' and 'LEU' being the beginning characters
#           in the file like 'NU blah blah.xlsx' and 'LEU blah blah.xlsx'. These
#           excel files must be copy and pasted acitivities as a function of time
#           from F71 output files from Origen. This includes the isotope names
#           being the column names with the activities as a function of time
#           progressing in the rows in the column. The irradiation/decay cycle
#           for the NU and LEU obviously must be the same for the two excel
#           documents. The NU and LEU inventories will inveitably have different
#           isotopes in their inventory. This is not a problem.
#       The 'Half_Lives_List.txt' half-life library used to check whether the
#           isotopes have a half-life less than or greater than or equal to
#           120 days.
################################################################################

#   No 100 gNU MCNP calculations were performed for the optimized UTA-2 configuration
# def convert_to_100gNU(NU) :
#
#     fraction_FP_and_An_in_100gNU_over_total_NU = 0.01743
#     fraction_U237_in_100gNU_over_total_NU = 0.03485
#
#     Time = NU['Unnamed: 0']
#     NU = NU.drop(columns = 'Unnamed: 0')
#     Updated_Inventory = NU*fraction_FP_and_An_in_100gNU_over_total_NU
#     if kind_of_isotopes.lower() == 'actinides' or kind_of_isotopes.lower() == 'an' :
#         Updated_Inventory['u237'] = Updated_Inventory['u237']*fraction_U237_in_100gNU_over_total_NU/fraction_FP_and_An_in_100gNU_over_total_NU
#     Updated_Inventory = pd.DataFrame.sort_values(Updated_Inventory,Updated_Inventory.shape[0]-1,axis=1,ascending=False)
#     Updated_Inventory.insert(loc=0,column = f'Time ({time_units})',value = Time)
#
#     print('Writing updated inventory to Inventory_Hottest_100gNU.xlsx ...\n')
#
#     while True :
#         try :
#             Updated_Inventory.to_excel('Inventory_Hottest_100gNU.xlsx')
#             break
#         except :
#             print('There was a problem with writing Inventory_Hottest_100gNU.xlsx. '\
#                 'It may already exist. Delete it if it does. The script will try to '\
#                 'write it again in 15 seconds.\n')
#             time.sleep(15)
#     return Updated_Inventory

def convert_to_1kgNU(NU) :

    Mass_per_rod_gU = 134.6
    Rods_per_1kgNU = 1000/Mass_per_rod_gU
    scaling = Rods_per_1kgNU/7


    fraction_FP_and_An_in_7rods_over_total_NU = 0.1187849
    fraction_U237_in_7rods_over_total_NU = 0.3376

    fraction_FP_and_An_in_1kgNU_over_total_NU = fraction_FP_and_An_in_7rods_over_total_NU * scaling     # Linearly scaling fractions from 7 rods to ~ 7.429 rods in 1 kgNU
    fraction_U237_in_1kgNU_over_total_NU = fraction_U237_in_7rods_over_total_NU * scaling               # Linearly scaling fractions from 7 rods to ~ 7.429 rods in 1 kgNU

    Time = NU['Unnamed: 0']
    NU = NU.drop(columns = 'Unnamed: 0')
    Updated_Inventory = NU*fraction_FP_and_An_in_1kgNU_over_total_NU

    if kind_of_isotopes.lower() == 'actinides' or kind_of_isotopes.lower() == 'an' :
        Updated_Inventory['u237'] = Updated_Inventory['u237']*fraction_U237_in_1kgNU_over_total_NU/fraction_FP_and_An_in_1kgNU_over_total_NU
    Updated_Inventory = pd.DataFrame.sort_values(Updated_Inventory,Updated_Inventory.shape[0]-1,axis=1,ascending=False)
    Updated_Inventory.insert(loc=0,column = f'Time ({time_units})',value = Time)

    print('Writing updated inventory to The_Hottest_1kgNU_Inventory.xlsx ...\n')

    while True :
        try :
            Updated_Inventory.to_excel('The_Hottest_1kgNU_Inventory.xlsx')
            break
        except :
            print('There was a problem with writing The_Hottest_1kgNU_Inventory.xlsx. '\
                'It may already exist. Delete it if it does. The script will try to '\
                'write it again in 15 seconds.\n')
            time.sleep(15)
    return Updated_Inventory

def U_237_adder(NU,LEU) :

    fraction_U_237_in_LEU = 0.737
    fraction_U_237_in_NU = 1.0 - fraction_U_237_in_LEU
    Total_core_reaction_rate_per_e = 2.386e-4     # Total U-237 reactions/e for 20 MeV electrons in traditional UTA-2 geometry
    Electron_rate = 2.184e15
    print(f'The total core reaction rate per electron for U-237 production '\
        f'{Total_core_reaction_rate_per_e:.3e} and the electron source intensity '\
        f'{Electron_rate:.3e} are hardcoded in for a 20 MeV electron beam and need to be changed for alternate '\
        'configurations of UTA-2.\n'\
        'The neutron flux to achieve the ORIGEN results and the electron rate to '\
        'achieve the U-237 production are no longer physically linked. So, be '\
        'careful and make sure the hardcoded electron rate corresponds to the '\
        'electron rate necessary to produce the fission power input into ORIGEN.\n\n')

    Total_core_reaction_rate = Electron_rate * Total_core_reaction_rate_per_e


    half_life_U_237 = 6.752*86400
    lambda_U_237 = np.log(2)/half_life_U_237
    try :
        test_activity = pd.Series.to_numpy(LEU['np239'],dtype = 'float')
    except :
        print('Np239 doesnt exist in the LEU spreadsheet. This probably means you incorrectly asked for what youre plotting.\n')
        exit()
    Time = pd.Series.to_numpy(NU['Unnamed: 0'],dtype = 'float')

    if time_units.lower() == 'years' :
        dt_multiplier = 86400*365.25

    elif time_units.lower() == 'days' :
        dt_multiplier = 86400.0


    U_237 = np.zeros(len(Time))


    growth_guess = 0
    first_guess_completed = False

    for time_values in range(len(Time)-1) :


        if test_activity[time_values] == 0 or (test_activity[time_values+1] - test_activity[time_values])/test_activity[time_values] >= growth_guess:

            dt = (Time[time_values + 1] - Time[time_values])*dt_multiplier
            dU_237 = (Total_core_reaction_rate - lambda_U_237*U_237[time_values])*dt

        else :

            if first_guess_completed == False :
                growth_guess = (test_activity[time_values-1] - test_activity[time_values])/(50*test_activity[time_values-1])
                first_guess_completed = True


            dt = (Time[time_values + 1] - Time[time_values])*dt_multiplier
            dU_237 =                           - lambda_U_237*U_237[time_values]*dt

        if time_units == 'Years' and (Time[time_values] == 4.006471 or Time[time_values] ==4.004729):
            #print('\nin here\n')
            dU_237 = 0.0
        #print(Time[time_values],test_activity[time_values+1] - test_activity[time_values],dU_237,U_237[time_values],dt)

        U_237[time_values+1] = U_237[time_values] + dU_237
    U_237 = U_237 * lambda_U_237/3.7e10

    #plt.plot(Time,U_237)
    #plt.plot(Time,U_237*fraction_U_237_in_NU)
    #plt.plot(Time,U_237*fraction_U_237_in_LEU)
    #plt.show()

    if 'u237' not in NU.columns :
        NU.insert(loc = 0,column = 'u237',value=U_237*fraction_U_237_in_NU)
    else :
        NU = NU.add(pd.DataFrame(U_237*fraction_U_237_in_NU,columns = ['u237']),fill_value = 0)

    if 'u237' not in LEU.columns :
        LEU.insert(loc = 0,column = 'u237',value=U_237*fraction_U_237_in_LEU)
    else :
        LEU = LEU.add(pd.DataFrame(U_237*fraction_U_237_in_LEU,columns = ['u237']),fill_value = 0)
    return NU,LEU


def plotting(The_Inventory) :
    eff_list = ['kr85m','kr88','kr85','kr87','i131','i132','i133','i135','xe133','xe133m','xe135']
    Input = list()


    Splitting = True    # Choosing to always split the inventories for plotting purposes

#       Asking for what to plot (totals or specific isotopes)
    top_regex = '[Tt]op [0-9]+'
    while True :
        #try :
        Input.append(input('Name isotopes you wish to plot. You can also plot the total by typing \'Total\', the top x isotopes by activity at final time by typing \'Top <integer number of isotopes you want to see>\', or the effluents list by typing \'Effluents\'. (Hit enter after each one and type \'Stop\' to quit entering isotopes)\n'))
        if Input[-1].lower() == 'effluents' :
            Input = Input[:-1] + eff_list
        if len(re.findall(top_regex,Input[-1])) > 0:
            top_quantity = int(Input[-1].split()[1])
            Input = Input[:-1] + list(The_Inventory.columns[3:top_quantity+3])
        if Input[-1].lower() == 'stop' :
            Input = Input[:-1]
            break
        #except :
            #print('Try that again. Make sure to hit enter after each entry. The form should be: \'np239\'\n')



    Greater_than,Less_than = split_120(The_Inventory)     # Split the inventory by half-lives and retrieve the time vector

    Time = The_Inventory[f'Time ({time_units})']

    if 'Total' in Input:
        # -----------------------
        # Plotting both HL's
        # -----------------------
        plt.plot(Time,Less_than['Total'])
        if len(Greater_than['Total']) > 0:
            plt.plot(Time,Greater_than['Total'])
        legend_list = ['Half Life < 120 d','Half Life > 120 d']
        for vals in Input :
            if vals != 'Total'  :
                legend_list.append(vals)
        #plt.show()
        if len(Greater_than['Total']) > 0:
            max = (Greater_than['Total'] + Less_than['Total']).max()
            end = pd.Series.to_numpy(Greater_than['Total'] + Less_than['Total'])[-1]
            print(f'\nThe max total activity was {max:.3f} (Ci)')
            print(f'The final total activity was {end:.3f} (Ci)')
            max = Greater_than['Total'].max()
            end = pd.Series.to_numpy(Greater_than['Total'])[-1]
            print(f'The max activity (HL > 120 d) was {max:.3f} (Ci)')
            print(f'The final activity (HL > 120 d) was {end:.3f} (Ci)')
            max = Less_than['Total'].max()
            end = pd.Series.to_numpy(Less_than['Total'])[-1]
            print(f'The max activity (HL < 120 d) was {max:.3f} (Ci)')
            print(f'The final activity (HL < 120 d) was {end:.3f} (Ci)')
        else :
            max = Less_than['Total'].max()
            end = pd.Series.to_numpy(Less_than['Total'])[-1]
            print(f'The max total activity was {max:.3f} (Ci)')
            print(f'The final total activity was {end:.3f} (Ci)\n')
        for vals in Input :
            if vals != 'Total'  :

                plt.plot(Time,pd.Series.to_numpy(The_Inventory[vals]))
                print(f'The max activity of {vals} was {pd.Series.to_numpy(The_Inventory[vals]).max():.3f} (Ci)')
                print(f'The final activity of {vals} was {pd.Series.to_numpy(The_Inventory[vals])[-1]:.3f} (Ci)')
        plt.grid(which = 'both', axis = 'both')
        plt.legend(legend_list)
        plt.title(f'Activity of {Title}')
        plt.xlabel(time_units)
        plt.ylabel('Activity (Ci)')
        plt.savefig(fname + '_Both.png',bbox_inches = 'tight')
        print(f'\nFigure {fname}_Both.png produced and saved.\n')
        plt.close()
        # -----------------------
        # Plotting HL >
        # -----------------------
        if len(Greater_than['Total']) > 0:
            plt.plot(Time,Greater_than['Total'])
            legend_list = ['Half Life > 120 d']
            for vals in Input :
                if vals != 'Total'  :
                    legend_list.append(vals)
                    plt.plot(Time,pd.Series.to_numpy(The_Inventory[vals]))
            plt.grid(which = 'both', axis = 'both')
            plt.legend(legend_list)
            plt.title(f'Activity of {Title} (HL > 120 days)')
            plt.xlabel(time_units)
            plt.ylabel('Activity (Ci)')
            plt.savefig(fname + '_Greaterthan.png',bbox_inches = 'tight')
            print(f'Figure {fname}_Greaterthan.png produced and saved.\n')
            plt.close()
        # -----------------------
        # Plotting HL <
        # -----------------------
        plt.plot(Time,Less_than['Total'])
        legend_list = ['Half Life < 120 d']
        for vals in Input :
            if vals != 'Total'  :
                plt.plot(Time,pd.Series.to_numpy(The_Inventory[vals]))
                legend_list.append(vals)
        plt.grid(which = 'both', axis = 'both')
        plt.legend(legend_list)
        plt.title(f'Activity of {Title} (HL < 120 days)')
        plt.xlabel(time_units)
        plt.ylabel('Activity (Ci)')
        plt.savefig(fname + '_Lessthan.png',bbox_inches = 'tight')
        print(f'Figure {fname}_Lessthan.png produced and saved.\n')
        plt.close()
        # -----------------------
        # Plotting Individual Isotopes (doesnt work)
        # -----------------------
        # for vals in Input :
        #     if vals != 'Total'  :
        #         plt.plot(Time,pd.Series.to_numpy(The_Inventory[vals]))
        #         legend_list.append(vals)
        # plt.grid(which = 'both', axis = 'both')
        # plt.legend(legend_list)
        # plt.title(f'Activity of {Title} (HL < 120 days)')
        # plt.xlabel(time_units)
        # plt.ylabel('Activity (Ci)')
        # plt.savefig(fname + 'Less.png',bbox_inches = 'tight')
        # print(f'Figure {fname}Less.png produced and saved.\n')
        # plt.close()

    else :
        legend_list = list()
        for vals in Input :
            try :
                if vals != 'Total'  :
                    plt.plot(Time,pd.Series.to_numpy(The_Inventory[vals]),linewidth=0.75)
                    print(f'The max activity of {vals} was {pd.Series.to_numpy(The_Inventory[vals]).max():.3f} (Ci)')
                    print(f'The final activity of {vals} was {pd.Series.to_numpy(The_Inventory[vals])[-1]:.3f} (Ci)')
                    legend_list.append(vals)
            except :
                print(f'\nPlotting {vals} wasnt found. Check if it is in the isotope list and try again.\n')
                continue

        if len(legend_list)>0 :
            plt.grid(which = 'both', axis = 'both')
            plt.legend(legend_list)
            plt.title(f'Activity of {Title}')
            plt.xlabel(time_units)
            plt.ylabel('Activity (Ci)')
            plt.savefig(fname,bbox_inches = 'tight')
            print(f'\nFigure {fname} produced and saved.\n')
            plt.close()













def obtain_inventory() :
    print('LEU and NU inventories must be named with LEU and NU in the first characters of each respective file name.\nAlso, there can be only the NU and LEU inventory excel documents in the directory.\n')
    print('\n\nTHIS SCRIPT ASSUMES THAT ANY ISOTOPE NOT FOUND IN THE ISOTOPE HALF-LIFE LIBRARY HAS A HALF-LIFE LESS THAN 120 DAYS!!!\n\n')
    cwd = os.getcwd()
    Files = os.listdir(cwd)
    excel_list = list()
    for file in Files :
        if '.' in file :
            if file.split('.')[1] == 'xlsx' :
                excel_list.append(file)

    excel_list.sort()
    for i,excel_files in enumerate(excel_list) :
        if excel_files == 'The_Hottest_1kgNU_Inventory.xlsx' or excel_files == 'Total_core.xlsx':
            continue
        if i == 0 :
            print(f'Pulling LEU inventory from {excel_files}\n')
            LEU = pd.read_excel(excel_files)

        elif i == 1 :
            print(f'Pulling NU inventory from {excel_files}\n')
            NU = pd.read_excel(excel_files)




#   U-237 has to be entered into NU and LEU here before added to total core.


    if kind_of_isotopes.lower() == 'actinides' or kind_of_isotopes.lower() == 'an' :
        print('Computing U-237 activity as a function of time and adding it to the inventories.\n')
        NU,LEU = U_237_adder(NU,LEU)


    if Portion_of_core == 1 :
        print(f'Adding the LEU and NU dataframes.\n')
        Total_core = NU.add(LEU,fill_value = 0)
        Time = pd.Series.to_numpy(NU['Unnamed: 0'])
        Total_core = Total_core.drop(columns = ['Unnamed: 0'])
        # Sorting the dataframe by highest endpoint activity
        Total_core = pd.DataFrame.sort_values(Total_core,Total_core.shape[0]-1,axis = 1,ascending = False)
        Time_column_name = f'Time ({time_units})'
        Total_core.insert(loc=0,column = Time_column_name,value= Time)
        # Writing the total core excel spreadsheet
        print(f'Writing total inventory to Total_core.xlsx\n')
        print(Total_core.head())
        Total_core.to_excel('Total_core.xlsx')
        print(f'Total Core inventory saved in Total_core.xlsx\n')
        return Total_core

    if Portion_of_core == 2 :
        print(f'Converting NU inventory into hottest 1 kgNU.\n')

        Inventory = convert_to_1kgNU(NU)

        return Inventory





def half_life_greater_than(isotope) :
    with open('Half_Lives_List.txt','r') as file_handle :
        bool = False
        for line in file_handle :
            if line.split()[0] == isotope:
                half_life = line.split()[3]

                # print(isotope, float(half_life) >= 86400*120.0)
                if float(half_life) >= 86400*120.0 :
                    bool = True
                    return True
                else :
                    bool = True
                    return False

        if bool == False :
            return False
            raise ValueError(f'Isotope {isotope} not found in half_lives_list.txt')



def split_120(original) :


    Greater_than = pd.DataFrame()
    Less_than = pd.DataFrame()

    isotopes = list(original)
    time_identifier = f'Time ({time_units})'

    for isotope in isotopes :


        if isotope == 'Totals' or isotope == 'Subtotals':

            continue

        elif isotope != time_identifier :
            if half_life_greater_than(isotope) :
                Greater_than.insert(0,isotope,original[isotope])
            else :
                Less_than.insert(0,isotope,original[isotope])

        else :
            pass
            #raise ValueError(f'Isotope {isotope} passed if tests.\n')


    total_list = list()

    for key,value in Greater_than.iterrows() :
        sum = 0.0
        for vals in value :
            sum += vals
        total_list.append(sum)
    Greater_than.insert(0,'Total',total_list)

    total_list = list()

    for key,value in Less_than.iterrows() :
        sum = 0.0
        for vals in value :
            sum += vals
        total_list.append(sum)
    Less_than.insert(0,'Total',total_list)

    return Greater_than, Less_than
print('The Inventory Plotter: Chad Denbrock, Niowave Inc. August 2020\n\n')

while True :
    time_units = input('What are the time units given in the excel files? (e.g. Days or Years)\n')
    if time_units.lower() == 'years' :

        break
    elif time_units.lower() == 'days' :

        break
    else :
        print('The time units must be either days or years. Try again.\n')

#       Plotting fission products or actinides?

while True :
    kind_of_isotopes = input('What are you plotting? (Fission Products = FP or Actinides = An)\n')
    if kind_of_isotopes == 'Fission Products' or kind_of_isotopes == 'FP' :
        Title = 'Fission Products'
        fname = 'Fission-Products_UTA-2'
        break
    elif kind_of_isotopes.lower() == 'actinides' or kind_of_isotopes.lower() == 'an':
        Title = 'Actinides'
        fname = 'Actinides_UTA-2'
        break
    else :
        print('You must be plotting either Actinides or fission products, not both or neither.')

while True :
    Portion_of_core = int(input('What portion of the core would you like to analyze (1 or 2)? \n'\
                                '1: Whole Core (LEU + NU)\n'\
                                '2: Dispersable (Hottest 1 kgNU)\n'))
    if Portion_of_core == 1:
        Title = Title + ' in the Whole Core'
        fname = fname + '_whole_core'
        break
    elif Portion_of_core == 2:
        Title = Title + ' in the hottest 1 kgNU'
        fname = fname + '_hottest_1kgNU'
        break
    else :
        print('Type 1 or 2 as your selection for what part of the core you would like to analyze.\n')



The_Inventory = obtain_inventory()
plotting(The_Inventory)
time.sleep(600)
