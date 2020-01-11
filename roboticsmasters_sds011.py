# The MIT License (MIT)
#
# Copyright (c) 2020 Cian Byrne for Robotics Masters Limited
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
`roboticsmasters_sds011`
================================================================================

CircuitPython helper library for SDS011 Pollution Sensor


* Author(s): Cian Byrne

Implementation Notes
--------------------

**Hardware:**

.. todo:: Add links to any specific hardware product page(s), or category page(s). Use unordered list & hyperlink rST
   inline format: "* `Link Text <url>`_"

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

.. todo:: Uncomment or remove the Bus Device and/or the Register library dependencies based on the library's use of either.

# * Adafruit's Bus Device library: https://github.com/adafruit/Adafruit_CircuitPython_BusDevice
# * Adafruit's Register library: https://github.com/adafruit/Adafruit_CircuitPython_Register
"""

import math
from time import sleep
from micropython import const
try:
    import struct
except ImportError:
    import ustruct as struct

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/robotics-masters/CircuitPython_SDS011.git"


_SDS011_HEAD            = b'\xaa'  # message header
_SDS011_TAIL            = b'\xab'  # message tail
_SDS011_CMD_ID          = b'\xb4'  # message ID

_SDS011_CMD_READ        = b'\x00'  # commands are either READ or
_SDS011_CMD_WRITE       = b'\x01'  #  WRITE for the sensor
_SDS011_CMD_REPORT_MODE = b'\x02'  # set work mode
_SDS011_CMD_QUERY       = b'\x04'  # get data base
_SDS011_CMD_SLEEP       = b'\x06'  # sleeps sensor
_SDS011_CMD_WORK_PERIOD = b'\x08'  # set work period

_SDS011_REPORT_ACTIVE   = b'\x00'  # report - active (continuous)
_SDS011_REPORT_PASSIVE  = b'\x01'  # report - passive (requested)

_SDS011_SLEEP_SLEEP     = b'\x00'  # sleep - sleep
_SDS011_SLEEP_WORK      = b'\x01'  # sleep - active/work


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




class SDS011:
    """Driver for Nova SDS011 air quality sensor
       :param int refresh_rate: Maximum number of readings per second. Faster property reads
         will be from the previous reading."""
    def __init__(self, uart, refresh_rate=10):
        self._uart = uart
        self.pm25 = 0
        self.pm10 = 0
        
        # set the initial state of the sensor
        #self.set_sleep(0)
        
        # Check device Firmware Version.
        #if self.firmware_ver() != True:
        #    raise RuntimeError('Failed to find SDS011!')
            
        #self.set_working_period(PERIOD_CONTINUOUS)
        #self.set_mode(MODE_QUERY)
        

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
        
        if checksum == r[4] and r[5] == 0xab:
            crc = True
        else:
            crc = False
        
        #ret = {'Y': r[0], 'M': r[1], 'D': r[2], 'ID': hex(r[3]), 'CRC': crc }
        print("Y: {}, M: {}, D: {}, ID: {}, CRC={}".format(r[0], r[1], r[2], hex(r[3]), "OK" if (checksum==r[4] and r[5]==0xab) else "NOK"))
        return crc
    
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
        print("original: ", d)
        delta = d.encode('hex')
        print('delta: ', delta)
        print(prefix + ' '.join(x.encode('hex') for x in d))
          
    def write(self, cmd, data=[]):
        assert len(data) <= 12
        data += [0,]*(12-len(data))
        checksum = (sum(data)+cmd-2) % 256
        ret = b"\xaa\xb4" + hex(cmd)
        ret += ''.join(hex(x) for x in data)
        ret += b"\xff\xff" + hex(checksum) + b"\xab"
        
        if DEBUG:
            self.dump(ret, '> ')
        
        # write transaction to UART port
        print("transaction: ", ret)
        print("checksum: ", checksum)
        print("command: {0} {1}".format(cmd, chr(cmd)))
        self._uart.write(ret)
    
    def read(self):
        # read from UART port until start byte \aa is found.
        byte = 0
        while byte != "\xaa":
            byte = self._uart.read(1)
            print(byte)

        # read 9 data bytes from UART port.
        d = self._uart.read(9)

        if DEBUG:
            dump(d, '< ')
        # return the 10 bytes from the transaction
        return byte + d
            
    
