import Master as M
from datetime import datetime
import sys 

config_file_path = str(sys.argv[-1])

Tunnel, PLC_IP = M.config_reader(config_file_path, "Snapshot")

Client = M.Make_Client(PLC_IP)

now = datetime.today().strftime('%y%m%d_%H%M%S') #Taking the current time in YYMMDD_HHmm format to save the plot and the txt file

M.Snapshot(Client, Tunnel, filename = f'.\Output Data\{Tunnel}\Snapshots\{now}_snapshot.txt')
