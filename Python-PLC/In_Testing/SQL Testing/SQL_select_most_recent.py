import pyodbc
import datetime
import matplotlib
import matplotlib.pyplot as plt

###############################################################################
# Connect to SQL Server Database
serv = 'B1904-1\SQLEXPRESS'
db = 'NiowaveDB'


con = pyodbc.connect('Driver={SQL Server};'
                  'Server=' + serv + ';'
                  'Database=' + db + ';'
                  'Trusted_Connection=yes;')

cursor = con.cursor()

###############################################################################
# Load SQL select query
fname = 'SELECT_most_recent.txt'
f = open(fname, 'r')
sql_query = f.read()

###############################################################################
# Execute SQL select query
cursor.execute(sql_query)

###############################################################################
# Extract column values and store as list
time_stamp = [];
cu_gun_voltage = [];

for row in cursor:
    # Row object is similar to a tuple
    time_stamp.append(row[0][:-2]) # Remove last zero in the datetime variable 
                                   # to match python datetime formating
    cu_gun_voltage.append(row[1])
    print(row)
   
# Convert time_stamp to datetime.datetime type
for i in range(len(time_stamp)):
    time_stamp[i] = datetime.datetime.strptime(time_stamp[i], '%Y-%m-%d %H:%M:%S.%f')


###############################################################################
# Plots
    
# Initialize plotting
fig = plt.figure(1)
a1 = plt.subplot2grid((1,1), (0,0))
a1_title = datetime.datetime.strftime(time_stamp[0], '%Y-%m-%d')
    
# Convert from datetime.datetime to matplotlib.dates for plotting    
for i in range(len(time_stamp)):
    time_stamp[i] = matplotlib.dates.date2num(time_stamp[i])

# Generate plots
a1.step(time_stamp, cu_gun_voltage)
a1.set_xlabel('Time (hour:min:sec)')
a1.set_ylabel('Cu Gun Voltage (unit)')
a1.grid(b=True, which='both', axis='both')
a1.set_title(a1_title)
a1.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%H:%M:%S"))


    
    
    
    
    
    
    
    
    
    
    
    
    
    
    