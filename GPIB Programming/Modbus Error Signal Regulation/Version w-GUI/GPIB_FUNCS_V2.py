import pyvisa
import time

def freq(Device):
    frequency = Device.query("freq:cw?")
    Device.write("*wai")
    
    return float(frequency)

def write_frequency(Device, Value, Units = "MHZ"):
    Device.write("freq:cw {} {}".format(Value,Units))
    Device.write("*wai")
    
    return

def read_mv(Device, measurement, long = False):
    #value = 1000*float(Device.query("MEASU:MEAS{}:VAL?".format(measurement)).split(' ')[0].strip("\n"))
    if long == False:
        value = 1000*float(Device.query("MEASU:MEAS{}:VAL?".format(measurement)))
        Device.write("*wai")
        return value
    if long == True:
        value = 1000*float(Device.query("MEASU:MEAS{}:VAL?".format(measurement)).split(' ')[1].strip("\n"))
        Device.write("*wai")
        return value

def read_v(Device, measurement, long = True):
    if long == False:
        value = float(Device.query("MEASU:MEAS{}:VAL?".format(measurement)))
        Device.write("*wai")
        return value
    if long == True:
        value = float(Device.query("MEASU:MEAS{}:VAL?".format(measurement)).split(' ')[1].strip("\n"))
        Device.write("*wai")
        return value

def measurement_setup(Device, channel, measurement, scale = False):
    
    if type(channel) and type(measurement) != int:
        print("Must be integers!")
    
    if not scale == False:
        Device.write("CH3:SCA {:.1E}".format())
        
    Device.write("MEASU:MEAS{}:SOURCE1 CH{}".format(measurement, channel))
    Device.write("MEASU:MEAS{}:UNI v".format(measurement))
    Device.write("MEASU:MEAS{}:STATE ON".format(measurement))
    Device.write("MEASU:MEAS{}:TYP MEAN".format(measurement))
    Device.write("*wai")
    time.sleep(2.5)
    return Device.query("MEASU:meas{}:val?".format(measurement))


def channel_settings_check(Device, channel):
    Device.write("SELECT:CH{} 1".format(channel))
    Device.write("HORIZONTAL:SCALE .010")
    Format_String = ':CH{}:SCA 1.0E-2;POS 0.0E0;OFFS 0.0E0;COUP DC;BAN TWE;DESK 0.0E0;IMP MEG;PRO 1.0E0;YUN "V";'.format(channel)#ID "";INV 0'
    if Device.query("CH{}?".format(channel))[:90] != Format_String:
    
        Device.write("CH{}:SCALE .010".format(channel))
        Device.write("CH{}:POSITION 0".format(channel))
        Device.write("CH{}:OFFSET 0".format(channel))
        Device.write("CH{}:COUPLING DC".format(channel))
        Device.write("CH{}:BANDWIDTH TWE".format(channel))
        Device.write("CH{}:DESKEW 0".format(channel))
        Device.write("CH{}:IMPEDANCE MEG".format(channel))
        Device.write("CH{}:PROBE 1".format(channel))
        Device.write("CH{}:YUNIT 'V'".format(channel))
        Device.write("*wai")
        
    return

def trigger_settings_set(Device, channel, level):
    Device.write("SELECT:CH{} 1".format(channel))
    Device.write("CH{}:SCALE .050".format(channel))
    Device.write("CH{}:POSITION -3.00E0".format(channel))
    Device.write("CH{}:OFFSET 0".format(channel))
    Device.write("CH{}:COUPLING DC".format(channel))
    Device.write("CH{}:BANDWIDTH TWE".format(channel))
    Device.write("CH{}:DESKEW 0".format(channel))
    Device.write("CH{}:IMPEDANCE MEG".format(channel))
    Device.write("CH{}:PROBE 1".format(channel))
    Device.write("CH{}:YUNIT 'V'".format(channel))
    Device.write("*wai")
    
    Device.write(":TRIG:A:EDG:SOU CH{0};COUP DC;SLO FALL;:TRIG:A:VID:STAN NTS;SOU CH{0};FIELD ALLL;:TRIG:A:LEV {1:.2E}".format(channel,level))
    return


def vertical_marker_pulsing(Device, channel):
    Device.write("CURS:FUNC VBA")
    Device.write('CURS:VBA:POSITION1 0.0E0')
    Device.write("CURS:VBA:POSITION2 0.0E0")
    Device.write("CURS:VBA:UNI 'V'")
    Device.write("SEL:CONTRO CH{}".format(channel))
    return

def cursor_vbar_read_mv(Device, Cursor = 1):
    try:
        value = 1000*float(Device.query("CURS:VBA:HPOS{}?".format(Cursor)).split(" ")[1])
    except:
        value = 1000*float(Device.query("CURS:VBA:HPOS{}?".format(Cursor)).split(" ")[0])
    return value

def config_reader(file, config_type):
    '''
    LOI: Lines of interest, these are the lines with the data. In them.
    '''
    Lines = []
    try:
        with open(file, 'r') as f:
            for line in f:
                Lines.append(line)
    except:
        print("Error in the filename, please check the file name and make sure it is in the current directory")
        return 
            
    if config_type == "Dipole Scan":
        LOI = Lines[2:10]
        Parameters = []
        for param in LOI:
            if param == "\n":
                continue
            current_param = param.strip("\n").replace(" ","").split(":")
            try:
                if ('Runs' in current_param[0]) or ('count' in current_param[0]):
                    Parameters.append(int(current_param[1]))   
                else:
                    Parameters.append(float(current_param[1]))
            except:
                Parameters.append(current_param[1])
        return Parameters
    
    if config_type == "Dog Leg":
        LOI = Lines[2:10]
        Parameters = []
        for param in LOI:
            if param == "\n":
                continue
            current_param = param.strip("\n").replace(" ","").split(":")
            try:
                if ('Steps' in current_param[0]) or ('count' in current_param[0]):
                    Parameters.append(int(current_param[1]))   
                else:
                    Parameters.append(float(current_param[1]))
            except:
                if (current_param[1].lower() == "false") or (current_param[1].lower() == "true"):
                    Parameters.append('true' in current_param[1].lower())
                else:
                    Parameters.append(current_param[1])
        return Parameters
    
    if config_type == "IF Regulation":
        LOI = Lines[2:20]
        Parameters = []
        for param in LOI:
            if param == "\n":
                continue
            current_param = param.strip("\n").replace(" ","").split(":")
            try:
                if ('Channel' in current_param[0]) or ('Measurement' in current_param[0])\
                or ('size' in current_param[0]) or ('Debounce' in current_param[0]):
                    Parameters.append(int(current_param[1]))   
                else:
                    Parameters.append(float(current_param[1]))
            except:
                if (current_param[1].lower() == "false") or (current_param[1].lower() == "true"):
                    Parameters.append('true' in current_param[1].lower())
                else:
                    Parameters.append(current_param[1])
        return Parameters
    
    if config_type == "Cutoffs":
        LOI = Lines[2:8]
        Parameters = []
        for param in LOI:
            if param == "\n":
                continue
            current_param = param.strip("\n").replace(" ","").split(":")
            try:
                if ('V0' in current_param[0]) or ('sawtooths' in current_param[0]):
                    Parameters.append(int(current_param[1]))   
                else:
                    Parameters.append(float(current_param[1]))
            except:
                if (current_param[1].lower() == "false") or (current_param[1].lower() == "true"):
                    Parameters.append('true' in current_param[1].lower())
                else:
                    Parameters.append(current_param[1])
        return Parameters
    
    if config_type == "Gun Walker":
        LOI = Lines[2:16]
        Parameters = []
        for param in LOI:
            if param == "\n":
                continue
            current_param = param.strip("\n").replace(" ","").split(":")
            try:
                if ('GPIB' in current_param[0]):
                    Parameters.append(int(current_param[1]))   
                else:
                    Parameters.append(float(current_param[1]))
            except:
                if (current_param[1].lower() == "false") or (current_param[1].lower() == "true"):
                    Parameters.append('true' in current_param[1].lower())
                else:
                    Parameters.append(current_param[1])
        return Parameters
    
    print("Error in the type of config file. \n\
Please use one of the following verbose:\n------------\nDipole Scan\nDog Leg\n\
IF Regulation\nCutoffs\nGun Walker\n------------")
    return ""