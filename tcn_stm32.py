'''
Only usable for special motor controller board
whieh core is stm32
'''

import threading
import traceback
import sys
import time
import logging
import serial
from TCN_gpio import Stm32Power
import tcn_shared_variable


'''Initial section of STM32 '''
# stm32 = None
# stm32_client = None
# stm32_run = False



class Stm32Command():
    """ class only use for communicate with STM32 on Raspberry PI 3 """

    # Parameters below can be used for entirly control whole function
    # auto_detect_port = True
    # usb_port_num = 0
    # USB_port_path = "/dev/ttyUSB"
    # baudrate = 115200

    def __init__(self, SharedVariable_STM):
    # def __init__(self, usb_port_path="/dev/ttyUSB", auto_detect_port=True, usb_port_num=0, baudrate=115200, timeout=1):
        '''When "STM32_command" is called, this function automatically run'''
        # Initial parameters 
        logging.basicConfig(filename='STM32_main.log', filemode='w', level=logging.INFO)
        temp = tcn_shared_variable.SharedVariables()
        self.STM = temp.STM


        # Initial process
        self.stm32_power = Stm32Power()
        self.on()
        if self.STM.stm_auto_detect_port:
            self.auto_detect_port()
        else:
            self.ser = serial.Serial(self.STM.usb_port, self.STM.baudrate, serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_ONE, timeout=1)
        self.ser.write([0xFF, 0xFE, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0])



    def run(self):
        '''Run full stm32 system'''

        self.main()
        self.stm32_end()
        self.end_background_thread()


    def main(self):
        '''Main function for stm32'''
        self.start_backgound_thread()
        while self.stm32_run:
            try:
                data_get = self._stm32_client.recv_list()
                # logging.info('Command in : {} \n'.format(data_get))
                self.stm32_portocol(data_get)
            except:
                traceback.print_exc()
                logging.exception("Got error \n")
                self.stm32_run = False
                self.stm32_end()
                self.end_background_thread()


    def stm32_end(self):
        '''just turn off the power of STM32 '''
        print("STM32 power off, please wait 0.5 second")
        self._pin_check = self.stm32_power.off()
        logging.info('STM32 is off \n')

    def end_background_thread(self):
        '''Close back ground thread communication with bridge'''
        self._stm32_thread_client.send_list([self.usb_full_port_path, self.stm32_run, self._pin_check])
        self._stm32_thread_client.close()
        # sys.exit()


    def start_backgound_thread(self):
        '''The background thread for sending status to bridge'''
        logging.info('Backgound thread started')
        thread = threading.Thread(target=self.send_status, daemon=True)
        thread.start()


    def send_status(self):
        '''The background thread for sending status to bridge'''
        while self.stm32_run:
            self._stm32_thread_client.send_list([self.usb_full_port_path, self.stm32_run, self._pin_check])
            time.sleep(0.5)


    def auto_detect_port(self):
        '''Find which port binds to STM32'''
        find_ser = True # This flag determine if the system scan port or not

        try:
            while find_ser:

                # It is very rare that port ID is more than 10
                # Thus cut searching when ID is too much. (Time save)
                if self.STM.usb_port_num > 10:
                    # print('Can not find correct port from 0~10, Please check STM32 connection or STM32 protocol !! \n')
                    self.STM.usb_port_num = 0
                self.STM.usb_port = self.STM.usb_port_path + str(self.STM.usb_port_num)
                # Setup communication with serial port
                # If port not found, trigger IOError
                # If found, test protocol.
                logging.info('Connect to' + str(self.STM.usb_port))
                self.ser = serial.Serial(self.STM.usb_port, self.STM.baudrate, serial.EIGHTBITS,\
                     serial.PARITY_NONE, serial.STOPBITS_ONE, timeout=1)
                logging.info("Number of bytes in input buffer {}".format(self.ser.in_waiting))
                data = bytearray(self.ser.read(12))
                logging.info('USB port return : {}'.format(data))
                # Test protocol
                # Start byte of serial output of STM32 is 0xff, 0xfe,.......
                if data[0] == 255 and data[1] == 254:
                    find_ser = False
                    print("Successfully connect to STM32 controller")

                else:
                    # Scan next port in next loop
                    
                    logging.debug("Number of bytes in input buffer {}".format(self.ser.in_waiting))
                    self.STM.usb_port_num = self.STM.usb_port_num + 1
                    # self.usb_full_port_path = self.usb_port_path + str(self.usb_port_num) 
                    # self.ser.close()
                    self.ser.reset_input_buffer()
                    self.ser.close()

        except IOError:
            # If not found, scan next port and reload this function
            # print('port not found :'+ self.USB_port_PATH)
            self.STM.usb_port_num = self.STM.usb_port_num + 1
            # self.usb_full_port_path = self.usb_port_path + str(self.usb_port_num)
            self.auto_detect_port()
        
        except IndexError:
            # If time out, it may happens that missing array index
            print('IndexError : data missing, scanning next port')
            self.usb_port_num = self.usb_port_num + 1
            # self.usb_full_port_path = self.usb_port_path + str(self.usb_port_num)
            self.auto_detect_port()

    def move(self, car=[0, 0, 0]):
        ''' move car ,car = [x ,y ,z, mode ] , mode = 0 position mode ; mode = 1 velocity mode '''
        car = self.limit_maximum_value(car)
        dir_byte = self.reverse_or_not(car)
        coords = self.change_to_hex(car)
        self.ser.write([0xFF, 0xFE, 1, coords[0], coords[1], coords[2], coords[3], coords[4],\
             coords[5], dir_byte, coords[6], coords[7]])

    def stop(self):
        '''stop motor'''
        self.ser.write([0xFF, 0xFE, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0])




    def on(self):
        '''just turn on the power of STM32 '''
        print('Turnning on STM32, please wait 2 second')
        self._pin_check = self.stm32_power.on()


################################################################################
################################################################################
################################################################################

    def stm32_portocol(self, data_get):
        ''' For interpret message from bridge'''
        if data_get[0] == 'S':
            if data_get[1] == 'exit':
                self.stm32_run = False
                logging.info(" 'exit' command received, start terminating program\n")
            elif data_get[1] == 'xbox_move':
                self.move(data_get[2])
                self._stm32_client.send_list(['S', 'next'])
            elif data_get[1] == 'move':
                self.move(data_get[2])
                self._stm32_client.send_list(['S', 'next'])
                logging.info(" 'move' command received, movie with " + str(data_get[2]) + '\n')
            elif data_get[1] == 'stop':
                self.move([0, 0, 0])
                logging.info(" 'stop' command received, movie with " + str([0, 0, 0]) + '\n')
            elif data_get[1] == 'power_off':
                self.off()
                logging.info(" '{}' command received, power off stm32")
            elif data_get[1] == 'power_on':
                self.on()
                logging.info(" '{}' command received, power on stm32")

        else:
            print(str(data_get) + " received by STM32. Wrong potorcol ! ")
            logging.info(str(data_get) + " received by STM32. Wrong potorcol, please check TCN_bridge.py \n")



    def change_to_hex(self, car):
        ''' Change the value of x, y, z into hex to satisfy the protocol of STM32 controller '''
        x_high_high_byte = int(abs(car[0]) / 65536)
        x_high_byte = int((abs(car[0]) % 65536) / 256)
        x_low_byte = int((abs(car[0]) % 65536) % 256)
        y_high_high_byte = int(abs(car[1]) / 65536)
        y_high_byte = int((abs(car[1]) % 65536) / 256)
        y_low_byte = int((abs(car[1]) % 65536) % 256)
        z_high_byte = int(abs(car[2]) / 256)
        z_low_byte = (abs(car[2]) % 256)
        return x_high_byte, x_low_byte, y_high_byte, y_low_byte, z_high_byte, z_low_byte, x_high_high_byte, y_high_high_byte

    def limit_maximum_value(self, car): 
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

    def reverse_or_not(self, car):
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
        direction_byte = int('00000{}{}{}'.format(xrev, yrev, zrev))
        return direction_byte






###############################
#       Test Program
###############################

class Stm32TestCommunication:
    ''' This class is used for testing Stm32Command '''
    def __init__(self):
        try:
            self.main_flag = False
            self.usb_full_port_path = 0
            self.stm32_program_run = 0
            self.stm32_power = 0

            import tcn_xbox
            import os
            if os.getuid() != 0:
                print('please Run with sudo\n\n')
                sys.exit(0)
            self.xbox = tcn_xbox.XboxController()
            self._stm32_server = tcn_socket.TCP_server(50006)
            self._stm32_thread_server = tcn_socket.UDP_server(50007)
            stm32_data = self._stm32_server.recv_list()
            self.bridge_potorcol(stm32_data)
            self.main_flag = True
            self.main()
        except:
            time.sleep(0.3)
            self._stm32_server.close()
            traceback.print_exc()
            print('Bridge initializing fail at stm32_init()')


    def main(self):
        '''Main for testing'''
        self.bridge_background_thread()
        while self.main_flag:
            try:
                command = input("command or press 'h' for help : ")
                if command == 'exit':
                    self._stm32_server.send_list(['S', 'exit'])
                    print('All server will be close in 3 second')
                    self.main_flag = False
                    time.sleep(3)
                    self._stm32_server.close()
                elif command == 'pf':
                    if self.stm32_power == 1:
                        self._stm32_server.send_list(['S', 'power_off'])
                    else:
                        print('STM32 already power off')
                elif command == 'po':
                    if self.stm32_power == 0:
                        self._stm32_server.send_list(['S', 'power_on'])
                    else:
                        print('STM32 already power on')


                elif command == 'mwx':
                    while not self.xbox.joy.Back():
                        move_command = self.xbox.xbox_control()
                        self._stm32_server.send_list(['S', 'xbox_move', move_command])
                        receive = self._stm32_server.recv_list()
                        self.bridge_potorcol(receive)
                elif command == 'cm':
                    velocity_x = int(input('velocity x '))
                    velocity_y = int(input('velocity y '))
                    velocity_z = int(input('velocity y '))
                    if velocity_x is None:
                        velocity_x = 0
                    if velocity_y is None:
                        velocity_y = 0
                    if velocity_z is None:
                        velocity_z = 0
                    self._stm32_server.send_list(['S', 'move', [velocity_x, velocity_y, velocity_z]])
                    receive = self._stm32_server.recv_list()
                    self.bridge_potorcol(receive)

                elif command == 'stop':
                    self._stm32_server.send_list(['S', 'stop'])

                elif command == 'status':
                    print('stm32 power : {} '.format(self.stm32_power))
                    print('stm32 USB : {}'.format(self.usb_full_port_path))
                    print('stm32 run : {} '.format(self.stm32_program_run))
                elif command == 'h':
                    print('exit   : quit all')
                    print('status : get stm32 info')
                    print('mwx    : move with xbox controller')
                    print('cm     : enter x,y,z velocity, machine keep moving in that direction')
                    print("stop   : stop motor")

                else:
                    print('{} received . Wrong potorcol  !'.format(command))
            except:
                self._stm32_server.send_list(['S', 'exit'])
                self.xbox.close()
                time.sleep(0.3)
                self._stm32_server.close()
                self.main_flag = False
                traceback.print_exc()


    def bridge_background_thread(self):
        '''back ground thread'''
        thread = threading.Thread(target=self.get_status, daemon=True)
        thread.start()


    def get_status(self):
        ''' Get status from stm32'''
        while self.main_flag:
            stm32_status = self._stm32_thread_server.recv_list(8192)
            if stm32_status is not None:
                self.usb_full_port_path = stm32_status[0]
                self.stm32_program_run = stm32_status[1]
                self.stm32_power = stm32_status[2]
            time.sleep(0.5)

    def bridge_potorcol(self, receive_data):
        ''' Interpret message from stm32'''
        if receive_data[0] == 'S':
            if receive_data[1] == 'next':
                pass


if __name__ == "__main__":

    stm = Stm32Command()
    stm.run()
