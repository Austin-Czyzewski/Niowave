def freq(Device):
    '''
    Inputs the signal generator device as already opened by
    resource manager.
    
    Outputs: The frequency of the system in Hz
    
    '''
    
    frequency = Device.query("freq:cw?")
    
    return float(frequency)

def write_frequency(Device, Value, Units = "MHZ"):
    '''
    Inputs: (Device, Value, Units)
        - Device: Signal generator that we have defined by resource manager
        - Value: The frequency of the new signal, units determined by units (Default is MHz)
        - Units: Must be string, can either be (in any case) Mhz, Khz, or Hz
        
    Outputs: Just writes the new frequency
    '''
    
    Device.write("freq:cw {} {}".format(Vaslue,Units))