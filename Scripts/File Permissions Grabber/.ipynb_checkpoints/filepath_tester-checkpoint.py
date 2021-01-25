import os, string
import re
import folderstats
import pandas as pd
import time

def progress_bar(current, total, number_of_bars = 25):
    current = current + 1
    print("[{}{}] ({}%)\r".format("#"*int(round(current/total,10)*number_of_bars),\
                            " "*(-1 + number_of_bars - int(round(current/total,10)*number_of_bars)), round(100*current/total, 2)), end = '')
    
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
    important_info = re.findall('[(].{,3}[)]', permissions)[-1]
    important_info = re.sub('\(|\)','',important_info)
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
    else:
        return permissions

    
def inheritance_interpreter(permissions):
    important_info = re.findall('[(].{,3}[)]', permissions)[0]
    important_info = re.sub('\(|\)','',important_info)
    if important_info == 'I':
        return True
    else:
        return False
    
def current_directory(single_slash = False):
    directory = os.popen('cd')
    for obj in directory:
        if single_slash:
            return re.sub('\n','',obj)
        obj = re.sub('\\\\','\\\\\\\\',obj)
        return re.sub('\n','',obj)
    
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

print("Writing unprocessed paths and permissions to .txt")

with open('Permissions_Audit_text.txt', 'w') as file:
    for line in list_of_things:
        file.write(str(line) + '\n')
    file.close()
    
print("Finshed writing to .txt")

# print('Going through Tree structure')

# for number, path in enumerate(df_mask.path):
#     progress_bar(number, len(df_mask.path), number_of_bars = 50)
#     list_of_things.append(icacls_interpreter(icacls_runner(path)))
# print("Done")

print(len(list_of_things))
# for thing in list_of_things:
#     print(thing)

print("Storing Data into DataFrame")
directory_info = list()
for number, directory in enumerate(list_of_things):

#     if not (1000 < number < 1025):
#         continue
#     if number == 413:
#         error_counter = 0
#     else:
#         continue
    
    if directory[0][0] == '[]':
        continue
        
    path = re.split('\\\\\\\\(?:.(?!\\\\\\\\))+$', directory[0][0])
    path = re.sub('NT AUTHORITY','',path[0])

    if len(re.findall('\.\\\\.+\\\\',path)) >= 1:
        base = False
    else:
        base = True
    path = re.sub("\.\s*\\\\",'N:', path)
    if path[-8:] == ' NIOWAVE':
        path = path[:-8]
    users = list()
    perms = list()
    domains = list()
    for num, user in enumerate(directory):
        try:
            permissions = re.findall(",(?:.(?!,))+$", user[0])[0]
            permissions = re.sub(",\s+|\\\\n|\]\]",'',permissions)
#             if type(permissions) != str:
#                 print(number, "What the dip")
        except:
            print(number, end = ',')
            
        try:
            
#             print(user)
            user_gatherer = re.findall("\w*\\\\\\\\\w*",user[0])[-1]
            domain_user_split = re.split("\\\\\\\\",user_gatherer)
            domain = domain_user_split[0]
            user = domain_user_split[1]
#             print(domain, user)
            
        except:
            print(domain, user)
            user = permissions
            domain = permissions
            print('Did not work at ', number)
            error_counter += 1
            continue
#         print(permissions)
        perms.append(permissions)
        users.append(user)
        domains.append(domain)
        
        if error_counter > 100:
            break




    for user, auth, domain in zip(users, perms, domains):
        if not inheritance_interpreter(auth) or base: #If it is not inherited or it is a base of the directory
            directory_info.append([path, domain, user, auth, permissions_interpreter(auth)])
    
directory_info_df = pd.DataFrame(directory_info, columns = ['Directory', 'Domain','User','Permissions', 'Permissions_Explanation'])
print("Sorting DataFrame")
sorted_directories = directory_info_df.sort_values(by = 'Directory',axis = 0)
Filename = 'Permissions_Audit.xlsx'
print("Pushing file to excel")
sorted_directories.to_excel(Filename, index = False)
print('File Output to {}'.format(Filename))
input("Hit enter to close this command prompt")
