################################################################################
# Chad Denbrock
# Editor: Austin Czyzewski
# Niowave Inc.
# Produced: 03.04.2020
# Last updated: 02.10.2021 (AC)
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
import glob
import xlsxwriter
# Time = time.time()
mpl.rcParams['savefig.dpi']  = 500
mpl.rcParams['font.size']    = 12
mpl.rcParams['mathtext.fontset'] = 'stix'
mpl.rcParams['font.family'] = 'STIXGeneral'


################################################################################
# Goal: Plot a fission product/actinide inventory from UTA-2 for a given
#           irradiation/decay cycle.
#
#
# Requirements: (Outdated)
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

def convert_to_1kgNU(NU, time_units) :

    Mass_per_rod_gU = 134.6
    Rods_per_1kgNU = 1000/Mass_per_rod_gU
    scaling = Rods_per_1kgNU/7


    fraction_FP_and_An_in_7rods_over_total_NU = 0.1187849
    fraction_U237_in_7rods_over_total_NU = 0.3376
    
    print(f'Assumptions made:'\
         f'Mass per rod: {Mass_per_rod_gU:.2f} grams'\
          f'Fraction of fission products and actinides in 7 rods over total NU: {fraction_FP_and_An_in_7rods_over_total_NU:.6f}'\
          f'Fraction of U-237 in 7 rods over total NU: {fraction_U237_in_7rods_over_total_NU:.4f}')

    fraction_FP_and_An_in_1kgNU_over_total_NU = fraction_FP_and_An_in_7rods_over_total_NU * scaling     # Linearly scaling fractions from 7 rods to ~ 7.429 rods in 1 kgNU
    fraction_U237_in_1kgNU_over_total_NU = fraction_U237_in_7rods_over_total_NU * scaling               # Linearly scaling fractions from 7 rods to ~ 7.429 rods in 1 kgNU

    Time = NU['Time ({})'.format(time_units)]
    NU = NU.drop(columns = 'Time ({})'.format(time_units))
    Updated_Inventory = NU*fraction_FP_and_An_in_1kgNU_over_total_NU

    if kind_of_isotopes.lower() == 'actinides' or kind_of_isotopes.lower() == 'an' :
        Updated_Inventory['u237'] = Updated_Inventory['u237']*fraction_U237_in_1kgNU_over_total_NU/fraction_FP_and_An_in_1kgNU_over_total_NU
#     Updated_Inventory = pd.DataFrame.sort_values(Updated_Inventory,Updated_Inventory.shape[0]-1,axis=1,ascending=False)
#     Updated_Inventory["Total_Activity"] = Updated_Inventory.iloc[:, 1:].sum(axis = 1)
#     print("AHH")
#     print(Updated_Inventory['Total_Activity'])
#     Updated_Inventory = Updated_Inventory.sort_values(Updated_Inventory.index[Updated_Inventory.shape[0]-1], axis = 1, ascending = False) #Added by Austin to replace the above commented out line
#     Updated_Inventory = Updated_Inventory.sort_values(Updated_Inventory.iloc[-1], axis = 0, ascending = False) #Added by Austin to replace the above commented out line
    Updated_Inventory = Updated_Inventory.sort_values(Updated_Inventory.iloc[-1].name, axis = 1, ascending = False)
    Updated_Inventory.insert(loc=0,column = f'Time ({time_units})',value = Time)

    print('Writing updated inventory to The_Hottest_1kgNU_Inventory.xlsx ...')
    print("This may take a few minutes ...\n")
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

def U_237_adder(NU,LEU, time_units) :

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
        'electron rate necessary to produce the fission power input into ORIGEN.')
    

    Total_core_reaction_rate = Electron_rate * Total_core_reaction_rate_per_e


    half_life_U_237 = 6.752*86400
    lambda_U_237 = np.log(2)/half_life_U_237
    
    print("-"*80 + "\nAssumptions made for U-237:")
    print(f'Fraction of U-237 in LEU: {fraction_U_237_in_LEU:.3f}\n'\
         f'Fraction of U-237 in NU: {fraction_U_237_in_NU:.3f}\n'\
         f'Total Core reaction rate per electron: {Total_core_reaction_rate_per_e:.3E}\n'\
         f'Electron Rate: {Electron_rate:.3E}\n'\
         f'The half life of U-237: {half_life_U_237:.3f}\n\n')
    
    try :
        test_activity = pd.Series.to_numpy(LEU['np239'],dtype = 'float')
    except :
        print('Np239 doesnt exist in the LEU spreadsheet. This probably means you incorrectly asked for what youre plotting.\n')
        exit()
    
    Time = pd.Series.to_numpy(NU['Time ({})'.format(time_units)],dtype = 'float')
#     print("Time ",len(Time))
#     print(NU['ac224'])
#     if time_units.lower() == 'years' :
#         dt_multiplier = 86400*365.25

#     elif time_units.lower() == 'days' :
#         dt_multiplier = 86400.0
    if time_units == 'years':
        dt_multiplier = 86400*365.25

    elif time_units == 'days':
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

#         if time_units == 'Years' and (Time[time_values] == 4.006471 or Time[time_values] ==4.004729):
        if time_units == 'years' and (Time[time_values] == 4.006471 or Time[time_values] ==4.004729):
            #print('\nin here\n')
            dU_237 = 0.0
        #print(Time[time_values],test_activity[time_values+1] - test_activity[time_values],dU_237,U_237[time_values],dt)

        U_237[time_values+1] = U_237[time_values] + dU_237
    U_237 = U_237 * lambda_U_237/3.7e10
#     print("U237 ",len(U_237))

    #plt.plot(Time,U_237)
    #plt.plot(Time,U_237*fraction_U_237_in_NU)
    #plt.plot(Time,U_237*fraction_U_237_in_LEU)
    #plt.show()

    if 'u237' not in NU.columns:
#         print('False ',len(U_237*fraction_U_237_in_NU))
        NU.insert(loc = 1,column = 'u237',value=U_237*fraction_U_237_in_NU)
    else :
#         print('True ',len(U_237*fraction_U_237_in_NU))
        U_237_Col = U_237*fraction_U_237_in_NU + NU.u237
        #print(U_237_Col)
#         NU = NU.add(pd.DataFrame(U_237*fraction_U_237_in_NU,columns = ['u237']),fill_value = 0)
        NU.u237 = U_237_Col

    if 'u237' not in LEU.columns:
#         print('False ',len(U_237*fraction_U_237_in_LEU))
        LEU.insert(loc = 1,column = 'u237',value=U_237*fraction_U_237_in_LEU)
    else :
#         print('True ',len(U_237*fraction_U_237_in_LEU))
        U_237_Col = U_237*fraction_U_237_in_LEU + LEU.u237
        #print(U_237_Col)
#         LEU = LEU.add(pd.DataFrame(U_237*fraction_U_237_in_LEU,columns = ['u237']),fill_value = 0)
        LEU.u237 = U_237_Col
    return NU,LEU


def plotting(The_Inventory):
    eff_list = ['kr85m','kr88','kr85','kr87','i131','i132','i133','i135','xe133','xe133m','xe135']
    Input = list()


    Splitting = True    # Choosing to always split the inventories for plotting purposes

#       Asking for what to plot (totals or specific isotopes)
    top_regex = '[Tt]op [0-9]+'
    while True :
        #try :
        Input.append(input('Name isotopes you wish to plot. You can also plot the total by typing \'Total\', the top x isotopes by activity at final time by typing \'Top <integer number of isotopes you want to see>\', or the effluents list by typing \'Effluents\'. (Hit enter after each one and type \'Stop\' to quit entering isotopes)\n').lower())
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
    print("\n")

    if 'total' in Input:
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
            print(f'\nThe max Total activity was {max:.3f} (Ci)')
            print(f'The final Total activity was {end:.3f} (Ci)')
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
            try:
                if vals != 'total'  :

                    plt.plot(Time,pd.Series.to_numpy(The_Inventory[vals]))
                    print(f'The max activity of {vals} was {pd.Series.to_numpy(The_Inventory[vals]).max():.3f} (Ci)')
                    print(f'The final activity of {vals} was {pd.Series.to_numpy(The_Inventory[vals])[-1]:.3f} (Ci)')
            except:
                print(f'\nPlotting {vals} wasnt found. Check if it is in the isotope list and try again.')
                continue
        plt.grid(which = 'both', axis = 'both')
        plt.legend(legend_list)
        plt.title(f'Activity of {Title}')
        plt.xlabel(time_units.capitalize())
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
                try:
                    if vals != 'total'  :
                        legend_list.append(vals)
                        plt.plot(Time,pd.Series.to_numpy(The_Inventory[vals]))
                except :
#                     print(f'\nPlotting {vals} wasnt found. Check if it is in the isotope list and try again.')
                    continue
            plt.grid(which = 'both', axis = 'both')
            plt.legend(legend_list)
            plt.title(f'Activity of {Title} (HL > 120 days)')
            plt.xlabel(time_units.capitalize())
            plt.ylabel('Activity (Ci)')
            plt.savefig(fname + '_Greaterthan.png',bbox_inches = 'tight')
            print(f'\nFigure {fname}_Greaterthan.png produced and saved.\n')
            plt.close()
        # -----------------------
        # Plotting HL <
        # -----------------------
        plt.plot(Time,Less_than['Total'])
        legend_list = ['Half Life < 120 d']
        for vals in Input :
            try:
                if vals != 'total'  :
                    plt.plot(Time,pd.Series.to_numpy(The_Inventory[vals]))
                    legend_list.append(vals)
            except :
#                 print(f'\nPlotting {vals} wasnt found. Check if it is in the isotope list and try again.')
                continue
        plt.grid(which = 'both', axis = 'both')
        plt.legend(legend_list)
        plt.title(f'Activity of {Title} (HL < 120 days)')
        plt.xlabel(time_units.capitalize())
        plt.ylabel('Activity (Ci)')
        plt.savefig(fname + '_Lessthan.png',bbox_inches = 'tight')
        print(f'\nFigure {fname}_Lessthan.png produced and saved.\n')
        plt.close()

    else :
        legend_list = list()
        for vals in Input :
            try :
                if vals != 'total'  :
                    plt.plot(Time,pd.Series.to_numpy(The_Inventory[vals]),linewidth=0.75)
                    print(f'The max activity of {vals} was {pd.Series.to_numpy(The_Inventory[vals]).max():.3f} (Ci)')
                    print(f'The final activity of {vals} was {pd.Series.to_numpy(The_Inventory[vals])[-1]:.3f} (Ci)')
                    legend_list.append(vals)
            except :
                print(f'\nPlotting {vals} wasnt found. Check if it is in the isotope list and try again.')
                continue

        if len(legend_list)>0 :
            plt.grid(which = 'both', axis = 'both')
            plt.legend(legend_list)
            plt.title(f'Activity of {Title}')
            plt.xlabel(time_units.capitalize())
            plt.ylabel('Activity (Ci)')
            plt.savefig(fname,bbox_inches = 'tight')
            print(f'\nFigure {fname} produced and saved.\n')
            plt.close()


def output_reader(filename, NOI, time_units = 'days'):
    """
    Austin Czyzewski's function to read values from ORIGEN .out files
    The workflow of this function goes something like this:
        - Import a file as one large string
        - Seperate string into Cases in .out file
        - Create a dataframe from the actual cases themselves
            - Get rid of the information we already know that surrounds the data
            - Split each case into its three parts: Light Elements, Fission Products, and Actinides
            - Use temporary dataframes that will constantly be overwritten to not destroy our PC
        - Append each case to an overall dataframe for each isotope source type (AC, LE, FP)
        - Add the index in as a Time column in the dataframe for plotting
        - Use pandas built in method to convert from strings to floats
    """
    ###################################
    ### Import the file as a string ###
    ###################################
    with open(filename, 'r') as file:
        first_file_string = file.read()#.replace('\n', '')
        file.close()
        
    first_file_string = re.sub(r'(\d{1}.\d{4})(-\d{3})', r'\1E\2', first_file_string)
#     #The above searches for "#.####-###" and replaces them with "#.####E-###"
    Case_Intervals = re.findall(r't\s*=\s*\[[^\]]*\]|time\s*=\s*\[[^\]]*\]', first_file_string)
#     #This regex searches for the times that each case runs for. The amount gathered here will be used later
        #To verify all cases are present in the output files.
    
    Integer_Interval_List = list()
    Case_Start_List = list()
    Case_End_List = list()
    for Interval in Case_Intervals:
        if 'i' in Interval:

            Interval_String = re.split('\[|i\s+',Interval) #This detects the number before i, the amount of timesteps in the interval
            Integer_Interval_List.append(int(Interval_String[1]))
            Case_times = re.split('\s{1,}|\]',Interval_String[2])

            Case_Start_List.append(float(Case_times[0])) #this is the start time. Most often zero
            Case_End_List.append(float(Case_times[1])) #End time. The useful bit



    print("{} Cases in {}".format(len(Integer_Interval_List), filename))
    
    
    ###################################
    # Split them using key phrase, "in curies for case {decay/irrad}"
    ###################################
    groups = re.split(r'in\ curies\ for\ case\ \Sirrad\S|in\ curies\ for\ case\ \Sdecay\S', \
                      first_file_string, flags=re.MULTILINE)
    
    groups = groups[1:]
    # The first group is all of the junk before the first actual table. Just dump it
    if len(Integer_Interval_List) != len(groups):
        print("#"*120 + "\nWARNING: \nDetected number of case time intervals does not match the amount of tables found."\
              "\nPlease ensure the proper print statement is present in all cases in the input file."\
             "\nIf all cases are present, one case may not have printed properly, please rerun the ORIGEN input file and check again.\n" + "#"*120)

    all_times = list()
    header_unit_list = list()
    Start_End_Times = list()

    All_LE = pd.Series(dtype = object)
    All_AC = pd.Series(dtype = object)
    All_FP = pd.Series(dtype = object)
    
    print("Creating DataFrames")
    for number, case in enumerate(groups):
        print("Case ({}/{})\r".format(number+1,len(groups)), end = '')
        
        # Handle the last table from each split section
        #################################
        data_from_case = re.sub(r'\s{2,}(?=\d+)',"  ", case)
        data_from_case = re.sub(r'^[.]\s*|^\s{2}',"", data_from_case, flags = re.MULTILINE)
        data_from_case = re.split(r'he-3', data_from_case)
        
        header_unit_string = re.findall('\d{1,}[a-z]{1,2}\s{2}',data_from_case[0], flags = re.MULTILINE)
        header_unit = re.findall('[a-z]{2}|[a-z]{1}', header_unit_string[1])[0]
        header_unit_list.append(header_unit)

        header_handling = re.split(r"{}(.+)".format(header_unit),data_from_case[0], flags = re.MULTILINE)

        times = header_handling[1].split('{}'.format(header_unit))
        
        start_time = times[1] 
        times.insert(1,start_time)
        Start_End_Times.append((float(times[0]),float(times[-2])))
        
        cut_number = 0
        if (number == 0):# or (number == len(groups)-1):
            cut_number = -1
        else:
            cut_number = -2
            
        if time_units == 'years':
            times = np.array(times[:cut_number]).astype(float)/365.25 #The first and last objects are empty strings
        else:
            times = np.array(times[:cut_number]).astype(float)
            
        all_times.append(times)
        
        temp_data = header_handling[2].split('\n') 
        
        #t_df is short for temporary DataFrame. I abbreviate to make it a little bit easier to read
        
        t_df = pd.DataFrame(temp_data)
        t_df = t_df[0].str.split(" * ", expand = True)
        t_df = t_df.transpose() # We will be transposing all of our dataframes.
                    # We want to build on times Not on isotopes.
        header = t_df.iloc[0] #The first row in this dataframe is the isotope names we want
        for num, head in enumerate(header):
            if num > 0:
                header[num] = re.sub(r'\-', "", head) #Get rid of the dash in the isotope names

        ##################################################################################################################
        
        temp_data = data_from_case[1].split('\n')
        t_df = pd.DataFrame(temp_data)
        t_df = t_df[0].str.split(" * ", expand = True)
#         t_df.iloc[0] = t_df.iloc[0].shift(1)
        t_df = t_df.transpose()
        header = t_df.iloc[0]
        for num, head in enumerate(header):
            if num > 0:
                header[num] = re.sub(r'\-', "", head)
            
        header = pd.concat([pd.Series(["he3"]),header[1:]]) #Adding he3 as the name back to its respective isotope
        
        #Here we create a mask in order to name columns and index easier (maybe not easier but I like it this way)
#         df_naming_mask = t_df[2:]
        if (number == 0):# or (number == len(groups) - 1):
#             print("-"*80)
            df_naming_mask = t_df.iloc[1:]
        else:
            df_naming_mask = t_df[2:] #Get rid of those pesky empty lines
            
        df_naming_mask.columns = header #Name the columns by their isotope partner's name
        LE_df_final = df_naming_mask.set_index(times).iloc[1:]


        ##################################################################################################################
        #See above for what we're doing here
        temp_data = data_from_case[2].split('\n')
        t_df = pd.DataFrame(temp_data)
        t_df = t_df[0].str.split(" * ", expand = True)
        t_df = t_df.transpose()
        header = t_df.iloc[0]
        for num, head in enumerate(header):
            if num > 0:
                header[num] = re.sub(r'\-', "", head)
                
                
        header = pd.concat([pd.Series(["he3"]),header[1:]])
        if (number == 0):# or (number == len(groups) - 1):
            df_naming_mask = t_df.iloc[1:]
        else:
            df_naming_mask = t_df[2:] #Get rid of those pesky empty lines
        df_naming_mask.columns = header
        AC_df_final = df_naming_mask.set_index(times).iloc[1:]
#         print(times)
        ##################################################################################################################
        # Handle the last table from each split section
        FP_handling = re.split(r"\-{6,}",data_from_case[3]) #Gets rid of everything after the actual .out file
        
        #Back to what we've seen before (if you've been paying attention ;)
        temp_data = FP_handling[0].split('\n')
        t_df = pd.DataFrame(temp_data)
        t_df = t_df[0].str.split(" * ", expand = True)
        t_df.iloc[0] = t_df.iloc[0].shift(1)
        t_df = t_df.transpose()
        header = t_df.iloc[0]
        for num, head in enumerate(header):
            if num > 0:
                header[num] = re.sub(r'\-', "", head)
        header = pd.concat([pd.Series(["he3"]),header[1:]])
        if (number == 0):# or (number == len(groups) - 1):
            df_naming_mask = t_df.iloc[1:]
        else:
            df_naming_mask = t_df[2:] #Get rid of those pesky empty lines
        df_naming_mask.columns = header
        
        
        FP_df_final = df_naming_mask.set_index(times).iloc[1:] #This is very close to doing what I want
        
        ##################################################################################################################
        ###################################
        # Append the new data to the big dataframe with each data type
        ###################################
        All_LE = pd.concat([All_LE,LE_df_final],sort = True)
        All_AC = pd.concat([All_AC,AC_df_final],sort = True)
        All_FP = pd.concat([All_FP,FP_df_final],sort = True)
        
        if (len(All_LE) == 0) or (len(All_AC) == 0) or (len(All_FP) == 0):
            print("#"*120 + "\nWARNING: \nDetected length of tables is 0.\nThis problem may occur if there are no print statements in the input file."\
                  "\nPlease ensure the proper print statement is present in all cases in the input file."\
                 "\nThe format for the print statement is as follows and should precede the save statement in each case:\n"\
                  "print{\n        nuc{ units=CURIES }\n        cutoffs[ ALL = 0 ]\n    }\n" + "#"*120)
            input("Please press enter to acknowledge this statement and close the script.")
            exit()

    print("All cases stored in DataFrames as strings")
    

    global Times_list
    Times_list = list()   #[Start_End_Times[0][0]]
    #print(Start_End_Times)

    Starts = 0
    Ends = 0
    for Interval, Start, End in zip(Integer_Interval_List, Case_Start_List,Case_End_List):
        Ends += Start + End
        Calculated_Times = np.linspace(Starts,Ends,2+Interval)[:-1]
        Starts += End

        for time in Calculated_Times:
            Times_list.append(time)

    Times_list.append(Ends)
    if time_units == 'years' :
        for num, time in enumerate(Times_list):
            Times_list[num] = time/365.25
    
    #Here, NOI is to identify the Type of isotope of interest
    if NOI == 'FP':
        All_FP = All_FP.drop([0,''], axis = 1)
        All_FP.index = pd.Series(Times_list)#, downcast="float")
        print("Converting strings to floats in DataFrame. This could take some time")
        
        for column in All_FP:
            All_FP[All_FP[column].name] = pd.to_numeric(All_FP[All_FP[column].name])
        
        print("String conversion complete\n")
        
        All_FP.insert(loc = 0, column = 'Time ({})'.format(time_units),value = Times_list)
        
        return All_FP
    
    
    if NOI == 'AC':
        All_AC = All_AC.drop([0,''], axis = 1)
        All_AC.index = pd.Series(Times_list)#, downcast="float")
        print("Converting strings to floats in DataFrame. This could take some time")
        
        for column in All_AC:
        #Converting strings to floats in DataFrame
            All_AC[All_AC[column].name] = pd.to_numeric(All_AC[All_AC[column].name])
            
        print("String conversion complete\n")
        
        All_AC.insert(loc = 0, column = 'Time ({})'.format(time_units),value = Times_list)
        
        return All_AC
    

def dataframe_merger(List_of_DataFrames, time_units):
    """
    Here List_of_DataFrames, List_of_DataFrames[0] is intended to be LEU and 
        List_of_DataFrames[1] is intended to be NU
    """
#     print("Here are the time units: {}".format(time_units))
    if kind_of_isotopes.lower() == 'actinides' or kind_of_isotopes.lower() == 'an' :
            print('Computing U-237 activity as a function of time and adding it to the inventories.\n')
            List_of_DataFrames[1],List_of_DataFrames[0] = U_237_adder(List_of_DataFrames[1],List_of_DataFrames[0], time_units = time_units)
            
    if Portion_of_core == 1:

        Reset_Index_LEU = List_of_DataFrames[0].drop(columns = ["Time ({})".format(time_units)])
        Reset_Index_LEU["Total_Activity"] = Reset_Index_LEU.iloc[:, 1:].sum(axis=1)
        Reset_Index_LEU = Reset_Index_LEU.sort_values(by = Reset_Index_LEU.iloc[-1].name, axis = 1, ascending = False)



        Reset_Index_NU = List_of_DataFrames[1].drop(columns = ["Time ({})".format(time_units)])
        Reset_Index_NU["Total_Activity"] = Reset_Index_NU.iloc[:, 1:].sum(axis=1)
        Reset_Index_NU = Reset_Index_NU.sort_values(by = Reset_Index_NU.iloc[-1].name, axis = 1, ascending = False)



        Reset_Index_LEU = Reset_Index_LEU.reset_index(drop = True)
        Reset_Index_NU = Reset_Index_NU.reset_index(drop = True)

        Total_Activity = Reset_Index_LEU.add(Reset_Index_NU, fill_value = 0)

        Total_Activity["Total_Activity"] = Total_Activity.iloc[:, 1:].sum(axis=1)
        Total_Activity = Total_Activity.sort_values(Total_Activity.iloc[-1].name, axis = 1, ascending = False)
    
        Total_Activity.index = pd.Series(Times_list)
        Reset_Index_LEU.index = pd.Series(Times_list)
        Reset_Index_NU.index = pd.Series(Times_list)
        Total_Activity.insert(loc = 0, column = 'Time ({})'.format(time_units),value = Times_list)
        Reset_Index_LEU.insert(loc = 0, column = 'Time ({})'.format(time_units),value = Times_list)
        Reset_Index_NU.insert(loc = 0, column = 'Time ({})'.format(time_units),value = Times_list)
        
        time1 = time.time()
        print("Writing data to excel file...")
        print("Hang around, this may take a few minutes...")

        attempts_at_saving = 0
        while True:

            try:
                workbook = xlsxwriter.Workbook("Total_Core.xlsx")
                Total = workbook.add_worksheet("Total")
                LEU = workbook.add_worksheet("LEU")
                NU = workbook.add_worksheet("NU")

                worksheets = [Total, LEU, NU]
                dfs = [Total_Activity, Reset_Index_LEU, Reset_Index_NU]
                
                for iterative_value in range(3):
                    temporary_data_list = [list(dfs[iterative_value].columns)] + dfs[iterative_value].values.tolist()
                    for x, i in enumerate(temporary_data_list):
                        for y, _ in enumerate(i):
                            worksheets[iterative_value].write(x,y,temporary_data_list[x][y])
                    worksheets[iterative_value].freeze_panes(1,1)

                workbook.close()
                break
                
            except:
                print("Error Saving Total_Core.xlsx, please ensure all open copies are closed. Trying again in 15 seconds")
                attempts_at_saving += 1
                if attempts_at_saving >= 5:
                    break
                time.sleep(15)

        print("Total_Core.xlsx saved")
    if Portion_of_core == 2:
        Total_Activity = convert_to_1kgNU(List_of_DataFrames[1], time_units = time_units)
    return Total_Activity  
            
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
print('The Inventory Plotter: Author: Chad Denbrock, Co-Author: Austin Czyzewski, Niowave Inc. August 2020; revised February 2021\n\n')
print(f'This script makes the following assumptions in regard to how the ORIGEN simulations are run:'\
     f'The units in the input file are in DAYS. Other units will either crash the program or output invalid data.\n'\
     f'There is a print statement for every case ran in the file. In this print statement, the units must be specified to '\
     f'be CURIES and the CUTOFFS for ALL element tables must be set to 0.\n'\
      f'The output files are in the directory that this Python script is run. There must be one LEU and one NU output file.')

while True :
    time_units = input('What time units do you want the excel and plots to have? (e.g. Days or Years)\n')
    time_units = time_units.lower()
#    if time_units.lower() == 'years' :
    if time_units == 'years':
        break
#    elif time_units.lower() == 'days' :
    elif time_units == 'days':
        break
    else :
        print('The time units must be either days or years. Try again.\n')

#       Plotting fission products or actinides?
while True :
    kind_of_isotopes = input('What are you plotting? (Fission Products = FP or Actinides = An)\n')
    if kind_of_isotopes.lower() == 'fission products' or kind_of_isotopes.lower() == 'fp' :
        Title = 'Fission Products'
        fname = 'Fission-Products_UTA-2'
        plotting_type = "FP"
        break
    elif kind_of_isotopes.lower() == 'actinides' or kind_of_isotopes.lower() == 'an':
        Title = 'Actinides'
        fname = 'Actinides_UTA-2'
        plotting_type = "AC"
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

files = glob.glob("*.out")
LEU_files = glob.glob("*LEU*.out")
NU_files = glob.glob("*NU*.out")
#print(LEU_files, NU_files)
print("#"*60)
print("---LEU---")
print("#"*60)
attempts = 0
while True:
    try:
        if len(LEU_files) == 1:
            LEU_file = LEU_files[0]
        else:
            print("Please select which output file to analyze (LEU)")
            for number,file in enumerate(LEU_files):
                print("{}: {}\n".format(number, file))
            file_number_LEU = int(input(""))
            LEU_file = LEU_files[file_number_LEU]
    #         print("Loading {}".format(files[file_number_LEU]))
        print("{} Selected".format(LEU_file))
        break
    except:
        print("Please enter an integer corresponding to the filename above")
        attempts += 1
        if attempts > 5:
            exit()
        continue


print("#"*60)
print("---NU---")
print("#"*60)
while True:
    try:
        if len(NU_files) == 1:
            NU_file = NU_files[0]
        else:
            print("Please select which output file to analyze (NU)")
            for number,file in enumerate(NU_files):
                print("{}: {}\n".format(number, file))
            file_number_NU = int(input(""))
            NU_file = NU_files[file_number_NU]
    #         print("Loading {}".format(files[file_number_LEU]))
        print("{} Selected\n\n".format(NU_file))
        break
    except:
        print("Please enter an integer corresponding to the filename above")
        continue
        
#Run it
###############################################################################
LEU = output_reader(LEU_file, plotting_type, time_units = time_units.lower())
NU = output_reader(NU_file, plotting_type, time_units = time_units.lower())
dfs = dataframe_merger([LEU, NU], time_units = time_units.lower())
The_Inventory = dfs

while True:
    try:
        plotting(The_Inventory)
    except:
        print("Error raised in plotting, please make sure plots are closed")
    end = input("Did this produce the plots that you desired? (Y/N)  ")
    if (end.lower() == "y") or (end.lower() == "yes"):
        break
    else:
        print("\nPlease try again\n")
        continue
        
print("\n" + "-"*60 + "\nInventory Plotter Complete\n" + "-"*60)
input("Please Press 'Enter' to close this script")
