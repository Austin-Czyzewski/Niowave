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

DST_Conversion = 3
if time.localtime().tm_isdst == 1:
    DST_Conversion = 4

Start_Time = time.time()*10**3-DST_Conversion*60*60*1000

Update_time = 250

temp_roll_scale = 10000

ROLL = int(1000*60*60*24/Update_time)

span = 10       *60 #Minutes

line_width = 4

y_max = None
y_min = None
range_scale = 0.2
curdoc().theme = 'dark_minimal'

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

r1 = p.line(list(data[:,0]), list(data[:,1]), color = 'white', line_width=line_width, y_range_name = "temps")
r2 = p.line(list(data[:,0]), list(data[:,2]), color = Turbo256[43], line_width=line_width, y_range_name = "temps")
r3 = p.line(list(data[:,0]), list(data[:,3]), color = Turbo256[86], line_width=line_width, y_range_name = "temps")
r4 = p.line(list(data[:,0]), list(data[:,4]), color = Turbo256[129], line_width=line_width, y_range_name = "temps")
r5 = p.line(list(data[:,0]), list(data[:,5]), color = Turbo256[172], line_width=line_width, y_range_name = "temps")
r6 = p.line(list(data[:,0]), list(data[:,6]), color = Turbo256[210], line_width=line_width, y_range_name = "temps")

#print('\n'*5, r1.data_source.properties_with_values()['data']['x'], '\n'*5)
data = False
## For each new range add it here
p.extra_y_ranges = {"temps": DataRange1d(only_visible = True, 
                                         renderers = [r1,r2,r3,r4,r5,r6],
                                         range_padding_units = 'percent',range_padding = range_scale)}

p.add_layout(LinearAxis(y_range_name="temps", axis_label = "Pressures"), 'left')

#p.yaxis.formatter = BasicTickFormatter(precision = 2)

p.grid.grid_line_color = 'gray'
p.grid.minor_grid_line_alpha = 0.4
p.grid.grid_line_alpha = 0.4

#################################
#Add data here
#################################

legend = Legend(items=[("Gun Vac" , [r1]),
                       ("Gun Cross Vac" ,  [r2]), 
                       ("SRF Cavity Vac", [r3]),
                       ("HE Straight Vac", [r4]),
                       ("Insulatin Vac", [r5]),
                       ("E-Station Vac", [r6]),
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
        ds1.data['y'].append(temp_list[1])

        ds2.data['x'].append(temp_list[0])
        ds2.data['y'].append(temp_list[2])

        ds3.data['x'].append(temp_list[0])
        ds3.data['y'].append(temp_list[3])
        
        ds4.data['x'].append(temp_list[0])
        ds4.data['y'].append(temp_list[4])

        ds5.data['x'].append(temp_list[0])
        ds5.data['y'].append(temp_list[5])

        ds6.data['x'].append(temp_list[0])
        ds6.data['y'].append(temp_list[6])
        
        ds1.trigger('data', ds1.data, ds1.data)
        ds2.trigger('data', ds2.data, ds2.data)
        ds3.trigger('data', ds3.data, ds3.data)
        ds4.trigger('data', ds4.data, ds4.data)
        ds5.trigger('data', ds5.data, ds5.data)
        ds6.trigger('data', ds6.data, ds6.data)

        last_time = temp_list[0]

    
curdoc().add_root(p)

# Add a periodic callback to be run every 500 milliseconds
curdoc().add_periodic_callback(update, Update_time)