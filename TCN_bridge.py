#!/usr/bin/python3
import TCN_socket
import time
import traceback
import subprocess
import sys
import threading
import logging
import TCN_xbox
import os

class Bridge:
    def __init__(self, AUTO_START = True):
        '''If AUTO_START is False, program automatically run __init__ only'''
        logging.basicConfig(filename='Bridge.log',filemode = 'w',level =logging.INFO)

        # Bridge initial variables
        self.AUTO_START = AUTO_START
        self.BRIDGE_RUN = False

        # XBOX initial variables
        self.XBOX_RUN = False
        self.XBOX_X = 0
        self.XBOX_Y = 0
        self.XBOX_Z = 0
        self.XBOX_STEP = 0
        self.XBOX_MOVE_STM32 = False

        # Commander initail variables
        self.COMMANDER_SERVER_RUN = False

        # Vision initial variables
        self.X = 0
        self.Y = 0
        self.THETA = 0
        self.VISION_STATUS = 0
        self.VISION_DATA = []
        self.VISION_CLIENT_RUN = False
        self.VISION_SERVER_RUN = False
        self.VISION_THREAD_SERVER_RUN = False
        self.VISION_THREAD_SERVER_STATUS = 0
        self.VISION_THREAD_CLIENT_RUN = False

        # Lidar initial variables
        self.LIDAR_DATA = []
        self.LIDAR_SERVER_RUN = False
        self.LIDAR_THREAD_SERVER_RUN = False
        self.LIDAR_THREAD_SERVER_STATUS = 0
        self.LIDAR_USB_PORT = ""
        self.LIDAR_CLIENT_RUN = False
        self.LIDAR_THREAD_CLIENT_RUN = False

        # STM32 inital variables
        self.STM32_SERVER_RUN = False
        self.STM32_THREAD_SERVER_RUN = False
        self.STM32_THREAD_SERVER_STATUS = 0
        self.STM32_USB_PORT_PATH = 0
        self.STM32_PROGRAM_RUN = 0
        self.STM32_POWER = 0

        # Algorithm initial variables
        self.ALGORITHM_RUN = False

        if self.AUTO_START:
            self.xbox_init()
            self.commander_init()
            self.vision_init()
            self.lidar_init()
            self.stm32_init()
            self.COMMANDER_SERVER.send_list(['C','next'])
            self.bridge_main()
        

############ XBOX initialize #########
    def xbox_init(self): 
        self.XBOX = TCN_xbox.Xbox_controller()

    def xbox_get_data(self):
        self.XBOX_THREAD = threading.Thread(target = self.xbox_main , daemon = True)
        self.XBOX_THREAD.start()
        

    def xbox_main(self):
        self.XBOX_RUN = True
        while self.XBOX_RUN:
            move_command = self.XBOX.xbox_control()
            self.XBOX_X = move_command[0]
            self.XBOX_Y = move_command[1]
            self.XBOX_Z = move_command[2]
            self.XBOX_STEP = move_command[3]
            if self.XBOX_MOVE_STM32 == True:
                self.STM32_SERVER.send_list(['S','xbox_move',[self.XBOX_X,self.XBOX_Y,self.XBOX_Z]])
                self.STM32_SERVER.recv_list()
            time.sleep(0.05)

    def end_xbox(self):
        self.XBOX_RUN = False
        self.XBOX_MOVE_STM32 = False
        self.XBOX.close()



############### Commander TCP Client Version ###############

    def commander_init(self):
        try:
            time.sleep(0.2) # Make sure server initialize first
            logging.info("Initialize commander client\n")
            self.COMMANDER_UDP_CLIENT = TCN_socket.UDP_client(50001)
            self.COMMANDER_SERVER = TCN_socket.TCP_client(50000)
            self.COMMANDER_SERVER.send_list(['C','next'])
            logging.info("Commander connection complete !\n")
            self.COMMANDER_SERVER_RUN = True
        except:
            self.end_commander_server()
            print('\nError from Bridge : commander_init\n')
            traceback.print_exc()
            print('\n Commander is not initialize')
            logging.info('Bridge initializing fail at commander_init()\n')
            logging.exception("Got error : \n")

    def end_commander_server(self):
        self.COMMANDER_UDP_CLIENT.close()
        self.COMMANDER_SERVER.close()
        self.COMMANDER_SERVER_RUN = False
        logging.info('End commander client')


############### Commander TCP Server Version ###############

    # def commander_init(self):
    #     try:
    #         logging.info("Initialize commander server\n")
    #         self.COMMANDER_SERVER = TCN_socket.TCP_server(50000,1)
    #         self.COMMANDER_SERVER.send_list(['C','next'])
    #         logging.info("Commander connection complete !\n")
    #         self.COMMANDER_SERVER_RUN = True
    #     except:
    #         self.end_commander_server()
    #         traceback.print_exc()
    #         print('\n Commander is not initialize')
    #         logging.info('Bridge initializing fail at commander_init()\n')
    #         logging.exception("Got error : \n")

    # def end_commander_server(self):
    #     self.COMMANDER_SERVER.close()
    #     self.COMMANDER_SERVER_RUN = False


################## Vision ##############

    def vision_init(self):
        try:
            logging.info("Initialize vision server\n")
            process_vision = subprocess.Popen('python3 TCN_vision.py',shell = True ,start_new_session = True)
            self.VISION_THREAD_SERVER = TCN_socket.UDP_server(50003)
            self.VISION_SERVER = TCN_socket.TCP_server(50002)
            self.VISION_SERVER_RECEIVE = self.VISION_SERVER.recv_list()
            if self.VISION_SERVER_RECEIVE == ['V','status','Alive']:
                logging.info("Vision communication successfully established !\ncommunication center get : {} \n".format(self.VISION_SERVER_RECEIVE) )
                # self.COMMANDER_SERVER.send_list(['C','next'])
                self.VISION_SERVER_RUN = True
                self.VISION_THREAD_SERVER_RUN = True
                self.vision_start_background_thread()
            else:
                self.end_vision_server()
                self.end_vision_thread_server()
                print('{} received from TCN_vision'.format(self.VISION_DATA))
                print('Either vision module got problem or undefined communication error of Vision module, please check test message')
                logging.info('{} received from TCN_vision'.format(self.VISION_DATA))
                logging.info("Either vision module got problem or undefined communication error of Vision module, please check test message\n")      
        except:
            self.VISION_SERVER.close()
            self.VISION_THREAD_SERVER.close()
            print('\nError from Bridge : vision_init \n')
            traceback.print_exc()
            logging.info('Bridge initializing fail at vision_init()\n')
            logging.exception("Got error : \n")         

    def vision_start_background_thread(self):
        self.VISION_THREAD = threading.Thread(target = self.vision_thread_main , daemon = True)
        self.VISION_THREAD.start()
        logging.info('Vision thread start')

    def vision_thread_main(self):
        while self.VISION_THREAD_SERVER_RUN:
            self.VISION_THREAD_SERVER_STATUS = self.VISION_THREAD.is_alive()
            vision_data = self.VISION_THREAD_SERVER.recv_list()
            if vision_data != None:
                self.X = vision_data[0]
                self.Y = vision_data[1]
                self.THETA = vision_data[2]
                self.VISION_STATUS = vision_data[3]
                self.VISION_CLIENT_RUN = vision_data[4]
                self.VISION_THREAD_CLIENT_RUN = vision_data[5]
                time.sleep(0.1)

    def end_vision_server(self):
        if self.VISION_SERVER_RUN:
            self.VISION_SERVER.send_list(['V','exit'])
            time.sleep(1)
            self.VISION_SERVER.close()
            self.VISION_SERVER_RUN = False
            logging.info('Vision server end')
        else:
            print('Vision TCP server already off')

    def end_vision_thread_server(self):
        self.VISION_THREAD_SERVER.close()
        if self.VISION_THREAD_SERVER_RUN == True:
            self.VISION_THREAD_SERVER_RUN = False
            self.VISION_THREAD.join()
            self.VISION_THREAD_SERVER_STATUS = self.VISION_THREAD.is_alive()
        logging.info('Vision thread stop')


################## LiDAR ######################

    def lidar_init(self):
        try:
            logging.info("Initialize lidar server\n")
            process_lidar = subprocess.Popen('python3 TCN_rplidar.py',shell = True , start_new_session = True)
            self.LIDAR_SERVER = TCN_socket.TCP_server(50004,1)
            self.LIDAR_THREAD_SERVER = TCN_socket.UDP_server(50005)
            lidar_data = self.LIDAR_SERVER.recv_list()
            if lidar_data == ['L','status','Good']:
                logging.info("Lidar communication successfully established !\ncommunication center get : {} \n".format(lidar_data) )
                self.LIDAR_SERVER_RUN = True
                self.LIDAR_THREAD_SERVER_RUN = True
                # self.COMMANDER_SERVER.send_list(['C','next'])
                self.lidar_start_background_thread()
            else:
                self.end_lidar_server()
                self.end_lidar_thread_server()
                print('Undefined communication error of Vision module, please check test message')
                logging.info("Undefined communication error of Vision module, please check test message\n")
                raise KeyboardInterrupt      
        except:
            self.LIDAR_SERVER.close()
            self.LIDAR_THREAD_SERVER.close()
            print('\nError from Bridge : lidar_init\n')
            traceback.print_exc()
            logging.info('Bridge initializing fail at lidar_init()\n')
            logging.exception("Bridge initializing fail at lidar_init() : \n")

    def lidar_start_background_thread(self):
        self.LIDAR_THREAD = threading.Thread(target = self.lidar_thread_main ,daemon = True)
        self.LIDAR_THREAD.start()
        logging.info('LiDAR thread start')

    def lidar_thread_main(self):
        while self.LIDAR_THREAD_SERVER_RUN:
            self.LIDAR_THREAD_SERVER_STATUS = self.LIDAR_THREAD.is_alive()  
            if self.LIDAR_THREAD_SERVER.server_alive:
                temp_lidar_data = self.LIDAR_THREAD_SERVER.recv_list(65536)
                if temp_lidar_data:
                    self.LIDAR_USB_PORT = temp_lidar_data[0]
                    self.LIDAR_DATA = temp_lidar_data[1]
            time.sleep(0.2)

    def end_lidar_server(self):
        if self.LIDAR_SERVER_RUN == True:
            self.LIDAR_SERVER.send_list(['L','exit'])
            time.sleep(1)
            self.LIDAR_SERVER.close()
            self.LIDAR_SERVER_RUN = False
            logging.info('LiDAR server end')
        else:
            print('LiDAR TCP server already off')

    def end_lidar_thread_server(self):
        self.LIDAR_THREAD_SERVER.close()
        if self.LIDAR_THREAD_SERVER_RUN == True:
            self.LIDAR_THREAD_SERVER_RUN = False
            self.LIDAR_THREAD.join()
            self.LIDAR_THREAD_SERVER_STATUS = self.LIDAR_THREAD.is_alive()       
        logging.info('LiDAR thread end')

############## STM32 #####################
    
    def stm32_init(self):
        try:
            logging.info("Initialize STM32 server\n")
            process_stm32 = subprocess.Popen('python3 TCN_STM32.py',shell = True , start_new_session = True)
            self.STM32_SERVER = TCN_socket.TCP_server(50006,1)
            self.STM32_THREAD_SERVER = TCN_socket.UDP_server(50007)
            stm32_data = self.STM32_SERVER.recv_list()
            if stm32_data == ['S','next']:
                self.STM32_SERVER_RUN = True
                self.STM32_THREAD_SERVER_RUN = True
                logging.info("STM32 communication successfully established !\ncommunication center get : {} \n".format(stm32_data) )
                self.stm32_start_background_thread()
            else:
                self.end_stm32_server()
                self.end_stm32_thread_server()
        except:
            time.sleep(0.3)
            self.STM32_SERVER.close()
            self.STM32_THREAD_SERVER.close()
            print('\nError from Bridge : stm32_init\n')
            traceback.print_exc()
            print('Bridge initializing fail at stm32_init()')
            logging.exception('Bridge initializing fail at stm32_init() :\n')

    def stm32_start_background_thread(self):
        self.STM32_THREAD = threading.Thread(target = self.stm32_thread_main , daemon = True)
        self.STM32_THREAD.start()
        logging.info('STM32 thread start')

    def stm32_thread_main(self):
        while self.STM32_THREAD_SERVER_RUN:
            self.STM32_THREAD_SERVER_STATUS = self.STM32_THREAD.is_alive()
            STM32_STATUS = self.STM32_THREAD_SERVER.recv_list(8192)
            if STM32_STATUS != None:
                self.USB_PORT_PATH = STM32_STATUS[0]
                self.STM32_PROGRAM_RUN = STM32_STATUS[1]
                self.STM32_POWER = STM32_STATUS[2]
            time.sleep(0.5)

    def end_stm32_server(self):
        if self.STM32_SERVER_RUN == True:
            self.STM32_SERVER.send_list(['S','exit'])
            time.sleep(1)
            self.STM32_SERVER.close()
            self.STM32_SERVER_RUN = False
            logging.info('STM32 server end')
        else:
            print('STM32 TCP server already off')

    def end_stm32_thread_server(self):
        self.STM32_THREAD_SERVER.close()
        if self.STM32_THREAD_SERVER_RUN == True:
            self.STM32_THREAD_SERVER_RUN = False
            self.STM32_THREAD.join()
            self.STM32_THREAD_SERVER_STATUS = self.STM32_THREAD.is_alive()  
        logging.info('STM32 thread end')

############ Bridge main ###################
    def bridge_main(self):
        retry = 0
        self.BRIDGE_RUN = True
        while self.BRIDGE_RUN:
            try:
                self.BRIDGE_RECEIVE = self.COMMANDER_SERVER.recv_list()
                if self.BRIDGE_RECEIVE != None:
                    self.bridge_protocol(self.BRIDGE_RECEIVE)
                else:
                    print('Bridge received {}'.format(self.BRIDGE_RECEIVE))
                    print('Please check commander status !')
                    retry += 1
                    time.sleep(0.5)
                    if retry > 4 :
                        print('Maximum retries reached, force shutdown')
                        self.end_bridge_all()

            except:
                print('Critical error happened on Bridge , all programs have to be shutdown')
                self.end_bridge_all()
                print('\nError from Bridge : bridge_main \n')
                traceback.print_exc()
                logging.exception('Got error :')
                self.BRIDGE_RUN = False

    def end_bridge_all(self):
            self.end_xbox()
            self.end_lidar_server()
            self.end_lidar_thread_server()
            self.end_stm32_server()
            self.end_stm32_thread_server()
            self.end_vision_server()
            self.end_vision_thread_server()
            self.end_commander_server()

    def bridge_protocol(self,bridge_receive):
        '''First, get commander command (TCN_main.py)'''
        try:
            if bridge_receive == None:
                print('Bridge : socket may got problem')

            elif bridge_receive[0] == 'C':
                if bridge_receive[1] == 'exit':
                    if bridge_receive[2] == 'all':
                        self.end_bridge_all()
                        self.BRIDGE_RUN = False
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
                    print('XBOX run : {}\nXBOX move stm32 : {}\nXBOX X : {}\nXBOX Y : {}\nXBOX Z : {}\nXBOX STEP : {}\nXBOX thread alive : {}'\
                        .format(self.XBOX_RUN,self.XBOX_MOVE_STM32,self.XBOX_X,self.XBOX_Y,self.XBOX_Z,self.XBOX_STEP,self.XBOX_THREAD.is_alive()))
                elif bridge_receive[1] == 'si':
                    if self.STM32_SERVER_RUN == False:
                        self.stm32_init()
                    else:
                        print('STM32 run already')
                    self.COMMANDER_SERVER.send_list(['C','next'])
                elif bridge_receive[1] == 'mwx':
                    self.XBOX_MOVE_STM32 = True
                    self.xbox_get_data()
                    while self.XBOX_MOVE_STM32:
                        try:
                            temp_list = self.COMMANDER_UDP_CLIENT.recv_list()
                            if temp_list[0] == 'end':
                                self.XBOX_MOVE_STM32 = False
                            else:
                                self.XBOX_MOVE_STM32 = True  
                            time.sleep(0.1)
                        except TypeError:
                            pass
                    self.XBOX_MOVE_STM32 = False
                    self.COMMANDER_SERVER.send_list(['C','next'])
                    
                elif bridge_receive[1] == 'stop':
                    self.STM32_SERVER.send_list(['S','stop'])

######################## LiDAR #################
                elif bridge_receive[1] == 'li':
                    if self.LIDAR_SERVER_RUN == False:
                        self.lidar_init()
                    else:
                        print('LiDAR run already')
                    self.COMMANDER_SERVER.send_list(['C','next'])
                elif bridge_receive[1] == 'gld':
                    print(self.LIDAR_DATA)



######################## Vision ################
                elif bridge_receive[1] == 'vi':
                    if self.VISION_SERVER_RUN == False:
                        self.vision_init()
                    else:
                        print('Vision run already')
                    self.COMMANDER_SERVER.send_list(['C','next'])
                elif bridge_receive[1] == 'al':
                    self.VISION_SERVER.send_list(['V','al'])
                elif bridge_receive[1] == 'cc':
                    self.VISION_SERVER.send_list(['V','cc'])
                elif bridge_receive[1] == 'vs':
                    print('Vision server : {}\nVision thread server : {}\nVision client : {}\nVision thread client : {}'\
                        .format(self.VISION_SERVER_RUN,self.VISION_THREAD_SERVER_RUN,self.VISION_CLIENT_RUN,self.VISION_THREAD_CLIENT_RUN))
                elif bridge_receive[1] == 'gp':
                    try:
                        if bridge_receive[2] == 'c':
                            self.bridge_show_vision_data()
                        elif bridge_receive[2] == 'x':
                            self.bridge_show_vision_data_xbox()
                        elif bridge_receive[2] == 'exit':
                            self.BRIDGE_SHOW_VISION_DATA_RUN = False
                            self.XBOX_MOVE_STM32 = False
                    except IndexError:
                        print('status : {} | x : {} | y : {} | theta : {} '.format(self.VISION_STATUS , self.X , self.Y , self.THETA))
                elif bridge_receive[1] == 'gs':
                    self.show_vision_status()
                elif bridge_receive[1] == 'sv':
                    self.VISION_SERVER.send_list(['V','sv'])
                elif bridge_receive[1] == 'rs':
                    self.VISION_SERVER.send_list(['V','rs'])
                    print('reset vision , please wait 5 second')
                    time.sleep(5)
                elif bridge_receive[1] == 'bm' or bridge_receive[1] == 'um' or bridge_receive[1] == 'kbm':
                    if type(bridge_receive[2]) == int:
                        if bridge_receive[2] >= 0:
                            self.VISION_SERVER.send_list(['V',bridge_receive[1],int(bridge_receive[2])])
                            self.bridge_show_vision_data_xbox()
                        else:
                            print('mapid must be positive integer')
                    elif bridge_receive[2] == None:
                        print('Please specify mapid (bm mapid). Ex : {} 1 '.format(bridge_receive[1]))
                    elif bridge_receive[2] == 'end':
                        self.BRIDGE_SHOW_VISION_DATA_RUN = False
                        self.XBOX_MOVE_STM32 = False
                # elif bridge_receive[1] == 'um':
                #     if type(bridge_receive[2]) == int:
                #         if bridge_receive[2] >= 0:
                #             self.VISION_SERVER.send_list(['V','um',int(bridge_receive[2])])
                #             self.bridge_show_vision_data_xbox()
                #         else:
                #             print('mapid must be positive integer')
                #     elif bridge_receive[2] == None:
                #         print('Please specify mapid (bm mapid). Ex : bm 1 ')
                #     elif bridge_receive[2] == 'end':
                #         self.BRIDGE_SHOW_VISION_DATA_RUN = False
                #         self.XBOX_MOVE_STM32 = False
                # elif bridge_receive[1] == 'kbm':
                #     if type(bridge_receive[2]) == int:
                #         if bridge_receive[2] >= 0:
                #             self.VISION_SERVER.send_list(['V','kbm',int(bridge_receive[2])])
                #             self.bridge_show_vision_data_xbox()
                #         else:
                #             print('mapid must be positive integer')
                #     elif bridge_receive[2] == None:
                #         print('Please specify mapid (bm mapid). Ex : bm 1 ')
                #     elif bridge_receive[2] == 'end':
                #         self.BRIDGE_SHOW_VISION_DATA_RUN = False
                #         self.XBOX_MOVE_STM32 = False
                        



            elif bridge_receive[0] == 'S':
                if bridge_receive[1] == 'next':
                    # self.COMMANDER_SERVER.send_list(['C','next'])
                    pass


            elif bridge_receive[0] == 'V':
                if bridge_receive[1] == 'next':
                    self.COMMANDER_SERVER.send_list(['C','next'])      


            elif bridge_receive[0] == 'L':
                if bridge_receive[1] == 'next':
                    self.COMMANDER_SERVER.send_list(['C','next']) 


            else:
                print('{} received . Wrong potorcol  !'.format(bridge_receive))
                logging.info('{} received . Wrong potorcol  !'.format(bridge_receive))
                

        except:
            print('\nError from Bridge : bridge_protocol \n')
            traceback.print_exc()
            logging.exception('Got error : ')
            print('\n\nForce abort current order')



    def bridge_show_vision_data(self):
        self.BRIDGE_SHOW_VISION_DATA_RUN = True
        while self.BRIDGE_SHOW_VISION_DATA_RUN:
            try:
                # self.COMMANDER_SERVER.send_list([self.VISION_STATUS , self.X , self.Y , self.THETA ])
                # self.BRIDGE_RECEIVE = self.COMMANDER_SERVER.recv_list()
                # self.bridge_protocol(self.BRIDGE_RECEIVE)
                receive = self.COMMANDER_UDP_CLIENT.recv_list()
                if receive == ['end']:
                    self.BRIDGE_SHOW_VISION_DATA_RUN = False
                print('status : {} | x : {} | y : {} | theta : {} | Use Ctrl+C or enter any key to end current process : '\
                    .format(self.VISION_STATUS,self.X,self.Y,self.THETA))
                time.sleep(0.1)
            except:
                print('\nError from Bridge : bridge_send_vision_data_to_commander\n')
                traceback.print_exc()
                logging.exception('Got error : ')
                self.BRIDGE_SHOW_VISION_DATA_RUN = False
        self.COMMANDER_SERVER.send_list(['C','next'])



    def bridge_show_vision_data_xbox(self):
        self.BRIDGE_SHOW_VISION_DATA_RUN = True
        self.XBOX_MOVE_STM32 = True
        self.xbox_get_data()
        while self.BRIDGE_SHOW_VISION_DATA_RUN:
            try:
                receive = self.COMMANDER_UDP_CLIENT.recv_list()
                if receive == ['end']:
                    self.BRIDGE_SHOW_VISION_DATA_RUN = False
                    self.XBOX_RUN = False
                print('status : {} | x : {} | y : {} | theta : {} | Use Ctrl+C or enter any key to end current process : '\
                    .format(self.VISION_STATUS,self.X,self.Y,self.THETA))                
                time.sleep(0.1)
            except:
                print('\nError from Bridge : bridge_send_vision_data_to_commander_xbox\n')
                traceback.print_exc()
                logging.exception('Got error : ')
                self.BRIDGE_SHOW_VISION_DATA_RUN = False
                self.XBOX_RUN = False
        self.XBOX_MOVE_STM32 = False
        self.COMMANDER_SERVER.send_list(['C','next'])



    def show_vision_status(self):
        if self.VISION_STATUS == 0:
            print("Vision module status : {} | Vision module is booting".format(self.VISION_STATUS))
        elif self.VISION_STATUS == 1:
            print("Vision module status : {} | Vision module is waiting for 'st $mapid' command".format(self.VISION_STATUS))
        elif self.VISION_STATUS == 2:
            print("Vision module status : {} | Vision module is loading data ".format(self.VISION_STATUS))
        elif self.VISION_STATUS == 3:
            print('Vision module status : {} | Please move slowly, fp-slam is searching a set of best images to initialize'.format(self.VISION_STATUS))
        elif self.VISION_STATUS == 4:
            print('Vision module status : {} | System is working normaaly'.format(self.VISION_STATUS))
        elif self.VISION_STATUS == 5:
            print('Vision module status : {} | Lost Lost Lost'.format(self.VISION_STATUS))
        else:
            print('Unknown status code : {}'.format(self.VISION_STATUS))







if __name__ == "__main__":
    # bridge_init()
    # bridge_main()
    # end_bridge()
    Bridge()

