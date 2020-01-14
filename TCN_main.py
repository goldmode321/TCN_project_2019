#!/usr/bin/python3
''' tcn_main is the user controller, it is called 'commander' in the system '''


import time
import subprocess
import traceback
import logging
import tcn_shared_variable
import TCN_socket

class Main():

    def __init__(self, auto_start=True):

        self.SV = tcn_shared_variable.SharedVariables()
        self.TCN_VEHICLE = self.SV.TCN_VEHICLE
        self.VI = self.SV.VI
        self.LI = self.SV.LI
        self.STM = self.SV.STM
        self.MAP = self.SV.MAP
        self.CAL = self.SV.CAL
        self.LOBS = self.SV.LOBS
        self.GOBS = self.SV.GOBS
        self.GUI = self.SV.GUI
        self.XBOX = self.SV.XBOX

        # Main initial variables
        self.auto_start = auto_start
        self.main_run = False
        self.main_receive = []

        # Commander initail variables
        self.commander_server_run = False

        self.vision_build_map_mode = False
        self.vision_use_map_mode = False

        # Algorithm initial variables
        self.algorithm_run = False
        self.algorithm_server_run = False

        # GUI initial variables
        self.gui_server_run = False
        self.gui_receive = []


        # STM32 initial variables
        self.stm32_server_run = False
        self.stm32_receive = []

        self.command_dictionary = {'cs':self._cs, 'bi':self.bridge_init, 'h':self._help}
        self.command_dictionary_bridge_require = {'exit all':self._exit_all, 'exit b':self._exit_b, 'exit l':self._exit_l, \
            'exit s':self._exit_s, 'exit v':self._exit_v, 'exit':self._exit, 'li':self._li, \
                'gld':self._gld, 'vi':self._vi, 'vs':self._vs, 'sv':self._sv, 'gs':self._gs, 'al':self._al, \
                    'cc':self._cc, 'vrs':self._vrs, 'gp c':self._gp_c, 'gp x':self._gp_x, \
                        'gp exit':self._gp_exit, 'gp':self._gp, 'bm':self._bm, 'um':self._um, \
                            'kbm':self._kbm, 'xs':self._xs, 'si':self._si, 'mwx':self._mwx, \
                                'stop':self._stop, 'xi':self._xi}



# class CommandDictionary:
#     ''' Dictionary for command'''
#     def __init__(self, _commander_tcp_server, _commander_udp_client, commander_tcp_server_run,\
#          commander_run, show_vision_data_run, logging):
#         self._commander_tcp_server = _commander_tcp_server
#         self._commander_udp_client = _commander_udp_client
#         self.commander_tcp_server_run = commander_tcp_server_run
#         self.commander_run = commander_run
#         self.show_vision_data_run = show_vision_data_run
#         self.logging = logging

#         self.command_dictionary = {'cs':self._cs, 'bi':self.bridge_init, 'h':self._help}
#         self.command_dictionary_bridge_require = {'exit all':self._exit_all, 'exit b':self._exit_b, 'exit l':self._exit_l, \
#             'exit s':self._exit_s, 'exit v':self._exit_v, 'exit':self._exit, 'li':self._li, \
#                 'gld':self._gld, 'vi':self._vi, 'vs':self._vs, 'sv':self._sv, 'gs':self._gs, 'al':self._al, \
#                     'cc':self._cc, 'vrs':self._vrs, 'gp c':self._gp_c, 'gp x':self._gp_x, \
#                         'gp exit':self._gp_exit, 'gp':self._gp, 'bm':self._bm, 'um':self._um, \
#                             'kbm':self._kbm, 'xs':self._xs, 'si':self._si, 'mwx':self._mwx, \
#                                 'stop':self._stop, 'xi':self._xi}

#     def _cs(self):
#         print('Commander run : {} \nCommander server run : {}'.\
#             format(self.commander_run, self.commander_tcp_server_run))
#     def _bi(self):
#         self.bridge_init()
#     def _h(self):
#         self._help()


#     def _exit_all(self):
#         self.commander_run = False
#     def _exit_b(self):
#         self._commander_tcp_server.send_list(['C', 'exit all'])
#         print('Commander server will be close in 5 second')
#         time.sleep(5)
#         self._commander_tcp_server.close()
#         self._commander_udp_client.close()
#         self._commander_tcp_server = None
#         self.commander_tcp_server_run = False
#     def _exit_l(self):
#         self._commander_tcp_server.send_list(['C', 'exit l'])
#     def _exit_s(self):
#         self._commander_tcp_server.send_list(['C', 'exit s'])
#     def _exit_v(self):
#         self._commander_tcp_server.send_list(['C', 'exit v'])
#     def _exit_x(self):
#         self._commander_tcp_server.send_list(['C', 'exit x'])
#     def _exit(self):
#         print("Please specify which exit command to use Ex:'exit all'")

#     ################ LiDAR ###############
#     def _li(self):
#         self._commander_tcp_server.send_list(['C', 'li'])
#         self._commander_tcp_server.recv_list()
#     def _gld(self):
#         self._commander_tcp_server.send_list(['C', 'gld'])

#     ################ Vision #############
#     def _vi(self):
#         self._commander_tcp_server.send_list(['C', 'vi'])
#         self._commander_tcp_server.recv_list()
#     def _vs(self):
#         self._commander_tcp_server.send_list(['C', 'vs'])
#     def _gs(self):
#         self._commander_tcp_server.send_list(['C', 'gs'])
#     def _al(self):
#         self._commander_tcp_server.send_list(['C', 'al'])
#     def _cc(self):
#         self._commander_tcp_server.send_list(['C', 'cc'])
#     def _sv(self):
#         self._commander_tcp_server.send_list(['C', 'sv'])
#     def _vrs(self):
#         self._commander_tcp_server.send_list(['C', 'vrs'])
#         print('Vision is reseting , please wait 7 second')
#         time.sleep(7)
#     def _gp_c(self):
#         self._commander_tcp_server.send_list(['C', 'gp c'])
#         try:
#             input("Use Ctrl+C or enter any key to end current process : ")
#             self._commander_udp_client.send_list(['end'])
#         except KeyboardInterrupt:
#             self._commander_udp_client.send_list(['end'])
#         self._commander_tcp_server.recv_list()
#     def _gp_x(self):
#         self._commander_tcp_server.send_list(['C', 'gp x'])
#         try:
#             input("Use Ctrl+C or enter any key to end current process : ")
#             self._commander_udp_client.send_list(['end'])
#         except KeyboardInterrupt:
#             self._commander_udp_client.send_list(['end'])
#         self._commander_tcp_server.recv_list()
#     def _gp_exit(self):
#         self._commander_tcp_server.send_list(['C', 'gp exit'])
#     def _gp(self):
#         self._commander_tcp_server.send_list(['C', 'gp'])
#     def _bm(self):
#         try:
#             mapid = int(input('MapID : '))
#             self._commander_tcp_server.send_list(['C', 'bm', mapid])
#             try:
#                 input("Use Ctrl+C or enter any key to end current process : ")
#                 self._commander_udp_client.send_list(['end'])
#             except KeyboardInterrupt:
#                 self._commander_udp_client.send_list(['end'])
#             self._commander_tcp_server.recv_list()
#         except ValueError:
#             print('Please specify MapID in integer')
#         except KeyboardInterrupt:
#             print('Abort')
#     def _um(self):
#         try:
#             mapid = int(input('MapID : '))
#             self._commander_tcp_server.send_list(['C', 'um', mapid])
#             try:
#                 input("Use Ctrl+C or enter any key to end current process : ")
#                 self._commander_udp_client.send_list(['end'])
#             except KeyboardInterrupt:
#                 self._commander_udp_client.send_list(['end'])
#             self._commander_tcp_server.recv_list()
#         except ValueError:
#             print('Please specify MapID in integer')
#         except KeyboardInterrupt:
#             print('Abort')
#     def _kbm(self):
#         try:
#             mapid = int(input('MapID : '))
#             self._commander_tcp_server.send_list(['C', 'kbm', mapid])
#             try:
#                 input("Use Ctrl+C or enter any key to end current process : ")
#                 self._commander_udp_client.send_list(['end'])
#             except KeyboardInterrupt:
#                 self._commander_udp_client.send_list(['end'])
#             self._commander_tcp_server.recv_list()
#         except ValueError:
#             print('Please specify MapID in integer')
#         except KeyboardInterrupt:
#             print('Abort')

#     ############ XBOX and STM32 #################
#     def _xs(self):
#         self._commander_tcp_server.send_list(['C', 'xs'])
#     def _si(self):
#         self._commander_tcp_server.send_list(['C', 'si'])
#         self._commander_tcp_server.recv_list()
#     def _mwx(self):
#         try:
#             self._commander_tcp_server.send_list(['C', 'mwx'])
#             input("Use Ctrl+C or enter any key to end current process : ")
#             self._commander_udp_client.send_list(['end'])
#         except KeyboardInterrupt:
#             print('KeyboardInterrupt')
#             self._commander_udp_client.send_list(['end'])
#             time.sleep(0.5)
#         self._commander_tcp_server.recv_list()
#     def _stop(self):
#         self._commander_tcp_server.send_list(['C', 'stop'])
#     def _xi(self):
#         self._commander_tcp_server.send_list(['C', 'xi'])
#         self._commander_tcp_server.recv_list()

#     ########### Commander TCP Server version #############
#     def bridge_init(self):
#         ''' This is used to initial bridge, it also initialize other components'''
#         if self.commander_tcp_server_run is False:
#             subprocess.Popen('sudo python3 tcn_bridge.py'\
#                 , shell=True, start_new_session=True)
#             print('##### Initializing communication center #####')
#             logging.info("Bridge initializing")
#             self._commander_udp_client = tcn_socket.UDP_client(50001)
#             self._commander_tcp_server = tcn_socket.TCP_server(50000)
#             self._commander_tcp_server.recv_list()
#             logging.info("Bridge - commander initialization completed\n")
#             self.commander_tcp_server_run = True
#         else:
#             print('Bridge run already')

#     def end_commander(self):
#         '''Used for end tcn_main , please note this will also shutdown tcn system'''
#         if self._commander_tcp_server is not None:
#             self._commander_tcp_server.send_list(['C', 'exit', 'all'])
#             print('All process will be closed in 5 second')
#             time.sleep(5)
#             self._commander_tcp_server.close()
#             self._commander_udp_client.close()
#             self._commander_tcp_server = None
#         self.commander_tcp_server_run = False
#         self.commander_run = False
#         logging.info('Commander end')

#     def _help(self):
#         ''' Help manmual'''
#         print('\nCommander relative\n')
#         print("cs : Check for commander status")
#         print("exit all : Close all process")

#         print("\nBridge relative\n")
#         print("exit b : Close bridge and commander server")
#         print("bi : Initialize bridge")

#         print("\nLiDAR relative\n")
#         print("gld : Show instant LiDAR data")
#         print("li : Initialize LiDAR")
#         print("exit l : Close LiDAR ")

#         print("\nVision relative\n")
#         print("gs : Get vision module status")
#         print("gp : Show vision data")
#         print("gp c : Continuous show vision data")
#         print("gp x : Contunuous show vision data, with XBOX control")
#         print("vs : Vision status")
#         print("vi : Initialize Vision")
#         print("exit v : Close vision")

#         print("\nSTM32 relative\n")
#         print("si : Initialize STM32")
#         print("exit s : Close STM32")
#         print("stop : stop motor")

#         print("\nXBOX relative\n")
#         print("mwx : Enable xbox control")
#         print("xi : Initialize xbox ")
#         print("xs : Show xbox status")
#         print("exit x : Close xbox")



# class Commander(CommandDictionary):
#     ''' Master of current TCN system '''
#     def __init__(self, auto_run=True):
#         logging.basicConfig(filename='Main.log', filemode='w', level=logging.INFO)
#         self.auto_run = auto_run
#         self.commander_run = False
#         self.commander_tcp_server_run = False
#         self.show_vision_data_run = False
#         self._commander_tcp_server = None
#         self._commander_udp_client = None

#         super().__init__(self._commander_tcp_server, self._commander_udp_client, \
#             self.commander_tcp_server_run, self.commander_run, self.show_vision_data_run, logging)

#         if self.auto_run:
#             self.bridge_init()
#             self._commander_tcp_server.recv_list()
#             self.commander_main()
#             self.end_commander()

#     def commander_main(self):
#         '''Main function for commander '''
#         logging.info('Commander main start')
#         self.commander_run = True
#         while self.commander_run:
#             try:
#                 command = input("\nPlease enter command , enter 'h' for _help : ")
#                 logging.info('Command : %s', command)
#                 if command in self.command_dictionary:
#                     self.command_dictionary[command]() # Referenced from CommanderDictionary
#                 elif command in self.command_dictionary_bridge_require and self.commander_tcp_server_run:
#                     self.command_dictionary_bridge_require[command]()
#                 elif command in self.command_dictionary_bridge_require and not self.commander_tcp_server_run:
#                     print("Commander server is not working, please use 'bi' \
#                         command to initialize bridge first ")
#                 time.sleep(0.1)
#             except KeyboardInterrupt:
#                 print('Keyboard Interrupt')
#                 self.commander_run = False
#             except IndexError:
#                 pass
#             except KeyError:
#                 traceback.print_exc()
#             except:
#                 self.commander_run = False
#                 print('\nError From Commander\n')
#                 traceback.print_exc()



if __name__ == "__main__":
    Main()
    # xbox_init()
    # commander_init()
    # main()
