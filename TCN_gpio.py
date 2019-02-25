import RPi.GPIO as gpio 
import time

class STM32_power(object):
    ''' Class for turn on or off the power of STM32 '''

    def __init__(self, pin = 4):
        self.pin = pin
        # The input can be BOARD and BCM , refer to definded pin number 
        gpio.setmode(gpio.BCM) 
        # Each time we setup a gpio pin , it will show warning . This disable the waring mechanism
        gpio.setwarnings(False) 
        gpio.setup(self.pin,gpio.OUT)

    def on(self): 
        gpio.output(self.pin,gpio.HIGH)
        print('Turnning on STM32, please wait 2 second')
        time.sleep(2)

    def off(self):
        gpio.output(self.pin,gpio.LOW)
        print("STM32 power off")

class led_yellow(object):
    '''Class for turn on led (pin 17) '''

    def __init__(self, pin = 17):
        self.pin = pin
        # The input can be BOARD and BCM , refer to definded pin number 
        gpio.setmode(gpio.BCM) 
        # Each time we setup a gpio pin , it will show warning . This disable the waring mechanism
        gpio.setwarnings(False) 
        gpio.setup(self.pin,gpio.OUT)    

    def on(self): 
        gpio.output(self.pin,gpio.HIGH)

    def off(self):
        gpio.output(self.pin,gpio.LOW)


     
