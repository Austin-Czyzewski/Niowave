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