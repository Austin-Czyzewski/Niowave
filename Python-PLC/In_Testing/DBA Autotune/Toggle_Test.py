import numpy as np
import Master as M
import Tag_Database as Tags

Client = M.Make_Client('192.168.1.2')

Status = (M.Read(Client,'00015') == True)

def Toggle(Client, Tag_Number):
    
    M.Write(Client, Tag_Number, (M.Read(Client,Tag_Number) == False))
    
    return