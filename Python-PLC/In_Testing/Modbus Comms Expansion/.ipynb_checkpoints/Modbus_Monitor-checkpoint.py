import Master as M
import numpy as np
import Tag_Database as Tags
import os
import time

Client = M.Make_Client("10.50.0.10")

M.Read(Client,Tags.CU_V)

start = 134

os.system("Color 8a")
variables = vars(Tags)
variables = np.array(list(variables.items()))
variables = variables[start:]
#variables[:,1] = variables[:,1].astype(int)
#variables = variables[variables[:,1].argsort()]
Tag_List = []
for item in variables:
    if "Emitted_Current" in item[0]:
        Tag_List.append([item[1], True])
    else:
        Tag_List.append([item[1], False])
    
while True:
    temp_list = []
    a = time.time()
    temp_list.append(M.Gather(Client, Tag_List, count = 20, sleep_time = 0.010))
    os.system('cls')
    print(time.time()-a)
    for item in range(len(temp_list[0])):
        print("{}: {:.3f}".format(variables[item,0], temp_list[0][item]))
    #Client.close()
    time.sleep(5)
