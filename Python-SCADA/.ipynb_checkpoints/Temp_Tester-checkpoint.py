#####################
#bokeh serve --show Temp_Tester.py
#####################

##########################################################
##########################################################
# Temperature trends
##########################################################
##########################################################

import numpy as np
from bokeh.plotting import figure
from bokeh.io import show, output_notebook, curdoc
from bokeh.models import LinearAxis, Range1d, BoxSelectTool
from bokeh.models.formatters import DatetimeTickFormatter, BasicTickFormatter
from bokeh.models import Legend
from bokeh.models.ranges import DataRange1d
from bokeh.plotting import figure, curdoc
from bokeh.driving import linear
from bokeh.palettes import Category20, Turbo256
import numpy.random as random

from bokeh.layouts import column
from bokeh.models import Slider
#from bokeh.io import show

from datetime import datetime
import time
import os
from bokeh.models.widgets import CheckboxGroup
from Tag_Database import *

Vacuums = [Gun_Vac, Gun_Cross, SRF_Cavity_Vac, HE_Sraight_Vac, # All of the vacuum tags that we currently have, in order
           Insulating_Vac, E_Station_Vac]

Temps = [BH_OC_Temp, DBA_Pipe_Temp, Cu_Gun_Temp, HE_Straight_Col, 
         DBA_Dump_CHWR, DBA_Dump_CHWS, Tuner_Plate_Temp, 
         Gate_Valve_Downstream_Temp, Gate_Valve_Upstream_Temp, 
         Loop_Bypass_CHWS, Loop_Bypass_CHWR, DBA_Coupler, 
         Coupler_Shoulder, Solenoid_4_Temp, Solenoid_5_Temp]

DST_Conversion = 3
if time.localtime().tm_isdst == 1:
    DST_Conversion = 4

Start_Time = time.time()*10**3-DST_Conversion*60*60*1000

Update_time = 250

temp_roll_scale = 10000

ROLL = int(1000*60*60*24/Update_time)

span = 10*60 #Seconds

line_width = 4

y_max = None
y_min = None
range_scale = 0.2
curdoc().theme = 'dark_minimal'
#DataRange1d(only_visible = True)

p = figure(plot_width=1000, plot_height=400,
           x_axis_label = 'Time', y_axis_label = 'Numbers', x_axis_type = 'datetime', 
           tools="pan,xwheel_zoom,ywheel_zoom,xbox_zoom,reset",
           y_range=DataRange1d(only_visible = True, max_interval = y_max, min_interval = y_min),
           sizing_mode='stretch_both',
#           output_backend="webgl",
           x_range = DataRange1d(only_visible = True,
                                 follow = "end", follow_interval = span*1000,
                                 max_interval = 60*1000*60*24, min_interval = 1000, 
                                 range_padding_units = 'absolute',range_padding = 1000,))
          #other_property = here)
p.yaxis.visible = False
p.xaxis.formatter = DatetimeTickFormatter(milliseconds = '%H:%M:%S.%2N',seconds = "%H:%M:%S",minsec = "%H:%M:%S",minutes = "%H:%M:%S",hourmin = "%H:%M:%S",hours = "%H:%M:%S",days = ['%m/%d', '%a%d'],months = ['%m/%Y', '%b %Y'],years = ['%Y'])
    

with open("Data.txt",'r') as file:
    lines = file.readlines()
for num,line in enumerate(lines[1:]):
    lines[num+1] = line.strip("\nr").split(",")
data = np.array(lines[1:]).astype(float)

r1 = p.line(list(data[:,0]), list(data[:,7]), color = 'white', line_width=line_width, y_range_name = "temps")
r2 = p.line(list(data[:,0]), list(data[:,8]), color = Turbo256[17], line_width=line_width, y_range_name = "temps")
r3 = p.line(list(data[:,0]), list(data[:,9]), color = Turbo256[34], line_width=line_width, y_range_name = "temps")
r4 = p.line(list(data[:,0]), list(data[:,10]), color = Turbo256[51], line_width=line_width, y_range_name = "temps")
r5 = p.line(list(data[:,0]), list(data[:,11]), color = Turbo256[68], line_width=line_width, y_range_name = "temps")
r6 = p.line(list(data[:,0]), list(data[:,12]), color = Turbo256[85], line_width=line_width, y_range_name = "temps")
r7 = p.line(list(data[:,0]), list(data[:,13]), color = Turbo256[102], line_width=line_width, y_range_name = "temps")
r8 = p.line(list(data[:,0]), list(data[:,14]), color = Turbo256[119], line_width=line_width, y_range_name = "temps")
r9 = p.line(list(data[:,0]), list(data[:,15]), color = Turbo256[136], line_width=line_width, y_range_name = "temps")
r10 = p.line(list(data[:,0]), list(data[:,16]), color = Turbo256[153], line_width=line_width, y_range_name = "temps")
r11 = p.line(list(data[:,0]), list(data[:,17]), color = Turbo256[170], line_width=line_width, y_range_name = "temps")
r12 = p.line(list(data[:,0]), list(data[:,18]), color = Turbo256[187], line_width=line_width, y_range_name = "temps")
r13 = p.line(list(data[:,0]), list(data[:,19]), color = Turbo256[204], line_width=line_width, y_range_name = "temps")
r14 = p.line(list(data[:,0]), list(data[:,20]), color = Turbo256[221], line_width=line_width, y_range_name = "temps")
r15 = p.line(list(data[:,0]), list(data[:,21]), color = Turbo256[255], line_width=line_width, y_range_name = "temps")

#print('\n'*5, r1.data_source.properties_with_values()['data']['x'], '\n'*5)
data = False
## For each new range add it here
p.extra_y_ranges = {"temps": DataRange1d(only_visible = True, 
                                         renderers = [r1,r2,r3,r4,r5,r6,r7,r8,r9,r10,r11,r12,r13,r14,r15],
                                         range_padding_units = 'percent',range_padding = range_scale)}

p.add_layout(LinearAxis(y_range_name="temps", axis_label = "Temps"), 'left')

#p.yaxis.formatter = BasicTickFormatter(precision = 2)

p.grid.grid_line_color = 'gray'
p.grid.minor_grid_line_alpha = 0.4
p.grid.grid_line_alpha = 0.4

#################################
#Add data here
#################################

legend = Legend(items=[("BH OC" , [r1]),
                       ("DBA Pipe" ,  [r2]), 
                       ("Copper Gun", [r3]),
                       ("HE Straight Collimator", [r4]),
                       ("DBA Dump CHWR", [r5]),
                       ("DBA Dump CHWS", [r6]),
                       ("Tuner Plate", [r7]),
                       ("Gate Valve Downstream", [r8]),
                       ("Gate Valve Upstream", [r9]),
                       ("Loop Bypass CHWS", [r10]),
                       ("Loop Bypass CHWR", [r11]),
                       ("DBA Coupler", [r12]),
                       ("Coupler Shoulder", [r13]),
                       ("Solenoid 4", [r14]),
                       ("Solenoid 5", [r15]),
                      ],
                location="center", click_policy = "hide")

p.add_layout(legend, 'right')
#p.legend.click_policy= "hide"

ds1 = r1.data_source
ds2 = r2.data_source
ds3 = r3.data_source
ds4 = r4.data_source
ds5 = r5.data_source
ds6 = r6.data_source
ds7 = r7.data_source
ds8 = r8.data_source
ds9 = r9.data_source
ds10 = r10.data_source
ds11 = r11.data_source
ds12 = r12.data_source
ds13 = r13.data_source
ds14 = r14.data_source
ds15 = r15.data_source

run = True

@linear()
def update(step):
    
    global last_time
    run = True
    
    with open('Data.txt', 'rb') as file: #delete to f?
        file.seek(-2, os.SEEK_END)
        while file.read(1) != b'\n':
            file.seek(-2, os.SEEK_CUR) 
        last_line = file.readline().decode().split(",")
    temp_list = []
    for item in last_line:
        try:
            temp_list.append(float(item))
        except:
            temp_list.append(float(item.strip("\rn")))
            
    #currenttime = time.time()*10**3-DST_Conversion*60*60*1000
    try:
        print("temp list",temp_list[0])
        print("last time",last_time)
        print(len(temp_list))
        if temp_list[0] == last_time:
            run = False
    except:
        run = True
    
    if run:
        ds1.data['x'].append(temp_list[0])
        ds1.data['y'].append(temp_list[7])

        ds2.data['x'].append(temp_list[0])
        ds2.data['y'].append(temp_list[8])

        ds3.data['x'].append(temp_list[0])
        ds3.data['y'].append(temp_list[9])
        
        ds4.data['x'].append(temp_list[0])
        ds4.data['y'].append(temp_list[10])

        ds5.data['x'].append(temp_list[0])
        ds5.data['y'].append(temp_list[11])

        ds6.data['x'].append(temp_list[0])
        ds6.data['y'].append(temp_list[12])
        
        ds7.data['x'].append(temp_list[0])
        ds7.data['y'].append(temp_list[13])

        ds8.data['x'].append(temp_list[0])
        ds8.data['y'].append(temp_list[14])

        ds9.data['x'].append(temp_list[0])
        ds9.data['y'].append(temp_list[15])
        
        ds10.data['x'].append(temp_list[0])
        ds10.data['y'].append(temp_list[16])

        ds11.data['x'].append(temp_list[0])
        ds11.data['y'].append(temp_list[17])

        ds12.data['x'].append(temp_list[0])
        ds12.data['y'].append(temp_list[18]) 
        
        ds13.data['x'].append(temp_list[0])
        ds13.data['y'].append(temp_list[19])

        ds14.data['x'].append(temp_list[0])
        ds14.data['y'].append(temp_list[20])

        ds15.data['x'].append(temp_list[0])
        ds15.data['y'].append(temp_list[21]) 

        ds1.trigger('data', ds1.data, ds1.data)
        ds2.trigger('data', ds2.data, ds2.data)
        ds3.trigger('data', ds3.data, ds3.data)
        ds4.trigger('data', ds4.data, ds4.data)
        ds5.trigger('data', ds5.data, ds5.data)
        ds6.trigger('data', ds6.data, ds6.data)
        ds7.trigger('data', ds7.data, ds7.data)
        ds8.trigger('data', ds8.data, ds8.data)
        ds9.trigger('data', ds9.data, ds9.data)
        ds10.trigger('data', ds10.data, ds10.data)
        ds11.trigger('data', ds11.data, ds11.data)
        ds12.trigger('data', ds12.data, ds12.data)
        ds13.trigger('data', ds13.data, ds13.data)
        ds14.trigger('data', ds14.data, ds14.data)
        ds15.trigger('data', ds15.data, ds15.data)

        last_time = temp_list[0]

    
curdoc().add_root(p)

# Add a periodic callback to be run every 500 milliseconds
curdoc().add_periodic_callback(update, Update_time)