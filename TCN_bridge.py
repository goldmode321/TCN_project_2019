#!/usr/bin/python3
import TCN_socket
import time
import traceback
import subprocess
import sys
import threading
import logging
import TCN_xbox

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

        # Commander initail variables
        self.COMMANDER_SERVER_RUN = False

        # Vision initial variables
        self.X = 0
        self.Y = 0
        self.THETA = 0
        self.VISION_STATUS = 0
        self.VISION_RUN = False
        self.VISION_SERVER_RUN = False
        self.VISION_THREAD_SERVER_RUN = False
        self.VISION_THREAD_SERVER_STATUS = 0

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
            self.bridge_main()
        

############ XBOX initialize #########
    def xbox_init(self): 
        self.XBOX = TCN_xbox.Xbox_controller()

    def xbox_get_data(self):
        self.XBOX_THREAD = threading.Thread(target = self.xbox_main , daemon = True)
        self.XBOX_THREAD.start()

    def xbox_main(self):




############### Commander TCP Client Version ###############

    def commander_init(self):
        try:
            logging.info("Initialize commander client\n")
            self.COMMANDER_SERVER = TCN_socket.TCP_client(50000)
            self.COMMANDER_SERVER.send_list(['C','next'])
            logging.info("Commander connection complete !\n")
            self.COMMANDER_SERVER_RUN = True
        except:
            self.end_commander_server()
            traceback.print_exc()
            print('\n Commander is not initialize')
            logging.info('Bridge initializing fail at commander_init()\n')
            logging.exception("Got error : \n")

    def end_commander_server(self):
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
            self.VISION_THREAD_SERVER = TCN_socket.UDP_client(50006)
            self.VISION_SERVER = TCN_socket.TCP_server(50001)
            self.VISION_SERVER_RECEIVE = vision_server.recv_list()
            if self.VISION_SERVER_RECEIVE == ['V','status','Alive']:
                logging.info("Vision communication successfully established !\ncommunication center get : {} \n".format(self.VISION_SERVER_RECEIVE) )
                self.COMMANDER_SERVER.send_list(['C','next'])
                self.VISION_SERVER_RUN = True
                self.VISION_THREAD_SERVER_RUN = True
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
                self.VISION_RUN = vision_data[4]
                time.sleep(0.1)

    def end_vision_server(self):
        self.VISION_SERVER.send_list(['V','exit'])
        time.sleep(1)
        self.VISION_SERVER.close()
        self.VISION_SERVER_RUN = False
        logging.info('Vision server end')

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
            self.LIDAR_SERVER = TCN_socket.TCP_server(50002,1)
            self.LIDAR_THREAD_SERVER = TCN_socket.UDP_server(50004)
            lidar_data = self.LIDAR_SERVER.recv_list()
            if lidar_data == ['L','status','Good']:
                logging.info("Lidar communication successfully established !\ncommunication center get : {} \n".format(lidar_data) )
                self.LIDAR_SERVER_RUN = True
                self.LIDAR_THREAD_SERVER_RUN = True
                self.COMMANDER_SERVER.send_list(['C','next'])
            else:
                self.end_lidar_server()
                self.end_lidar_thread_server()
                print('Undefined communication error of Vision module, please check test message')
                logging.info("Undefined communication error of Vision module, please check test message\n")
                raise KeyboardInterrupt      
        except:
            self.LIDAR_SERVER.close()
            self.LIDAR_THREAD_SERVER.close()
            traceback.print_exc()
            logging.info('Bridge initializing fail at lidar_init()\n')
            logging.exception("Got error : \n")

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
        self.LIDAR_SERVER.send_list(['V','exit'])
        time.sleep(1)
        self.LIDAR_SERVER.close()
        self.LIDAR_SERVER_RUN = False
        logging.info('LiDAR server end')

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
            self.STM32_SERVER = TCN_socket.TCP_server(50003,1)
            self.STM32_THREAD_SERVER = TCN_socket.UDP_server(50005)
            stm32_data = self.STM32_SERVER.recv_list()
            if stm32_data == ['S','next']:
                self.STM32_SERVER_RUN = True
                self.STM32_THREAD_SERVER_RUN = True
                logging.info("Lidar communication successfully established !\ncommunication center get : {} \n".format(stm32_data) )
            else:
                self.end_stm32_server()
                self.end_stm32_thread_server()
        except:
            time.sleep(0.3)
            self.STM32_SERVER.close()
            self.STM32_THREAD_SERVER.close()
            traceback.print_exc()
            print('Bridge initializing fail at stm32_init()')

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
        self.STM32_SERVER.send_list(['S','exit'])
        time.sleep(1)
        self.STM32_SERVER.close()
        self.STM32_SERVER_RUN = False
        logging.info('STM32 server end')

    def end_stm32_thread_server(self):
        self.STM32_THREAD_SERVER.close()
        if self.STM32_THREAD_SERVER_RUN == True:
            self.STM32_THREAD_SERVER_RUN = False
            self.STM32_THREAD.join()
            self.STM32_THREAD_SERVER_STATUS = self.STM32_THREAD.is_alive()  
        logging.info('STM32 thread ')

############ Bridge main ###################
    def bridge_main(self):
        self.BRIDGE_RUN = True
        while self.BRIDGE_RUN:
            try:
                self.BRIDGE_RECEIVE = self.COMMANDER_SERVER.recv_list()
                if self.BRIDGE_RECEIVE != None:
                    self.bridge_protocol(self.BRIDGE_RECEIVE)
                else:
                    print('Bridge received {}'.format(self.BRIDGE_RECEIVE))
                    print('Please check commander status !')
                    time.sleep(0.5)
            except:
                print('Critical error happened on Bridge , all programs have to be shutdown')
                self.end_bridge_all()
                traceback.print_exc()
                logging.exception('Got error :')
                self.BRIDGE_RUN = False

    def end_bridge_all(self):
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
                print('socket may got problem')

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

                if bridge_receive[1] == 'next':
                    pass
                
                    
                # elif commander_data[1] == 'key_move':
                #     stm32_server.send_list(['S','move',[ commander_data[2],commander_data[3],commander_data[4] ] ])
                
                elif bridge_receive[1] == 'mwx':
                    self.STM32_SERVER.send_list(['S','move',bridge_receive[2]])
                    bridge_receive = self.STM32_SERVER.recv_list()
                    self.bridge_potorcol(bridge_receive)

                elif bridge_receive[1] == 'gld':
                    self.COMMANDER_SERVER.send_list([self.LIDAR_DATA])
                    

                elif bridge_receive[1] == 'stop_motor':
                    self.STM32_SERVER.send_list(['S','stop'])


                elif bridge_receive[1] == 'al':
                    self.VISION_SERVER.send_list(['V','al'])
                elif bridge_receive[1] == 'cc':
                    self.VISION_SERVER.send_list(['V','cc'])
                elif bridge_receive[1] == 'gp':
                    try:
                        if bridge_receive[2] == 'c':
                            self.bridge_send_vision_data_to_commander()
                        elif bridge_receive[2] == 'x':
                            self.bridge_send_vision_data_to_commander_xbox()
                    except IndexError:
                        self.COMMANDER_SERVER.send_list([ self.VISION_STATUS , self.X , self.Y , self.THETA ])
                elif bridge_receive[1] == 'gs':
                    self.COMMANDER_SERVER.send_list([self.VISION_STATUS])
                elif bridge_receive[1] == 'sv':
                    self.VISION_SERVER.send_list(['V','sv'])
                elif bridge_receive[1] == 'rs':
                    self.VISION_SERVER.send_list(['V','rs'])
                    print('reset vision , please wait 5 second')
                    time.sleep(5)
                elif bridge_receive[1] == 'bm':
                    if type(bridge_receive[2]) == int:
                        if bridge_receive[2] >= 0:
                            self.VISION_SERVER.send_list(['V','bm',int(bridge_receive[2])])
                            self.bridge_send_vision_data_to_commander()
                        else:
                            print('mapid must be positive integer')
                    elif bridge_receive[2] == None:
                        print('Please specify mapid (bm mapid). Ex : bm 1 ')
                    elif bridge_receive[2] == 'end':
                        self.BRIDGE_SEND_VISION_DATA_TO_COMMANDER_RUN = False
                elif bridge_receive[1] == 'um':
                    if type(bridge_receive[2]) == int:
                        if bridge_receive[2] >= 0:
                            self.VISION_SERVER.send_list(['V','um',int(bridge_receive[2])])
                            self.bridge_send_vision_data_to_commander()
                        else:
                            print('mapid must be positive integer')
                    elif bridge_receive[2] == None:
                        print('Please specify mapid (bm mapid). Ex : bm 1 ')
                    elif bridge_receive[2] == 'end':
                        self.BRIDGE_SEND_VISION_DATA_TO_COMMANDER_RUN = False
                elif bridge_receive[1] == 'kbm':
                    if type(bridge_receive[2]) == int:
                        if bridge_receive[2] >= 0:
                            self.VISION_SERVER.send_list(['V','kbm',int(bridge_receive[2])])
                            self.bridge_send_vision_data_to_commander()
                        else:
                            print('mapid must be positive integer')
                    elif bridge_receive[2] == None:
                        print('Please specify mapid (bm mapid). Ex : bm 1 ')
                    elif bridge_receive[2] == 'end':
                        self.BRIDGE_SEND_VISION_DATA_TO_COMMANDER_RUN = False



            elif bridge_receive[0] == 'S':
                if bridge_receive[1] == 'next':
                    self.COMMANDER_SERVER.send_list(['C','next'])


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
            traceback.print_exc()
            print('\n\nForce abort current order')



    def bridge_send_vision_data_to_commander(self):
        self.BRIDGE_SEND_VISION_DATA_TO_COMMANDER_RUN = True
        while self.BRIDGE_SEND_VISION_DATA_TO_COMMANDER_RUN:
            try:
                self.COMMANDER_SERVER.send_list([self.VISION_STATUS , self.X , self.Y , self.THETA ])
                self.BRIDGE_RECEIVE = self.COMMANDER_SERVER.recv_list()
                self.bridge_protocol(self.BRIDGE_RECEIVE)
                # print('status : {} | x : {} | y : {} | theta : {} | Use Ctrl+C to terminate'.format(self.VISION_STATUS,self.X,self.Y,self.THETA))
                time.sleep(0.1)
            except:
                traceback.print_exc()
                self.BRIDGE_SEND_VISION_DATA_TO_COMMANDER_RUN = False

    def bridge_send_vision_data_to_commander_xbox(self):
        self.BRIDGE_SEND_VISION_DATA_TO_COMMANDER_RUN = True
        while self.BRIDGE_SEND_VISION_DATA_TO_COMMANDER_RUN:
            try:
                self.COMMANDER_SERVER.send_list([self.VISION_STATUS , self.X , self.Y , self.THETA ])
                self.BRIDGE_RECEIVE = self.COMMANDER_SERVER.recv_list()
                self.bridge_protocol(self.BRIDGE_RECEIVE)
                # print('status : {} | x : {} | y : {} | theta : {} | Use Ctrl+C to terminate'.format(self.VISION_STATUS,self.X,self.Y,self.THETA))
                time.sleep(0.1)
            except:
                traceback.print_exc()
                self.BRIDGE_SEND_VISION_DATA_TO_COMMANDER_RUN = False


'''Portocol'''
''' "C" to Main , "L" to LiDAR , "S" to STM32 , "G" to GPIO , "X" to xbox, "V" to Vision , "M" to motion '''

###                                                                   ###
###    global variables                                               ###
###                                                                   ###


commander_server = None
lidar_server = None
stm32_server = None
vision_server = None
bridge_run = False



def bridge_init():
    global commander_server,stm32_server , vision_server , lidar_server , bridge_run
    try:
        commander_init()
        vision_init()
        lidar_init()
        stm32_init()
        bridge_run = True
        logging.info("Bridge is ready to run ! \n")
    except:
        if commander_server != None:
            commander_server.close()
        if vision_server != None:
            vision_server.close()
        if stm32_server != None:
            stm32_server.close()
        bridge_run = False
        sys.exit(0)


###                                                                   ###
###    Gateway for commander communication. See TCN_main.py           ###
###                                                                   ###
def commander_init():
    global commander_server
    try:
        logging.info("Initialize commander server\n")
        commander_server = TCN_socket.TCP_server(50000,1)
        commander_server.send_list(['C','next'])
        logging.info("Commander connection complete !\n")

    except:
        commander_server.close()
        traceback.print_exc()
        logging.info('Bridge initializing fail at commander_init()\n')
        logging.exception("Got error : \n")
        

###                                                                            ###
###    Gateway for Vision module communication. See TCN_vision_main.py         ###
###                                                                            ###

def vision_init():
    global vision_server,commander_server
    try:
        logging.info("Initialize vision server\n")
        vision_server = TCN_socket.TCP_server(50001,1)
        vision_data = vision_server.recv_list()
        if vision_data == ['V','status','Alive']:
            logging.info("Vision communication successfully established !\ncommunication center get : {} \n".format(vision_data) )
            commander_server.send_list(['C','next'])
        else:
            print('Undefined communication error of Vision module, please check test message')
            logging.info("Undefined communication error of Vision module, please check test message\n")
            raise KeyboardInterrupt      
    except:
        traceback.print_exc()
        logging.info('Bridge initializing fail at vision_init()\n')
        logging.exception("Got error : \n")



###                                                                            ###
###    Gateway for RPLiDAR communication. See TCN_vision_main.py               ###
###                                                                            ###

def lidar_init():
    global lidar_server,commander_server
    try:
        logging.info("Initialize lidar server\n")
        lidar_server = TCN_socket.TCP_server(50002,1)
        lidar_data = lidar_server.recv_list()
        if lidar_data == ['L','status','Good']:
            logging.info("Lidar communication successfully established !\ncommunication center get : {} \n".format(lidar_data) )
            commander_server.send_list(['C','next'])
        else:
            print('Undefined communication error of Vision module, please check test message')
            logging.info("Undefined communication error of Vision module, please check test message\n")
            raise KeyboardInterrupt      
    except:
        traceback.print_exc()
        logging.info('Bridge initializing fail at lidar_init()\n')
        logging.exception("Got error : \n")





###                                                                   ###
###    Gateway for STM32 communication. See TCN_STM32_main.py         ###
###                                                                   ###

def stm32_init():
    global stm32_server
    try:
        logging.info("Initialize STM32 server\n")
        stm32_server = TCN_socket.TCP_server(50003,1)
        stm32_data = stm32_server.recv_list()
        bridge_potorcol(stm32_data)
        # if stm32_data == ['S',1,2,3]:
        #     print("STM32 communication successfully established !\ncommunication center get : {}".format(stm32_data) )
        #     stm32_server.send_list(['S','T','M',3,2])
        #     print("Send back ['S','T','M',3,2] for double check")
        #     commander_server.send_list(['C','next'])
        # else:
        #     print('Undefined communication error of STM32, please check test message')
        #     raise KeyboardInterrupt      
    except:
        stm32_server.close()
        traceback.print_exc()
        print('Bridge initializing fail at stm32_init()')
        logging.info('Bridge initializing fail at stm32_init()\n')
        logging.exception("Got error : \n")


###                                                                   ###
###    Portocol for bridge                                            ###
###                                                                   ###

'''
[ 'C' , 'exit ']                received
    ['S', 'exit' ]              send to STM

[ 'C' , 'mwx' , [x,y,z] ]       received
    ['S' ,'move', [x,y,z] ]     send to STM
        ['S' , next]            received
            ['C' , 'next']      send to commander

[ 'C' , 'stop_motor ']          received
    ['S' , 'stop' ]             send to STM




'''
'''
['S' , 'next']
    ['C' , 'next' ]

'''

def bridge_potorcol(receive_data):
    global commander_server , stm32_server , vision_server , bridge_run
    '''First, get commander command (TCN_main.py)'''
    try:
        if receive_data == None:
            print('socket got problem')

        elif receive_data[0] == 'C':
            if receive_data[1] == 'exit':
                if receive_data[2] == 'all':
                    stm32_server.send_list(['S','exit'])
                    vision_server.send_list(['V','exit'])
                    lidar_server.send_list(['L','exit'])
                    print('All server will be close in 3 second')
                    time.sleep(3)
                    commander_server.close()
                    stm32_server.close()
                    vision_server.close()
                    lidar_server.close()
                    bridge_run = False
                
            # elif commander_data[1] == 'key_move':
            #     stm32_server.send_list(['S','move',[ commander_data[2],commander_data[3],commander_data[4] ] ])
            
            elif receive_data[1] == 'mwx':
                stm32_server.send_list(['S','move',receive_data[2]])
                receive_data = stm32_server.recv_list()
                bridge_potorcol(receive_data)

            elif receive_data[1] == 'gld':
                lidar_server.send_list(['L','gld'])
                lidar_data = lidar_server.recv_list()
                logging.info("gld : received from lidar : {} ".format(lidar_data))
                bridge_potorcol(lidar_data)
                

            elif receive_data[1] == 'stop_motor':
                stm32_server.send_list(['S','stop'])

        elif receive_data[0] == 'S':
            if receive_data[1] == 'next':
                commander_server.send_list(['C','next'])



        elif receive_data[0] == 'V':
            if receive_data[1] == 'next':
                commander_server.send_list(['C','next'])      

        elif receive_data[0] == 'L':
            if receive_data[1] == 'next':
                commander_server.send_list(['C','next']) 
            
            if receive_data[1] == 'gld':
                commander_server.send_list(['C','gld',receive_data[2]])

        else:
            print('{} received . Wrong potorcol  !'.format(receive_data))
            logging.info('{} received . Wrong potorcol  !'.format(receive_data))
            

    except:
        commander_server.close()
        stm32_server.close()
        vision_server.close()
        traceback.print_exc()
        logging.exception("Got error : \n")
    




###                                                                   ###
###    Waiting for command from TCN_main.py                           ###
###                                                                   ###
def bridge_main():
    global commander_server,stm32_server , vision_server , bridge_run

    while bridge_run:
        try:
            commander_data = commander_server.recv_list()
            logging.info("Bridge receive {} from commander\n".format(commander_data))
            bridge_potorcol(commander_data)

        except:
            commander_server.close()
            vision_server.close()
            stm32_server.close()
            traceback.print_exc()
            logging.exception("Got error : \n")
            bridge_run = False

def end_bridge():
    commander_server.close()
    vision_server.close()
    stm32_server.close()
    logging.info("Bridge close successfully")
            



if __name__ == "__main__":
    # bridge_init()
    # bridge_main()
    # end_bridge()
    Bridge()


# time.sleep(5)
# commander_server.close()
# stm32_server.close()












# class bridge_portocol(object):

#     def Command_potorcol(self,command):
#         if command[0] == 'C':
#             if command[1] == 'exit':
#                 stm32_server.send_list['S',command[1]]
#                 commander_server.close()
#                 stm32_server.close()

#         else:
#             print('Wrong potorcol from commander ')


