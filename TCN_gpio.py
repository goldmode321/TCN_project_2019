import RPi.GPIO as gpio 
import time
import TCN_socket as tcns

# The input can be BOARD and BCM , refer to definded pin number 
gpio.setmode(gpio.BCM) 
# Each time we setup a gpio pin , it will show warning . This disable the waring mechanism
gpio.setwarnings(False) 


# Channal for our system to check if everything work well.
tcns.UDP_client(50001)

class STM32_power(object):
    ''' Class for turn on or off the power of STM32 '''

    def __init__(self, pin_power = 4 , pin_check = 27):
        self.pin_power = pin_power
        self.pin_check = pin_check
        gpio.setup(self.pin_power,gpio.OUT)
        gpio.setup(self.pin_check,gpio.IN)

    def on(self): 
        gpio.output(self.pin_power,gpio.HIGH)
        print('Turnning on STM32, please wait 2 second')
        time.sleep(2) # 2 second is for turn on process for STM32
        

    def off(self):
        gpio.output(self.pin_power,gpio.LOW)
        print("STM32 power off, please wait 0.5 second")
        time.sleep(0.5) # Make sure the Relay is off
        print(gpio.input(self.pin_check))

class led(object):
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


     
if __name__ == "__main__":
    STM32_power = STM32_power()
    STM32_power.on()
    STM32_power.off()
