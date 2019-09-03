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
            self.COMMANDER_UDP_SERVER = TCN_socket.UDP_server(50001)
            self.COMMANDER_TCP_SERVER = TCN_socket.TCP_server(50000)
            self.COMMANDER_TCP_SERVER.recv_list()
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
                        self.COMMANDER_TCP_SERVER.recv_list()
                    elif command == 'gld':
                        self.COMMANDER_TCP_SERVER.send_list(['C','gld'])


                    ################ Vision #############
                    elif command == 'vi':
                        self.COMMANDER_TCP_SERVER.send_list(['C','vi'])
                        self.COMMANDER_TCP_SERVER.recv_list()
                    elif command == 'vs':
                        self.COMMANDER_TCP_SERVER.send_list(['C','vs'])
                    elif command == 'gs':
                        self.COMMANDER_TCP_SERVER.send_list(['C','gs'])
                    elif command == 'al':
                        self.COMMANDER_TCP_SERVER.send_list(['C','al'])
                    elif command == 'cc':
                        self.COMMANDER_TCP_SERVER.send_list(['C','cc'])
                    elif command == 'gp':
                        if len(command_list) > 1:
                            self.COMMANDER_TCP_SERVER.send_list(['C','gp',command_list[1]])
                            try:
                                input("Use Ctrl+C or enter any key to end current process : ")
                                self.COMMANDER_UDP_SERVER.send_list(['end'])
                            except:
                                self.COMMANDER_UDP_SERVER.send_list(['end'])
                            self.COMMANDER_TCP_SERVER.recv_list()
                        else:
                            self.COMMANDER_TCP_SERVER.send_list(['C','gp'])
                    elif command == 'bm' or command == 'um' or command == 'kbm':
                        if len(command_list) > 1:
                            self.COMMANDER_TCP_SERVER.send_list(['C', command , command_list[1] ])
                            try:
                                input("Use Ctrl+C or enter any key to end current process : ")
                                self.COMMANDER_UDP_SERVER.send_list(['end'])
                            except:
                                self.COMMANDER_UDP_SERVER.send_list(['end'])
                            self.COMMANDER_TCP_SERVER.recv_list()
                        else:
                            print('Please specify mapid')

                    ############### STM32 & XBOX ##############
                    elif command == 'xs':
                        self.COMMANDER_TCP_SERVER.send_list(['C','xs'])
                    elif command == 'si':
                        self.COMMANDER_TCP_SERVER.send_list(['C','si'])
                        self.COMMANDER_TCP_SERVER.recv_list()                   
                    elif command == 'mwx':
                        try:
                            self.COMMANDER_TCP_SERVER.send_list(['C','mwx'])
                            input("Use Ctrl+C or enter any key to end current process : ")
                            self.COMMANDER_UDP_SERVER.send_list(['end'])
                        except KeyboardInterrupt:
                            print('KeyboardInterrupt')
                            self.COMMANDER_UDP_SERVER.send_list(['end'])
                            time.sleep(0.5)
                        self.COMMANDER_TCP_SERVER.recv_list()
                    elif command == 'stop':
                        self.COMMANDER_TCP_SERVER.send_list(['C','stop'])
                    
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
        print("si : Initialize STM32")
        print("exit s : Close STM32")
        print("stop : stop motor")
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




if __name__ == "__main__":
    Commander()
    # xbox_init()
    # commander_init()
    # main()
