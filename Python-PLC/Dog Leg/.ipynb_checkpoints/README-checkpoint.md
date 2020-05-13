Wha! Hello there, it seems that you have fallen upon the code the will scissor two magnets.
  This scissoring is done to center a parallel beam through our superconducting cavity.

This is something that we refer to as a dog leg, because of the movement of the beam throughout
  this process. I like to call it my leg, as I was an adventurer once... until I took an arrow to the knee.
  
  
In this script you will find a lot going on. This is one of our larger scripts as it must contain a plethora of
  safety features. Some of these features are the following:
  
  - If a human interacts with the magents that are scanning, the program will stop running
  - We can set a threshold of collection as to not slam beam into the walls of our superconducting cavity
  
There are quite a few things that are written in as variables, and they are covered in the file through comments.

However, as Iceberg Slim would appreciate, here's a rundown:

Before any loops begin we define the client, which tells us where our PLCs (Programmable Logic Controllers are)
  this will vary by each system (and even the same system when we feel like it)

The target tags, what these are is the two dumps that collect our electron beam at the other end of our beamline
  these are summed together as collection lost on the main dump doesn't mean we are scraping in the cavity (which
  is what we're looking for)
  
The threshold percent is that percentage that was mentioned earlier and is used to turn the beam around if we dip below the threshold.

Zoom_In_Factor: I created this factor to zoom in on any artifacts or regions of interest that we may encounter.

Read_steps is the amount of steps that we take to get our deltas that we can see below.
Count is the number fo data points at each step that we take and average over, this is variable so that we can pulse beam.
sleep time is the amount of milliseconds that we sleep for between each count. This has a minimum to get rid of 
  redundant reads from the PLC.
  
Delta6&7: These values create a ratio and breadth of our beamline as calculated from the strength and seperation of our 
  magnets. Since these values are calculated, it is not a bad idea to go over them and check the calculation again.
  
  
Everything else is just the script. This will output a plot, it will save the plot, and it will output a txt file.
  This txt file will be hard to interpret because I am bad at getting rid of parentheses before saving. 


Recent Updates: Dog_Leg_V2_1
	- Added the info table with FWHM Calculations 
	- Added FWHM plotting differences
	- Added the ability to move to the optimal point as calculated by the FWHM
	- Added a column to the data table of the emitted current for normalization
    
Logic Walkthrough (Not by line):
10 - Load in the Client
20 - Define the tags we will be moving, the parameters we will be using
30 - Take beginning readings
40 - Lay out the data format
50 - Take first data point
60 - Begin loop for user defined steps, this is moving to the right
70 - check to see if user has broken the loop, if yes skip to 220
80 - Calculate the new values for the two magnets we are moving
90 - Write the new values for the two magnets we are moving
100 - Take the data, store into the data list
110 - Check if we are below threshold for collection if so move to 120 if not move back to 70 and repeat 
120 - Walk quickly back to the start values using both magnets simultaneously
130 - Take first data point
140 - Begin loop for user defined steps, this is moving to the left
150 - check to see if user has broken the loop, if yes skip to 220
160 - Calculate the new values for the two magnets we are moving
170 - Write the new values for the two magnets we are moving
180 - Take the data, store into the data list
190 - Check if we are below threshold for collection if so move to 200 if not move back to 150 and repeat 
200 - Quickly move back to the center
210 - Repeat these same steps upwards and downwards
220 - Take the current time and date
230 - Write a txt file with all data taken, name it the current date and time in yymmdd_hhmm.txt format
240 - Extract each column of the data and store into their own arrays
250 - Calculate the percent collected as a fraction of that emitted, normalized to each emitted point
260 - Calculate the FWHM for each of the dog leg curves
270 - Plot the curves, use the data calculated and the ratios of magnets to display the displacement values
280 - set graphing parameters
290 - Check if we want to move to optimum point after the dog leg, if so, then move there
300 - Show the plot