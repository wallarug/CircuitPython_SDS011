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
        
        # set the initial state of the sensor
        self.set_sleep(0)
        self.set_mode(0)
        
        # Check device Firmware Version.
        #if self.firmware_ver() != True:
        #    raise RuntimeError('Failed to find SDS011!')

    def set_sleep(self, value):
        """ Set if the sensor is Sleep or Work mode.
              0: Sleep (default)
              1: Work
        """
        mode = _SDS011_SLEEP_WORK if value else _SDS011_SLEEP_SLEEP
        self.write(_SDS011_CMD_SLEEP, mode)
    
    def set_mode(self, value):
        """ Set if the sensor is Active or Passive mode.
              0: Passive (default)
              1: Active
        """
        mode = _SDS011_REPORT_ACTIVE if value else _SDS011_REPORT_PASSIVE
        self.write(_SDS011_CMD_REPORT_MODE, mode)
    
    def set_working_period(self, period):
        """ Set the sensor work period in active mode [0 - 30].
              0 - 30
        """
        assert period >= 0 and period <= 30
        self.write(CMD_WORKING_PERIOD, bytes([period]))
    
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
    
    def query(self):
        """ Helper function for QUERY data """
        # set header for transfer
        cmd = _SDS011_HEAD + _SDS011_CMD_ID

        # process all the data for transfer
        cmd += ( _SDS011_CMD_QUERY + b'\x00' * 12 )
    
        # end of data
        cmd += b'\xff' + b'\xff'

        # checksum and close
        checksum = sum(d for d in cmd[2:]) % 256
        cmd += bytes([checksum]) + _SDS011_TAIL

        # send to uart device
        self._uart.write(cmd)
        
        # process the data returned
        raw = self.reply()
        if raw is None:
            return None  # TODO

        data = struct.unpack('<HH', raw[2:6])
        pm25 = data[0] / 10.0
        pm10 = data[1] / 10.0

        return (pm25, pm10)     

    def write(self, base, mode):
        """ Helper function for REPORT, SLEEP and PERIOD setting """   
        # set header for transfer
        cmd = _SDS011_HEAD + _SDS011_CMD_ID

        # process all the data for transfer
        cmd += ( base + _SDS011_CMD_WRITE + mode + b'\x00' * 10 )

        # end of data
        cmd += b'\xff' + b'\xff'

        # checksum and close
        checksum = sum(d for d in cmd[2:]) % 256
        cmd += bytes([checksum]) + _SDS011_TAIL

        print("command: ", cmd)

        # send to uart device
        self._uart.write(cmd)
        sleep(0.100)

        # read the response and process as required...
        data = self._uart.read(1)
        while data is None:
            data = self._uart.read(1)
            print(data)
            sleep(0.100)
        self.reply()

    def reply(self):

        # wait for reply
        raw = None

        while raw is None:
            raw = self._uart.read(10)
            sleep(0.001)

        if raw is not None:
            data = raw[2:8]

        if (sum(d for d in data) & 255) != raw[8]:
            return None #TODO: also check cmd id

        return raw
    
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
            
    
