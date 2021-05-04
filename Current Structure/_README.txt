## Niowave
Austin Czyzewski
04/29/2021
README - process programs for operation -- current file

This directory contains the current active scripts for use in the process
	programs for Operators file. This directory contains files that call
	to this absolute path. Any changes to folder names or file names
	should be accounted for in the following places:
		- Run files for each program at each tunnel
		- Output data sections found scattered throughout each script
			and in the Master.py file.
	If there is trouble finding all of the outlying places where the path is
	coded, contact Austin Czyzewski (or just have him do it from the start).



Hello Traveler,

You've come far and I can see that you are tired. Let me offer you some assistance.

If you are reading this, chances are that you're looking at a bunch of folders and 
	dying to know what's inside of each and every one of them. Well... you're in luck.
	Before we give an overview, let's talk about what YOU should expect to see when 
	going into each of these folders. 

	The layout should track something like this, with some changes according to how
	popular each script is.

	Current:
		- East
			- Configuration Files
			- Run Files
		- Test
			- Configuration Files
			- Run Files
		- West
			- Configuration Files
			- Run Files
		- Output Data
			- East
				- Types of scripts
					- Data
			- West
				- Types of scripts
					- Data
			- Test
				- Types of scripts
					- Data

		- A bunch of .py files
		- This README file

	What this means: To run a dog leg, dipole scan, etc. you first need to select
		the corresponding tunnel, the you will select the run file from there.
		You may need to make changes to how the program operates. This is
		done in the configuration file for that program.
		To find the data for that run, you will navigate to the Output Data
		folder.

The files in this directory as of 04/29/2021 are:
	(that's in mm/dd/yyyy)

	
A file titled: Dog_Leg_V5.py
	Dog Legs are a diagnostic created to take advantage of the geometry of our system.
	This script sweeps two magnets concurrently in opposite directions to move our
	electron beam parallel through the superconducting cavity. This gives us an idea
	of how parallel and centered our beam is through the cavity axis.
	
A file titled: DP1_Scan_V_5.py
	Dipole Scans are a useful diagnostic for our accelerator injector. This program 
	takes advantage of our system design that uses our injector as an energy filter. 
	This script sweeps the current of Dipole One down and back up and records the 
	collected beam at the end of our injector setup (DBA Dump). This program has
	the ability to collect data from either the DBA dump current readback fed
	into the PLC or the attached oscilloscope "Measurement" function.
	(If Ocope: True in the configuration file, this is a run file that 
	must be run from the "GPIB" PC).

A file titled: Gun_Walker.py
	The Gun Walker is a tool purely conceived for convenience. This automates the
	last, sometimes tedious task of putting the Cu Gun in resonance. This process
	assumes that the Cu gun is at operating power, on the 'correct' side of
	resonance. (This is a run file that must be run from the "GPIB" PC).
	
A file titled: Snapshot.py
	This method takes a rapid reading of every currently read value on from the PLC 
	(this is not every PLC tag, only the ones in the corresponding 
	"Tag_Database.py"). This can be useful when operating and more run info is desired
	than just magnet currents.

A file titled: GPIB_FUNCS.py
	This file is a module created for ease-of-use and readability of code using GPIB 
	functions.

A file titled: Master.py
	This is the bread and butter of these programs, and each one needs this file, 
	(hence the name). This file is a large list of functions used in the other
	programs in this directory. This consists of tools to make communicating
	with the PLC intuitive, more readable, and efficient. There are some functions
	in the Master.py file that are not used currently. These are usually remnants of
	some older scripts that never made their way to the big leagues (this directory).
	
Two files: Tag_Database_West.py, Tag_Database_East.py
	These files are the corresponding Tag_Databases for each of the Tunnels. 
	Each one of these contain the names and associated modbus address for 
	the tags listed in the file. This is not every PLC tag used, and only contains
	ones that are commonly used or are deemed useful. The tunnels have different
	physical setups which is why there needs to be seperate tag databases for them.