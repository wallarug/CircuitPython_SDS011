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
        
        """Check the BME680 was found, read the coefficients and enable the sensor for continuous
           reads."""
        self._write(_BME680_REG_SOFTRESET, [0xB6])
        time.sleep(0.005)

        # Check device ID.
        chip_id = self._read_byte(_BME680_REG_CHIPID)
        
    def set_sleep(value):
        mode = 0 if value else 1
        self._write(CMD_SLEEP, [0x1, mode])
        self._read()
    
    def set_mode(mode=MODE_QUERY):
        self._write(CMD_MODE, [0x1, mode])
        self._read()
    
    def set_working_period(period):
        self._write(CMD_WORKING_PERIOD, [0x1, period])
        self._read()
    
    def firmware_ver():
        self._write(CMD_FIRMWARE)
        data = self._read()
        r = struct.unpack('<BBBHBB', d[3:])
        checksum = sum(ord(v) for v in d[2:8])%256
        #TODO:  Return something useful.
        print("Y: {}, M: {}, D: {}, ID: {}, CRC={}".format(r[0], r[1], r[2], hex(r[3]), "OK" if (checksum==r[4] and r[5]==0xab) else "NOK"))
    
    def set_id(id):
        id_h = (id>>8) % 256
        id_l = id % 256
        
        self._write(CMD_DEVICE_ID, [0]*10+[id_l, id_h])
        self._read()
    
    def query_data():
        self._write(CMD_QUERY_DATA)
        d = self._read()
        
        values = []
        
        if d[1] == "\xc0":
            r = struct.unpack('<HHxxBB', d[2:])
            pm25 = r[0]/10.0
            pm10 = r[1]/10.0
            checksum = sum(ord(v) for v in d[2:8])%256
            values = [pm25, pm10]
            
        return values
  
    def dump(d, prefix=''):
        print(prefix + ' '.join(x.encode('hex') for x in d))
        
    
    def _write(cmd, data=[]):
        assert len(data) <= 12
        data += [0,]*(12-len(data))
        checksum = (sum(data)+cmd-2) % 256
        ret = "\xaa\xb4" + chr(cmd)
        ret += ''.join(chr(x) for x in data)
        ret += "\xff\xff" + chr(checksum) + "\xab"
        
        if DEBUG:
            self.dump(ret, '> ')
        
        # TODO: write to UART port
        self._uart.write(ret)
    
    def _read():
        # TODO: read from UART port
        data = self._uart.read()
        byte = 0
        while byte != "\xaa":
            byte = ser.read(size=1)

        d = ser.read(size=9)

        if DEBUG:
            dump(d, '< ')
        return byte + d
            
    
    
