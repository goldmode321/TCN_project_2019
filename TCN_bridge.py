#!/usr/bin/python3
''' Bridge, also known as communication center, used to store and
    transfer data and command '''
import time
import traceback
import subprocess
import threading
import logging
import xbox
import tcn_socket

class MoveAlgorithm:
    ''' Provide different moving mode '''
    def __init__(self, vision_status, vision_data, lidar_data, recorded_vision_coordinate):
        self.vision_data = vision_data
        self.vision_status = vision_status
        self.lidar_data = lidar_data
        self.recorded_vision_coordinate = recorded_vision_coordinate
        self.global_obstacle = []

    def algorithm_move_between_waypoints(self):
        pass

    def algorithm_get_global_obstacle(self):
        if self.vision_status != 4:
            pass



class Bridge(MoveAlgorithm):
    '''Communication center Bridge(auto_start=True)'''
    def __init__(self, auto_start=True):
        '''If auto_start is False, program automatically run __init__ only'''
        logging.basicConfig(filename='Bridge.log', filemode='w', level=logging.INFO)

        # Bridge initial variables
        self.auto_start = auto_start
        self.bridge_run = False
        self.bridge_receive = []

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
        self.recorded_vision_coordinate = []
        self.vision_record_coordinate = False
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
        self.lidar_package = [self.lidar_data, self.lidar_usb_port]

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
        self.algorithm_server_run = False

        # GUI initial variables
        self.gui_server_run = False
        self.gui_receive = []


        self.command_dictionary_bridge = {'exit all':self._exit_all, 'exit b':self._exit_b, 'exit l':self._exit_l, \
            'exit s':self._exit_s, 'exit v':self._exit_v, 'li':self._li, \
                'gld':self._gld, 'vi':self._vi, 'vs':self._vs, 'gs':self._gs, 'al':self._al, \
                    'cc':self._cc, 'sv':self._sv, 'vrs':self._vrs, 'gp c':self._gp_c, 'gp x':self._gp_x, \
                        'gp exit':self._gp_exit, 'gp':self._gp, 'bm':self._bm, 'um':self._um, \
                            'kbm':self._kbm, 'xs':self._xs, 'si':self._si, 'mwx':self._mwx, \
                                'stop':self._stop, 'xi':self._xi, 'next':self._next}

        # Inherit MoveAlgorithm
        # super.__init__(self.vision_data, self.lidar_data, self.recorded_vision_coordinate)

        if self.auto_start:
            self.xbox_init()
            self.commander_init()
            self.vision_init()
            self.lidar_init()
            self.stm32_init()
            self.commander_server.send_list(['C', 'next']) # Tell commander bridge is ready
            self.bridge_main()


########### Send to GUI ##############
    def gui_connection_init(self):
        self.gui_udp_server = tcn_socket.UDP_server(50008, 0, "192.168.5.10")
        self.gui_server_run = True


    def gui_send_and_read(self):
        while self.gui_server_run:
            self.gui_receive = self.gui_udp_server.recv_list()
            if self.gui_udp_server.addr is not None:
                self.gui_udp_server.send_list_back([self.lidar_package])


############ XBOX initialize #########
    def xbox_init(self):
        '''Connect to XBOX controller'''
        try:
            self.xbox = xbox.Joystick()
            self.xbox_on = True
        # self.xbox = tcn_xbox.XboxController()
        except IOError:
            print('Xbox connect error, auto retry again ; Please move joystick or press any button')
            self.xbox_init()


    def xbox_get_data(self):
        '''Xbox run in back ground'''
        self.xbox_thread = threading.Thread(target=self.xbox_main, daemon=True)
        self.xbox_thread.start()


    def xbox_main(self):
        '''Get XBOX data'''
        self.xbox_run = True
        while self.xbox_run:
            self.xbox_control()
            if self.xbox_move_stm32:
                self.stm32_server.send_list(['S', 'xbox_move', [self.xbox_x, self.xbox_y, self.xbox_z]])
                self.stm32_server.recv_list()
            if self.vision_record_coordinate:
                if self.xbox.X():
                    self.recorded_vision_coordinate.append([self.vision_x, self.vision_y, self.theta])
                    print('Way point added : {}'.format([self.vision_x, self.vision_y, self.theta]))
                if self.xbox.Y():
                    try:
                        print('Way point deleted : {}'.\
                            format(self.recorded_vision_coordinate[len(self.recorded_vision_coordinate) - 1]))
                        del self.recorded_vision_coordinate[len(self.recorded_vision_coordinate) - 1]
                    except IndexError:
                        print('No way point left for delete')

            time.sleep(0.01)

    def end_xbox(self):
        '''Close XBOX connection'''
        self.xbox_run = False
        self.xbox_move_stm32 = False
        self.xbox_on = False
        self.xbox.close()

    def xbox_control(self):
        '''which return left stick position and right stick x-direction position'''
        # Key A means accelerate
        if int(self.xbox.A()) and self.xbox_step <= 131:
            self.xbox_step = self.xbox_step + 1
            print(self.xbox_step)
            time.sleep(0.05)
        # Key B means deaccelerate
        if int(self.xbox.B()) and self.xbox_step > 0:
            self.xbox_step = self.xbox_step - 1
            print(self.xbox_step)
            time.sleep(0.05)

        self.xbox_x = int(self.xbox_step*round(self.xbox.leftX(),2)) 
        self.xbox_y = int(self.xbox_step*round(self.xbox.leftY(),2))
        self.xbox_z = int(self.xbox_step*round(self.xbox.rightX(),2))

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
            self.vision_data = self.vision_thread_server.recv_list()
            if self.vision_data is not None:
                self.vision_x = self.vision_data[0]
                self.vision_y = self.vision_data[1]
                self.theta = self.vision_data[2]
                self.vision_status = self.vision_data[3]
                self.vision_client_run = self.vision_data[4]
                self.vision_thread_client_run = self.vision_data[5]
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
                self.bridge_receive = self.commander_server.recv_list()
                if self.bridge_receive is not None:
                    self.bridge_protocol()
                else:
                    print('Bridge received {}'.format(self.bridge_receive))
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


    def bridge_protocol(self):
        '''First, get commander command (TCN_main.py)'''
        try:
            if self.bridge_receive is None:
                print('Bridge : socket may got problem')

            elif self.bridge_receive[0] == 'C':
                self.command_dictionary_bridge[self.bridge_receive[1]]()

            elif self.bridge_receive[0] == 'S':
                if self.bridge_receive[1] == 'next':
                    # self.commander_server.send_list(['C','next'])
                    pass


            elif self.bridge_receive[0] == 'V':
                if self.bridge_receive[1] == 'next':
                    self.commander_server.send_list(['C', 'next'])


            elif self.bridge_receive[0] == 'L':
                if self.bridge_receive[1] == 'next':
                    self.commander_server.send_list(['C', 'next'])


            else:
                print('{} received . Wrong potorcol  !'.format(self.bridge_receive))
                logging.info('{} received . Wrong potorcol  !'.format(self.bridge_receive))


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






############ Command relative function ###########
    def _exit_all(self):
        self.end_bridge_all()
        self.bridge_run = False
    def _exit_b(self):
        self.end_bridge_all()
        self.bridge_run = False
    def _exit_l(self):
        self.end_lidar_server()
        self.end_lidar_thread_server()
    def _exit_s(self):
        self.end_stm32_server()
        self.end_stm32_thread_server()
    def _exit_v(self):
        self.end_vision_server()
        self.end_vision_thread_server()
    def _exit_x(self):
        self.end_xbox()


    ################ LiDAR ###############
    def _li(self):
        if not self.lidar_server_run:
            self.lidar_init()
        else:
            print('LiDAR run already')
    def _gld(self):
        print(self.lidar_data)

    ################ Vision #############
    def _vi(self):
        if not self.vision_server_run:
            self.vision_init()
        else:
            print('Vision run already')
        self.commander_server.send_list(['C', 'next'])
    def _vs(self):
        print('Vision server : {}\nVision thread server : {}\nVision client : {}\nVision thread client : {}'\
            .format(self.vision_server_run, self.vision_thread_server_run, self.vision_client_run, self.vision_thread_client_run))
    def _gs(self):
        self.show_vision_status()
    def _sv(self):
        self.vision_server.send_list(['V', 'sv'])
    def _al(self):
        self.vision_server.send_list(['V', 'al'])
    def _cc(self):
        self.vision_server.send_list(['V', 'cc'])
    def _vrs(self):
        self.vision_server.send_list(['V', 'rs'])
    def _gp_c(self):
        self.bridge_show_vision_data()
    def _gp_x(self):
        self.bridge_show_vision_data_xbox()
    def _gp_exit(self):
        self.bridge_show_vision_data_run = False
        self.xbox_move_stm32 = False
    def _gp(self):
        print('status : {} | x : {} | y : {} | theta : {} '.format(self.vision_status, self.vision_x, self.vision_y, self.theta))
    def _bm(self):
        if type(self.bridge_receive[2]) == int:
            if self.bridge_receive[2] >= 0:
                self.vision_server.send_list(['V', 'bm', int(self.bridge_receive[2])])
                self.bridge_show_vision_data_xbox()
            else:
                print('mapid must be positive integer')
        elif self.bridge_receive[2] is None:
            print('Please specify mapid. Ex : bm 1 ')
        elif self.bridge_receive[2] == 'end':
            self.bridge_show_vision_data_run = False
            self.xbox_move_stm32 = False
    def _um(self):
        if type(self.bridge_receive[2]) == int:
            if self.bridge_receive[2] >= 0:
                self.vision_server.send_list(['V', 'um', int(self.bridge_receive[2])])
                self.bridge_show_vision_data_xbox()
            else:
                print('mapid must be positive integer')
        elif self.bridge_receive[2] is None:
            print('Please specify mapid. Ex : um 1 ')
        elif self.bridge_receive[2] == 'end':
            self.bridge_show_vision_data_run = False
            self.xbox_move_stm32 = False
    def _kbm(self):
        if type(self.bridge_receive[2]) == int:
            if self.bridge_receive[2] >= 0:
                self.vision_server.send_list(['V', 'kbm', int(self.bridge_receive[2])])
                self.bridge_show_vision_data_xbox()
            else:
                print('mapid must be positive integer')
        elif self.bridge_receive[2] is None:
            print('Please specify mapid. Ex : kbm 1 ')
        elif self.bridge_receive[2] == 'end':
            self.bridge_show_vision_data_run = False
            self.xbox_move_stm32 = False

    ############ XBOX and STM32 #################
    def _xs(self):
        print('XBOX run : {}\nXBOX move stm32 : {}\nXBOX X : {}\nXBOX Y : {}\nXBOX Z : {}\nXBOX STEP : {}'\
            .format(self.xbox_run, self.xbox_move_stm32, self.xbox_x, self.xbox_y, self.xbox_z, self.xbox_step))
    def _si(self):
        if not self.stm32_server_run:
            self.stm32_init()
        else:
            print('STM32 run already')
        self.commander_server.send_list(['C', 'next'])
    def _mwx(self):
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
    def _stop(self):
        self.stm32_server.send_list(['S', 'stop'])
    def _xi(self):
        if not self.xbox_on:
            self.xbox_init()
        else:
            print('XBOX run already')
        self.commander_server.send_list(['C', 'next'])
    def _next(self):
        pass






if __name__ == "__main__":
    Bridge()
