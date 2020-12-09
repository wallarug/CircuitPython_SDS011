Introduction
============

.. image:: https://readthedocs.org/projects/roboticsmasters-circuitpython-sds011/badge/?version=latest
    :target: https://circuitpython.readthedocs.io/projects/sds011/en/latest/
    :alt: Documentation Status

.. image:: https://img.shields.io/discord/327254708534116352.svg
    :target: https://adafru.it/discord
    :alt: Discord

.. image:: https://github.com/robotics-masters/Roboticsmasters_CircuitPython_SDS011/workflows/Build%20CI/badge.svg
    :target: https://github.com/robotics-masters/Roboticsmasters_CircuitPython_SDS011/actions
    :alt: Build Status

CircuitPython helper library for SDS011 Pollution Sensor


Dependencies
=============
This driver depends on:

* `Adafruit CircuitPython <https://github.com/adafruit/circuitpython>`_

Please ensure all dependencies are available on the CircuitPython filesystem.
This is easily achieved by downloading
`the Adafruit library and driver bundle <https://circuitpython.org/libraries>`_.


Usage Example
=============

.. code-block:: python
import time
import board
import busio

import roboticsmasters_SDS011

uart = busio.UART(board.GROVE_TX, board.GROVE_RX, baudrate=9600)

sensor = roboticsmasters_SDS011.SDS011(uart)

while True:
    data = sensor.query()
    print(data)
    time.sleep(5)
```

Contributing
============

Contributions are welcome! Please read our `Code of Conduct
<https://github.com/robotics-masters/Roboticsmasters_CircuitPython_SDS011/blob/master/CODE_OF_CONDUCT.md>`_
before contributing to help this project stay welcoming.

Documentation
=============

For information on building library documentation, please check out `this guide <https://learn.adafruit.com/creating-and-sharing-a-circuitpython-library/sharing-our-docs-on-readthedocs#sphinx-5-1>`_.
