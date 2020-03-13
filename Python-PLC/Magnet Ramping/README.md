(Please excuse the lack of sarcasm)

USER MANUAL-- RAMPDOWN.PY, MAG_LOAD.PY

############################################################################
Rampdown.py:
############################################################################


Short & Sweet:
	Execute the file, this will ramp all of the magnets down to zero, this will take a few minutes.
	
Likely changes to be made with a new system:

Client-- to change the modbus IP address, go down to the line, "Client = M.Make_Client('192.168.1.2')"
	Update the name, keeping the quotes, to update the IP address.
	

On a new system, if there are more or less window frames, solenoids, or dipoles, edit the lines that read

WFHnum = 21 #The number of horizontal window frames to control
WFVnum = 21 #The number of vertical window frames to control
DPnum = 8 #The number of Dipoles
Solnum = 9 #Number of solenoids

The loops that create the tag names may need to be altered if Modbus tags are no longer being used.
In the loops you may want to adjust the step size taken, this is the change in amperage and typically the GUI will show 2 to 3 of these per step (PLC updates faster than GUI)
The step sizes are chosen to be conservative and safe, beware when changing these.

############################################################################
Mag_Load.py:
############################################################################

Short & Sweet:
	This file must be executed in the command line, when doing so, you will be prompted with the following message, "Which Magnet save to load? (YYMMDD_HHMM) ""
	This is referring to the magnet saves as created by python. These are not found in this folder, for both clutter and safety sakes (don't want to accidentally ramp down the magnets)
	
	Simply input the file name without the .xlsx extension
	
	Example: Which Magnet save to load? (YYMMDD_HHMM) " 191212_1049
	
	Notes: You must include the underscore, and you ,must have the filename correct for it to read
	
Likey changes to be made:

Same as the changes mentioned above. Since this must be executed in the command line, no safety prompt is required.

Special notes with formatting:

print("Window Frame {} V".format(i+1),Vnums[i],excel_as_df['WF V'].iloc[i])
M.Ramp_One_Way(Client, Vnums[i],excel_as_df['WF V'].iloc[i],Max_Step = 0.010)

Element breakdown of the above lines:

print - prints the function, standard
"Window Frame {} V".format() Here the {} brackets indicate which variable to print
Vnums[i] this is telling the loop which tag we are writing to now, using the same indexing number as the next variable, excel_as_df, to ensure that we are writing to the correct magnet
excel_as_df['WF V'].iloc[i] excel_as_df is the stored dataframe, we are accessing only the column named, "WF V", the row that we are accessing is i so we have dataframe -> column -> row
