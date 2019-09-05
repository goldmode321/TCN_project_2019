#!/usr/bin/python
# -*- coding: UTF-8 -*-
'''
One of the component system to control
Vision module from TCN company
'''


import time
import xmlrpc.client as xmlrpclib
import traceback
import threading
import logging
import tcn_gpio
import tcn_socket

class Vision:
    '''
    The module for controlling Vision module, communicate with
    bridge, ip should be specify as the fix ip of vision module
    '''
    def __init__(self, auto_start=True, ip='192.168.5.100'):
        self.ip = ip
        self.vision_client_run = False
        self.vision_thread_client_run = False
        self.reset_flag = False
        self.vision_x = 0
        self.vision_y = 0
        self.vision_theta = 0
        self.vision_status = 0
        self.vision = None
        self.vision_client = None
        self.vision_thread_client = None

        if auto_start:
            self.run()

    def run(self):
        ''' Auto start step'''
        self.init()
        self.start_background_thread()
        self.main()
        self.end()
        self.end_background_thread()

    def init(self):
        ''' Initialize communication with vision module and tcn_bridge'''
        try:
            time.sleep(0.2) # Make sure server initialize first
            logging.basicConfig(filename='Vision_main.log', filemode='w', level=logging.INFO)
            self.vision = xmlrpclib.ServerProxy("http://{}:8080".format(self.ip))
            self.vision_thread_client = tcn_socket.UDP_client(50003)
            self.vision_client = tcn_socket.TCP_client(50002)
            if self.vision.alive() == [0, 'Alive']:
                logging.info('Connection to Vision module establiished , Vision module status : {}\n'.format(self.vision.alive()))
                self.vision_client.send_list(['V', 'status', 'Alive'])
                self.vision_client_run = True
                self.vision_thread_client_run = True
            else:
                logging.info('Vision module is not Alive\n')
                raise KeyboardInterrupt
        except:
            self.end()
            self.end_background_thread()
            traceback.print_exc()
            logging.exception('Got error : ')

    def main(self):
        '''Process that wait for bridge command'''
        while self.vision_client_run:
            try:
                vision_receive = self.vision_client.recv_list()
                logging.info('Command in : {} '.format(vision_receive))
                self.vision_portocol(vision_receive)
            except:
                traceback.print_exc()
                self.vision_client_run = False
                self.vision_thread_client_run = False
                logging.exception('Got error : \n')
                self.end()
                self.end_background_thread()

    def start_background_thread(self):
        '''Start sending data thread'''
        thread = threading.Thread(target=self.send_vision_status, daemon=True)
        thread.start()
        logging.info('Thread running')

    def send_vision_status(self):
        '''Send vision data to bridge'''
        while self.vision_thread_client_run:
            if self.reset_flag:
                time.sleep(4.8)
                self.reset_flag = False
            else:
                status = self.vision.get_status()
                pose = self.vision.get_pose()
                self.vision_status = status[0]
                self.vision_x = pose[3]
                self.vision_y = pose[4]
                self.vision_theta = pose[5]
                self.vision_thread_client.send_list([self.vision_x, self.vision_y, \
                    self.vision_theta, self.vision_status, self.vision_client_run, \
                        self.vision_thread_client_run])
            time.sleep(0.15)


    def vision_portocol(self, vision_receive):
        '''Intepret message from bridge'''
        if vision_receive[0] == 'V':
            if vision_receive[1] == 'exit':
                self.vision_client_run = False
                logging.info("'exit' command received, start terminating program\n")
            elif vision_receive[1] == 'al':
                alive_resp = self.vision.alive()
                print('alive(), response: {}'.format(alive_resp))
            elif vision_receive[1] == 'cc':
                cc_resp = self.vision.check_cpu_speed()
                print('get_att(), response: {}'.format(cc_resp))
            elif vision_receive[1] == 'gp':
                pose_resp = self.vision.get_pose()
                print('get_pose(), response: {}'.format(pose_resp))
            elif vision_receive[1] == 'gs':
                status_resp = self.vision.get_status()
                print('get_status(), response: {}'.format(status_resp))
            elif vision_receive[1] == 'sv':
                save_resp = self.vision.save_db()
                print('save_db(), response: {}'.format(save_resp))
            elif vision_receive[1] == 'rs':
                self.reset_flag = True
                time.sleep(0.2)
                reset_resp = self.vision.reset()
                print('reset(), response: {}'.format(reset_resp))
            elif vision_receive[1] == 'bm': # Build map
                if vision_receive[2] is not None:
                    start_resp = self.vision.set_start(1, [vision_receive[2]])
                    print('set_start(), response: {}'.format(start_resp))
                    logging.info("'Build map' command received , mapid : %s ", vision_receive[2])
                else:
                    print("'Build map' command received , but no mapid")
                    logging.info("'Build map' command received , but no mapid")
            elif vision_receive[1] == 'um': # Use map
                if vision_receive[2] is not None:
                    start_resp = self.vision.set_start(0, [vision_receive[2]])
                    print('set_start(), response: {}'.format(start_resp))
                    logging.info("'Use map' command received , mapid : %s ", vision_receive[2])
                else:
                    print("'Use map' command received , but no mapid")
                    logging.info("'Use map' command received , but no mapid")
            elif vision_receive[1] == 'kbm': # Keep building map
                if vision_receive[2] is not None:
                    start_resp = self.vision.set_start(2, [vision_receive[2]])
                    print('set_start(), response: {}'.format(start_resp))
                    logging.info("'Keep build map' command received , mapid : %s ", vision_receive[2])
                else:
                    print("'Keep build map' command received , but no mapid")
                    logging.info("'Build map' command received , but no mapid")


        else:
            print(str(vision_receive) + " received by vision module. Wrong potorcol ! ")


    def end(self):
        '''End vision program'''
        self.vision_client_run = False
        self.vision_client.close()
        logging.info(" Vision module disconnect \n")

    def end_background_thread(self):
        '''End vision thread'''
        self.vision_thread_client_run = False
        self.vision_thread_client.send_list([self.vision_x, self.vision_y, self.vision_theta, self.vision_status,\
             self.vision_client_run, self.vision_thread_client_run])
        self.vision_thread_client.close()




class VisionTest:
    def __init__(self):
        try:
            self.vision_x = 0
            self.vision_y = 0
            self.vision_theta = 0
            self.vision_status = 0
            self.vision_client_run = False
            self.vision_server_run = False
            self.vision_thread_server_run = False
            self.vision_thread_server_status = False
            self.vision_thread_client_run = False

            self.vision_thread_server = tcn_socket.UDP_server(50003)
            self.vision_server = tcn_socket.TCP_server(50002)
            vision_receive = self.vision_server.recv_list()
            self.vision_protocol(vision_receive)
            self.vision_server_run = True
            self.vision_thread_server_run = True
            self.start_background_thread()
            self.main()
        except:
            self.end()
            self.end_background_thread()


    def main(self):
        while self.vision_server_run:
            try:
                command = input('command : ')
                self.vision_command(command)
            except:
                self.vision_server.send_list(['V', 'exit'])
                time.sleep(1)
                self.vision_server_run = False
                self.vision_thread_server_run = False
                self.end()
                self.end_background_thread()

    def start_background_thread(self):
        self.thread = threading.Thread(target=self.get_vision_data, daemon=True)
        self.thread.start()

    def get_vision_data(self):
        while self.vision_thread_server_run:
            self.vision_thread_server_status = self.thread.is_alive()
            vision_data = self.vision_thread_server.recv_list()

            if vision_data != None:
                self.vision_x = vision_data[0]
                self.vision_y = vision_data[1]
                self.vision_theta = vision_data[2]
                self.vision_status = vision_data[3]
                self.vision_client_run = vision_data[4]
                self.vision_thread_client_run = vision_data[5]
                time.sleep(0.1)



    def vision_command(self, command):
        cmd_list = command.lower().split() #splits the input string on spaces
        cmd = cmd_list[0]
        if cmd == 'exit':
            self.vision_server.send_list(['V', 'exit'])
            time.sleep(1)
            self.vision_server_run = False
            self.vision_thread_server_run = False
            self.end()
            self.end_background_thread()
        elif cmd == 'status':
            print('server run : {}'.format(self.vision_server_run))
            print('server thread run : {}'.format(self.vision_thread_server_run))
            print('server thread alive : {}'.format(self.vision_thread_server_status))
            print('client run : {}'.format(self.vision_client_run))
            print('client thread run : {}'.format(self.vision_thread_client_run))
            self.show_vision_status()
        elif cmd == 'h':
            self.help_manual()
        elif cmd == 'al':
            self.vision_server.send_list(['V', 'al'])
        elif cmd == 'cc':
            self.vision_server.send_list(['V', 'cc'])
        elif cmd == 'gp':
            self.vision_server.send_list(['V', 'gp'])
            print('vision_x : {} | vision_y : {} | vision_theta : {} '\
                .format(self.vision_x, self.vision_y, self.vision_theta))
        elif cmd == 'gs':
            self.vision_server.send_list(['V', 'gs'])
            self.show_vision_status()
        elif cmd == 'sv':
            self.vision_server.send_list(['V', 'sv'])
        elif cmd == 'rs':
            self.vision_server.send_list(['V', 'rs'])
            print('reset vision , please wait 3 second')
            time.sleep(5)
        elif cmd == 'bm':
            if cmd_list[1] is not None:
                self.vision_server.send_list(['V', 'bm', int(cmd_list[1])])
                self.show_vision_data()
            else:
                print('Please specify mapid (bm mapid). Ex : bm 1 ')
        elif cmd == 'um':
            if cmd_list[1] is not None:
                self.vision_server.send_list(['V', 'um', int(cmd_list[1])])
                self.show_vision_data()
            else:
                print('Please specify mapid (bm mapid). Ex : bm 1 ')
        elif cmd == 'kbm':
            if cmd_list[1] is not None:
                self.vision_server.send_list(['V', 'kbm', int(cmd_list[1])])
                self.show_vision_data()
            else:
                print('Please specify mapid (bm mapid). Ex : bm 1 ')


    def end(self):
        self.vision_server.close()


    def end_background_thread(self):
        self.vision_thread_server.close()
        self.thread.join()
        self.vision_thread_server_status = self.thread.is_alive()


    def vision_protocol(self, receive):
        if receive[0] == 'V':
            if receive[1] == 'next':
                pass
        else:
            print('{} received. Wrong protocol')

    def show_vision_data(self):

        self.show_vision_status()
        run = True
        while run:
            try:
                print('status : {} | vision_x : {} | vision_y : {} | vision_theta : {} | Use Ctrl+C to terminate'\
                    .format(self.vision_status, self.vision_x, self.vision_y, self.vision_theta))
                time.sleep(0.2)
            except:
                run = False

    def show_vision_status(self):
        if self.vision_status == 0:
            print("Vision module status : {} | Vision module is booting".format(self.vision_status))
        elif self.vision_status == 1:
            print("Vision module status : {} | Vision module is waiting for 'st $mapid'\
                 command".format(self.vision_status))
        elif self.vision_status == 2:
            print("Vision module status : {} | Vision module is loading data "\
                .format(self.vision_status))
        elif self.vision_status == 3:
            print('Vision module status : {} | Please move slowly, fp-slam is searching a set of \
                best images to initialize'.format(self.vision_status))
        elif self.vision_status == 4:
            print('Vision module status : {} | System is working \
                normaaly'.format(self.vision_status))
        elif self.vision_status == 5:
            print('Vision module status : {} | Lost Lost Lost'.format(self.vision_status))
        else:
            print('Unknown status code : {}'.format(self.vision_status))

    def help_manual(self):
        print("al: chekc fp-slam is alive.")
        print("cc: check cpu speed.")
        print("gp: get pose from fp-slam.")
        print("gs: get state from fp-slam.")
        print("qi: quit client program.")
        print("s1: scenario1")
        print("sc1 <standard> <length1> <length2> <length3>  <length4> : to correct initial corridation.")
        print("rs: reset the fp-slam system. before re-start another system mode.")
        print("sd: shutdown the fp-slam system.")
        print("sn <nfs address> : set nfs address")
        print("st <system mode> <map id> <map id> ....<map id>: set fp-slam to start.")
        print("sv: save database.")
        # print("cr: control coordinate mode.")
        # print("tr: tracking mode")
        # print("gpio:test if relay alive")
        # print("pr:keep moving at 2 position")
        return


if __name__ == "__main__":
    Vision()