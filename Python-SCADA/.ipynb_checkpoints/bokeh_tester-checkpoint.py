#####################
#bokeh serve --show bokeh_tester.py
#####################
import numpy as np
from bokeh.plotting import figure
from bokeh.io import show, output_notebook, curdoc
from bokeh.models import LinearAxis, Range1d, BoxSelectTool
from bokeh.models.formatters import DatetimeTickFormatter, BasicTickFormatter
from bokeh.models import Legend

from bokeh.models.ranges import DataRange1d

from bokeh.plotting import figure, curdoc
from bokeh.driving import linear
import random
from datetime import datetime
import time

from bokeh.models.widgets import CheckboxGroup

#output_file("checkbox_group.html")

#checkbox_group = CheckboxGroup(labels=["Option 1", "Option 2", "Option 3"], active=[0, 1])

#show(vform(checkbox_group))
Start_Time = time.time()*10**3-4*60*60*1000

Update_time = 50

temp_roll_scale = 10000

ROLL = int(1000*60*60*24/Update_time           /temp_roll_scale)
span = 15 #Seconds

y_max = 120
y_min = -20
y_min2 = -10
y_max2 = 60

curdoc().theme = 'dark_minimal'
#DataRange1d(only_visible = True)

p = figure(plot_width=1000, plot_height=400,
           x_axis_label = 'Time', y_axis_label = 'Random Number', x_axis_type = 'datetime', 
           tools="pan,xwheel_zoom,ywheel_zoom,xbox_zoom,reset",
           y_range=DataRange1d(only_visible = True, max_interval = y_max, min_interval = y_min),
           sizing_mode='stretch_both',
           x_range = DataRange1d(only_visible = True,
                                 follow = "end", follow_interval = span*1000,
                                 max_interval = 60*1000*60*24, min_interval = 1000, 
                                 range_padding_units = 'absolute',range_padding = 1000,))
          #other_property = here)
p.yaxis.visible = False
p.xaxis.formatter = DatetimeTickFormatter(milliseconds = '%H:%M:%S.%2N',seconds = "%H:%M:%S",minsec = "%H:%M:%S",minutes = "%H:%M:%S",hourmin = "%H:%M:%S",hours = "%H:%M:%S",days = ['%m/%d', '%a%d'],months = ['%m/%Y', '%b %Y'],years = ['%Y'])
    
r1 = p.line([Start_Time], [0], color="yellow", line_width=2, y_range_name = "pressures")
#r2 = p.line([Start_Time], [35], color="skyblue", line_width=2, y_range_name = "temps")
#r3 = p.line([Start_Time], [60], color="green", line_width=3, y_range_name = "temps")

#r1 = p.line([], [], color="yellow", line_width=2, y_range_name = "pressures")
r2 = p.line([], [], color="skyblue", line_width=2, y_range_name = "temps")
r3 = p.line([], [], color="green", line_width=3, y_range_name = "temps")

print('\n'*5, r1.data_source.properties_with_values()['data']['x'], '\n'*5)

## For each new range add it here
p.extra_y_ranges = {"temps": DataRange1d(only_visible = True, renderers = [r2,r3]), 
                   "pressures": DataRange1d(only_visible = True,  renderers = [r1])}

p.add_layout(LinearAxis(y_range_name="temps", axis_label = "Temp4s"), 'left')
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


@linear()
def update(step):
    currenttime = time.time()*10**3-4*60*60*1000
    
    ds1.data['x'].append(currenttime)
    ds1.data['y'].append(random.randint(5,10)*1e-6)
    
    ds2.data['x'].append(currenttime)
    ds2.data['y'].append(random.randint(35,50)) 
    
    ds3.data['x'].append(currenttime)
    ds3.data['y'].append(random.randint(60,75))  
    
    ds1.trigger('data', ds1.data, ds1.data)
    #ds1.stream({"x": ds1.data['x'], "y": ds1.data['y']}, rollover=ROLL) ##### THIS LINE IS ONLY IF TXT FILE IS NOT USED
    ds2.trigger('data', ds2.data, ds2.data)
    ds3.trigger('data', ds3.data, ds3.data)
    

curdoc().add_root(p)

# Add a periodic callback to be run every 500 milliseconds
curdoc().add_periodic_callback(update, Update_time)