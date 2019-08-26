import TCN_socket
import threading
import traceback
import sys
import time
import logging
import serial
from TCN_gpio import STM32_power 


'''Initial section of STM32 '''
# stm32 = None
# stm32_client = None
# KEEP_RUNNING = False



class STM32_command(object):
    """ class only use for communicate with STM32 on Raspberry PI 3 """
    
    # Parameters below can be used for entirly control whole function
    # AUTO_DETECT_PORT = True
    # USB_PORT_NUM = 0
    # USB_port_path = "/dev/ttyUSB"
    # baudrate = 115200


    def __init__(self, USB_port_path = "/dev/ttyUSB",AUTO_DETECT_PORT = True, USB_port_num = 0, baudrate = 115200, timeout =1):
        '''When "STM32_command" is called, this function automatically run'''
        # Initial parameters 
        logging.basicConfig(filename='STM32_main.log',filemode = 'w',level =logging.INFO)
        self.USB_PORT_NUM = USB_port_num # Initial port to scan (0)
        self.USB_port_path = USB_port_path # Default raspbian tty path is "/dev/ttyUSB"
        self.USB_PORT_PATH = self.USB_port_path + str(self.USB_PORT_NUM) # Full path for scanning USB
        self.BAUDRATE = baudrate # Baudrate for STM32 is 115200. If STM32 configuration changed, this should be change,too
        self.timeout = timeout # How long to wait for USB responses.
        self.KEEP_RUNNING = False


        # Initial process
        self.STM32_power = STM32_power()
        self.on()
        if AUTO_DETECT_PORT:
            self.auto_detect_port()
        else:
            self.ser = serial.Serial(self.USB_PORT_PATH, self.BAUDRATE,serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_ONE, self.timeout)
        self.ser.write([0xFF,0xFE, 1, 0 , 0 , 0 , 0 , 0 , 0 , 0 , 0 , 0 ])
        

    def run(self):
        self.init_socket()
        self.main()
        self.end()
        self.end_background_thread()

    def init_socket(self):
        try:
            logging.info('Successfully connect to STM32 , port : {} \n'.format(self.USB_PORT_PATH))
            self.STM32_CLIENT = TCN_socket.TCP_client(50003)
            self.STM32_BACKGROUND_CLIENT = TCN_socket.UDP_client(50005)
            logging.info('STM32 communication established\n')
            self.STM32_CLIENT.send_list(['S','next'])
            self.KEEP_RUNNING = True
        except:
            traceback.print_exc()
            logging.exception("Got error\n")
            self.end()
            self.end_background_thread()



    def main(self):
        self.start_backgound_thread()
        while self.KEEP_RUNNING:
            try:
                data_get = self.STM32_CLIENT.recv_list()
                # logging.info('Command in : {} \n'.format(data_get))
                self.stm32_portocol(data_get)
            except:
                traceback.print_exc()
                logging.exception("Got error \n")
                self.KEEP_RUNNING = False
                self.end()
                self.end_background_thread()
        

    def end(self):
        self.STM32_CLIENT.close()
        self.off()
        logging.info('STM32 is off \n')

    def end_background_thread(self):
        self.STM32_BACKGROUND_CLIENT.send_list([self.USB_PORT_PATH,self.KEEP_RUNNING,self.PIN_CHECK])
        self.STM32_BACKGROUND_CLIENT.close()
        # sys.exit()        


    def start_backgound_thread(self):
        logging.info('Backgound thread started')
        THREAD = threading.Thread(target = self.send_status , daemon = True)
        THREAD.start()

    
    def send_status(self):
        while self.KEEP_RUNNING:
            self.STM32_BACKGROUND_CLIENT.send_list([self.USB_PORT_PATH,self.KEEP_RUNNING,self.PIN_CHECK])
            time.sleep(0.5)


    def auto_detect_port(self):
        '''Find which port binds to STM32'''
        find_ser = True # This flag determine if the system scan port or not

        try:
            while find_ser:
                
                # It is very rare that port ID is more than 10
                # Thus cut searching when ID is too much. (Time save)
                if self.USB_PORT_NUM > 10:
                    # print('Can not find correct port from 0~10, Please check STM32 connection or STM32 protocol !! \n')
                    self.USB_PORT_NUM = 0
                self.USB_PORT_PATH = self.USB_port_path + str(self.USB_PORT_NUM) 
                # Setup communication with serial port
                # If port not found, trigger IOError
                # If found, test protocol.
                logging.info('Connect to'+str(self.USB_PORT_PATH))
                self.ser = serial.Serial(self.USB_PORT_PATH, self.BAUDRATE,serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_ONE, self.timeout)
                logging.info("Number of bytes in input buffer {}".format(self.ser.in_waiting))
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
                    self.USB_PORT_NUM = self.USB_PORT_NUM + 1
                    # self.USB_PORT_PATH = self.USB_port_path + str(self.USB_PORT_NUM) 
                    # self.ser.close()
                    self.ser.reset_input_buffer()
                    self.ser.close()

        except IOError:
            # If not found, scan next port and reload this function
            # print('port not found :'+ self.USB_port_PATH)
            self.USB_PORT_NUM = self.USB_PORT_NUM + 1
            # self.USB_PORT_PATH = self.USB_port_path + str(self.USB_PORT_NUM)
            self.auto_detect_port()
        
        except IndexError:
            # If time out, it may happens that missing array index
            print('IndexError : data missing , scanning next port')
            self.USB_PORT_NUM = self.USB_PORT_NUM + 1
            # self.USB_PORT_PATH = self.USB_port_path + str(self.USB_PORT_NUM)
            self.auto_detect_port()

    def move(self, car = [0,0,0]):
        ''' move car ,car = [x ,y ,z, mode ] , mode = 0 position mode ; mode = 1 velocity mode '''
        car = self.limit_maximum_value(car)
        dir_byte = self.reverse_or_not(car)
        coords = self.change_to_hex(car)
        self.ser.write([0xFF,0xFE, 1, coords[0] , coords[1] , coords[2] , coords[3] , coords[4] , coords[5] , dir_byte , coords[6] , coords[7] ])

    def stop(self):
        '''stop motor'''
        self.ser.write([0xFF,0xFE, 1, 0 , 0 , 0 , 0 , 0 , 0 , 0 , 0 , 0 ])

    def off(self):
        '''just turn off the power of STM32 '''
        print("STM32 power off, please wait 0.5 second")
        self.PIN_CHECK = self.STM32_power.off()


    def on(self):
        '''just turn on the power of STM32 '''
        print('Turnning on STM32, please wait 2 second')
        self.PIN_CHECK = self.STM32_power.on()


################################################################################
################################################################################
################################################################################

    def stm32_portocol(self,data_get):
        if data_get[0] == 'S':
            if data_get[1] == 'exit':
                self.KEEP_RUNNING = False
                logging.info(" 'exit' command received, start terminating program\n")
            elif data_get[1] == 'xbox_move':            
                self.move(data_get[2])
                self.STM32_CLIENT.send_list(['S','next'])
            elif data_get[1] == 'move':            
                self.move(data_get[2])
                self.STM32_CLIENT.send_list(['S','next'])
                logging.info(" 'move' command received, movie with "+str(data_get[2])+'\n')
            elif data_get[1] == 'stop':
                self.move([0,0,0])
                logging.info(" 'stop' command received, movie with "+str([0,0,0])+'\n')
            elif data_get[1] == 'power_off':
                self.off()
                logging.info(" '{}' command received, power off stm32")
            elif data_get[1] == 'power_on':
                self.on()
                logging.info(" '{}' command received, power on stm32")
        
        else:
            print(str(data_get)+" received by STM32. Wrong potorcol ! ")
            logging.info(str(data_get)+" received by STM32. Wrong potorcol, please check TCN_bridge.py \n")



    def change_to_hex(self,car):
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

    def limit_maximum_value(self,car): 
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

    def reverse_or_not(self,car):
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






###############################
#       Test Program
###############################

class STM32_Test_Communication:
    def __init__(self):
        try:
            self.MAIN_FLAG = False
            self.USB_PORT_PATH = 0
            self.STM32_PROGRAM_RUN = 0
            self.STM32_POWER = 0

            import TCN_xbox
            import os
            if os.getuid() != 0:
                print('please Run with sudo\n\n')
                sys.exit(0)
            self.xbox = TCN_xbox.xbox_controller()
            self.STM32_SERVER = TCN_socket.TCP_server(50003,1)
            self.STM32_BACKGROUND_SERVER = TCN_socket.UDP_server(50005)
            stm32_data = self.STM32_SERVER.recv_list()
            self.bridge_potorcol(stm32_data)
            self.MAIN_FLAG = True
            self.main()
        except:
            time.sleep(0.3)
            self.STM32_SERVER.close()
            traceback.print_exc()
            print('Bridge initializing fail at stm32_init()')


    def main(self):
        self.bridge_background_thread()
        while self.MAIN_FLAG:
            try:
                command = input("command or press 'h' for help : ")
                if command == 'exit':
                    self.STM32_SERVER.send_list(['S','exit'])
                    print('All server will be close in 3 second')
                    self.MAIN_FLAG = False
                    time.sleep(3)
                    self.STM32_SERVER.close()
                elif command == 'pf':
                    if self.STM32_POWER == 1:
                        self.STM32_SERVER.send_list(['S','power_off'])
                    else:
                        print('STM32 already power off')
                elif command == 'po':
                    if self.STM32_POWER == 0:
                        self.STM32_SERVER.send_list(['S','power_on'])
                    else:
                        print('STM32 already power on')


                elif command == 'mwx':
                    while not self.xbox.joy.Back():
                        move_command = self.xbox.xbox_control()
                        self.STM32_SERVER.send_list(['S','xbox_move',move_command])
                        receive = self.STM32_SERVER.recv_list()
                        self.bridge_potorcol(receive)
                elif command == 'cm':
                    x = int(input('velocity x '))
                    y = int(input('velocity y '))
                    z = int(input('velocity y '))
                    if x == None:
                        x = 0   
                    if y == None:
                        y = 0 
                    if z == None:
                        z = 0 
                    self.STM32_SERVER.send_list(['S','move',[x,y,z]])
                    receive = self.STM32_SERVER.recv_list()
                    self.bridge_potorcol(receive)

                elif command == 'stop':
                    self.STM32_SERVER.send_list(['S','stop'])

                elif command == 'status':
                    print('stm32 power : {} '.format(self.STM32_POWER))
                    print('stm32 USB : {}'.format(self.USB_PORT_PATH))
                    print('stm32 run : {} '.format(self.STM32_PROGRAM_RUN))
                elif command == 'h':
                    print('exit   : quit all')
                    print('status : get stm32 info')
                    print('mwx    : move with xbox controller')
                    print('cm     : enter x,y,z velocity, machine keep moving in that direction')
                    print("stop   : stop motor")

                else:
                    print('{} received . Wrong potorcol  !'.format(command))
            except:
                self.STM32_SERVER.send_list(['S','exit'])
                self.xbox.close()
                time.sleep(0.3)
                self.STM32_SERVER.close()
                self.MAIN_FLAG = False
                traceback.print_exc()


    def bridge_background_thread(self):
        THREAD = threading.Thread(target = self.get_status , daemon = True)
        THREAD.start()


    def get_status(self):
        # print('thread run')
        while self.MAIN_FLAG:
            STM32_STATUS = self.STM32_BACKGROUND_SERVER.recv_list(8192)
            if STM32_STATUS != None:
                self.USB_PORT_PATH = STM32_STATUS[0]
                self.STM32_PROGRAM_RUN = STM32_STATUS[1]
                self.STM32_POWER = STM32_STATUS[2]
            time.sleep(0.5)

    def bridge_potorcol(self,receive_data):
        if receive_data[0] == 'S':
            if receive_data[1] == 'next':
                pass



# def init():
#     global stm32,stm32_client,KEEP_RUNNING
#     try:
#         logging.basicConfig(filename='STM32_main.log',filemode = 'w',level =logging.INFO)
#         stm32 = STM32_command()
#         logging.info('Successfully connect to STM32 , port : {} \n'.format(stm32.USB_port_PATH))
#         stm32_client = TCN_socket.TCP_client(50003)
#         logging.info('STM32 communication established\n')
#         stm32_client.send_list(['S','next'])
#         KEEP_RUNNING = True
#     except:
#         traceback.print_exc()
#         logging.exception("Got error\n")
#         stm32_client.close()



#     '''Portocol function'''

# def stm32_portocol(data_get):
#     global stm32,stm32_client,KEEP_RUNNING
#     if data_get[0] == 'S':
#         if data_get[1] == 'exit':
#             KEEP_RUNNING = False
#             logging.info(" 'exit' command received, start terminating program\n")
#         elif data_get[1] == 'move':            
#             stm32.move(data_get[2])
#             stm32_client.send_list(['S','next'])
#             logging.info(" 'move' command received, movie with "+str(data_get[2])+'\n')
#         elif data_get[1] == 'stop':
#             stm32.move([0,0,0])
#             logging.info(" 'stop' command received, movie with "+str([0,0,0])+'\n')
    
#     else:
#         print(str(data_get)+" received by STM32. Wrong potorcol ! ")
#         logging.info(str(data_get)+" received by STM32. Wrong potorcol, please check TCN_bridge.py \n")



#     '''Running section '''

# def main():
#     global stm32,stm32_client,KEEP_RUNNING
#     while KEEP_RUNNING:
#         try:
#             data_get = stm32_client.recv_list()
#             logging.info('Command in : {} \n'.format(data_get))
#             stm32_portocol(data_get)


#         except:
#             traceback.print_exc()
#             logging.exception("Got error \n")
#             stm32_client.close()
#             KEEP_RUNNING = False



#     '''Ending section '''

# def end():
#     stm32_client.close()
#     stm32.off()
#     logging.info('STM32 is off \n')
#     sys.exit(0)

if __name__ == "__main__":
    # init()
    # main()
    # end()
    stm32 = STM32_command()
    stm32.run()
