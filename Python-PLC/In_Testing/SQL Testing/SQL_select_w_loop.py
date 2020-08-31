import pyodbc
import time

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
# SQL query to select the most recent row 
sql_query = '''
SELECT [Time_Stamp], [Cu Gun Voltage]
FROM (
        SELECT TOP 1 [Time_Stamp], [Cu Gun Voltage]
        FROM [NiowaveDB].[dbo].[Amplifiers]
        ORDER BY [Time_Stamp] DESC
) TAB ORDER BY [Time_stamp]
'''

###############################################################################
# Execute SQL select query inside loop

for i in range(20):
        
    cursor.execute(sql_query)   
    for row in cursor:
        print(time.ctime(), row)
        
        time.sleep(1)

    