


import serial
import sys
from TCN_gpio import STM32_power 



class STM32_command(object):
    """ class for communicate with STM32 on Raspberry PI 3 """
    
    # Parameters below can be used for entirly control whole function
    # AUTO_DETECT_PORT = True
    # USB_port_num = 0
    # USB_port_path = "/dev/ttyUSB"
    # baudrate = 115200


    def __init__(self, USB_port_path = "/dev/ttyUSB",AUTO_DETECT_PORT = True, USB_port_num = 0, baudrate = 115200, timeout =1):

        # Initial parameters 
        self.USB_port_num = USB_port_num
        self.USB_port_path = USB_port_path
        self.USB_port_PATH = self.USB_port_path + str(self.USB_port_num)
        self.baudrate = baudrate
        self.timeout = timeout

        # Initial process
        self.STM32_power = STM32_power()
        self.STM32_power.on()
        if AUTO_DETECT_PORT:
            self.auto_detect_port()
        else:
            self.ser = serial.Serial(self.USB_port_PATH, self.baudrate,serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_ONE, self.timeout)



    def auto_detect_port(self):
        
        find_ser = True

        try:
            while find_ser:
                
                # It is very rare that port ID is more than 10
                # Thus cut searching when ID is too much.
                if self.USB_port_num > 10:
                    print('Can not find correct port from 0~10, Please check STM32 connection or STM32 protocol !! \n')
                    self.STM32_power.off()
                    sys.exit(0)
                
                # Setup communication with serial port
                # If port not found, trigger IOError
                # If found, test protocol.
                print('Connect to'+str(self.USB_port_PATH))
                self.ser = serial.Serial(self.USB_port_PATH, self.baudrate,serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_ONE, self.timeout)
                data = bytearray(self.ser.read(12))
                
                # Test protocol
                # Start byte of serial output of STM32 is 0xff, 0xfe,....... 
                if data[0] == 255 and data[1] == 254 : 
                    find_ser = False
                    print("Successfully connect to STM32 controller")
                else:
                    # Scan next port in next loop
                    self.USB_port_num = self.USB_port_num + 1

        except IOError:
            # If not found, scan next port and reload this function
            print('port not found :'+ self.USB_port_PATH)
            self.USB_port_num = self.USB_port_num + 1
            self.USB_port_PATH = self.USB_port_path + str(self.USB_port_num)
            self.auto_detect_port()
        
        except IndexError:
            # If time out, if may happens that missing array index
            print('IndexError : data missing , scanning next port')
            self.USB_port_num = self.USB_port_num + 1
            self.USB_port_PATH = self.USB_port_path + str(self.USB_port_num)
            self.auto_detect_port()

    def move(self, car = [0,0,0,1]):
        ''' car = [x ,y ,z, mode ] , mode = 0 position mode ; mode = 1 velocity mode '''
        car = limit_maximum_value(car)
        dir_byte = reverse_or_not(car)
        coords = change_to_hex(car)
        self.ser.write([0xFF,0xFE, car[3], coords[0] , coords[1] , coords[2] , coords[3] , coords[4] , coords[5] , dir_byte , coords[6] , coords[7] ])
        
################################################################################
################################################################################
################################################################################

def change_to_hex(car):
    ''' Change the value of x, y, z into hex to satisfy the protocol of STM32 controller '''
    xhh = int(abs(car[0])/65536)
    xh = int((abs(car[0])%65536)/256)
    xl = int((abs(car[0])%65536)%256)
    yhh = int(abs(car[1])/65536)
    yh = int((abs(car[1])%65536)/256)
    yl = int((abs(car[1])%65536)%256)
    zh = int(abs(car[2])/256)
    zl = (abs(car[2])%256)

    return xh,xl,yh,yl,zh,zl,xhh,yhh

def limit_maximum_value(car): 
    ''' This function limit the value of x,y,z '''
    if car[0] >= 16777215:
        car[0] = 16777215
    if car[0] <= -16777215:
        car[0] = -16777215

    if car[1] >= 16777215:
        car[1] = 16777215
    if car[1] <= -16777215:
        car[1] = -16777215

    if car[2] >= 16777215:
        car[2] = 16777215
    if car[2] <= -16777215:
        car[2] = -16777215
    return car

def reverse_or_not(car):
    ''' This generate direction byte for STM32 depends on the direction of x,y,z'''

    #Direction X
    if car[0] < 0:
        xrev = 1
    if car[0] >= 0:
        xrev = 0
    #Direction Y
    if car[1] < 0:
        yrev = 1
    if car[1] >= 0:
        yrev = 0
    #Direction Z
    if car[2] < 0:
        zrev = 1
    if car[2] >= 0:
        zrev = 0
    direction_byte = int('00000{}{}{}'.format(xrev,yrev,zrev))
    return direction_byte


