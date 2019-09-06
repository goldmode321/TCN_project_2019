#!/usr/bin/python3
''' Bridge, also known as communication center, used to store and
    transfer data and command '''
import time
import traceback
import subprocess
import threading
import logging
import tcn_xbox
import tcn_socket

class Bridge:
    '''Communication center Bridge(auto_start=True)'''
    def __init__(self, auto_start=True):
        '''If auto_start is False, program automatically run __init__ only'''
        logging.basicConfig(filename='Bridge.log', filemode='w', level=logging.INFO)

        # Bridge initial variables
        self.auto_start = auto_start
        self.bridge_run = False

        # XBOX initial variables
        self.xbox_run = False
        self.xbox_x = 0
        self.xbox_y = 0
        self.xbox_z = 0
        self.xbox_step = 0
        self.xbox_move_stm32 = False
        self.xbox_on = False
        self.xbox_thread = None

        # Commander initail variables
        self.commander_server_run = False

        # Vision initial variables
        self.vision_x = 0
        self.vision_y = 0
        self.theta = 0
        self.vision_status = 0
        self.vision_data = []
        self.vision_client_run = False
        self.vision_server_run = False
        self.vision_thread_server_run = False
        self.vision_thread_server_status = 0
        self.vision_thread_client_run = False
        self.bridge_show_vision_data_run = False
        self.vision_thread = None

        # Lidar initial variables
        self.lidar_data = []
        self.lidar_server_run = False
        self.lidar_thread_server_run = False
        self.lidar_thread_server_status = 0
        self.lidar_usb_port = ""
        self.lidar_client_run = False
        self.lidar_thread_client_run = False
        self.lidar_thread = None

        # STM32 inital variables
        self.stm32_server_run = False
        self.stm32_thread_server_run = False
        self.stm32_thread_server_status = 0
        self.stm32_usb_port_path = ""
        self.stm32_program_run = 0
        self.stm32_power = 0
        self.stm32_thread = None

        # Algorithm initial variables
        self.algorithm_run = False

        if self.auto_start:
            self.xbox_init()
            self.commander_init()
            self.vision_init()
            self.lidar_init()
            self.stm32_init()
            self.commander_server.send_list(['C', 'next'])
            self.bridge_main()


############ XBOX initialize #########
    def xbox_init(self):
        '''Connect to XBOX controller'''
        self.xbox = tcn_xbox.XboxController()
        self.xbox_on = True

    def xbox_get_data(self):
        '''Xbox run in back ground'''
        self.xbox_thread = threading.Thread(target=self.xbox_main, daemon=True)
        self.xbox_thread.start()


    def xbox_main(self):
        '''Get XBOX data'''
        self.xbox_run = True
        while self.xbox_run:
            move_command = self.xbox.xbox_control()
            self.xbox_x = move_command[0]
            self.xbox_y = move_command[1]
            self.xbox_z = move_command[2]
            self.xbox_step = move_command[3]
            if self.xbox_move_stm32:
                self.stm32_server.send_list(['S', 'xbox_move', [self.xbox_x, self.xbox_y, self.xbox_z]])
                self.stm32_server.recv_list()
            time.sleep(0.01)

    def end_xbox(self):
        '''Close XBOX connection'''
        self.xbox_run = False
        self.xbox_move_stm32 = False
        self.xbox_on = False
        self.xbox.close()



############### Commander TCP Client Version ###############

    def commander_init(self):
        '''Initialize communication with tcn_main'''
        try:
            time.sleep(0.2) # Make sure server initialize first
            logging.info("Initialize commander client\n")
            self.commander_udp_server = tcn_socket.UDP_server(50001)
            self.commander_server = tcn_socket.TCP_client(50000)
            self.commander_server.send_list(['C', 'next'])
            logging.info("Commander connection complete !\n")
            self.commander_server_run = True
        except:
            self.end_commander_server()
            print('\nError from Bridge : commander_init\n')
            traceback.print_exc()
            print('\n Commander is not initialize')
            logging.info('Bridge initializing fail at commander_init()\n')
            logging.exception("Got error : \n")

    def end_commander_server(self):
        '''End commander server'''
        self.commander_udp_server.close()
        self.commander_server.close()
        self.commander_server_run = False
        logging.info('End commander client')


################## Vision ##############

    def vision_init(self):
        '''Initialize vision system and communication '''
        try:
            logging.info("Initialize vision server\n")
            subprocess.Popen('python3 tcn_vision.py', shell=True, start_new_session=True)
            self.vision_thread_server = tcn_socket.UDP_server(50003)
            self.vision_server = tcn_socket.TCP_server(50002)
            receive = self.vision_server.recv_list()
            if receive == ['V', 'status', 'Alive']:
                logging.info("Vision communication successfully established !\
                    \ncommunication center get : {} \n".format(receive))
                self.vision_server_run = True
                self.vision_thread_server_run = True
                self.vision_start_background_thread()
            else:
                self.end_vision_server()
                self.end_vision_thread_server()
                print('{} received from TCN_vision'.format(receive))
                print('Either vision module got problem or undefined communication error of\
                     Vision module, please check test message')
                logging.info('{} received from TCN_vision'.format(receive))
                logging.info("Either vision module got problem or undefined communication \
                    error of Vision module, please check test message\n")
        except:
            self.vision_server.close()
            self.vision_thread_server.close()
            print('\nError from Bridge : vision_init \n')
            traceback.print_exc()
            logging.info('Bridge initializing fail at vision_init()\n')
            logging.exception("Got error : \n")

    def vision_start_background_thread(self):
        '''Backgound thread that get store incoming data'''
        self.vision_thread = threading.Thread(target=self.vision_thread_main, daemon=True)
        self.vision_thread.start()
        logging.info('Vision thread start')

    def vision_thread_main(self):
        '''Get vision data'''
        while self.vision_thread_server_run:
            self.vision_thread_server_status = self.vision_thread.is_alive()
            vision_data = self.vision_thread_server.recv_list()
            if vision_data is not None:
                self.vision_x = vision_data[0]
                self.vision_y = vision_data[1]
                self.theta = vision_data[2]
                self.vision_status = vision_data[3]
                self.vision_client_run = vision_data[4]
                self.vision_thread_client_run = vision_data[5]
                time.sleep(0.1)

    def end_vision_server(self):
        '''End vision module system'''
        if self.vision_server_run:
            self.vision_server.send_list(['V', 'exit'])
            time.sleep(1)
            self.vision_server.close()
            self.vision_server_run = False
            logging.info('Vision server end')
        else:
            print('Vision TCP server already off')

    def end_vision_thread_server(self):
        '''Stop getting data from vision module'''
        self.vision_thread_server.close()
        if self.vision_thread_server_run:
            self.vision_thread_server_run = False
            self.vision_thread.join()
            self.vision_thread_server_status = self.vision_thread.is_alive()
        logging.info('Vision thread stop')


################## LiDAR ######################

    def lidar_init(self):
        '''Initialize Lidar system and communication'''
        try:
            logging.info("Initialize lidar server\n")
            subprocess.Popen('python3 tcn_rplidar.py', shell=True, start_new_session=True)
            self.lidar_server = tcn_socket.TCP_server(50004)
            self.lidar_thread_server = tcn_socket.UDP_server(50005)
            lidar_data = self.lidar_server.recv_list()
            if lidar_data == ['L', 'status', 'Good']:
                logging.info("Lidar communication successfully established !\ncommunication center get : {} \n".format(lidar_data))
                self.lidar_server_run = True
                self.lidar_thread_server_run = True
                self.lidar_start_background_thread()
            else:
                self.end_lidar_server()
                self.end_lidar_thread_server()
                print('Undefined communication error of Vision module, please check test message')
                logging.info("Undefined communication error of Vision module, please check test message\n")
                raise KeyboardInterrupt
        except:
            self.lidar_server.close()
            self.lidar_thread_server.close()
            print('\nError from Bridge : lidar_init\n')
            traceback.print_exc()
            logging.info('Bridge initializing fail at lidar_init()\n')
            logging.exception("Bridge initializing fail at lidar_init() : \n")

    def lidar_start_background_thread(self):
        '''Lidar get data in background'''
        self.lidar_thread = threading.Thread(target=self.lidar_thread_main, daemon=True)
        self.lidar_thread.start()
        logging.info('LiDAR thread start')

    def lidar_thread_main(self):
        '''Lidar get data'''
        while self.lidar_thread_server_run:
            self.lidar_thread_server_status = self.lidar_thread.is_alive()
            if self.lidar_thread_server.server_alive:
                temp_lidar_data = self.lidar_thread_server.recv_list(65536)
                if temp_lidar_data is not None:
                    self.lidar_usb_port = temp_lidar_data[0]
                    self.lidar_data = temp_lidar_data[1]
            time.sleep(0.2)

    def end_lidar_server(self):
        '''End lidar system'''
        if self.lidar_server_run:
            self.lidar_server.send_list(['L', 'exit'])
            time.sleep(1)
            self.lidar_server.close()
            self.lidar_server_run = False
            logging.info('LiDAR server end')
        else:
            print('LiDAR TCP server already off')

    def end_lidar_thread_server(self):
        '''Stop storing lidar data'''
        self.lidar_thread_server.close()
        if self.lidar_thread_server_run:
            self.lidar_thread_server_run = False
            self.lidar_thread.join()
            self.lidar_thread_server_status = self.lidar_thread.is_alive()
        logging.info('LiDAR thread end')

############## STM32 #####################

    def stm32_init(self):
        '''Initialize motor controller and communication'''
        try:
            logging.info("Initialize STM32 server\n")
            subprocess.Popen('python3 tcn_stm32.py', shell=True, start_new_session=True)
            self.stm32_server = tcn_socket.TCP_server(50006)
            self.stm32_thread_server = tcn_socket.UDP_server(50007)
            stm32_data = self.stm32_server.recv_list()
            if stm32_data == ['S', 'next']:
                self.stm32_server_run = True
                self.stm32_thread_server_run = True
                logging.info("STM32 communication successfully established !\ncommunication center get : {} \n".format(stm32_data))
                self.stm32_start_background_thread()
            else:
                self.end_stm32_server()
                self.end_stm32_thread_server()
        except:
            time.sleep(0.3)
            self.stm32_server.close()
            self.stm32_thread_server.close()
            print('\nError from Bridge : stm32_init\n')
            traceback.print_exc()
            print('Bridge initializing fail at stm32_init()')
            logging.exception('Bridge initializing fail at stm32_init() :\n')

    def stm32_start_background_thread(self):
        '''Get stm32 status in background'''
        self.stm32_thread = threading.Thread(target=self.stm32_thread_main, daemon=True)
        self.stm32_thread.start()
        logging.info('STM32 thread start')

    def stm32_thread_main(self):
        '''Get stm32 status'''
        while self.stm32_thread_server_run:
            self.stm32_thread_server_status = self.stm32_thread.is_alive()
            stm32_status = self.stm32_thread_server.recv_list(8192)
            if stm32_status is not None:
                self.stm32_usb_port_path = stm32_status[0]
                self.stm32_program_run = stm32_status[1]
                self.stm32_power = stm32_status[2]
            time.sleep(0.5)

    def end_stm32_server(self):
        '''End motor controller'''
        if self.stm32_server_run:
            self.stm32_server.send_list(['S', 'exit'])
            time.sleep(1)
            self.stm32_server.close()
            self.stm32_server_run = False
            logging.info('STM32 server end')
        else:
            print('STM32 TCP server already off')

    def end_stm32_thread_server(self):
        '''Stop getting stm32 status'''
        self.stm32_thread_server.close()
        if self.stm32_thread_server_run:
            self.stm32_thread_server_run = False
            self.stm32_thread.join()
            self.stm32_thread_server_status = self.stm32_thread.is_alive()
        logging.info('STM32 thread end')

############ Bridge main ###################
    def bridge_main(self):
        '''Bridge waiting for command'''
        retry = 0
        self.bridge_run = True
        while self.bridge_run:
            try:
                bridge_receive = self.commander_server.recv_list()
                if bridge_receive is not None:
                    self.bridge_protocol(bridge_receive)
                else:
                    print('Bridge received {}'.format(bridge_receive))
                    print('Please check commander status !')
                    retry += 1
                    time.sleep(0.5)
                    if retry > 4:
                        print('Maximum retries reached, force shutdown')
                        self.end_bridge_all()

            except:
                print('Critical error happened on Bridge , all programs have to be shutdown')
                self.end_bridge_all()
                print('\nError from Bridge : bridge_main \n')
                traceback.print_exc()
                logging.exception('Got error :')
                self.bridge_run = False

    def end_bridge_all(self):
        '''Close all system except for tnc_main'''
        self.end_xbox()
        self.end_lidar_server()
        self.end_lidar_thread_server()
        self.end_stm32_server()
        self.end_stm32_thread_server()
        self.end_vision_server()
        self.end_vision_thread_server()
        self.end_commander_server()

    def bridge_protocol(self, bridge_receive):
        '''First, get commander command (TCN_main.py)'''
        try:
            if bridge_receive is None:
                print('Bridge : socket may got problem')

            elif bridge_receive[0] == 'C':
                if bridge_receive[1] == 'exit':
                    if bridge_receive[2] == 'all':
                        self.end_bridge_all()
                        self.bridge_run = False
                    elif bridge_receive[2] == 'l':
                        self.end_lidar_server()
                        self.end_lidar_thread_server()
                    elif bridge_receive[2] == 's':
                        self.end_stm32_server()
                        self.end_stm32_thread_server()
                    elif bridge_receive[2] == 'v':
                        self.end_vision_server()
                        self.end_vision_thread_server()
                    elif bridge_receive[2] == 'x':
                        self.end_xbox()

                if bridge_receive[1] == 'next':
                    pass


######################## STM32 & XBOX #################
                elif bridge_receive[1] == 'xs':
                    print('XBOX run : {}\nXBOX move stm32 : {}\nXBOX X : {}\nXBOX Y : {}\nXBOX Z : {}\nXBOX STEP : {}'\
                        .format(self.xbox_run, self.xbox_move_stm32, self.xbox_x, self.xbox_y, self.xbox_z, self.xbox_step))
                elif bridge_receive[1] == 'si':
                    if not self.stm32_server_run:
                        self.stm32_init()
                    else:
                        print('STM32 run already')
                    self.commander_server.send_list(['C', 'next'])
                elif bridge_receive[1] == 'xi':
                    if not self.xbox_on:
                        self.xbox_init()
                    else:
                        print('XBOX run already')
                    self.commander_server.send_list(['C', 'next'])
                elif bridge_receive[1] == 'mwx':
                    self.xbox_move_stm32 = True
                    self.xbox_get_data()
                    while self.xbox_move_stm32:
                        try:
                            receive = self.commander_udp_server.recv_list()
                            if receive is not None:
                                self.xbox_move_stm32 = False
                            else:
                                self.xbox_move_stm32 = True
                            time.sleep(0.1)
                        except TypeError:
                            pass
                        except:
                            self.xbox_move_stm32 = False
                    self.xbox_move_stm32 = False
                    self.commander_server.send_list(['C', 'next'])
                elif bridge_receive[1] == 'stop':
                    self.stm32_server.send_list(['S', 'stop'])

######################## LiDAR #################
                elif bridge_receive[1] == 'li':
                    if not self.lidar_server_run:
                        self.lidar_init()
                    else:
                        print('LiDAR run already')
                    self.commander_server.send_list(['C', 'next'])
                elif bridge_receive[1] == 'gld':
                    print(self.lidar_data)



######################## Vision ################
                elif bridge_receive[1] == 'vi':
                    if not self.vision_server_run:
                        self.vision_init()
                    else:
                        print('Vision run already')
                    self.commander_server.send_list(['C', 'next'])
                elif bridge_receive[1] == 'al':
                    self.vision_server.send_list(['V', 'al'])
                elif bridge_receive[1] == 'cc':
                    self.vision_server.send_list(['V', 'cc'])
                elif bridge_receive[1] == 'vs':
                    print('Vision server : {}\nVision thread server : {}\nVision client : {}\nVision thread client : {}'\
                        .format(self.vision_server_run, self.vision_thread_server_run, self.vision_client_run, self.vision_thread_client_run))
                elif bridge_receive[1] == 'gp':
                    try:
                        if bridge_receive[2] == 'c':
                            self.bridge_show_vision_data()
                        elif bridge_receive[2] == 'x':
                            self.bridge_show_vision_data_xbox()
                        elif bridge_receive[2] == 'exit':
                            self.bridge_show_vision_data_run = False
                            self.xbox_move_stm32 = False
                    except IndexError:
                        print('status : {} | x : {} | y : {} | theta : {} '.format(self.vision_status, self.vision_x, self.vision_y, self.theta))
                elif bridge_receive[1] == 'gs':
                    self.show_vision_status()
                elif bridge_receive[1] == 'sv':
                    self.vision_server.send_list(['V', 'sv'])
                elif bridge_receive[1] == 'vrs':
                    self.vision_server.send_list(['V', 'rs'])
                elif bridge_receive[1] in ['bm', 'um', 'kbm']:
                    if type(bridge_receive[2]) == int:
                        if bridge_receive[2] >= 0:
                            self.vision_server.send_list(['V', bridge_receive[1], int(bridge_receive[2])])
                            self.bridge_show_vision_data_xbox()
                        else:
                            print('mapid must be positive integer')
                    elif bridge_receive[2] is None:
                        print('Please specify mapid. Ex : {} 1 '.format(bridge_receive[1]))
                    elif bridge_receive[2] == 'end':
                        self.bridge_show_vision_data_run = False
                        self.xbox_move_stm32 = False




            elif bridge_receive[0] == 'S':
                if bridge_receive[1] == 'next':
                    # self.commander_server.send_list(['C','next'])
                    pass


            elif bridge_receive[0] == 'V':
                if bridge_receive[1] == 'next':
                    self.commander_server.send_list(['C', 'next'])


            elif bridge_receive[0] == 'L':
                if bridge_receive[1] == 'next':
                    self.commander_server.send_list(['C', 'next'])


            else:
                print('{} received . Wrong potorcol  !'.format(bridge_receive))
                logging.info('{} received . Wrong potorcol  !'.format(bridge_receive))


        except:
            print('\nError from Bridge : bridge_protocol \n')
            traceback.print_exc()
            logging.exception('Got error : ')
            print('\n\nForce abort current order')



    def bridge_show_vision_data(self):
        '''Show vision data'''
        self.bridge_show_vision_data_run = True
        while self.bridge_show_vision_data_run:
            try:
                receive = self.commander_udp_server.recv_list()
                if receive is not None:
                    self.bridge_show_vision_data_run = False
                print('status : {} | x : {} | y : {} | theta : {} | Use Ctrl+C or enter any key to end current process : '\
                    .format(self.vision_status, self.vision_x, self.vision_y, self.theta))
                time.sleep(0.1)
            except:
                print('\nError from Bridge : bridge_send_vision_data_to_commander\n')
                traceback.print_exc()
                logging.exception('Got error : ')
                self.bridge_show_vision_data_run = False
        self.commander_server.send_list(['C', 'next'])



    def bridge_show_vision_data_xbox(self):
        '''Show vision data with xbox control'''
        self.bridge_show_vision_data_run = True
        self.xbox_move_stm32 = True
        self.xbox_get_data()
        while self.bridge_show_vision_data_run:
            try:
                receive = self.commander_udp_server.recv_list()
                if receive is not None:
                    self.bridge_show_vision_data_run = False
                    self.xbox_run = False
                print('status : {} | x : {} | y : {} | theta : {} | Use Ctrl+C or enter any key to end current process : '\
                    .format(self.vision_status, self.vision_x, self.vision_y, self.theta))
                time.sleep(0.1)
            except TypeError:
                pass
            except:
                print('\nError from Bridge : bridge_send_vision_data_to_commander_xbox\n')
                traceback.print_exc()
                logging.exception('Got error : ')
                self.bridge_show_vision_data_run = False
                self.xbox_run = False
        self.xbox_move_stm32 = False
        self.commander_server.send_list(['C', 'next'])



    def show_vision_status(self):
        '''Show message depends on vision status'''
        if self.vision_status == 0:
            print("Vision module status : {} | Vision module is booting".format(self.vision_status))
        elif self.vision_status == 1:
            print("Vision module status : {} | Vision module is waiting for 'st $mapid' command".format(self.vision_status))
        elif self.vision_status == 2:
            print("Vision module status : {} | Vision module is loading data ".format(self.vision_status))
        elif self.vision_status == 3:
            print('Vision module status : {} | Please move slowly, fp-slam is searching a set of best images to initialize'.format(self.vision_status))
        elif self.vision_status == 4:
            print('Vision module status : {} | System is working normaaly'.format(self.vision_status))
        elif self.vision_status == 5:
            print('Vision module status : {} | Lost Lost Lost'.format(self.vision_status))
        else:
            print('Unknown status code : {}'.format(self.vision_status))







if __name__ == "__main__":
    # bridge_init()
    # bridge_main()
    # end_bridge()
    Bridge()