import pyodbc

serv = 'B1904-1\SQLEXPRESS'
db = 'NiowaveDB'


con = pyodbc.connect('Driver={SQL Server};'
                  'Server=' + serv + ';'
                  'Database=' + db + ';'
                  'Trusted_Connection=yes;')

cursor = con.cursor()

sql_query =  'SELECT TOP (11) [Time_Stamp], [Cu Gun Voltage] FROM [NiowaveDB].[dbo].[Amplifiers]'
cursor.execute(sql_query)

for row in cursor:
    print(row)

#Here is a random commented line
    
