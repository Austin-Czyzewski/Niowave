## Niowave

Hello Traveler,

You have come far and I can see that you are tired. Let me offer you some assistance.

In this directory you will find the following items as of 06/29/2020 (that's in mm/dd/yyyy):	
	
A folder titled: Amp Scraper
	This project is intended to do a simple web scrape of a GUI output of a technologix
	amplifier. This program reads the values from the XML file that the amplifier outputs
	and pushes them to a PLC where ladder logic takes over and controls interlocks and 
	reports relevant values

A folder titled: DeGuass
	This is a simple script to degauss magnets in the system. This is to offset inconsistancies
	caused by magnet hysteresis. This program walks all the magnets connected to the PLC through 
	a decaying sin function until reaching zero. 
	
A folder titled: Dipole Scan
	Dipole Scans are a useful diagnostic for our accelerator injector. This program takes 
	advantage of our system design that uses our injector as an energy filter. This script
	sweeps the current of a magnet down and back up and records the collected beam at the 
	end of our injector setup. This has become a daily tool for operation.

A folder titled: Dog Leg
	Dog Legs are another diagnostic created to take advantage of the Geometry of our system. 
	This script sweeps two magnets concurrently in opposite directions to move our electron
	beam parallel through the superconducting cavity. This gives us an idea of how parallel
	and centered our beam is through the cavity axis.
	
A folder titled: East Tunnel
	An adaption of most of the daily scripts to run on our second system that has some minor design variations.
	
A folder titled: In_Testing
	This folder contains various scripts that are in the testing phase. This is primarily used
	for troubleshooting and the beginnings of version improvements.
	
A folder titled: Magnet Ramping
	This folder contains a project that stood in only for a few weeks. This was a temporary fix
	for a problem that operators faced with new updates to the GUI or Logic of the PLC's where 
	all of our magnets would be turned off and it would waste time to ramp them up. This was created 
	to load in a magnet save and ramp the magnets to the new values, it still took some time but saved
	many man-hours.
	
A folder titled: Magnet Saves
	This folder holds a dear place in my heart, and this is where this whole project began. This 
	started with an impromptu way to save magnet settings as a quick fix and the potential grew.
	
	
A python file named Master:
	This is a python file and acts as a library for other programs
	listed in the files below. In this file you will find the functions called in other
	programs. The purpose of these functions is to make the code modular and easier to adapt.
	
A python file named Master_All_Versions:
	Similar to Master, this contains functions from different versions of testing and minor
	side projects. This file is here to act as a quick reference for the continuation of
	long forgotten work.

A pytho file named Tag_Database:
	This simple script contains the modbus address for all commonly used tags in our system.
	The introduction of this script is to make the code more modular, future-proof, and readable.
	This document is update with changes in the PLCs and additions of new functionality (see Amp_Scraper.py).
	
A word document titled: future projects
	This document contains ramblings and ideas about future ideas with python as a modbus communicator.

