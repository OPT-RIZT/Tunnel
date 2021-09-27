import RPi.GPIO as gpio
import time
from threading import Thread
from PyQt5.QtCore import pyqtSignal

class gpio():
    pin1 = 17
    pin2 = 18
    IO_Signal = pyqtSignal()
    def __init__(self):
        gpio.setmode(gpio.BCM)
        gpio.setup(self.pin1, gpio.OUT)
        gpio.setup(self.pin2, gpio.IN)

    def set_pin1_high(self):
        gpio.output(self.pin1 , gpio.HIGH)
    def set_pin1_low(self):
        gpio.output(self.pin1 , gpio.LOW)
    def start_input(self):
        read = Thread(target=self.IO_recv)
        read.start()
    def IO_recv(self):
        if gpio.input(self.pin2) == gpio.LOW:
            #要加防抖代码
            self.IO_Signal.emit()
        else:
            time.sleep(0.1)

#PIN = 17 shi banzishang de GPIO 1,pin=18 shi banzishangde GPIO2




    
