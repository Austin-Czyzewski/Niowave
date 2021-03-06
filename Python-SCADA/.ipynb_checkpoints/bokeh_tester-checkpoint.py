#####################
#bokeh serve --show bokeh_tester.py
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
from bokeh.driving import linear, count
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

Update_time = 25

temp_roll_scale = 10000

ROLL = int(1000*60*60*24/Update_time)
ROLL = 1000

span = 10*60 #Seconds

line_width = 4

y_max = None
y_min = None
range_scale = 0.2
curdoc().theme = 'dark_minimal'
#DataRange1d(only_visible = True)

p = figure(plot_width=1000, plot_height=400,
           x_axis_label = 'Time', y_axis_label = 'Random Number', x_axis_type = 'datetime', 
           tools="pan,xwheel_zoom,ywheel_zoom,xbox_zoom,reset",
           y_range=DataRange1d(only_visible = True, max_interval = y_max, min_interval = y_min),
           sizing_mode='stretch_both',
           lod_timeout = 100,
           lod_threshold = 10,
           lod_factor = 2000,
#           output_backend = 'webgl',
           x_range = DataRange1d(only_visible = True,
                                 follow = "end", follow_interval = span*1000,
                                 max_interval = 60*1000*60*24, min_interval = 1000, 
                                 range_padding_units = 'absolute',range_padding = 1000,))
          #other_property = here)
p.yaxis.visible = False
p.xaxis.formatter = DatetimeTickFormatter(milliseconds = '%H:%M:%S.%2N',seconds = "%H:%M:%S",minsec = "%H:%M:%S",minutes = "%H:%M:%S",hourmin = "%H:%M:%S",hours = "%H:%M:%S",days = ['%m/%d', '%a%d'],months = ['%m/%Y', '%b %Y'],years = ['%Y'])
    
    
#slider = Slider(title = 'Follow Range', start= 2*1000 , end= 60*1000, step=1000, value=span*1000)
#slider.js_link('value', p.x_range, 'follow_interval')
#slider.on_change('value', p.x_range, 'follow_interval')
#Column = column(slider, width = 100, height = 100)
#p.add_layout(Column, 'below')

#r1 = p.line([], [], color="yellow", line_width=line_width, y_range_name = "pressures")
#r2 = p.line([], [], color="skyblue", line_width=line_width, y_range_name = "temps")
#r3 = p.line([], [], color="green", line_width=line_width, y_range_name = "temps")

import numpy as np
with open("Data.txt",'r') as file:
    lines = file.readlines()
for num,line in enumerate(lines[1:]):
    lines[num+1] = line.strip("\nr").split(",")
data = np.array(lines[1:]).astype(float)
data[:,0]

r1 = p.line([], [], color="yellow", line_width=line_width, y_range_name = "pressures")
r2 = p.line([], [], color="skyblue", line_width=line_width, y_range_name = "temps")
r3 = p.line([], [], color="green", line_width=line_width, y_range_name = "temps")

#print('\n'*5, r1.data_source.properties_with_values()['data']['x'], '\n'*5)

## For each new range add it here
p.extra_y_ranges = {"temps": DataRange1d(only_visible = True, renderers = [r2,r3],
                                         range_padding_units = 'percent',range_padding = range_scale), 
                   "pressures": DataRange1d(only_visible = True,  renderers = [r1],
                                            range_padding_units = 'percent',range_padding = range_scale)}

p.add_layout(LinearAxis(y_range_name="temps", axis_label = "Temps"), 'left')
p.add_layout(LinearAxis(y_range_name="pressures", axis_label = "Pressures"), 'left')

p.yaxis.formatter = BasicTickFormatter(precision = 1)

p.grid.grid_line_color = 'gray'
p.grid.minor_grid_line_alpha = 0.4
p.grid.grid_line_alpha = 0.4

#################################
#Add data here
#################################

#r1 = p.line([Start_Time], [0], color="yellow", line_width=2, y_range_name = "pressures")
#r2 = p.line([Start_Time], [0], color="skyblue", line_width=2, y_range_name = "temps")


legend = Legend(items=[("One" , [r1]),
                       ("Two" ,  [r2]), 
                       ("Three", [r3]), 
#                       ("Temps", [r2,r3]) 
                      ],
                location="center", click_policy = "hide")

p.add_layout(legend, 'right')
#p.legend.click_policy= "hide"

ds1 = r1.data_source
ds2 = r2.data_source
ds3 = r3.data_source

run = True

@count()
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
        #print("temp list",temp_list[0])
        #print("last time",last_time)
        temp_list[0] = time.time()*10**3-DST_Conversion*60*60*1000
        if temp_list[0] == last_time:
            run = False
    except:
        run = True
        
    
    if run:
        ds1.data['x'].append(temp_list[0])
        ds1.data['y'].append(random.normal(65,10)*1e-6)
        #ds1.data['y'].append(temp_list[1])

        ds2.data['x'].append(temp_list[0])
        ds2.data['y'].append(random.normal(47,5))
        #ds2.data['y'].append(temp_list[2])

        ds3.data['x'].append(temp_list[0])
        ds3.data['y'].append(random.normal(74,1))  
        #ds3.data['y'].append(temp_list[3])

        #ds1.trigger('data', ds1.data, ds1.data)
        ds1.stream({"x": ds1.data['x'], "y": ds1.data['y']}, rollover=ROLL) ##### THIS LINE IS ONLY IF TXT FILE IS NOT USED
        #ds2.trigger('data', ds2.data, ds2.data)
        ds2.stream({"x": ds2.data['x'], "y": ds2.data['y']}, rollover=ROLL) ##### THIS LINE IS ONLY IF TXT FILE IS NOT USED
        #ds3.trigger('data', ds3.data, ds3.data)
        ds3.stream({"x": ds3.data['x'], "y": ds3.data['y']}, rollover=ROLL) ##### THIS LINE IS ONLY IF TXT FILE IS NOT USED

        last_time = temp_list[0]

    
curdoc().add_root(p)

# Add a periodic callback to be run every 500 milliseconds
curdoc().add_periodic_callback(update, Update_time)