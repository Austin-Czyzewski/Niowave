Author: Austin Czyzewski
Date: 03/06/2020

README for the Error_Signal_Regulation.py script:

Purpose of the script:
    - A prototype program that demonstrates the capability to automate a monotonous and time-consuming job
        that is currently required whenever running a superconducting cavity. The existence of this program
        has the consequence of allowing the operator to apply themselves to other, more beneficial tasks
        to further aid the primary operator.

Method:
    - Using General Purpose Interface Bus (GPIB) communications between instruments and a dedicated computer,
        this python script will regulate the frequency to make up for what DCFM (Direct current frequency 
        modulation) cannot.
    - The following logic is applied:
  10    - Establish communication with the instruments (Signal generator and Oscilloscope)
            - Currently this is done manually but can be automated by listing available resources
  20    - Gathering the user-defined variables as explained below the Method portion
  30    - Defining functions to use later and make logic and editing more straightforward
  40    - Sets up the measurement that is required on the oscilloscope. This is the mean reading of the 
            user defined channel in order to account for noise filtering and oscillations. This has been
            tested with a noisy signal and with 40 Hz noise and both are compensated for
  50    - BEGINNING THE LOOP
  60    - Take in the current mean value reading from the oscilloscope
  70    - Check if that value is above or below the user-defined threshold (further logic is explained
            for only one case but applies equally to both)
  80        - If above the threshold, the script updates a value called, 'Ups' which tracks how many
                readings have consecutively been above or below the threshold. 
  90        - Once that value is greater than 3, we begin regulation, that regulation acts as:
  100       - Gather the current frequency of the signal generator
  110       - Check to see if the current frequency plus the user-defined step size is above the maximum
                range. If so, break the loop and output error message (Go to 160).
  120       - If the loop isn't broken, write the new frequency which consists of the current frequency plus
                the user-defined step size.
  130       - Do nothing for the user-defined amount of time. 
  140       - Check to see if we have gone more than the user-defined amount of steps in one direction
                without seeing the error signal deviate to the other direction. If so, break the loop
                (Go to 160) and output error message.
  150       - Go back to 60 
  160   - Output error messages
  170   - exit() (i.e. kill the program)

User-defined variables:
    Measurement: This is the measurement number in the oscope of the 4 available channels ; Default = 1
        MUST BE VERIFIED BEFORE BEGINNING
    Channel: Channel that the SRF IF signal is plugged into the oscope ; Default = 3
        MUST BE VERIFIED BEFORE BEGINNING
    Step_size: In Hz, how much do we want to deviate the error signal per regulation step ; Default = 20
    Max_Threshold: In Hz, how much are we going to allow deviation outside of the first gathered
        frequency ; Default = 10000
    Max_one_way_walk: In Hz, How far are we going to allow the signal to deviate in one direction before
        the mean goes into the other direction (i.e. 100 steps up but we never see the singal drop
        below during that time) ; Default = 3000
    Walk_Threshold: In mV, This is the plus or minus that we allow the error signal mean to reach before
        regulation begins. This value cannot be below 1.3 otherwise when SRF power is off, regulation
        will still take place. ; Default = 2.5
    Wait_after_step: In seconds, this is the amount of time we wait after a regulation step has been taken
        to allow the signal to level out. This is an estimate and has not been tested in full
        ; Default = 0.0500 (Conservative value)
    Wait_between_reads: The amount of time taken in between readings, this value effectively controls our
        debounce time before mean deviation and the regulation step is taken. Debounce time = 4x this value
        ; Default = 0.0100 (Chosen to allow oscilloscope to update between readings)
        
Known exception cases that are not handled:
    - Interlocks tripped: This is currently handled via a workaround that when the SRF cavity trips off, the
        voltage reads 1.1 - 1.3 mV on the oscilloscope. This is within our default gating value and is the
        reason that we have the minimum value set here.
    - Pulsing: The current set-up cannot handle any variation of pulsing
    - Oscilloscope measurement changes: Given the overhead of creating the measurement case in every loop,
        there is currently nothing in place to prevent an operator to mess with the measurement parameters
        on the oscilloscope. This could lead to an error in the regulation that wouldn't be immediately 
        obvious. The workaround here is to trust the operator to leave the SRF IF signal mean measurement
        alone.
    - Human intervention on the signal generator: Often times when there is an emergency that relates to
        the pressure on the cavity, the human operating the error signal must make a decision to follow
        error signal (regulate more quickly) or to leave it alone and let it come back naturally. Currently,
        there is no case to handle this and regulation will commence immediately. Additionally, in our
        current setup regulation happens at a given pace that does not depend on the magnitude of deviation,
        only that it is greater or less than our setpoint. In our initial testing, the regulation may be 
        too slow. Another note: for human intervention to occur, regulation must end and the "local" button 
        on the signal generator must be pressed. This is an easy work around by educating the operators on 
        this matter.