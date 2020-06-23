import Master as M
from datetime import datetime
import numpy as np

def Snapshot(Client, filename, start = 8):
    import Tag_Database as Tags
    
    M.Read(Client,Tags.CU_V)
    
    variables = vars(Tags)
    variables = np.array(list(variables.items()))
    variables = variables[start:]
    #variables[:,1] = variables[:,1].astype(int)
    #variables = variables[variables[:,1].argsort()]
    Tag_List = []
    for item in variables:
        Tag_List.append([item[1], False])
            
    temp_list = []
    temp_list.append(M.Gather(Client, Tag_List, count = 20, sleep_time = 0.010))
    
    with open(filename,'w') as f: #Opening a file with the current date and time
        for num, line in enumerate(temp_list[0]):
            f.write(variables[num,0] + ": " + str(line).strip("([])")+'\n') #Writing each line in that file
        f.close() #Closing the file to save it
        
now = datetime.today().strftime('%y%m%d_%H%M') #Taking the current time in YYMMDD_HHmm format to save the plot and the txt file
filename = now + '.txt'

Client = M.Make_Client('10.50.0.10')

Snapshot(Client, filename)