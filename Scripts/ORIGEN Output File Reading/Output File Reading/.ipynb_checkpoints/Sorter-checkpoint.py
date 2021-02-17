import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns
sns.set()
import time
from datetime import datetime
import re
import os
import glob


st = time.time()

files = glob.glob("*.out")
print(files)

with open(files[1], 'r') as file:
    first_file_string = file.read()#.replace('\n', '')
    file.close()
first_file_string = re.sub(r'(\d{1}.\d{4})(-\d{3})', r'\1E\2', first_file_string)
#The above searches for "#.####-###" and replaces them with "#.####E-###"
groups = re.split(r'in\ curies\ for\ case\ \Sirrad\S|in\ curies\ for\ case\ \Sdecay\S', \
                  first_file_string, flags=re.MULTILINE)
# groups = re.split(r'(?<=in\ curies\ for\ case)\w+', first_file_string, flags=re.MULTILINE)
groups = groups[1:]



all_times = list()

All_LE = pd.Series()
All_AC = pd.Series()
All_FP = pd.Series()
for case in groups:    #####################################################################
    # Handle the last table from each split section
    #################################
    tester = re.sub(r'\s{2,}(?=\d+)',"  ", case)
    tester = re.sub(r'^[.]\s*|^\s{2}',"", tester, flags = re.MULTILINE)
    # tester = re.sub(r'\s{2}',", ", tester)
    # print(tester)
    # tester = re.sub(r'^.+\)',"", tester, flags = re.MULTILINE)
    # tester = re.split("\n",tester)
    # print(tester)
    tester = re.split(r'he-3', tester)
    header_handling = re.split(r"d(.+)",tester[0], flags = re.MULTILINE) #Splitting the first 
                                                                #portion of list by the the first occuring d
    #################################
    times = header_handling[1].split('d') #Splitting string to list for numpy to use
#     print(times)
    start_time = times[1] #We have two cases of the first time. The index list must be the right length, so we append.
                        #This is an artifact of using the first 'd' to split our header
    times.insert(1,start_time)
    times = np.array(times[1:-1]).astype(float) #The first and last objects are empty strings. Numpy no likey
    all_times.append(times)
    first_table = header_handling[2].split('\n') 
    df = pd.DataFrame(first_table)
    df = df[0].str.split(" * ", expand = True)
    df.iloc[0] = df.iloc[0].shift(1)
    df = df.transpose()
    header = df.iloc[0]
    for number, head in enumerate(header):
        if number > 0:
            header[number] = re.sub(r'\-', "", head)
    new_df = df[2:]
    new_df.columns = header
    new_df = new_df.set_index(times)
    new_df
    print(new_df.shape)

    #####################################################################
    first_table = tester[1].split('\n')
    df = pd.DataFrame(first_table)
    df = df[0].str.split(" * ", expand = True)
    df.iloc[0] = df.iloc[0].shift(1)
    df = df.transpose()
    header = df.iloc[0]
    for number, head in enumerate(header):
        if number > 0:
            header[number] = re.sub(r'\-', "", head)
    header = pd.concat([pd.Series(["LE"]),header[1:]])
    new_df = df[2:]
    new_df.columns = header
    new_df = new_df.set_index(times)
    LE_df_final = new_df
    print("LE (light elements) shape",new_df.shape)

    #####################################################################
    save_1 = new_df
    first_table = tester[2].split('\n')
    df = pd.DataFrame(first_table)
    df = df[0].str.split(" * ", expand = True)
    df.iloc[0] = df.iloc[0].shift(1)
    df = df.transpose()
    header = df.iloc[0]
    for number, head in enumerate(header):
        if number > 0:
            header[number] = re.sub(r'\-', "", head)
    header = pd.concat([pd.Series(["AC"]),header[1:]])
    new_df = df[2:]
    new_df.columns = header
    new_df = new_df.set_index(times)
    AC_df_final = new_df
    print("AC (actinides) shape",new_df.shape)

    #####################################################################
    # Handle the last table from each split section
    #################################
    FP_handling = re.split(r"\-{6,}",tester[3])
    #################################
    first_table = FP_handling[0].split('\n')
    df = pd.DataFrame(first_table)
    df = df[0].str.split(" * ", expand = True)
    df.iloc[0] = df.iloc[0].shift(1)
    df = df.transpose()
    header = df.iloc[0]
    for number, head in enumerate(header):
        if number > 0:
            header[number] = re.sub(r'\-', "", head)
    header = pd.concat([pd.Series(["FP"]),header[1:]])
    new_df = df[2:]
    new_df.columns = header
    new_df = new_df.set_index(times)
    FP_df_final = new_df
    print("FP (Fission Products) shape",new_df.shape)
    
    All_LE = pd.concat([All_LE,LE_df_final],sort = True)
    All_AC = pd.concat([All_AC,AC_df_final],sort = True)
    All_FP = pd.concat([All_FP,FP_df_final],sort = True)
print(all_times)

print(time.time() - st)

All_FP.index = pd.to_numeric(All_FP.index, downcast="float")
print('Here I am')
for column in All_AC:
    name = All_AC[column].name
#     print(name)
    All_AC[All_AC[column].name] = pd.to_numeric(All_AC[All_AC[column].name], downcast="float")
for column in All_FP:
    name = All_FP[column].name
#     print(name)
    All_FP[All_FP[column].name] = pd.to_numeric(All_FP[All_FP[column].name], downcast="float")
for column in All_LE:
    name = All_LE[column].name
#     print(name)
    All_LE[All_LE[column].name] = pd.to_numeric(All_LE[All_LE[column].name], downcast="float")

All_LE['Unnamed: 0'] = All_LE.index
All_FP['Unnamed: 0'] = All_FP.index
All_AC['Unnamed: 0'] = All_AC.index
    
print(All_LE.head(5))
NU = All_AC
LEU = All_FP
    
# plt.plot(All_FP.index,All_FP['mo-99'])
# plt.xlabel("Time (Days)")
# plt.ylabel("Activity, mo-99 (Cu)")
# plt.show()