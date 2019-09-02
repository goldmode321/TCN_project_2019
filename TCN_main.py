#!/usr/bin/python3
import TCN_socket
import time
import subprocess
import os
import traceback
import threading
import TCN_xbox
import logging

class Commander():
    def __init__(self,AUTO_RUN = True):
        logging.basicConfig(filename='Main.log',filemode = 'w',level =logging.INFO)
        self.AUTO_RUN = AUTO_RUN
        self.COMMANDER_TCP_SERVER = None
        self.COMMANDER_RUN = False
        self.COMMANDER_TCP_SERVER_RUN = False


        if self.AUTO_RUN:
            self.bridge_init()
            self.COMMANDER_TCP_SERVER.recv_list()
            self.commander_main()
            

########### Commander TCP Server version #############
    def bridge_init(self):
        if self.COMMANDER_TCP_SERVER_RUN == False:
            self.PROCESS_BRIDGE = subprocess.Popen('sudo python3 TCN_bridge.py',shell = True, start_new_session = True)
            print('##### Initializing communication center #####')
            logging.info("Bridge initializing")
            print("Establish TCP connection to communication center\nSend test data ['C',1,2,3]")
            self.COMMANDER_UDP_SERVER = TCN_socket.UDP_server(50001)
            self.COMMANDER_TCP_SERVER = TCN_socket.TCP_server(50000)
            commander_receive = self.COMMANDER_TCP_SERVER.recv_list()
            self.commander_protocol(commander_receive) # Waiting for [ 'C' , 'next' ]
            logging.info("Bridge - commander initialization completed\n")
            self.COMMANDER_TCP_SERVER_RUN = True
        else:
            print('Bridge run already')

########### Commander TCP client version #############
    # def bridge_init(self):
    #     process_bridge = subprocess.Popen('python3 TCN_bridge.py',shell = True)
    #     print('##### Initializing communication center #####')
    #     logging.info("Bridge initializing")
    #     time.sleep(1)    # Wait some time for assuming Communication center(CC) work  稍微delay，以確保CC正常運作
    #     print("Establish TCP connection to communication center\nSend test data ['C',1,2,3]")
    #     commander_client = TCN_socket.TCP_client(50000)
    #     commander_receive = commander_client.recv_list()
    #     commander_portocol(commander_receive) # Waiting for [ 'C' , 'next' ]
    #     logging.info("Bridge - commander initialization completed\n")

    def commander_main(self):
        logging.info('Commander main start')
        self.COMMANDER_RUN = True
        while self.COMMANDER_RUN:
            try:
                command = input("Please enter command , enter 'h' for help : ")
                logging.info('Command : {}'.format(command))
                command_list = command.lower().split() #splits the input string on spaces
                command = command_list[0]
                
                if command == 'cs':
                    print('Commander run : {} \nCommander server run : {}'.format(self.COMMANDER_RUN,self.COMMANDER_TCP_SERVER_RUN))
                elif command == 'bi':
                    self.bridge_init()
                elif command == 'h':
                    self.help()

                elif command and self.COMMANDER_TCP_SERVER_RUN == False:
                    print("Commander server is not working, please use 'bi' command to initialize bridge first ")
                
                elif command and self.COMMANDER_TCP_SERVER_RUN == True:
                    if command == 'exit':
                        if len(command_list) > 1:
                            if command_list[1]== 'all':
                                self.end_commander()
                            elif command_list[1] == 'b':
                                self.COMMANDER_TCP_SERVER.send_list(['C','exit','all'])
                                print('Commander server will be close in 5 second')
                                time.sleep(5)
                                self.COMMANDER_TCP_SERVER.close()
                                self.COMMANDER_UDP_SERVER.close()
                                self.COMMANDER_TCP_SERVER = None
                                self.COMMANDER_TCP_SERVER_RUN = False
                            elif command_list[1] == 'l':
                                self.COMMANDER_TCP_SERVER.send_list(['C','exit','l'])
                            elif command_list[1] == 's':
                                self.COMMANDER_TCP_SERVER.send_list(['C','exit','s'])
                            elif command_list[1] == 'v':
                                self.COMMANDER_TCP_SERVER.send_list(['C','exit','v'])
                            elif command_list[1] == 'x':
                                self.COMMANDER_TCP_SERVER.send_list(['C','exit','x'])
                            else:
                                print("Please specify which exit command to use Ex:'exit all'")


                    ################ LiDAR ###############
                    elif command == 'li':
                        self.COMMANDER_TCP_SERVER.send_list(['C','li'])
                        self.commander_protocol(self.COMMANDER_TCP_SERVER.recv_list())
                    elif command == 'gld':
                        self.COMMANDER_TCP_SERVER.send_list(['C','gld'])
                        print(self.COMMANDER_TCP_SERVER.recv_list(16384))


                    ################ Vision #############
                    elif command == 'vi':
                        self.COMMANDER_TCP_SERVER.send_list(['C','vi'])
                        self.commander_protocol(self.COMMANDER_TCP_SERVER.recv_list())
                    elif command == 'vs':
                        self.COMMANDER_TCP_SERVER.send_list(['C','vs'])
                        commander_receive = self.COMMANDER_TCP_SERVER.recv_list()
                        print('Vision server : {}\nVision thread server : {}\nVision client : {}\nVision thread client : {}'.format(commander_receive[0],commander_receive[1],commander_receive[2],commander_receive[3]))
                    elif command == 'gs':
                        self.COMMANDER_TCP_SERVER.send_list(['C','gs'])
                        self.show_vision_status(self.COMMANDER_TCP_SERVER.recv_list())
                    elif command == 'gp':
                        if len(command_list) > 1:
                            if command_list[1] == 'c':
                                self.COMMANDER_TCP_SERVER.send_list(['C','gp','c'])
                                self.show_vision_data()
                            elif command_list[1] == 'x':
                                self.COMMANDER_TCP_SERVER.send_list(['C','gp','x'])
                                self.show_vision_data()
                        else:
                            self.COMMANDER_TCP_SERVER.send_list(['C','gp'])
                            commander_receive = self.COMMANDER_TCP_SERVER.recv_list()
                            print('status : {} | x : {} | y : {} | theta : {} | Use Ctrl+C to terminate'.format(commander_receive[0],commander_receive[1],commander_receive[2],commander_receive[3]))

                    ############### STM32 & XBOX ##############
                    elif command == 'xs':
                        self.COMMANDER_TCP_SERVER.send_list(['C','xs'])
                        commander_receive = self.COMMANDER_TCP_SERVER.recv_list()
                        print('XBOX run : {}\nXBOX move stm32 : {}\nXBOX X : {}\nXBOX Y : {}\nXBOX Z : {}\nXBOX STEP : {}\nXBOX thread alive : {}'\
                            .format(commander_receive[0],commander_receive[1],commander_receive[2],commander_receive[3],commander_receive[4],commander_receive[5],commander_receive[6]))
                    elif command == 'si':
                        self.COMMANDER_TCP_SERVER.send_list(['C','si'])
                        self.commander_protocol(self.COMMANDER_TCP_SERVER.recv_list())                   
                    elif command == 'mwx':
                        try:
                            self.COMMANDER_TCP_SERVER.send_list(['C','mwx'])
                            self.COMMANDER_TCP_SERVER.recv_list()
                        except KeyboardInterrupt:
                            print('KeyboardInterrupt')
                            self.COMMANDER_UDP_SERVER.send_list(['end'])
                            self.COMMANDER_TCP_SERVER.recv_list()
                            time.sleep(0.5)
                    
            except KeyboardInterrupt:
                print('Keyboard Interrupt')
                self.end_commander()
            except IndexError:
                pass
            except:
                self.end_commander()
                print('\nError From Commander\n')
                traceback.print_exc()            

    def show_vision_data(self):
        self.SHOW_VISION_DATA_RUN = True
        while self.SHOW_VISION_DATA_RUN:
            try:
                commander_receive = self.COMMANDER_TCP_SERVER.recv_list()
                print('status : {} | x : {} | y : {} | theta : {} | Use Ctrl+C to terminate'.format(commander_receive[0],commander_receive[1],commander_receive[2],commander_receive[3]))
                # time.sleep(0.2)
                self.COMMANDER_TCP_SERVER.send_list(['C','next'])
            except:
                self.COMMANDER_TCP_SERVER.send_list(['C','gp','exit'])
                self.SHOW_VISION_DATA_RUN = False
                time.sleep(0.5)
                self.COMMANDER_TCP_SERVER.recv_list()

    def help(self):
        print('\nCommander relative\n')
        print("cs : Check for commander status")
        print("exit all : Close all process")
        
        print("\nBridge relative\n")
        print("exit b : Close bridge and commander server")
        print("bi : Initialize bridge")
        
        print("\nLiDAR relative\n")
        print("gld : Show instant LiDAR data")
        print("li : Initialize LiDAR")
        print("exit l : Close LiDAR ")

        print("\nVision relative\n")
        print("gs : Get vision module status")
        print("gp : Show vision data")
        print("gp c : Continuous show vision data")
        print("gp x : Contunuous show vision data, with XBOX control")
        print("vs : Vision status")
        print("vi : Initialize Vision")
        print("exit v : Close vision")

        print("\nSTM32 relative\n")
        print("mwx : Enable xbox control")


    def end_commander(self):
        if self.COMMANDER_TCP_SERVER != None:
            self.COMMANDER_TCP_SERVER.send_list(['C','exit','all'])
            print('All process will be closed in 5 second')
            time.sleep(5)
            self.COMMANDER_TCP_SERVER.close()
            self.COMMANDER_UDP_SERVER.close()
            self.COMMANDER_TCP_SERVER = None
        self.COMMANDER_TCP_SERVER_RUN = False
        self.COMMANDER_RUN = False
        logging.info('Commander end')



    def commander_protocol(self,commander_receive):
        logging.info("Commander received : {}".format(commander_receive))

        if commander_receive[0] == 'C':
            if commander_receive[1] == 'next':
                pass
            elif commander_receive[1] == 'gp':
                if commander_receive[2] == 'exit':
                    self.SHOW_VISION_DATA_RUN = False
            elif commander_receive[1] == 'gld':
                print(commander_receive[2])
            elif commander_receive[1] == 'm':
                print(commander_receive[2])


    def show_vision_status(self,vision_status):
        if vision_status[0] == 0:
            print("Vision module status : {} | Vision module is booting".format(vision_status[0]))
        elif vision_status[0] == 1:
            print("Vision module status : {} | Vision module is waiting for 'st $mapid' command".format(vision_status[0]))
        elif vision_status[0] == 2:
            print("Vision module status : {} | Vision module is loading data ".format(vision_status[0]))
        elif vision_status[0] == 3:
            print('Vision module status : {} | Please move slowly, fp-slam is searching a set of best images to initialize'.format(vision_status[0]))
        elif vision_status[0] == 4:
            print('Vision module status : {} | System is working normaaly'.format(vision_status[0]))
        elif vision_status[0] == 5:
            print('Vision module status : {} | Lost Lost Lost'.format(vision_status[0]))
        else:
            print('Unknown status code : {}'.format(vision_status[0]))



process_stm32 = None
process_bridge = None
process_vision = None
process_lidar = None
process_algorithm = None
commander_client = None
commander_run = False
xbox = None

###                                                                   ###
###    Preview function                                               ###
###                                                                   ###

def help_menu():
    print(" exit : Quit software ")                 # [ 'C' , 'exit ']
    print(" xt : Xbox test ")                       # None
    print(" mwx : Xbox remote control ")            # [ 'C' , 'xbox' , [x,y,z] ]
    print(" xtg : Xbox test, gpio ")
    print(" gld : Get current lidar data ")
    


###                                                                   ###
###    Portocol for commander                                         ###
###                                                                   ###
'''
['C' , 'next' ]

'''
def commander_portocol(commander_receive):
    global commander_client,commander_run,xbox,process_bridge,process_stm32

    logging.info("Commander received : {}".format(commander_receive))

    if commander_receive[0] == 'C':
        if commander_receive[1] == 'next':
            pass

        if commander_receive[1] == 'gld':
            print(commander_receive[2])



###                                                                   ###
###    Initialize xbox. See TCN_xbox.py                               ###
###                                                                   ###
def xbox_init():
    global xbox
    xbox = TCN_xbox.Xbox_controller()
    logging.info('Xbox start without error')


###                                                                   ###
###    Run TCN_bridge.py (so called "Communication center (CC) ")     ###
###                                                                   ###
def commander_init():
    try:
        global commander_client,commander_run, process_bridge, process_stm32 , process_vision , process_lidar , process_algorithm
        
        process_bridge = subprocess.Popen('python3 TCN_bridge.py',shell = True)
        print('##### Initializing communication center #####')
        logging.info("Bridge - commander initialize")
        time.sleep(1)    # Wait some time for assuming Communication center(CC) work  稍微delay，以確保CC正常運作
        print("Establish TCP connection to communication center\nSend test data ['C',1,2,3]")
        commander_client = TCN_socket.TCP_client(50000)
        commander_receive = commander_client.recv_list()
        commander_portocol(commander_receive) # Waiting for [ 'C' , 'next' ]
        logging.info("Bridge - commander initialization completed\n")

        print('\n\n##### Initializing Vision module #####')
        logging.info("Vision module initialize")
        process_vision = subprocess.Popen('python3 TCN_vision_main.py',shell = True)
        commander_receive = commander_client.recv_list() # Waiting for [ 'C' , 'next' ]
        commander_portocol(commander_receive)
        logging.info("Vision module initialization complete\n")


        print('\n\n##### Initializing RPLiDAR #####')
        logging.info("RPLiDAR initialize")
        process_lidar = subprocess.Popen('python3 TCN_rplidar_main.py',shell = True)
        commander_receive = commander_client.recv_list() # Waiting for [ 'C' , 'next' ]
        commander_portocol(commander_receive)
        logging.info("Vision module initialization complete\n")


        print('\n\n##### Initializing STM32 #####')
        logging.info("STM32 initialize")
        process_stm32 = subprocess.Popen('python3 TCN_STM32_main.py',shell = True)
        commander_receive = commander_client.recv_list() # Waiting for [ 'C' , 'next' ]
        commander_portocol(commander_receive)
        logging.info("STM32 initialization complete\n")



        commander_run = True

            


    except:
        if process_algorithm != None:
            process_algorithm.kill()
        if process_stm32 != None:
            process_stm32.kill()
        if process_lidar != None:
            process_lidar.kill()
        if process_vision != None:
            process_vision.kill()
        if process_bridge != None:
            process_bridge.kill()            
        commander_client.close()
        xbox.close()
        traceback.print_exc()

        logging.exception("Got error : \n")




    # p_bridge = subprocess.Popen('python TCN_STM32_main.py',shell = True)
    # print('Initializing STM32 motor controller')


###                                                                   ###
###     Waiting for User Command                                      ###
###                                                                   ###
def main():
    global commander_client,commander_run, process_bridge, process_stm32 , process_vision , process_lidar , process_algorithm
    print('\n\n @@@ Program is all set, now is ready to run @@@')

    while commander_run:
        try:
            command = input('\nPlease enter command (Enter "h" for help menu) : ')
            if command == 'h':
                help_menu()

            elif command == 'exit':
                commander_client.send_list(['C','exit','all'])
                commander_run = False

            elif command == 'xt':
                xbox.xbox_test()

            elif command == 'mwx':
                while not xbox.joy.Back():
                    move_command = xbox.xbox_control()
                    commander_client.send_list(['C','mwx',move_command])
                    commander_receive = commander_client.recv_list()
                    commander_portocol(commander_receive)
                commander_client.send_list(['C','stop_motor'])

            elif command == 'gld':
                commander_client.send_list(['C','gld'])
                commander_receive = commander_client.recv_list()
                commander_portocol(commander_receive)


            else:
                commander_client.send_list(['C',command])
        
        except:
            commander_client.send_list(['C','exit','all'])
            commander_run = False
            
    commander_client.close()
    xbox.close()
    time.sleep(6)
    print('All program terminated')








if __name__ == "__main__":
    Commander()
    # xbox_init()
    # commander_init()
    # main()
