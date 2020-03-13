import numpy as np
import Master as M
import Tag_Database as Tags
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.payload import BinaryPayloadBuilder
from pymodbus.constants import Endian
Client = M.Make_Client('10.50.0.10')

Tag_Number = int('00015')-1
    
Payload = Client.read_holding_registers(Tag_Number,2,unit=1)
Tag_Value_Bit = BinaryPayloadDecoder.fromRegisters(Payload.registers, byteorder=Endian.Big, wordorder=Endian.Big)
Tag_Value = Tag_Value_Bit.decode_32bit_float()

print(True == int(Tag_Value))