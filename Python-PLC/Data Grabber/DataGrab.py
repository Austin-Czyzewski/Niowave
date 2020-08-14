import Master_All_Versions as M
import Tag_Database as Tags
from datetime import datetime
from time import sleep

IP = '10.50.0.10'

Client = M.Make_Client(IP)

while True:
    sleep(0.5)
    now = datetime.today().strftime('%y%m%d_%H%M%S.%f') + '.txt'
    try:
        M.Snapshot(Client, now)
    except:
        print("Failed connection to PLC at {}".format(now))
        continue