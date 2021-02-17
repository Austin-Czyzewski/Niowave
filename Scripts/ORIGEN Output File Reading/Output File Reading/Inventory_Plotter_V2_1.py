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
import glob
Time = time.time()
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

def convert_to_1kgNU(NU, time_units) :

    Mass_per_rod_gU = 134.6
    Rods_per_1kgNU = 1000/Mass_per_rod_gU
    scaling = Rods_per_1kgNU/7


    fraction_FP_and_An_in_7rods_over_total_NU = 0.1187849
    fraction_U237_in_7rods_over_total_NU = 0.3376

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
        'electron rate necessary to produce the fission power input into ORIGEN.\n\n')

    Total_core_reaction_rate = Electron_rate * Total_core_reaction_rate_per_e


    half_life_U_237 = 6.752*86400
    lambda_U_237 = np.log(2)/half_life_U_237
    try :
        test_activity = pd.Series.to_numpy(LEU['np239'],dtype = 'float')
    except :
        print('Np239 doesnt exist in the LEU spreadsheet. This probably means you incorrectly asked for what youre plotting.\n')
        exit()
    Time = pd.Series.to_numpy(NU['Time ({})'.format(time_units)],dtype = 'float')

#     if time_units.lower() == 'years' :
#         dt_multiplier = 86400*365.25

#     elif time_units.lower() == 'days' :
#         dt_multiplier = 86400.0
    if time_units == 'years' :
        dt_multiplier = 86400*365.25

    elif time_units == 'days' :
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
    
    Integer_Interval_List = list()
    Case_Start_List = list()
    Case_End_List = list()
    for Interval in Case_Intervals:
        if 'i' in Interval:
            Interval_String = re.split('\[|i\s+',Interval)
            Integer_Interval_List.append(int(Interval_String[1]))
            Case_times = re.split('\s{1,}|\]',Interval_String[2])
            #print(Case_times)
            Case_Start_List.append(float(Case_times[0]))
            Case_End_List.append(float(Case_times[1]))
    print(Case_Start_List)
    print(Case_End_List)

    print("{} Cases".format(len(Integer_Interval_List)))
    ###################################
    # Split them using key phrase, "in curies for case {decay/irrad}"
    ###################################
    groups = re.split(r'in\ curies\ for\ case\ \Sirrad\S|in\ curies\ for\ case\ \Sdecay\S', \
                      first_file_string, flags=re.MULTILINE)
    
    groups = groups[1:]
    # The first group is all of the junk before the first actual table.

    all_times = list()
    
    header_unit_list = list()

    Start_End_Times = list()

    All_LE = pd.Series()
    All_AC = pd.Series()
    All_FP = pd.Series()
    
    print("Creating DataFrames")
    for number, case in enumerate(groups):
        #Used for debugging
#         if number > 5:
#             break
        print("Case ({}/{})\r".format(number+1,len(groups)), end = '')
        
        # Handle the last table from each split section
        #################################
        
        data_from_case = re.sub(r'\s{2,}(?=\d+)',"  ", case)
        data_from_case = re.sub(r'^[.]\s*|^\s{2}',"", data_from_case, flags = re.MULTILINE)
        data_from_case = re.split(r'he-3', data_from_case)
        
        header_unit_string = re.findall('\d{1,}[a-z]{1,2}\s{2}',data_from_case[0], flags = re.MULTILINE)
        header_unit = re.findall('[a-z]{2}|[a-z]{1}', header_unit_string[1])[0]
    #     print(header_unit)
        header_unit_list.append(header_unit)

        header_handling = re.split(r"{}(.+)".format(header_unit),data_from_case[0], flags = re.MULTILINE)

        times = header_handling[1].split('{}'.format(header_unit))
    #     print(times)
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
#         t_df.iloc[0] = t_df.iloc[0].shift(1) #This gets rid of the first column. 
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
#         t_df.iloc[0] = t_df.iloc[0].shift(1)
        t_df = t_df.transpose()
        header = t_df.iloc[0]
        for num, head in enumerate(header):
            if num > 0:
                header[num] = re.sub(r'\-', "", head)
                
                
        header = pd.concat([pd.Series(["he3"]),header[1:]])
#         df_naming_mask = t_df[2:]
        if (number == 0):# or (number == len(groups) - 1):
#             print("-"*80)
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
#         df_naming_mask = t_df[2:]
        if (number == 0):# or (number == len(groups) - 1):
#             print("-"*80)
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

    print("All cases stored in DataFrames as strings")

    #We ignore LE for our purposes. But you can see there is some clear repitition here.
    
    #Drop empty column
    All_FP = All_FP.drop([0,''], axis = 1)
    All_AC = All_AC.drop([0,''], axis = 1)
    
    # DEBUGGING drop the last row to curb duplicates.
#     All_FP.drop(All_FP.tail(1).index,inplace=True) # drop last n rows
#     All_AC.drop(All_AC.tail(1).index,inplace=True) # drop last n rows
    
    #Convert the index from strings to floats
#     print(Start_End_Times[0][0])
    Times_list = list()   #[Start_End_Times[0][0]]
    print(Start_End_Times)
    #for Times, Interval in zip(Start_End_Times, Integer_Interval_List):
    Starts = 0
    Ends = 0
    for Interval, Start, End in zip(Integer_Interval_List, Case_Start_List,Case_End_List):
        Ends += Start + End
        Calculated_Times = np.linspace(Starts,Ends,2+Interval)[:-1]
        Starts += End
        #Calculated_Times = np.linspace(Times[0],Times[1],2+Interval)[:-1]
        for time in Calculated_Times:
            Times_list.append(time)
    #Times_list.append(Times[1]) #Add the second item from the last time.
    Times_list.append(Ends)
    if time_units == 'years' :
        for num, time in enumerate(Times_list):
            Times_list[num] = time/365.25
#     All_FP.index = pd.to_numeric(All_FP.index)#, downcast="float")
#     All_AC.index = pd.to_numeric(All_AC.index)#, downcast="float")
#     print(All_FP.index)
#     for item in All_FP.index:
#         print(item)
#     print(Times_list)
    All_FP.index = pd.Series(Times_list)#, downcast="float")
    All_AC.index = pd.Series(Times_list)#, downcast="float")

    print("Converting strings to floats in DataFrame")
    
    for column in All_AC:
        #Converting strings to floats in DataFrame
        All_AC[All_AC[column].name] = pd.to_numeric(All_AC[All_AC[column].name])
        
    print("Actinides complete")
    
    for column in All_FP:
        All_FP[All_FP[column].name] = pd.to_numeric(All_FP[All_FP[column].name])
        
    print("Fission Products complete")

    #Convert the index to a new column named Time ({Days/Years})
#     All_FP.insert(loc = 0, column = 'Time ({})'.format(time_units),value = All_FP.index)
#     All_AC.insert(loc = 0, column = 'Time ({})'.format(time_units),value = All_AC.index)
    All_FP.insert(loc = 0, column = 'Time ({})'.format(time_units),value = Times_list)
    All_AC.insert(loc = 0, column = 'Time ({})'.format(time_units),value = Times_list)
    
    #Here, NOI is to identify the Type of isotope of interest
    if NOI == 'FP':
        return All_FP
    if NOI == 'AC':
        return All_AC

def dataframe_merger(List_of_DataFrames, time_units):
    """
    Here List_of_DataFrames, List_of_DataFrames[0] is intended to be LEU and 
        List_of_DataFrames[1] is intended to be NU
    """
#     print("Here are the time units: {}".format(time_units))
    if Portion_of_core == 1:
        List_of_DataFrames[0] = List_of_DataFrames[0].drop(columns = ["Time ({})".format(time_units)])
        List_of_DataFrames[0]["Total_Activity"] = List_of_DataFrames[0].iloc[:, 1:].sum(axis=1)
        List_of_DataFrames[0] = List_of_DataFrames[0].sort_values(by = List_of_DataFrames[0].iloc[-1].name, axis = 1, ascending = False)
#         print(List_of_DataFrames[1].head())
        List_of_DataFrames[1]["Total_Activity"] = List_of_DataFrames[1].iloc[:, 1:].sum(axis=1)
        List_of_DataFrames[1] = List_of_DataFrames[1].sort_values(List_of_DataFrames[1].iloc[-1].name, axis = 1, ascending = False)
#         print(Total_Activity.head())
        Total_Activity = List_of_DataFrames[0].add(List_of_DataFrames[1], fill_value = 0)
        Total_Activity["Total_Activity"] = Total_Activity.iloc[:, 1:].sum(axis=1)
        Total_Activity = Total_Activity.sort_values(Total_Activity.iloc[-1].name, axis = 1, ascending = False)
#         print(Total_Activity.head())
        time1 = time.time()
        print("Writing data to excel file...")
        print("Hang around, this may take a few minutes...")
        with pd.ExcelWriter('Total_Core.xlsx') as writer:  
            Total_Activity.to_excel(writer, sheet_name='Total')
            List_of_DataFrames[0].to_excel(writer, sheet_name='LEU')
            List_of_DataFrames[1].to_excel(writer, sheet_name='NU')
        print("Total_Core.xlsx saved")
#         print('Wow, that took {:.1f} seconds'.format(time.time()-time1))
    if Portion_of_core == 2:
        Total_Activity = convert_to_1kgNU(List_of_DataFrames[1], time_units = time_units)
    return Total_Activity  
            

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
        print(Time)
        Total_core = Total_core.drop(columns = ['Unnamed: 0'])
        # Sorting the dataframe by highest endpoint activity
        Total_core = pd.DataFrame.sort_values(Total_core,Total_core.shape[0]-1,axis = 1,ascending = False)
        Time_column_name = f'Time ({time_units})'
        Total_core.insert(loc=0,column = Time_column_name,value= Time)
        # Writing the total core excel spreadsheet
        print(f'Writing total inventory to Total_core.xlsx\n')
        Total_core.reset_index(drop=True, inplace=True)
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
print("#"*60)
print("---LEU---")
print("#"*60)
while True:
    try:
        print("Please select which output file to analyze (LEU)")
        for number,file in enumerate(files):
            print("{}: {}\n".format(number, file))
        file_number_LEU = int(input(""))
        print("Loading {}".format(files[file_number_LEU]))
        break
    except:
        print("Please enter an integer corresponding to the filename above")
        continue

# The_Inventory = obtain_inventory()


print("#"*60)
print("---NU---")
print("#"*60)
while True:
    try:
        print("Please select which output file to analyze (NU)")
        for number,file in enumerate(files):
            print("{}: {}\n".format(number, file))
        file_number_NU = int(input(""))
        print("Loading {}".format(files[file_number_NU]))
        break
    except:
        print("Please enter an integer corresponding to the filename above")
        continue
        
#Run it
###############################################################################
LEU = output_reader(files[file_number_LEU], plotting_type, time_units = time_units.lower())
NU = output_reader(files[file_number_NU], plotting_type, time_units = time_units.lower())
dfs = dataframe_merger([LEU, NU], time_units = time_units.lower())
The_Inventory = dfs
plotting(The_Inventory)
print("Inventory Plotter Complete")
# time.sleep(600)
print(Time-time.time())
