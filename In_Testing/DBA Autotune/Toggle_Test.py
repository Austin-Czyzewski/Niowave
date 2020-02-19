import numpy as np
import Master as M
import Tag_Database as Tags

Client = M.Make_Client('192.168.1.2')

print(M.Read(Client, '00015'))