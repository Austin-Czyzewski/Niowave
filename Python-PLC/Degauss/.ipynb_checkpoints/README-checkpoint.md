No lollygagging!

This program is to degauss the magnets

Good job. You did it.

Have fun, be safe, and remember: Only YOU can prevent magnetfires.

If you want to change some things, I did not make this program quite as intuitive as the others.

First thing's first:

plot = True will produce a plot after we are done running, just for your own happiness. Or, more importantly, when you are
  trying to change or improve the decay time.
  
testing = True will deactivate the functionality that communicates with the PLCs. This can be useful for...idk... testing.

All of the Amplitudes can be scaled varying by the magnet type. Will be adding functionality to scale differently based on secition
 but, if you are taking the time to read this, you can also do this yourself (so I don't have to test and approve the new version)
 by simply adding a conditional statement in the Dipole Amplitude lists that may change by an additional factor. I don't care, do what
 you want.
 
Points will change the real world time that this takes to run, NOT the amount of peaks or any decay parameters.

This code can be pretty useful... If we use it. However, I would much rather use a version that is integrated into our
ladder logic for interlock reasons (I do not want to add the overhead to every single python script I run to check for broken interlocks)

Seriously, though, the 5 minute run time is fine. You can deal with it. Click the button to run this and go make sure your radiation signs
are posted correctly or something. Alternatively, you could clean the area around you and improve it. Up to you, no judgement,
I am not your boss. But remember, things run a lot better if you don't change any of the key parameters.

All the best, 

Your friendly neighborhood pythoner programmer accelerator engineer, 

Austin Czyzewski

:)
