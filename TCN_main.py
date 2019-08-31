#!/usr/bin/python3
import TCN_socket
import time
import subprocess
import traceback
import threading
import TCN_xbox
import logging

class Commander():
    def __init__(self,AUTO_RUN = True):
        logging.basicConfig(filename='Main.log',filemode = 'w',level =logging.INFO)
        self.AUTO_RUN = AUTO_RUN
        self.COMMANDER_SERVER = None
        self.COMMANDER_RUN = False
        self.COMMANDER_SERVER_RUN = True


        if self.AUTO_RUN:
            self.bridge_init()
            self.commander_main()

########### Commander TCP Server version #############
    def bridge_init(self):
        if self.COMMANDER_SERVER_RUN == False:
            self.PROCESS_BRIDGE = subprocess.Popen('sudo python3 TCN_bridge.py',shell = True)
            print('##### Initializing communication center #####')
            logging.info("Bridge initializing")
            time.sleep(1)    # Wait some time for assuming Communication center(CC) work  稍微delay，以確保CC正常運作
            print("Establish TCP connection to communication center\nSend test data ['C',1,2,3]")
            self.COMMANDER_SERVER = TCN_socket.TCP_server(50000)
            commander_receive = self.COMMANDER_SERVER.recv_list()
            self.commander_protocol(commander_receive) # Waiting for [ 'C' , 'next' ]
            logging.info("Bridge - commander initialization completed\n")
            self.COMMANDER_SERVER_RUN = True
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
                    print('Commander run : {} \nCommander server run : {}'.format(self.COMMANDER_RUN,self.COMMANDER_SERVER_RUN))
                elif command == 'bi':
                    self.bridge_init()

                elif command and self.COMMANDER_SERVER_RUN == False:
                    print("Commander server is not working, please use 'bi' command to initialize bridge first ")
                
                elif command and self.COMMANDER_SERVER_RUN == True:
                    if command == 'exit':
                        if len(command_list) > 1:
                            if command_list[1]== 'all':
                                self.end_commander()
                            elif command_list[1] == 'b':
                                self.COMMANDER_SERVER.send_list(['C','exit','all'])
                                print('Commander server will be close in 5 second')
                                time.sleep(5)
                                self.COMMANDER_SERVER.close()
                                self.COMMANDER_SERVER = None
                                self.COMMANDER_SERVER_RUN = False
                            elif command_list[1] == 'l':
                                self.COMMANDER_SERVER.send_list(['C','exit','l'])
                            elif command_list[1] == 's':
                                self.COMMANDER_SERVER.send_list(['C','exit','s'])
                            elif command_list[1] == 'v':
                                self.COMMANDER_SERVER.send_list(['C','exit','v'])
                            else:
                                print("Please specify which exit command to use Ex:'exit all'")
                    elif command == 'gld':
                        self.COMMANDER_SERVER.send_list(['C','gld'])
                        print(self.COMMANDER_SERVER.recv_list(16384))
                    elif command == 'gs':
                        self.COMMANDER_SERVER.send_list(['C','gs'])
                        self.show_vision_status(self.COMMANDER_SERVER.recv_list())
                    elif command == 'gp':
                        if len(command_list) > 1:
                            if command_list[1] == 'c':
                                self.COMMANDER_SERVER.send_list(['C','gp','c'])
                                self.show_vision_data()
                            elif command_list[1] == 'x':
                                self.COMMANDER_SERVER.send_list(['C','gp','x'])
                                self.show_vision_data()
                        else:
                            self.COMMANDER_SERVER.send_list(['C','gp'])
                            commander_receive = self.COMMANDER_SERVER.recv_list()
                            print('status : {} | x : {} | y : {} | theta : {} | Use Ctrl+C to terminate'.format(commander_receive[0],commander_receive[1],commander_receive[2],commander_receive[3]))


                    
            except KeyboardInterrupt:
                self.end_commander()
            except:
                self.end_commander()
                traceback.print_exc()            

    def show_vision_data(self):
        run = True
        while run:
            try:
                commander_receive = self.COMMANDER_SERVER.recv_list()
                print('status : {} | x : {} | y : {} | theta : {} | Use Ctrl+C to terminate'.format(commander_receive[0],commander_receive[1],commander_receive[2],commander_receive[3]))
                time.sleep(0.2)
                commander_receive.send_list(['C','next'])
            except:
                commander_receive.send_list(['C','halt'])
                run = False

    def help(self):
        print('\nCommander relative\n')
        print("cs : Check for commander status")
        print("bi : Initialize bridge")
        print("exit all : Close all process")
        
        print("\nBridge relative\n")
        print("exit b : Close bridge and commander server")
        
        print("\nLiDAR relative\n")
        print("gld : Show instant LiDAR data")
        print("exit l : Close LiDAR ")

        print("\nVision relative\n")
        print("gs : Get vision module status")
        print("gp : Show vision data")


    def end_commander(self):
        if self.COMMANDER_SERVER != None:
            self.COMMANDER_SERVER.send_list(['C','exit','all'])
            print('All process will be closed in 5 second')
            time.sleep(5)
            self.COMMANDER_SERVER.close()
            self.COMMANDER_SERVER = None
        self.COMMANDER_SERVER_RUN = False
        self.COMMANDER_RUN = False
        logging.info('Commander end')



    def commander_protocol(self,commander_receive):
        logging.info("Commander received : {}".format(commander_receive))

        if commander_receive[0] == 'C':
            if commander_receive[1] == 'next':
                pass

            if commander_receive[1] == 'gld':
                print(commander_receive[2])


    def show_vision_status(self,vision_status):
        if vision_status == 0:
            print("Vision module status : {} | Vision module is booting".format(vision_status))
        elif vision_status == 1:
            print("Vision module status : {} | Vision module is waiting for 'st $mapid' command".format(vision_status))
        elif vision_status == 2:
            print("Vision module status : {} | Vision module is loading data ".format(vision_status))
        elif vision_status == 3:
            print('Vision module status : {} | Please move slowly, fp-slam is searching a set of best images to initialize'.format(vision_status))
        elif vision_status == 4:
            print('Vision module status : {} | System is working normaaly'.format(vision_status))
        elif vision_status == 5:
            print('Vision module status : {} | Lost Lost Lost'.format(vision_status))
        else:
            print('Unknown status code : {}'.format(vision_status))



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
    xbox = TCN_xbox.xbox_controller()
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
