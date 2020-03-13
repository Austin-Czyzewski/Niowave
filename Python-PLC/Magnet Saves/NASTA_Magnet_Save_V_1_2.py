"""
Created on Mon Dec  2 15:50:56 2019

@author: aczyzewski

Goal: Read Values from the PLC into an excel file for the purpose of Magnet Saves

Route:
    -Create variables to write values to
    -Update values from the PLC
    -Write variables to DataFrame
    -Port DataFrame to Excel File (.xlsx)
"""
#imports, numpy and pandas for data manipulation modbus to communicate with PLC
import numpy as np
import pandas as pd
from datetime import datetime
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.payload import BinaryPayloadBuilder
from pymodbus.constants import Endian
import time



##Importing Values from the PLC 
###############################

#Scratch -- if we only use the magnets in a list this is one way to one line it
#WFH_1,WFH_2,WFH_3,WFH_4,WFH_5,WFH_6,WFH_7,WFH_8,WFH_9,WFH_10,WFH_11,WFH_12,WFH_13,WFH_14,WFH_15,WFH_16,WFH_17,WFH_18,WFH_19,WFH_20,WFH_21,WFH_22,WFH_23,WFH_24,WFH_25,WFH_26,WFH_27,WFH_28,WFV_1,WFV_2,WFV_3,WFV_4,WFV_5,WFV_6,WFV_7,WFV_8,WFV_9,WFV_10,WFV_11,WFV_12,WFV_13,WFV_14,WFV_15,WFV_16,WFV_17,WFV_18,WFV_19,WFV_20,WFV_21,WFV_22,WFV_23,WFV_24,WFV_25,WFV_26,WFV_27,WFV_28,DP_1,DP_2,DP_3,DP_4,DP_5,DP_6,DP_7,DP_8,Sol_1,Sol_2,Sol_3,Sol_4,Sol_5,Sol_6,Sol_7,Sol_8,Sol_9,Sol_10,Sol_11,Sol_12,Sol_13 = 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
#End Scratch

#Window Frames Vertical
WFV_1 = 0
WFV_2 = 0
WFV_3 = 0
WFV_4 = 0
WFV_5 = 0
WFV_6 = 0
WFV_7 = 0
WFV_8 = 0
WFV_9 = 0
WFV_10 = 0
WFV_11 = 0
WFV_12 = 0
WFV_13 = 0
WFV_14 = 0
WFV_15 = 0
WFV_16 = 0
WFV_17 = 0
WFV_18 = 0
WFV_19 = 0
WFV_20 = 0
WFV_21 = 0
WFV_22 = 0
WFV_23 = 0
WFV_24 = 0
WFV_25 = 0
WFV_26 = 0
WFV_27 = 0
WFV_28 = 0

#Window Frames Horizontal
WFH_1 = 0
WFH_2 = 0
WFH_3 = 0
WFH_4 = 0
WFH_5 = 0
WFH_6 = 0
WFH_7 = 0
WFH_8 = 0
WFH_9 = 0
WFH_10 = 0
WFH_11 = 0
WFH_12 = 0
WFH_13 = 0
WFH_14 = 0
WFH_15 = 0
WFH_16 = 0
WFH_17 = 0
WFH_18 = 0
WFH_19 = 0
WFH_20 = 0
WFH_21 = 0
WFH_22 = 0
WFH_23 = 0
WFH_24 = 0
WFH_25 = 0
WFH_26 = 0
WFH_27 = 0
WFH_28 = 0

#Solenoids
Sol_1 = 0
Sol_2 = 0
Sol_3 = 0
Sol_4 = 0
Sol_5 = 0
Sol_6 = 0
Sol_7 = 0
Sol_8 = 0
Sol_9 = 0
Sol_10 = 0
Sol_11 = 0
Sol_12 = 0
Sol_13 = 0  
Sol_R_4 = 0
Sol_R_5 = 0
Sol_R_6 = 0
Sol_R_7 = 0
Sol_R_9 = 0
Sol_R_10 = 0
Sol_R_11 = 0
Sol_R_12 = 0

#Dipoles
DP_1 = 0
DP_2 = 0
DP_3 = 0
DP_4 = 0
DP_5 = 0
DP_6 = 0
DP_7 = 0
DP_8 = 0
DP_R_3 = 0
DP_R_4 = 0
DP_R_5 = 0
DP_R_6 = 0
DP_R_7 = 0
DP_R_8 = 0
DP_R_9 = 0

#non magnets
#_________________________________________________________________________________________________

#Copper Gun PF,PR,PT
CU_Pf = 0
CU_Pr = 0
CU_Pt = 0
CU_V = 0
Cu_Vac = 0

#BH PF,PR,PT
BH_Pf = 0
BH_Pr = 0
BH_Pt = 0
BH_V = 0

#SRF PF,PR,PT
SRF_Pf = 0
SRF_Pr = 0
SRF_Pt = 0
SRF_V = 0
SRF_Gain = 0
SRF_Cavity_Vac = 0
SRF_I_Time = 0
SRF_D_Time = 0


#HV Bias
HV_Bias = 0

Pulse_Freq = 0
Pulse_Duty = 0
Pulse_Delay = 0

#Temps
IR_Temp = 0
CHWS = 0
T1_OC = 0
T2_OC = 0
HV_Off_Setpoint = 0
HV_On_Setpoint = 0
DBA_App = 0
Coupler = 0
SRF_Tuner = 0
Up_Gate = 0
Down_Gate = 0
Sol_4_Temp = 0
Sol_5_Temp = 0
WF_10_Temp = 0
Bellows_1 = 0
Bellows_2 = 0
Bellows_3 = 0
DP_3_Temp = 0
DP_4_Temp = 0
DP_5_Temp = 0
DP_6_Temp = 0
DP_7_Temp = 0
DP_8_Temp = 0
W_Up_Break = 0

#Beamline vacs + flow
Cross_Vac = 0
Insulating_Vac = 0
Estation_Vac = 0
Loop_Vac = 0
W_target = 0
Low_E = 0
Low_E_Dt = 0
Low_E_Heat = 0
Loop = 0
Loop_Dt = 0
Loop_Heat = 0
W_Flow = 0
W_Dt = 0
W_Heat = 0

#Current Collection and Emission
DBA_Dump = 0
Loop_Dump = 0
Loop_Half = 0
W_Collect = 0
IC = 0
IC_Range = 0
IC_Dose = 0
IC_Dose_Accum = 0
Current_Emitted = 0



#Putting magnets into lists so that we can update using loops
#############################################################

WFHs = [WFH_1,WFH_2,WFH_3,WFH_4,WFH_5,WFH_6,WFH_7,WFH_8,WFH_9,WFH_10,WFH_11,WFH_12,WFH_13,WFH_14,WFH_15,WFH_16,WFH_17,WFH_18,WFH_19,WFH_20,WFH_21,WFH_22,WFH_23,WFH_24,WFH_25,WFH_26,WFH_27,WFH_28]
#Window Frame Horizontal Modbus locations
WFHnum = 21 #The number of horizontal window frames to control
Hnums = []

WFVs = [WFV_1,WFV_2,WFV_3,WFV_4,WFV_5,WFV_6,WFV_7,WFV_8,WFV_9,WFV_10,WFV_11,WFV_12,WFV_13,WFV_14,WFV_15,WFV_16,WFV_17,WFV_18,WFV_19,WFV_20,WFV_21,WFV_22,WFV_23,WFV_24,WFV_25,WFV_26,WFV_27,WFV_28]
#Window Frame Vertical Modbus locations
WFVnum = 21 #The number of vertical window frames to control
Vnums = []

DPs = [DP_1,DP_2,DP_3,DP_4,DP_5,DP_6,DP_7,DP_8]
#Dipole Modbus locations
DPnum = 8 #The number of Dipoles
Dpnums = []

Sols = [Sol_1,Sol_2,Sol_3,Sol_4,Sol_5,Sol_6,Sol_7,Sol_8,Sol_9,Sol_10,Sol_11,Sol_12,Sol_13]
#Solenoid Modbus locations
Solnum = 9 #Number of solenoids
Solnums = []

for i in range(100):
    if i < WFHnum:
        Hnums.append(20202 + 4*i)
    if i < WFVnum:
        Vnums.append(20200 + 4*i)
    if i < DPnum:
        Dpnums.append(22200 + 2*i)
    if i < Solnum:
        Solnums.append(21200 + 2*i)
        
#for all numbers with leading 0s python will reject so must make a string. There is an integer conversion later.
CU_Tags = ['01100','01102','01104','01114']
BH_Tags = [21224,21226,21228]
HV_Tags = [11100,11300,11302]
SRF_Tags = ['02100','02102','02104']
Pulse_Tags = ['00014','00012','00010','10100','11102']
#Grabbing the values from each magnet, redacted is the write permissions
########################################################################

#Building a list to go into a function
DBA_Mag_Names = [WFH_1,WFH_2,WFH_3,WFH_4,WFH_5,WFH_6,WFH_7,WFH_8,WFH_9,WFH_10,WFH_11,WFH_12,WFH_13,WFH_14,WFH_15,WFH_16,WFH_17,WFH_18,WFH_19,WFH_20,WFH_21,
                 WFV_1,WFV_2,WFV_3,WFV_4,WFV_5,WFV_6,WFV_7,WFV_8,WFV_9,WFV_10,WFV_11,WFV_12,WFV_13,WFV_14,WFV_15,WFV_16,WFV_17,WFV_18,WFV_19,WFV_20,WFV_21,
                 DP_1,DP_2,DP_3,DP_4,DP_5,DP_6,DP_7,DP_8,
                 Sol_1,Sol_2,Sol_3,Sol_4,Sol_5,Sol_6,Sol_7,Sol_8,Sol_9,
                 CU_Pf,CU_Pr,CU_Pt,CU_V,
                 BH_Pf,BH_Pr,BH_Pt,
                 HV_Bias, HV_Off_Setpoint,HV_On_Setpoint,
                 SRF_Pf,SRF_Pr,SRF_Pt,
                 Pulse_Freq,Pulse_Duty,Pulse_Delay,IR_Temp,Current_Emitted]

#Building the list of tags to grab
DBA_Mag_Tags = Hnums + Vnums + Dpnums + Solnums + CU_Tags + BH_Tags + HV_Tags + SRF_Tags + Pulse_Tags

client = ModbusTcpClient('192.168.1.2')
p = 0
N = 1
temp_list = []
for j in range(len(DBA_Mag_Names)):
    result = client.read_holding_registers(int(DBA_Mag_Tags[j]),2,unit=1)
    number = BinaryPayloadDecoder.fromRegisters(result.registers, byteorder=Endian.Big, wordorder=Endian.Big)
    temp_list.append(round(number.decode_32bit_float(),3))

    time.sleep(.020)
client.close()

WFH_1,WFH_2,WFH_3,WFH_4,WFH_5,WFH_6,WFH_7,WFH_8,WFH_9,WFH_10,WFH_11,WFH_12,WFH_13,WFH_14,WFH_15,WFH_16,WFH_17,WFH_18,WFH_19,WFH_20,WFH_21,WFV_1,WFV_2,WFV_3,WFV_4,WFV_5,WFV_6,WFV_7,WFV_8,WFV_9,WFV_10,WFV_11,WFV_12,WFV_13,WFV_14,WFV_15,WFV_16,WFV_17,WFV_18,WFV_19,WFV_20,WFV_21,DP_1,DP_2,DP_3,DP_4,DP_5,DP_6,DP_7,DP_8,Sol_1,Sol_2,Sol_3,Sol_4,Sol_5,Sol_6,Sol_7,Sol_8,Sol_9,CU_Pf,CU_Pr,CU_Pt,CU_V,BH_Pf,BH_Pr,BH_Pt,HV_Bias,HV_Off_Setpoint,HV_On_Setpoint,SRF_Pf,SRF_Pr,SRF_Pt,Pulse_Freq,Pulse_Duty,Pulse_Delay,IR_Temp,Current_Emitted = temp_list

#Putting the dataframe into an excel file.
##########################################

#into the spreadsheet format
dftoexcel = pd.DataFrame([[WFV_1,WFH_1,Sol_1,DP_1,'','Cu Gun (1)',CU_Pf,CU_Pr,CU_Pt,CU_V,'','','','','','','','','',''],
                       [WFV_2,WFH_2,Sol_2,DP_2,'','BH (2)',BH_Pf,BH_Pr,BH_Pt,BH_V,'','','','','','','','','',''],
                       [WFV_3,WFH_3,Sol_3,DP_3,'','Bias (0)','--','--','--',HV_Bias,'','','','','','','','','',''],
                       [WFV_4,WFH_4,Sol_4,DP_4,'','SRF',SRF_Pf,SRF_Pr,SRF_Pt,'','','','','','','','','','',''],
                       [WFV_5,WFH_5,Sol_5,DP_5,'','','','','','','','','','','','','','','',''],
                       [WFV_6,WFH_6,Sol_6,DP_6,'','','IR_Temp',IR_Temp,'K','','','','','','','','','','',''],
                       [WFV_7,WFH_7,Sol_7,DP_7,'','','Emitted Current',Current_Emitted,'uA','','','','','','','','','','',''],
                       [WFV_8,WFH_8,Sol_8,DP_8,'','','','','','','','','','','','','','','',''],
                       [WFV_9,WFH_9,Sol_9,'','','','HV Off SP',HV_Off_Setpoint,'kV','','','','','','','','','','',''],
                       [WFV_10,WFH_10,Sol_10,'','','','HV On SP',HV_On_Setpoint,'kV','','','','','','','','','',''],
                       [WFV_11,WFH_11,Sol_11,'','','','','','','','','','','','','','','','',''],
                       [WFV_12,WFH_12,Sol_12,'','','','','','','','','','','','','','','','',''],
                       [WFV_13,WFH_13,Sol_13,'','','','','','','','','','','','','','','','',''],
                       [WFV_14,WFH_14,'','','','','','','','','','','','','','','','','',''],
                       [WFV_15,WFH_15,'','','','','','','','','','','','','','','','','',''],
                       [WFV_16,WFH_16,'','','','','','','','','','','','','','','','','',''],
                       [WFV_17,WFH_17,'','','','','','','','','','','','','','','','','',''],
                       [WFV_18,WFH_18,'','','','','','','','','','','','','','','','','',''],
                       [WFV_19,WFH_19,'','','','','','','','','','','','','','','','','',''],
                       [WFV_20,WFH_20,'','','','','','','','','','','','','','','','','',''],
                       [WFV_21,WFH_21,'','','','','','','','','','','','','','','','','',''],
                       [WFV_22,WFH_22,'','','','','','','','','','','','','','','','','',''],
                       [WFV_23,WFH_23,'','','','','Pulsing Params','','','','','','','','','','','','',''],
                       [WFV_24,WFH_24,'','','','','Freq (Hz)','Duty (%)','Delay (ms)','','','','','','','','','','',''],
                       [WFV_25,WFH_25,'','','','',Pulse_Freq,Pulse_Duty,Pulse_Delay,'','','','','','','','','','',''],
                       [WFV_26,WFH_26,'','','','','','','','','','','','','','','','','',''],
                       [WFV_27,WFH_27,'','','','','','','','','','','','','','','','','',''],
                       [WFV_28,WFH_28,'','','','','','','','','','','','','','','','','','']],
                      index=['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28',],
                      columns=['WF V','WF H','Sol','DP','','','Pf (W)','Pr (W)','Pt (dBm)','V (kV)','','','','','','','','','',''])



#Saving the file to an excel file. This syntax used as the date and time of now plus the file extension name
############################################################################################################

#Date and time so we don't have to specify manually
now = datetime.today().strftime('%y%m%d_%H%M')

#to save all values
dftoexcel.to_excel(str(now)+'.xlsx')

