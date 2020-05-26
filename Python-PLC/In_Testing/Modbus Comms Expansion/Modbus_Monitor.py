import Master as M
import numpy as np
import Tag_Database as Tags
import os
import time
os.system("Color 8a")
variables = vars(Tags)
variables = np.array(list(variables.items()))
variables = variables[117:]
while True:
    Client = M.Make_Client("10.50.0.10")
    Bool = False
    for item in variables:
        if "Pulsing_Output" in item[0]:
            Bool = True
        if Bool:
            print(item[0] + ": ",bool(M.Read(Client, item[1], Bool = Bool)))
        else:
            print(item[0] + ": ",round(M.Read(Client, item[1], Bool = Bool), 3))
    Client.close()
    time.sleep(30)
    os.system('cls') 
