def convert_to_mms(locs, Delta_1): #Converting the xlabels to mm
    new_list = []
    for i in locs:
        new_list.append(round(i/Delta_1*12,2)) #Our conversion formula
    return new_list

def Delta1_2(locs, Delta_1, Delta_2): #Converting the 1 values to the same displacement in 2
    new_list = []
    for i in locs:
        new_list.append(round(i/Delta_1*Delta_2,2))
    return new_list

def Dog_Leg(Client, WF1H_Tag, WF1V_Tag, WF2H_Tag, WF2V_Tag, Target_1_Tag, \
            Target_2_Tag, Tag_List, WF1H_Start, WF2H_Start, WF1V_Start, WF2V_Start, Read_Steps = 40, \
            Delta_1 = 0.384, Delta_2 = 0.228, Threshold_Percent = 20, count = 20, sleep_time = 0.010, \
            Deviation_Check = 0.001, Zoom_In_Factor = 1, Scale_Factor = 0.91, ):
    
    import Tag_Database as Tags
    
    Emission_Setpoint =  Read(Client, Tags.Emission_Set)
    Emission_Actual =  Read(Client, Tags.Emitted_Current, Average = True, count = count, sleep_time = sleep_time)
    WF1H =  Read(Client, Tags.WF1H)
    WF1V =  Read(Client, Tags.WF1V)
    WF2H =  Read(Client, Tags.WF2H)
    WF2V =  Read(Client, Tags.WF2V)
    WF3H =  Read(Client, Tags.WF3H)
    WF3V =  Read(Client, Tags.WF3V)
    WF4H =  Read(Client, Tags.WF4H)
    WF4V =  Read(Client, Tags.WF4V)
    WF5H =  Read(Client, Tags.WF5H)
    WF5V =  Read(Client, Tags.WF5V)
    DP1 =  Read(Client, Tags.DP1)
    DP2 =  Read(Client, Tags.DP2)
    Sol1 =  Read(Client, Tags.Sol1)
    Sol2 =  Read(Client, Tags.Sol2)
    Sol3 =  Read(Client, Tags.Sol3)
    WF6H_Start =  Read(Client,Tags.WF6H)
    WF7H_Start =  Read(Client,Tags.WF7H)
    WF6V_Start =  Read(Client,Tags.WF6V)
    WF7V_Start =  Read(Client,Tags.WF7V)
    IR_Temp =  Read(Client, Tags.IR_Temp)
    VA_Temp =  Read(Client, Tags.VA_Temp)
    V0_Setpoint =  Read(Client, Tags.V0_SP)
    V0_Read =  Read(Client, Tags.V0_Read)
    Cathode_V =  Read(Client, Tags.Voltage_Read)
    Cathode_I =  Read(Client, Tags.Current_Read)
    Cathode_Z =  Read(Client, Tags.Impedance_Read)
    Cathode_P =  Read(Client, Tags.Power_Read)
    CU_Gun_Pf =  Read(Client, Tags.CU_Pf)
    CU_Gun_Pr =  Read(Client, Tags.CU_Pr)
    CU_Gun_Pt =  Read(Client, Tags.CU_Pt)
    CU_Gun_V =  Read(Client, Tags.CU_V)
    BH_Gun_Pf =  Read(Client, Tags.BH_Pf)
    BH_Gun_Pr =  Read(Client, Tags.BH_Pr)
    BH_Gun_Pt =  Read(Client, Tags.BH_Pt)
    SRF_Pf =  Read(Client, Tags.SRF_Pf)
    SRF_Pr =  Read(Client, Tags.SRF_Pr)
    SRF_Pt =  Read(Client, Tags.SRF_Pt)
    Pulse_Freq =  Read(Client, Tags.Pulse_Frequency)
    Pulse_Duty =  Read(Client, Tags.Pulse_Duty)
    EC =  Read(Client, Tags.Emitted_Current)
    Cu_Gun_Temp =  Read(Client, Tags.Cu_Gun_Temp)
    BH_OC_Temp =  Read(Client, Tags.BH_OC_Temp)
    DBA_Dump_CHWS =  Read(Client, Tags.DBA_Dump_CHWS)
    
    #Move to our starting point
    Ramp_Two(Client, WF1H_Tag, WF2H_Tag, Magnet_1_Stop = WF1H_Start, Magnet_2_Stop = WF2H_Start, Resolution = Read_Steps, sleep_time = sleep_time)
    Ramp_Two(Client, WF1V_Tag, WF2V_Tag, Magnet_1_Stop = WF1V_Start, Magnet_2_Stop = WF2V_Start, Resolution = Read_Steps, sleep_time = sleep_time)
    
    Full_Data_Set = list()
    H_Broken = V_Broken = False #Creating the check tag for the dog leg, starting out as false as no errors could have been raised yet
    Start_Current = (Read(Client, Target_1_Tag, Average = True, count = count,sleep_time = sleep_time) + \
                 Read(Client, Target_2_Tag, Average = True, count = count,sleep_time = sleep_time))
    
    print("Right Displacement")

    ## Each of these are adding our data to a list as instantiated above. These will appear at each data gathering point
    Full_Data_Set.append(Gather(Client, Tag_List, count = count, sleep_time = sleep_time))

    for Right_Steps in range(1, Read_Steps + 1):
        if Right_Steps != 1: #Don't check on the first run due to absence of Window Frame write values
            #Comparing the current value to the last write value, if it is different, this updates the break loop for both Horizontal and Vertical
            if abs(Read(Client,WF1H_Tag) - WF1H_Write_Value) >= Deviation_Check or abs(Read(Client,WF2H_Tag) - WF2H_Write_Value) >= Deviation_Check: #WF1H Check
                H_Broken = V_Broken = True
                print("Loop Broken")
                break   

        WF1H_Write_Value = WF1H_Start + (Delta_1/Read_Steps)*Right_Steps #Calculated value to walk 1 to the right
        WF2H_Write_Value = WF2H_Start - (Delta_2/Read_Steps)*Right_Steps #Calculated value to walk 2 to the left

        #Write(Client, WF1H_Tag, WF1H_Write_Value) #Writing to 1h
        #Write(Client, WF2H_Tag, WF2H_Write_Value) #Writing to 2h
        print(WF1H_Write_Value)
        print(WF2H_Write_Value)

        Full_Data_Set.append(Gather(Client, Tag_List, count = count, sleep_time = sleep_time))
        if abs(Full_Data_Set[-1][5] + Full_Data_Set[-1][6]) < abs(Threshold_Percent*Start_Current*.01): #Checking our threshold
            break
    print("Moving to center")

    Ramp_Two(Client, WF1H_Tag, WF2H_Tag, Magnet_1_Stop = WF1H_Start, Magnet_2_Stop = WF2H_Start, Resolution = Right_Steps//2, sleep_time = sleep_time) #Moves back to the start in hald of the same # of steps taken

    print("Left Displacement")

    Full_Data_Set.append(Gather(Client, Tag_List, count = count, sleep_time = sleep_time))

    for Left_Steps in range(1, Read_Steps + 1):
        if H_Broken or V_Broken == True:
            break
        if Left_Steps != 1: #Don't check on the first run due to absence of Window Frame write values
            #Comparing the current value to the last write value, if it is different, this updates the break loop for both Horizontal and Vertical
            if abs(Read(Client,WF1H_Tag) - WF1H_Write_Value) >= Deviation_Check or abs(Read(Client,WF2H_Tag) - WF2H_Write_Value) >= Deviation_Check: #WF1H Check
                H_Broken = V_Broken = True
                print("Loop Broken")
                break

        WF1H_Write_Value = WF1H_Start - (Delta_1/Read_Steps)*Left_Steps
        WF2H_Write_Value = WF2H_Start + (Delta_2/Read_Steps)*Left_Steps

        #Write(Client, WF1H_Tag, WF1H_Write_Value) #Writing to 1h
        #Write(Client, WF2H_Tag, WF2H_Write_Value) #Writing to 2h
        print(WF1H_Write_Value)
        print(WF2H_Write_Value)

        Full_Data_Set.append(Gather(Client, Tag_List, count = count, sleep_time = sleep_time))

        if abs(Full_Data_Set[-1][5] + Full_Data_Set[-1][6]) < abs(Threshold_Percent*Start_Current*.01): #Checking our threshold
            break

    print("Moving to center")

    Ramp_Two(Client, WF1H_Tag, WF2H_Tag, Magnet_1_Stop = WF1H_Start, Magnet_2_Stop = WF2H_Start, Resolution = Left_Steps//2, sleep_time = sleep_time)

    print("Upward Displacement")

    Full_Data_Set.append(Gather(Client, Tag_List, count = count, sleep_time = sleep_time))

    for Upward_Steps in range(1, Read_Steps + 1):
        if H_Broken or V_Broken == True:
            break
        if Upward_Steps != 1: #Don't check on the first run due to absence of Window Frame write values
            #Comparing the current value to the last write value, if it is different, this updates the break loop for both Horizontal and Vertical
            if abs(Read(Client,WF1V_Tag) - WF1V_Write_Value) >= Deviation_Check or abs(Read(Client,WF2V_Tag) - WF2V_Write_Value) >= Deviation_Check: #WF1H Check
                H_Broken = V_Broken = True
                print("Loop Broken")
                break

        WF1V_Write_Value = WF1V_Start + (Delta_1/Read_Steps)*Upward_Steps
        WF2V_Write_Value = WF2V_Start - (Delta_2/Read_Steps)*Upward_Steps

        #Write(Client, WF1V_Tag, WF1V_Write_Value) #Writing to 1h
        #Write(Client, WF2V_Tag, WF2V_Write_Value) #Writing to 2h
        print(WF1V_Write_Value)
        print(WF2V_Write_Value)

        Full_Data_Set.append(Gather(Client, Tag_List, count = count, sleep_time = sleep_time))

        if abs(Full_Data_Set[-1][5] + Full_Data_Set[-1][6]) < abs(Threshold_Percent*Start_Current*.01): #Checking our threshold
            break

    print("Moving to center")

    Ramp_Two(Client, WF1V_Tag, WF2V_Tag, Magnet_1_Stop = WF1V_Start, Magnet_2_Stop = WF2V_Start, Resolution = Upward_Steps//2, sleep_time = sleep_time)

    print("Downward Displacement")

    Full_Data_Set.append(Gather(Client, Tag_List, count = count, sleep_time = sleep_time))

    for Downward_Steps in range(1, Read_Steps + 1):
        if H_Broken or V_Broken == True:
            break
        if Downward_Steps != 1: #Don't check on the first run due to absence of Window Frame write values
            #Comparing the current value to the last write value, if it is different, this updates the break loop for both Horizontal and Vertical
            if abs(Read(Client,WF1V_Tag) - WF1V_Write_Value) >= Deviation_Check or abs(Read(Client,WF2V_Tag) - WF2V_Write_Value) >= Deviation_Check: #WF1H Check
                H_Broken = V_Broken = True
                print("Loop Broken")
                break

        WF1V_Write_Value = WF1V_Start - (Delta_1/Read_Steps)*Downward_Steps
        WF2V_Write_Value = WF2V_Start + (Delta_2/Read_Steps)*Downward_Steps

        #Write(Client, WF1V_Tag, WF1V_Write_Value) #Writing to 1h
        #Write(Client, WF2V_Tag, WF2V_Write_Value) #Writing to 2h
        print(WF1V_Write_Value)
        print(WF2V_Write_Value)

        Full_Data_Set.append(Gather(Client, Tag_List, count = count, sleep_time = sleep_time))

        if abs(Full_Data_Set[-1][5] + Full_Data_Set[-1][6]) < abs(Threshold_Percent*Start_Current*.01): #Checking our threshold
            break

    print("Moving to center")

    Ramp_Two(Client, WF1V_Tag, WF2V_Tag, Magnet_1_Stop = WF1V_Start, Magnet_2_Stop = WF2V_Start, Resolution = Downward_Steps//2, sleep_time = sleep_time)
    
    now = datetime.today().strftime('%y%m%d_%H%M%S') #Taking the current time in YYMMDD_HHmm format to save the plot and the txt file
    
    Controlled_Magnets = []
    
    Moved_Magnets = [WF1H_Tag, WF1V_Tag, WF2H_Tag, WF2V_Tag]
    variables = vars(Tags)
    for Mag_Tag in Moved_Magnets:
        for item in variables.items():
            if item[1] == Mag_Tag:
                Controlled_Magnets.append(item[0])

    with open(now + ".txt",'w') as f: #Opening a file with the current date and time
        f.write("EC_Setpoint, EC_Read, IR_Temp, VA_Temp, WF1H, WF1V\n")
        f.write("V0_Set, V0_Read, Pulse_Bool, Rise_Threshold, WF2H, WF2V\n")
        f.write("Cathode Voltage, Cathode Current, Cathode Impedance, Cathode Power, WF3H, WF3V\n")
        f.write("Cu Gun Pf, Cu Gun Pr, Cu Gun Pt, Cu Gun V, WF4H, WF4V\n")
        f.write("BH Pf, BH Pr, BH Pt, Pulse Frequency, WF5H, WF5V\n")
        f.write("SRF Pf, SRF Pr, SRF Pt, Pulse Duty, DP1, DP2\n")
        f.write("Sol 1, Sol2, Sol3, Cu Gun T, BH OC T, DBA CHWS\n")
        f.write("{}(A), {}(A), {}(A), {}(A), Avg'd Emitted Current(mA), Avg'd Loop Mid(mA), Avg'd Loop Bypass(mA), Cu Gun (V), SRF Pt (dBm)\n"\
                .format(Controlled_Magnets[0], Controlled_Magnets[1], Controlled_Magnets[2], Controlled_Magnets[3]))
        f.write("{:.4f}, {:.4f}, {:.4f}, {:.4f}, {:.3f}, {:.3f}\n".format(Emission_Setpoint, Emission_Actual, IR_Temp, VA_Temp, WF1H, WF1V))
        f.write("{:.4f}, {:.4f}, {:.4f}, {:.4f}, {:.3f}, {:.3f}\n".format(V0_Setpoint, V0_Read, Pulsing_Status, Threshold_Percent, WF2H, WF2V))
        f.write("{:.4f}, {:.4f}, {:.4f}, {:.4f}, {:.3f}, {:.3f}\n".format(Cathode_V, Cathode_I, Cathode_Z, Cathode_P, WF3H, WF3V))
        f.write("{:.4f}, {:.4f}, {:.4f}, {:.4f}, {:.3f}, {:.3f}\n".format(CU_Gun_Pf, CU_Gun_Pr, CU_Gun_Pt, CU_Gun_V, WF4H, WF4V))
        f.write("{:.4f}, {:.4f}, {:.4f}, {:.4f}, {:.3f}, {:.3f}\n".format(BH_Gun_Pf, BH_Gun_Pr, BH_Gun_Pt, Pulse_Freq, WF5H, WF5V))
        f.write("{:.4f}, {:.4f}, {:.4f}, {:.4f}, {:.3f}, {:.3f}\n".format(SRF_Pf, SRF_Pr, SRF_Pt, Pulse_Duty, DP1, DP2))
        f.write("{:.3f}, {:.3f}, {:.3f}, {:.4f}, {:.4f}, {:.4f}\n".format(Sol1, Sol2, Sol3, Cu_Gun_Temp, BH_OC_Temp, DBA_Dump_CHWS))
        for line in Full_Data_Set:
            f.write(str(line).strip("([])")+'\n') #Writing each line in that file
        f.close() #Closing the file to save it

        Full_Data_Array = np.array(Full_Data_Set) #Converting from a list to an array

    Horizontal_1 = Full_Data_Array[:(Right_Steps + 2 + Left_Steps),0] #Defining the steps on in the horizontal
    Horizontal_2 = Full_Data_Array[:(Right_Steps + 2 + Left_Steps),1]

    Vertical_1 = Full_Data_Array[(Right_Steps + 2 + Left_Steps):,2] #Defining the steps only in the Vertical
    Vertical_2 = Full_Data_Array[(Right_Steps + 2 + Left_Steps):,3]
    Dump_1 = Full_Data_Array[:,5] #Dump 1 all values
    Dump_2 = Full_Data_Array[:,6] #Dump 2 all values
    Emitted_Current = Full_Data_Array[:,4] #Emitted current all values
    Dump_Sum = Dump_1 + Dump_2 #All dump values

    #Dump Sum into percent from start
    Horizontal_Percent = Dump_Sum[:(Right_Steps + 2 + Left_Steps)]/Emitted_Current[:(Right_Steps + 2 + Left_Steps)]*100 #Defining the percents
    Vertical_Percent = Dump_Sum[(Right_Steps + 2 + Left_Steps):]/Emitted_Current[(Right_Steps + 2 + Left_Steps):]*100

    #FWHM of all of our data
    Horizontal_Above, Horizontal_Below, H_Width, Center_Value_1H, H_Goodsum, H_Badsum = FWHM(Horizontal_1, Horizontal_Percent, extras = True) #FWHM Calclations
    Vertical_Above, Vertical_Below, V_Width, Center_Value_1V, V_Goodsum, V_Badsum = FWHM(Vertical_1, Vertical_Percent, extras = True)
    _,_1,_2,Center_Value_2H,_3, _4 = FWHM(Horizontal_2, Horizontal_Percent, extras = True)
    _,_1,_2,Center_Value_2V,_3, _4 = FWHM(Vertical_2, Vertical_Percent, extras = True)


    #Plotting
    plt.figure(figsize = (9,9)) #Changing the figure to be larger

    ax1 = plt.subplot(1,1,1)
    ax1.scatter(Horizontal_1 - Horizontal_1[0], Horizontal_Above, label = 'Horizontal above FWHM',color = 'C0', alpha = 0.75) #Plotting 1H Above FWHM
    ax1.scatter(Horizontal_1 - Horizontal_1[0], Horizontal_Below, label = 'Horizontal below FWHM', color = 'C0', alpha = 0.5, marker = '.') #Plotting 1H below FWHM
    ax1.scatter(Vertical_1 - Vertical_1[0], Vertical_Above, label = 'Vertical above FWHM', color = 'C1', alpha = 0.75) #Plotting 1V above FWHM
    ax1.scatter(Vertical_1 - Vertical_1[0], Vertical_Below, label = 'Vertical below FWHM', color = 'C1', alpha = 0.5, marker = '.') #plotting 1V Below FWHM
    ax1.set_xlabel("Displacement WF6 (Amps)", fontsize = 12) #Setting xlabel
    ax1.set_ylabel("Collection from start (%); ({0:.2f}\u03BCA) collected at start".format(1000*abs(min(Dump_Sum))), fontsize = 12) #Making the y axis label
    ax1.set_title("Dog Leg Taken at " + now, fontsize = 16) #Making the title 
    ax1.legend(bbox_to_anchor = (0.5,0.27), loc = 'upper center') #Adding the legend and placing it in the bottom center of the plot

    ax1.minorticks_on() #Turning on the minor axis
    ax1.grid(True,alpha = 0.25,which = 'both',color = 'gray') #Making the grid (and making it more in the background)

    locs = ax1.get_xticks() #Grabbing the xticks from that axis

    ax2 = ax1.twiny() #Copying axis

    ax2.set_xticks(locs) #Setting xticks to same position
    ax2.set_xticklabels(convert_to_mms(locs, Delta_1, Delta_2)) #Converting to mm
    ax2.xaxis.set_ticks_position('top') # set the position of the second x-axis to top
    ax2.xaxis.set_label_position('top') # set the position of the second x-axis to top
    ax2.spines['top'].set_position(('outward', 0)) #Setting the ticks to go out of graph area
    ax2.set_xlabel('Displacement (mm)', fontsize = 12) #Label
    ax2.set_xlim(ax1.get_xlim()) #Setting to the same limit as prior axis

    ax3 = ax1.twiny() #Repeat for axis 3

    ax3.set_xticks(locs)
    ax3.set_xticklabels(Delta1_2(locs, Delta_1))
    ax3.xaxis.set_ticks_position('bottom') # set the position of the second x-axis to bottom
    ax3.xaxis.set_label_position('bottom') # set the position of the second x-axis to bottom
    ax3.spines['bottom'].set_position(('outward', 40))
    ax3.set_xlabel('Displacement WF7(Amps)', fontsize = 12)
    ax3.set_xlim(ax1.get_xlim())

    col_labels = ['WF6 Start (A)','WF7 Start (A)','FWHM', 'Center (6,7) (A)', 'Sum Above', 'Sum Below'] #Making the table column names
    row_labels = ['Horizontal','Vertical','Params'] #making the table row names
    table_vals = [[round(WF1H_Start,3), round(WF2H_Start,3), round(H_Width,3), "{:.3f}; {:.3f}".format(Center_Value_1H, Center_Value_2H), round(H_Goodsum,1), round(H_Badsum,1)],
                  [round(WF1V_Start,3) , round(WF2V_Start,3), round(V_Width,3), "{:.3f}; {:.3f}".format(Center_Value_1V, Center_Value_2V) , round(V_Goodsum,1), round(V_Badsum,1)],
                  ["Threshold %: {:.0f}".format(Threshold_Percent),"Zoom: {:.2f}".format(Zoom_In_Factor),"Scale: {:.2f}".format(Scale_Factor),
                   "# H Steps: {:.0f}".format(Right_Steps + 2 + Left_Steps),"# V Steps: {:.0f}".format(Upward_Steps + 2 + Downward_Steps), "EC (mA): {:.3f}".format(EC)]] #Setting values

    the_table = plt.table(cellText=table_vals, #Putting the table onto the plot
                      colWidths = [0.13]*6,
                      rowLabels=row_labels,
                      colLabels=col_labels,
                      loc='lower center', zorder = 1) #Putting in the center and in front of all else

    plt.gca().set_ylim(bottom=-2) #Making sure the plot always goes below 0 in the y axis

    plt.tight_layout() #configuring plot to not cut off extraneous objects like title and x axes

    plt.savefig(now + "_graph.svg",transparent = True) #Saving the figure to a plot

    print("This DogLeg took {0:.1f} Seconds to run".format(time.time() - start_time)) #Printing the amount of time the dog leg took

    #plt.show()