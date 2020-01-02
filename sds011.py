# The MIT License (MIT)
#
# Copyright (c) 2020 wallarug for Robotics Masters Limited
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""
`sds011` - Nova PM Sensor - PM2.5, PM10 Pollution Sensor
=========================================================================================
CircuitPython driver from Nova PM Sensor - PM2.5, PM10 Pollution Sensor
* Author(s): wallarug
"""
import math
from time import sleep
from micropython import const
try:
    import struct
except ImportError:
    import ustruct as struct


__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/wallarug/CircuitPython_SDS011.git"


DEBUG = 0
CMD_MODE = 2
CMD_QUERY_DATA = 4
CMD_DEVICE_ID = 5
CMD_SLEEP = 6
CMD_FIRMWARE = 7
CMD_WORKING_PERIOD = 8
MODE_ACTIVE = 0
MODE_QUERY = 1
PERIOD_CONTINUOUS = 0


class Nova_SDS011:
    """Driver from SDS011 air quality sensor
       :param int refresh_rate: Maximum number of readings per second. Faster property reads
         will be from the previous reading."""
    def __init__(self, uart, refresh_rate=10):
        self._uart = uart
        self.pm25 = 0
        self.pm10 = 0
        
        # set the initial state of the sensor
        self.set_sleep(0)
        
        # Check device Firmware Version.
        if self.firmware_ver() != True:
            raise RuntimeError('Failed to find SDS011!')
            
        self.set_working_period(PERIOD_CONTINUOUS)
        self.set_mode(MODE_QUERY)
        

    def set_sleep(self, value):
        mode = 0 if value else 1
        self.write(CMD_SLEEP, [0x1, mode])
        self.read()
    
    def set_mode(self, mode=MODE_QUERY):
        self.write(CMD_MODE, [0x1, mode])
        self.read()
    
    def set_working_period(self, period):
        self.write(CMD_WORKING_PERIOD, [0x1, period])
        self.read()
    
    def firmware_ver(self):
        self.write(CMD_FIRMWARE)
        data = self.read()
        r = struct.unpack('<BBBHBB', d[3:])
        checksum = sum(ord(v) for v in d[2:8])%256
        #TODO:  Return something useful.
        crc = False
        
        if checksum = =r[4] and r[5] == 0xab:
            crc = True
        else:
            crc = False
        
        #ret = {'Y': r[0], 'M': r[1], 'D': r[2], 'ID': hex(r[3]), 'CRC': crc }
        return crc
        #print("Y: {}, M: {}, D: {}, ID: {}, CRC={}".format(r[0], r[1], r[2], hex(r[3]), "OK" if (checksum==r[4] and r[5]==0xab) else "NOK"))
    
    def set_id(self, id):
        id_h = (id>>8) % 256
        id_l = id % 256
        
        self.write(CMD_DEVICE_ID, [0]*10+[id_l, id_h])
        self.read()
    
    def query_data(self):
        self.write(CMD_QUERY_DATA)
        d = self.read()
        
        values = []
        
        if d[1] == "\xc0":
            r = struct.unpack('<HHxxBB', d[2:])
            pm25 = r[0]/10.0
            pm10 = r[1]/10.0
            checksum = sum(ord(v) for v in d[2:8])%256
            values = [pm25, pm10]
            
        return values
  
    def dump(self, d, prefix=''):
        print(prefix + ' '.join(x.encode('hex') for x in d))
          
    def write(self, cmd, data=[]):
        assert len(data) <= 12
        data += [0,]*(12-len(data))
        checksum = (sum(data)+cmd-2) % 256
        ret = "\xaa\xb4" + chr(cmd)
        ret += ''.join(chr(x) for x in data)
        ret += "\xff\xff" + chr(checksum) + "\xab"
        
        if DEBUG:
            self.dump(ret, '> ')
        
        # write transaction to UART port
        self._uart.write(ret)
    
    def read(self):
        # read from UART port until start byte \aa is found.
        byte = 0
        while byte != "\xaa":
            byte = self._uart.read(1)

        # read 9 data bytes from UART port.
        d = self._uart.read(9)

        if DEBUG:
            dump(d, '< ')
        # return the 10 bytes from the transaction
        return byte + d
            
    
    
