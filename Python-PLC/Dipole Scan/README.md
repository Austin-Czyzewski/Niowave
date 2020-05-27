Greetings, Adventurer,

Congratulations! You have stumbled upon a Scan of Dipole 1!

To Run this software, simply double click on the python file currently named, "DP1_Test_West_V_2_3"

Some things you may need to change in this software, without the assistance of my humble creator, Austin Czyzewski, are the following:

'Runs': this is at default set to 1, this means that the scan will run 1 time, if you want to scan multiple times for more data, simply change this value to
	any non-zero positive integer.

'Dipole_Tag': This is currently set to 22201, which is the Modbus tag for Dipole 1, changing this tag will change the magnet that you are scanning.
	Therefore, if you are looking to see collected current by scanning any different magnet, simply change this tag (You will likely need to change
	the Read_Tag as well as the default is set to the DBA dump)

'Step_size': This is how precise the run will be, the default is 1 mA, be careful, a large step size may not be good for the magnets

'Read': This is the read tag, it is in quotes in case you want to read a value that starts with 0, this is the modbus we are collecting through the scan.

'count': This is the amount of time that the read tag is read and averaged over, the starting value is 20, this is a good median value.
	Increasing this number will increase the amount of time that the script takes to run.

'pulsing_count': Similar to count, this is the amount of data points gathered that we average over. This is only when we are pulsing.
	The script knows when the system is pulsing.

##############################
Moving far down the script now
##############################

*Naming Section*

plt.ylabel: Change the text here to change the y axis label
plt.xlabel: Change the text here to change the x axis label
plt.title: change the name of the plot, the {} brackets indicate the variable they are reading in the .format section of that string
	If you are really confused, grab thine creator or google "Python string formatting"
plt.suptitle: Instead of a legend, I am using a smaller title to indicate that the colors represent differences in the direction of the run

For the table you can either figure it out or grab Austin. If he is not around. Then you must figure it out.

Farewell, and safe travels.
