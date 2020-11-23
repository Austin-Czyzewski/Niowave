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
