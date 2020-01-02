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
