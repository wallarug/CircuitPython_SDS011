###  Comparison between drivers
##
import time
import board
import busio

### SDS011
import roboticsmasters_SDS011

uart = busio.UART(board.GROVE_TX, board.GROVE_RX, baudrate=9600)

sensor = roboticsmasters_SDS011.SDS011(uart)

print("set sleep")
sensor.set_sleep(0)

print("set mode")
sensor.set_mode(0)

while True:
    data = sensor.reply()
    print(data)
    time.sleep(10)
