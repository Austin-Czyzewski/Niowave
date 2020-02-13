import Master as M
import Tag_Database as Tags
import time

Client = M.Make_Client('10.50.0.10')

print(M.Read(Client,Tags.RF_Beam_Mon))

time.sleep(0.01)

print(M.Read(Client,Tags.RF_Beam_Mon))