import os, string
import re
import folderstats
import pandas as pd
import time
from datetime import datetime

def progress_bar(current, total, number_of_bars = 25):
    current = current + 1
    print("[{}{}] ({}%)\r".format("#"*int(round(current/total,10)*number_of_bars),\
                            " "*(-1 + number_of_bars - int(round(current/total,10)*number_of_bars)), \
                                  round(100*current/total, 2)), end = '')
    
def icacls_runner(path):
    return os.popen('icacls "{}" /C'.format(path))

def icacls_interpreter(icacls_output):
    temp_list = []
    for line in icacls_output:
        if ":" in line:
            line = re.sub('\s{3,}','',line)
            temp_list.append(re.split(':',line))
    return temp_list

def permissions_interpreter(permissions):
    try:
        important_info = re.findall('[(][\w|,]+[)]', permissions)[-1]
        important_info = re.sub('\(|\)','',important_info)    
    except:
        return permissions
    if important_info == 'D':
        return 'Delete Access'
    elif important_info == 'F':
        return 'Full Access'
    elif important_info == 'N':
        return 'No Access'
    elif important_info == 'M':
        return 'Modify Access'
    elif important_info == 'RX':
        return 'Read and Execute Access'
    elif important_info == 'R':
        return 'Read-only Access'
    elif important_info == 'W':
        return 'Write-only Access'
    ############################################
    ##### Outside of standard permissions groups
    ############################################
    if ',' in important_info:
        perms = re.split(',', important_info)
    total_perms = ''
    print(perms)
    for string in perms:
        print(string)
        if "REA" in string:
            total_perms += "Read extended attributes//"
            continue
        elif "WEA" in string:
            total_perms += "Write extended attributes//"
            continue
        elif "WDAC" in string:
            total_perms += "Write DAC//"
            continue
        elif "RC" in string:
            total_perms += "Read Control//"
            continue
        elif "WO" in string:
            total_perms += "Write Owner//"
            continue
        elif "DE" in string:
            total_perms += "Delete//"
            continue
        elif "AS" in string:
            total_perms += "Access System Security//"
            continue
        elif "MA" in string:
            total_perms += "Maximum Allowed//"
            continue
        elif "GR" in string:
            total_perms += "Generic Read//"
            continue
        elif "GW" in string:
            total_perms += "Generic Write//"
            continue
        elif "GE" in string:
            total_perms += "Generic Execute//"
            continue
        elif "GA" in string:
            total_perms += "Generic All//"
            continue
        elif "RD" in string:
            total_perms += "Read Data + List Directory//"
            continue
        elif "WD" in string:
            total_perms += "Write Data + Add File//"
            continue
        elif "AD" in string:
            total_perms += "Append Data + Add subdirectory//"
            continue
        elif "DC" in string:
            total_perms += "Delete Child//"
            continue
        elif "RA" in string:
            total_perms += "Read Attributes//"
            continue
        elif "WA" in string:
            total_perms += "Write Attributes//"
            continue
        elif "S" in string:
            total_perms += "Synchronize//"
            continue
        elif "X" in string:
            total_perms += "Execute + Traverse//"
            continue
        elif 'D' in string:
            total_perms += 'Delete Access//'
        elif 'M' in string:
            total_perms +=  'Modify Access//'
            continue
        elif 'RX' in string:
            total_perms += 'Read and Execute Access//'
            continue
        elif 'R' in string:
            total_perms +=  'Read Access//'
            continue
        elif 'W' in string:
            total_perms +=  'Write Access//'
            continue

    if total_perms != str():
        return total_perms[:-2]
    else:
        return permissions

    
def inheritance_interpreter(permissions):
    important_info = re.findall('[(].{,3}[)]', permissions)[0]
    important_info = re.sub('\(|\)','',important_info)
    if important_info == 'I':
        return True
    else:
        return False
    
# def current_directory(single_slash = False):
#     directory = os.popen('cd')
#     for obj in directory:
#         if single_slash:
#             return re.sub('\n','',obj)
#         obj = re.sub('\\','\\\\',obj)
#         return re.sub('\n','',obj)
    
def current_directory(single_slash = False):
    directory = os.popen('cd')
    for obj in directory:
        if single_slash:
            return re.sub('\n','',obj)
        obj = re.sub('\\\\','\\\\\\\\',obj)
        return re.sub('\n','',obj)
    
def root_interpreter(path):
    if len(re.split('\\\\',path)) <= 2:
        return True
    else:
        return False
    
print("Starting at root: {}".format(current_directory(True)))
print('Gathering Paths')
path = '.'
path = os.path.normpath(path)
paths = [path]
walk = list(os.walk(path,topdown = True))
# print(len(walk))

for number, (root,dirs,files) in enumerate(walk):#os.walk(path, topdown=True):
    progress_bar(number, len(walk), number_of_bars = 50)
    depth = root[len(path) + len(os.path.sep):].count(os.path.sep)
#     print(depth)
    if depth < 50:
        # We're currently two directories in, so all subdirs have depth 3
        paths += [os.path.join(root, d) for d in dirs]
#         dirs[:] = [] # Don't recurse any deeper

print("\nPaths Gathered")
list_of_things = list()
print('Gathering permissions through Tree structure')
# for number, path in enumerate(df_mask.path):
for number, path in enumerate(paths):
#     progress_bar(number, len(df_mask.path), number_of_bars = 50)
    progress_bar(number, len(paths), number_of_bars = 50)
    list_of_things.append(icacls_interpreter(icacls_runner(path)))
print("\nDone iterating through tree")

now = datetime.today().strftime('%y%m%d')
drive = current_directory()[0]
drive_and_date = drive + "_drive_" + now

print("Writing unprocessed paths and permissions to {}.txt".format(drive_and_date))

with open('{}.txt'.format(drive_and_date), 'w') as file:
    for line in list_of_things:
        file.write(str(line) + '\n')
    file.close()
    
print("Finshed writing to {}.txt".format(drive_and_date))

path_info = list()
permissions = list()
domains = list()
users = list()
paths = list()
raw_permissions = list()

print("Loading in {}.txt".format(drive_and_date))

with open("{}.txt".format(drive_and_date), 'r') as file:
    for line in file:
        path_info.append(line)
    file.close()
thing = list() 

print('Extracting data from {}.txt'.format(drive_and_date))

for line in path_info:
    thing.append(line.split('], ['))
    
for number, t in enumerate(thing):
    for i in range(len(t)):
        value = t[i].split("', '")
        if len(value) == 1:
            if "[]\n" in value:
                print(value)
                continue
            value = t[i].split("\", \'")
            value = re.split('[\"\'],\s{1}',t[i])
#             print(value, len(value))
#         if len(value) != 2:
#             print(value)
        if i == 0:
            paths_users = re.split('NT AUTHORITY|NIOWAVE',value[0])
#             print(value)
            if len(paths_users) == 1:
                hr_exception = re.findall('[\S+-]+',paths_users[0])
                users.append(hr_exception[-1])
                path = ''
                for s in hr_exception[:-1]:
                    path += s
                paths.append(path)
                domains.append("NIOWAVE")
#                 paths_users[1] = ""
#                 paths_users[0] = 
            else:
                paths.append(paths_users[0])
                domains.append("NIOWAVE")
                users.append(paths_users[1])
        else:
            paths.append(paths_users[0])
            domains_users = re.split("\\\\\\\\", value[0])
            if len(domains_users) != 2:
                domains_users.append(domains_users[0])
                domains_users[0] = 'NIOWAVE'
            domains.append(domains_users[0])
            users.append(domains_users[1])
        raw_permissions.append(value[1])
        permissions.append(permissions_interpreter(value[1]))
#     print('-'*60)
print("Checking that lengths of extracted information")
print("Lengths of information is consistent: {}".format(len(paths) \
                                                        == len(domains) == \
                                                        len(users) == \
                                                        len(permissions) == \
                                                        len(raw_permissions)))

print("{} paths gathered".format(len(paths)))

cleaned_paths = list()
cleaned_domains = list()
cleaned_users = list()
cleaned_permissions = list()
print("Cleaning data (Making more human readable)")
for number,path in enumerate(paths):
    if len(path) == 3:
        cleaned_paths.append('{}:\\'.format(drive))
        continue
    cleaned_paths.append("{}:\\".format(drive) + path[6:])
# print(cleaned_paths[:10])
for number, domain in enumerate(domains):
    cleaned_domains.append(re.sub("\'|\s+","",domain))
# print(cleaned_domains[:10])
for number, user in enumerate(users):
    cleaned_users.append(re.sub("\\\\|\'\s{1}|\'",'',user))
# print(cleaned_users[:10])
for numner, permission in enumerate(raw_permissions):
    cleaned_permissions.append(re.sub("[n]|\]\]|\\\\|\'","",permission))
# print(cleaned_permissions[:10])

print("Storing cleaned information into DataFrame")
data = pd.DataFrame([cleaned_paths,cleaned_domains,cleaned_users,cleaned_permissions,permissions])
print("Transposing DataFrame")
data = data.transpose()
data.columns = ["Paths","Domains","Users","Permissions","Permissions_Explanation"]

print("Writing all paths and permissions to {}_All_Permissions.xlsx".format(drive_and_date))
print("This may take a few minutes...")
data.to_excel('{}_All_Permissions.xlsx'.format(drive_and_date))

print("Analyzing DataFrame to determine Inherited and Root status")

data['Inherited'] = data['Permissions'].apply(inheritance_interpreter)
data['Root'] = data['Paths'].apply(root_interpreter)
#data.head()

print("Creating mask to look only at root and inherited directories")
mask = (data['Root']) | (data['Inherited'] == False)
clean_data = data[mask]
#clean_data.count

print("Writing Root and Inherited permissions to {}_Permissions_Audit.xlsx".format(drive_and_date))
clean_data.to_excel("{}_Permissions_Audit.xlsx".format(drive_and_date), index = False)
print("Finished writing to {}_Permissions_Audit.xlsx".format(drive_and_date))
input("Please hit enter to close this command prompt")
