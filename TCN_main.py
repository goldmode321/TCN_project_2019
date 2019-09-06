#!/usr/bin/python3
''' tcn_main is the user controller, it is called 'commander' in the system '''


import time
import subprocess
import traceback
import logging
import tcn_socket

class Commander():
    ''' Master of current TCN system '''
    def __init__(self, auto_run=True):
        logging.basicConfig(filename='Main.log', filemode='w', level=logging.INFO)
        self.auto_run = auto_run
        self._commander_tcp_server = None
        self.commander_run = False
        self.commander_tcp_server_run = False
        self.show_vision_data_run = False


        if self.auto_run:
            self.bridge_init()
            self._commander_tcp_server.recv_list()
            self.commander_main()

########### Commander TCP Server version #############
    def bridge_init(self):
        ''' This is used to initial bridge, it also initialize other components'''
        if self.commander_tcp_server_run is False:
            subprocess.Popen('sudo python3 TCN_bridge.py'\
                , shell=True, start_new_session=True)
            print('##### Initializing communication center #####')
            logging.info("Bridge initializing")
            self._commander_udp_client = tcn_socket.UDP_client(50001)
            self._commander_tcp_server = tcn_socket.TCP_server(50000)
            self._commander_tcp_server.recv_list()
            logging.info("Bridge - commander initialization completed\n")
            self.commander_tcp_server_run = True
        else:
            print('Bridge run already')

    def commander_main(self):
        '''Main function for commander '''
        logging.info('Commander main start')
        self.commander_run = True
        while self.commander_run:
            try:
                command = input("\nPlease enter command , enter 'h' for _help : ")
                logging.info('Command : %s', command)
                command_list = command.lower().split() #splits the input string on spaces
                command = command_list[0]

                if command == 'cs':
                    print('Commander run : {} \nCommander server run : {}'.\
                        format(self.commander_run, self.commander_tcp_server_run))
                elif command == 'bi':
                    self.bridge_init()
                elif command == 'h':
                    _help()

                elif command is not None and not self.commander_tcp_server_run:
                    print("Commander server is not working, please use 'bi' \
                        command to initialize bridge first ")

                elif command is not None and self.commander_tcp_server_run:
                    if command == 'exit':
                        if len(command_list) > 1:
                            if command_list[1] == 'all':
                                self.end_commander()
                            elif command_list[1] == 'b':
                                self._commander_tcp_server.send_list(['C', 'exit', 'all'])
                                print('Commander server will be close in 5 second')
                                time.sleep(5)
                                self._commander_tcp_server.close()
                                self._commander_udp_client.close()
                                self._commander_tcp_server = None
                                self.commander_tcp_server_run = False
                            elif command_list[1] == 'l':
                                self._commander_tcp_server.send_list(['C', 'exit', 'l'])
                            elif command_list[1] == 's':
                                self._commander_tcp_server.send_list(['C', 'exit', 's'])
                            elif command_list[1] == 'v':
                                self._commander_tcp_server.send_list(['C', 'exit', 'v'])
                            elif command_list[1] == 'x':
                                self._commander_tcp_server.send_list(['C', 'exit', 'x'])
                            else:
                                print("Please specify which exit command to use Ex:'exit all'")


                    ################ LiDAR ###############
                    elif command == 'li':
                        self._commander_tcp_server.send_list(['C', 'li'])
                        self._commander_tcp_server.recv_list()
                    elif command == 'gld':
                        self._commander_tcp_server.send_list(['C', 'gld'])


                    ################ Vision #############
                    elif command == 'vi':
                        self._commander_tcp_server.send_list(['C', 'vi'])
                        self._commander_tcp_server.recv_list()
                    elif command == 'vs':
                        self._commander_tcp_server.send_list(['C', 'vs'])
                    elif command == 'gs':
                        self._commander_tcp_server.send_list(['C', 'gs'])
                    elif command == 'al':
                        self._commander_tcp_server.send_list(['C', 'al'])
                    elif command == 'cc':
                        self._commander_tcp_server.send_list(['C', 'cc'])
                    elif command == 'vrs':
                        self._commander_tcp_server.send_list(['C', 'vrs'])
                        print('Vision is reseting , please wait 5 second')
                        time.sleep(5)
                    elif command == 'gp':
                        if len(command_list) > 1:
                            self._commander_tcp_server.send_list(['C', 'gp', command_list[1]])
                            try:
                                input("Use Ctrl+C or enter any key to end current process : ")
                                self._commander_udp_client.send_list(['end'])
                            except KeyboardInterrupt:
                                self._commander_udp_client.send_list(['end'])
                            self._commander_tcp_server.recv_list()
                        else:
                            self._commander_tcp_server.send_list(['C', 'gp'])
                    elif command in ['bm', 'um', 'kbm']:
                        if len(command_list) > 1:
                            self._commander_tcp_server.send_list(['C', command, command_list[1]])
                            try:
                                input("Use Ctrl+C or enter any key to end current process : ")
                                self._commander_udp_client.send_list(['end'])
                            except KeyboardInterrupt:
                                self._commander_udp_client.send_list(['end'])
                            self._commander_tcp_server.recv_list()
                        else:
                            print('Please specify mapid')


                    ############### STM32 & XBOX ##############
                    elif command == 'xs':
                        self._commander_tcp_server.send_list(['C', 'xs'])
                    elif command == 'si':
                        self._commander_tcp_server.send_list(['C', 'si'])
                        self._commander_tcp_server.recv_list()
                    elif command == 'mwx':
                        try:
                            self._commander_tcp_server.send_list(['C', 'mwx'])
                            input("Use Ctrl+C or enter any key to end current process : ")
                            self._commander_udp_client.send_list(['end'])
                        except KeyboardInterrupt:
                            print('KeyboardInterrupt')
                            self._commander_udp_client.send_list(['end'])
                            time.sleep(0.5)
                        self._commander_tcp_server.recv_list()
                    elif command == 'stop':
                        self._commander_tcp_server.send_list(['C', 'stop'])
                    elif command == 'xi':
                        self._commander_tcp_server.send_list(['C', 'xi'])
                        self._commander_tcp_server.recv_list()

                time.sleep(0.1)
            except KeyboardInterrupt:
                print('Keyboard Interrupt')
                self.end_commander()
            except IndexError:
                pass
            except:
                self.end_commander()
                print('\nError From Commander\n')
                traceback.print_exc()

    def end_commander(self):
        '''Used for end tcn_main , please note this will also shutdown tcn system'''
        if self._commander_tcp_server is not None:
            self._commander_tcp_server.send_list(['C', 'exit', 'all'])
            print('All process will be closed in 5 second')
            time.sleep(5)
            self._commander_tcp_server.close()
            self._commander_udp_client.close()
            self._commander_tcp_server = None
        self.commander_tcp_server_run = False
        self.commander_run = False
        logging.info('Commander end')



    def _commander_protocol(self, commander_receive):
        ''' Used for handle the protocol between commander and bridge'''
        logging.info("Commander received : {}".format(commander_receive))

        if commander_receive[0] == 'C':
            if commander_receive[1] == 'next':
                pass
            elif commander_receive[1] == 'gp':
                if commander_receive[2] == 'exit':
                    self.show_vision_data_run = False
            elif commander_receive[1] == 'gld':
                print(commander_receive[2])
            elif commander_receive[1] == 'm':
                print(commander_receive[2])


    @staticmethod
    def _help():
        ''' Help manmual'''
        
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

        print("\nXBOX relative\n")
        print("mwx : Enable xbox control")
        print("xi : Initialize xbox ")
        print("xs : Show xbox status")
        print("exit x : Close xbox")



if __name__ == "__main__":
    Commander()
    # xbox_init()
    # commander_init()
    # main()
