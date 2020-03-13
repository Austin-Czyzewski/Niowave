#### Creator: Austin Czyzewski
## Date: 02/03/2020

#This is an importable tag database designed to make writing code for automation direct interaction a little bit
#    more intuitive. The intention here is to get rid of the need to look into the modbus excel file for a new tag
#    as most of the legwork is done here. Simply reference this program for what I've named each item. This program
#    is currently in its early stages so it is best to remember that these names may change and so may the tags.


########################################
### Window Frame Request
########################################

WF1V = 20201
WF1H = 20203
WF2V = 20205
WF2H = 20207
WF3V = 20209
WF3H = 20211
WF4V = 20213
WF4H = 20215
WF5V = 20217
WF5H = 20219
WF6V = 20221
WF6H = 20223
WF7V = 20225
WF7H = 20227
WF8V = 20229
WF8H = 20231
WF9V = 20233
WF9H = 20235
WF10V = 20237
WF10H = 20239
WF11V = 20241
WF11H = 20243
WF12V = 20245
WF12H = 20247
WF13V = 20249
WF13H = 20251
WF14V = 20253
WF14H = 20255
WF15V = 20257
WF15H = 20259
WF16V = 20261
WF16H = 20263
WF17V = 20265
WF17H = 20267
WF18V = 20269
WF18H = 20271
WF19V = 20273
WF19H = 20275
WF20V = 20277
WF20H = 20279
WF21V = 20281
WF21H = 20283

########################################
### Dipole Request
########################################

DP1 = 22201
DP2 = 22203
DP3 = 22205
DP4 = 22207
DP5 = 22209
DP6 = 22211
DP7 = 22213
DP8 = 22215

########################################
### Solenoid Request
########################################

Sol1 = 21201
Sol2 = 21203
Sol3 = 21205
Sol4 = 21207
Sol5 = 21209
Sol6 = 21211
Sol7 = 21213
Sol8 = 21215
Sol9 = 21217

########################################
### Window Frame Readback
########################################

WF1V_Read = 20101
WF1H_Read = 20103
WF2V_Read = 20105
WF2H_Read = 20107
WF3V_Read = 20109
WF3H_Read = 20111
WF4V_Read = 20113
WF4H_Read = 20115
WF5V_Read = 20117
WF5H_Read = 20119
WF6V_Read = 20121
WF6H_Read = 20123
WF7V_Read = 20125
WF7H_Read = 20127
WF8V_Read = 20129
WF8H_Read = 20131
WF9V_Read = 20133
WF9H_Read = 20135
WF10V_Read = 20137
WF10H_Read = 20139
WF11V_Read = 20141
WF11H_Read = 20143
WF12V_Read = 20145
WF12H_Read = 20147
WF13V_Read = 20149
WF13H_Read = 20151
WF14V_Read = 20153
WF14H_Read = 20155
WF15V_Read = 20157
WF15H_Read = 20159
WF16V_Read = 20161
WF16H_Read = 20163
WF17V_Read = 20165
WF17H_Read = 20167
WF18V_Read = 20169
WF18H_Read = 20171
WF19V_Read = 20173
WF19H_Read = 20175
WF20V_Read = 20177
WF20H_Read = 20179
WF21V_Read = 20181
WF21H_Read = 20183

########################################
### Dipole Readback
########################################

DP1_Read = 22101
DP2_Read = 22103
DP3_Read = 22105
DP4_Read = 22107
DP5_Read = 22109
DP6_Read = 22111
DP7_Read = 22113
DP8_Read = 22115

########################################
### Solenoid Readback
########################################

Sol1_Read = 21101
Sol2_Read = 21103
Sol3_Read = 21105
Sol4_Read = 21107
Sol5_Read = 21109
Sol6_Read = 21111
Sol7_Read = 21113
Sol8_Read = 21115
Sol9_Read = 21117

########################################
### Cathode Controls
########################################

IR_Temp = 10101
VA_Temp = 10111
Heater_Amps_Set = 10107
Temperature_Set = 10303
Emission_Set = 10305
Voltage_Read = 10103
Current_Read = 10105
Impedance_Read = 10121
Power_Read = 10123

########################################
### Current Readbacks
########################################

Emitted_Current = 11103
DBA_Bypass = 11109
Recirculator_Halfway = 11111
Recirculator_Bypass = 11113
RF_Beam_Mon = 11117

########################################
### Pulse Controls
########################################

Pulse_Frequency = 10309
Pulse_Duty = 10311
Pulse_Delay = 13013

########################################
### Cu Gun, BH Coupler, SRF Pf, Pr, Pt
########################################

CU_Pf = '01101'
CU_Pr = '01103'
CU_Pt = '01105'
CU_V = '01115'
BH_Pf = 21225
BH_Pr = 21227
BH_Pt = 21229
SRF_Pf = '02101'
SRF_Pr = '02103'
SRF_Pt = '02105'

########################################
### HV Bias Paremeters
########################################

HV_Bias =  11101
HV_Off_Setpoint = 11301
HV_On_Setpoint = 11303
Trek_V = 11501
Trek_I = 11503
V0_SP = 11311
V0_Read = 11101