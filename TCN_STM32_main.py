import TCN_socket
import threading
import traceback
import sys
import time
import logging
import serial
from TCN_gpio import STM32_power 


'''Initial section of STM32 '''
stm32 = None
stm32_client = None
keep_running = False



class STM32_command(object):
    """ class only use for communicate with STM32 on Raspberry PI 3 """
    
    # Parameters below can be used for entirly control whole function
    # AUTO_DETECT_PORT = True
    # USB_port_num = 0
    # USB_port_path = "/dev/ttyUSB"
    # baudrate = 115200


    def __init__(self, USB_port_path = "/dev/ttyUSB",AUTO_DETECT_PORT = True, USB_port_num = 0, baudrate = 115200, timeout =1):
        '''When "STM32_command" is called, this function automatically run'''
        # Initial parameters 
        logging.basicConfig(filename='STM32_main.log',filemode = 'a',level =logging.INFO)
        self.USB_port_num = USB_port_num # Initial port to scan (0)
        self.USB_port_path = USB_port_path # Default raspbian tty path is "/dev/ttyUSB"
        self.USB_port_PATH = self.USB_port_path + str(self.USB_port_num) # Full path for scanning USB
        
        self.baudrate = baudrate # Baudrate for STM32 is 115200. If STM32 configuration changed, this should be change,too
        self.timeout = timeout # How long to wait for USB responses.

        # Initial process
        self.STM32_power = STM32_power()
        self.on()
        if AUTO_DETECT_PORT:
            self.auto_detect_port()
        else:
            self.ser = serial.Serial(self.USB_port_PATH, self.baudrate,serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_ONE, self.timeout)
        self.ser.write([0xFF,0xFE, 1, 0 , 0 , 0 , 0 , 0 , 0 , 0 , 0 , 0 ])



    def auto_detect_port(self):
        '''Find which port binds to STM32'''
        find_ser = True # This flag determine if the system scan port or not

        try:
            while find_ser:
                
                # It is very rare that port ID is more than 10
                # Thus cut searching when ID is too much. (Time save)
                if self.USB_port_num > 10:
                    # print('Can not find correct port from 0~10, Please check STM32 connection or STM32 protocol !! \n')
                    self.USB_port_num = 0
                    # self.STM32_power.off()
                    # sys.exit(0)
                
                # Setup communication with serial port
                # If port not found, trigger IOError
                # If found, test protocol.
                logging.info('Connect to'+str(self.USB_port_PATH))
                self.ser = serial.Serial(self.USB_port_PATH, self.baudrate,serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_ONE, self.timeout)
                # self.ser.reset_input_buffer()

                logging.debug("Number of bytes in input buffer {}".format(self.ser.in_waiting))
                data = bytearray(self.ser.read(12))
                logging.info('USB port return : {}'.format(data))
                # Test protocol
                # Start byte of serial output of STM32 is 0xff, 0xfe,....... 
                if data[0] == 255 and data[1] == 254 : 
                    find_ser = False
                    print("Successfully connect to STM32 controller")

                else:
                    # Scan next port in next loop
                    
                    logging.debug("Number of bytes in input buffer {}".format(self.ser.in_waiting))
                    self.USB_port_num = self.USB_port_num + 1
                    self.USB_port_PATH = self.USB_port_path + str(self.USB_port_num) 
                    # self.ser.close()
                    self.ser.reset_input_buffer()
                    self.ser.close()

        except IOError:
            # If not found, scan next port and reload this function
            # print('port not found :'+ self.USB_port_PATH)
            self.USB_port_num = self.USB_port_num + 1
            self.USB_port_PATH = self.USB_port_path + str(self.USB_port_num)
            self.auto_detect_port()
        
        except IndexError:
            # If time out, it may happens that missing array index
            print('IndexError : data missing , scanning next port')
            self.USB_port_num = self.USB_port_num + 1
            self.USB_port_PATH = self.USB_port_path + str(self.USB_port_num)
            self.auto_detect_port()

    def move(self, car = [0,0,0]):
        ''' move car ,car = [x ,y ,z, mode ] , mode = 0 position mode ; mode = 1 velocity mode '''
        car = limit_maximum_value(car)
        dir_byte = reverse_or_not(car)
        coords = change_to_hex(car)
        self.ser.write([0xFF,0xFE, 1, coords[0] , coords[1] , coords[2] , coords[3] , coords[4] , coords[5] , dir_byte , coords[6] , coords[7] ])

    def stop(self):
        '''stop motor'''
        self.ser.write([0xFF,0xFE, 1, 0 , 0 , 0 , 0 , 0 , 0 , 0 , 0 , 0 ])

    def off(self):
        '''just turn off the power of STM32 '''
        print("STM32 power off, please wait 0.5 second")
        self.pin_check = self.STM32_power.off()


    def on(self):
        '''just turn on the power of STM32 '''
        print('Turnning on STM32, please wait 2 second')
        self.pin_check = self.STM32_power.on()


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



def init():
    global stm32,stm32_client,keep_running
    try:
        logging.basicConfig(filename='STM32_main.log',filemode = 'w',level =logging.INFO)
        stm32 = STM32_command()
        logging.info('Successfully connect to STM32 , port : {} \n'.format(stm32.USB_port_PATH))
        stm32_client = TCN_socket.TCP_client(50003)
        logging.info('STM32 communication established\n')
        # stm32_client.send_list(['S',1,2,3])
        # logging.info("Test connection to communication center,['S',1,2,3'] sent, ['S','T','M',3,2] should be received\n")
        # data_get = stm32_client.recv_list()
        # if data_get == ['S','T','M',3,2]:
        #     keep_running = True
        #     logging.info("['S','T','M',3,2] received , connection test complete. Program start\n")
        # else:
        #     keep_running = False
        #     print('Something wrong for connection check, wrong potorcol')
        #     logging.info(str(data_get)+" . Wrong potorcol, please check TCN_bridge.py , STM32 initial section ; And check TCN_STM32_main.py\n")
        stm32_client.send_list(['S','next'])
        keep_running = True
    except:
        traceback.print_exc()
        logging.exception("Got error\n")
        stm32_client.close()



    '''Portocol function'''

def stm32_portocol(data_get):
    global stm32,stm32_client,keep_running
    if data_get[0] == 'S':
        if data_get[1] == 'exit':
            keep_running = False
            logging.info(" 'exit' command received, start terminating program\n")
        elif data_get[1] == 'move':            
            stm32.move(data_get[2])
            stm32_client.send_list(['S','next'])
            logging.info(" 'move' command received, movie with "+str(data_get[2])+'\n')
        elif data_get[1] == 'stop':
            stm32.move([0,0,0])
            logging.info(" 'stop' command received, movie with "+str([0,0,0])+'\n')
    
    else:
        print(str(data_get)+" received by STM32. Wrong potorcol ! ")
        logging.info(str(data_get)+" received by STM32. Wrong potorcol, please check TCN_bridge.py \n")



    '''Running section '''

def main():
    global stm32,stm32_client,keep_running
    while keep_running:
        try:
            data_get = stm32_client.recv_list()
            logging.info('Command in : {} \n'.format(data_get))
            stm32_portocol(data_get)


        except:
            traceback.print_exc()
            logging.exception("Got error \n")
            stm32_client.close()
            keep_running = False



    '''Ending section '''

def end():
    stm32_client.close()
    stm32.off()
    logging.info('STM32 is off \n')
    sys.exit(0)

if __name__ == "__main__":
    init()
    main()
    end()
