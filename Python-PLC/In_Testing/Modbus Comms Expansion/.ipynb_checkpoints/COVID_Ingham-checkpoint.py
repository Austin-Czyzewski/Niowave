# Ingham County Coronavirus Tracker for Niowave

import numpy as np
import Master as M
import Tag_Database as Tags
import time
import os
from datetime import datetime


def One_Case_Prob(Cases_In_Pop, Population, N):
    """
    Probability of one being sick (P_sick)= Total_Cases_In_Region/Region_Population
    Probability of one not being sick P_Healthy= 1 - P_sick
    Probability one fails = 1 - (P_Healthy)^N
    """
    P_has = Cases_In_Pop/Population
    P_not = 1-P_has
    return 1-P_not**(N)

try:
    data = !curl https://www.michigan.gov/coronavirus/0,9753,7-406-98163_98173---,00.html
        
except:
    data = os.system("curl https://www.michigan.gov/coronavirus/0,9753,7-406-98163_98173---,00.html")
    
data = np.array(data)

Ingham_Start = 0
for num, item in enumerate(data):
    if "Ingham" in item:
        print(item, num)
        Ingham_Start = num
Ingham_Data = data[Ingham_Start:Ingham_Start+5]
Ingham_Population = 292406

Cases_Total = int(Ingham_Data[1].split('">')[1].strip("</td>"))
Deaths_Total = int(Ingham_Data[2].split('">')[1].strip("</td>"))
print(Cases_Total, Deaths_Total)

Cases_Percent_of_Pop = Cases_Total/Ingham_Population
Deaths_Percent_of_Pop = Deaths_Total/Ingham_Population
Cases_Per_Resident = int(1/Cases_Percent_of_Pop)
Deaths_Per_Resident = round(1/Deaths_Percent_of_Pop,3)

today = datetime.today().strftime('%m/%d/%Y')
print("Ingham County Coronavirus Data for {}\n".format(today) + \
      "-"*60 + "\n" + \
      "Total Cases = {}\n".format(Cases_Total) + \
      "Total Deaths = {}\n".format(Deaths_Total) + \
      "Percent of Ingham with COVID = {:.3f}%\n".format(Cases_Percent_of_Pop*100) + \
      "Percent of Ingham deceased from COVID = {:.3f}%\n".format(Deaths_Percent_of_Pop*100) + \
      "Residents per case from COVID = {}\n".format(Cases_Per_Resident) + \
      "Residents per death from COVID = {}\n".format(Deaths_Per_Resident) + \
      "Percent chance at least one employee has COVID = {:.3f}%\n".format(100*One_Case_Prob(Cases_Total, Ingham_Population, Niowave_Reporting_Employees)))