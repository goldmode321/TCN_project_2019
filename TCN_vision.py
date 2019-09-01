#!/usr/bin/python
# -*- coding: UTF-8 -*-


import TCN_socket
import sys, time
import xmlrpc.client as xmlrpclib
import math
import traceback
import threading
import logging
import TCN_gpio

class Vision:
    def __init__(self,AUTO_START = True , ip = '192.168.5.100'):
        self.IP = ip
        self.VISION_CLIENT_RUN = False
        self.VISION_THREAD_RUN = False
        self.RESET_FALG = False
        if AUTO_START:
            self.run()

    def run(self):
        self.init()
        self.start_background_thread()
        self.main()
        self.end()
        self.end_background_thread()

    def init(self):
        try:
            time.sleep(0.2) # Make sure server initialize first
            logging.basicConfig(filename='Vision_main.log',filemode = 'w',level =logging.INFO)
            self.VISION = xmlrpclib.ServerProxy("http://{}:8080".format(self.IP))
            self.VISION_THREAD_CLIENT = TCN_socket.UDP_client(50003)
            self.VISION_CLIENT = TCN_socket.TCP_client(50002)
            if self.VISION.alive() == [0,'Alive']:
                logging.info('Connection to Vision module establiished , Vision module status : {}\n'.format(self.VISION.alive()))
                self.VISION_CLIENT.send_list(['V','status','Alive'])
                self.VISION_CLIENT_RUN = True
                self.VISION_THREAD_RUN = True
            else:
                logging.info('Vision module is not Alive\n')
                raise KeyboardInterrupt            
        except:
            self.end()
            self.end_background_thread()
            traceback.print_exc()
            logging.exception('Got error : ')

    def main(self):
        while self.VISION_CLIENT_RUN:
            try:
                vision_receive = self.VISION_CLIENT.recv_list()
                logging.info('Command in : {} '.format(vision_receive))
                self.vision_portocol(vision_receive)
            except:
                traceback.print_exc()
                self.VISION_CLIENT_RUN = False
                self.VISION_THREAD_RUN = False
                logging.exception('Got error : \n')
                self.end()
                self.end_background_thread()

    def start_background_thread(self):
        THREAD = threading.Thread(target = self.send_vision_status , daemon = True)
        THREAD.start()
        logging.info('Thread running')

    def send_vision_status(self):
        while self.VISION_CLIENT_RUN:
            if self.RESET_FALG == True:
                time.sleep(4.8)
                self.RESET_FALG = False
            else:
                status = self.VISION.get_status()
                pose = self.VISION.get_pose()
                self.status = status[0]
                self.x = pose[3]
                self.y = pose[4]
                self.theta = pose[5]
                # print(sys.getsizeof([self.x , self.y , self.theta , self.status , self.VISION_CLIENT_RUN]))
                self.VISION_THREAD_CLIENT.send_list([self.x , self.y , self.theta , self.status , self.VISION_CLIENT_RUN , self.VISION_THREAD_RUN])
            time.sleep(0.15)


    def vision_portocol(self,vision_receive):
        if vision_receive[0] == 'V':
            if vision_receive[1] == 'exit':
                self.VISION_CLIENT_RUN = False
                logging.info(" 'exit' command received, start terminating program\n")
            elif vision_receive[1] == 'al':
                alive_resp = self.VISION.alive()
                print( 'alive(), response: {}'.format(alive_resp) )
            elif vision_receive[1] == 'cc':
                cc_resp = self.VISION.check_cpu_speed()
                print( 'get_att(), response: {}'.format(cc_resp) )                    
            elif vision_receive[1] == 'gp':
                pose_resp = self.VISION.get_pose()
                print( 'get_pose(), response: {}'.format(pose_resp) )
            elif vision_receive[1] == 'gs':
                status_resp = self.VISION.get_status()
                print( 'get_status(), response: {}'.format(status_resp) )  
            elif vision_receive[1] == 'sv':
                save_resp = self.VISION.save_db()
                print( 'save_db(), response: {}'.format(save_resp) )
            elif (vision_receive[1] == 'rs'):
                self.RESET_FALG = True
                time.sleep(0.2)
                reset_resp = self.VISION.reset()
                print( 'reset(), response: {}'.format(reset_resp) )
            elif vision_receive[1] == 'bm': # Build map
                if vision_receive[2] != None:
                    start_resp = self.VISION.set_start(1,[vision_receive[2]])
                    print( 'set_start(), response: {}'.format(start_resp) )
                    logging.info("'Build map' command received , mapid : {} ".format(vision_receive[2])) 
                else:
                    print("'Build map' command received , but no mapid")
                    logging.info("'Build map' command received , but no mapid") 
            elif vision_receive[1] == 'um': # Use map
                if vision_receive[2] != None:
                    start_resp = self.VISION.set_start(0,[vision_receive[2]])
                    print( 'set_start(), response: {}'.format(start_resp) )
                    logging.info("'Use map' command received , mapid : {} ".format(vision_receive[2])) 
                else:
                    print("'Use map' command received , but no mapid")
                    logging.info("'Use map' command received , but no mapid") 
            elif vision_receive[1] == 'kbm': # Keep building map
                if vision_receive[2] != None:
                    start_resp = self.VISION.set_start(2,[vision_receive[2]])
                    print( 'set_start(), response: {}'.format(start_resp) )
                    logging.info("'Keep build map' command received , mapid : {} ".format(vision_receive[2])) 
                else:
                    print("'Keep build map' command received , but no mapid")
                    logging.info("'Build map' command received , but no mapid") 


        else:
            print(str(vision_receive)+" received by vision module. Wrong potorcol ! ")


    def end(self):
        self.VISION_CLIENT_RUN = False
        self.VISION_CLIENT.close()
        logging.info(" Vision module disconnect \n")

    def end_background_thread(self):
        self.VISION_THREAD_CLIENT.send_list([self.x , self.y , self.theta , self.status , self.VISION_CLIENT_RUN , self.VISION_THREAD_RUN])
        self.VISION_THREAD_CLIENT.close()




class Vision_Test:
    def __init__(self):
        try:
            self.X = 0
            self.Y = 0
            self.THETA = 0
            self.STATUS = 0
            self.VISION_CLIENT_RUN = False
            self.VISION_SERVER_RUN = False
            self.VISION_THREAD_SERVER_RUN = False

            self.VISION_THREAD_SERVER = TCN_socket.UDP_server(50003)
            self.VISION_SERVER = TCN_socket.TCP_server(50002)
            vision_receive = self.VISION_SERVER.recv_list()
            self.vision_protocol(vision_receive)
            self.VISION_SERVER_RUN = True
            self.VISION_THREAD_SERVER_RUN = True
            self.start_background_thread()
            self.main()
        except:
            self.end()
            self.end_background_thread()
    


    def main(self):
        while self.VISION_SERVER_RUN:
            try:
                command = input('command : ')
                self.vision_command(command)
            except:
                self.VISION_SERVER.send_list(['V','exit'])
                time.sleep(1)
                self.VISION_SERVER_RUN = False
                self.VISION_THREAD_SERVER_RUN = False
                self.end()
                self.end_background_thread()

    def start_background_thread(self):
        self.THREAD = threading.Thread(target = self.get_vision_data , daemon = True)
        self.THREAD.start()

    def get_vision_data(self):
        while self.VISION_THREAD_SERVER_RUN:
            self.VISION_THREAD_SERVER_STATUS = self.THREAD.is_alive()
            vision_data = self.VISION_THREAD_SERVER.recv_list()
            
            if vision_data != None:
                self.X = vision_data[0]
                self.Y = vision_data[1]
                self.THETA = vision_data[2]
                self.STATUS = vision_data[3]
                self.VISION_CLIENT_RUN = vision_data[4]
                self.VISION_THREAD_CLIENT_RUN = vision_data[5]
                time.sleep(0.1)



    def vision_command(self, command):
        cmd_list = command.lower().split() #splits the input string on spaces
        cmd = cmd_list[0]
        if cmd == 'exit':
            self.VISION_SERVER.send_list(['V','exit'])
            time.sleep(1)
            self.VISION_SERVER_RUN = False
            self.VISION_THREAD_SERVER_RUN = False
            self.end()
            self.end_background_thread()
        elif cmd == 'status':
            print('server run : {}'.format(self.VISION_SERVER_RUN))
            print('server thread run : {}'.format(self.VISION_THREAD_SERVER_RUN))
            print('server thread alive : {}'.format(self.VISION_THREAD_SERVER_STATUS))
            print('client run : {}'.format(self.VISION_CLIENT_RUN))
            print('client thread run : {}'.format(self.VISION_THREAD_CLIENT_RUN))
            self.show_vision_status()
        elif cmd == 'h':
            self.help_manual()
        elif cmd == 'al':
            self.VISION_SERVER.send_list(['V','al'])
        elif cmd == 'cc':
            self.VISION_SERVER.send_list(['V','cc'])
        elif cmd == 'gp':
            self.VISION_SERVER.send_list(['V','gp'])
            print('x : {} | y : {} | theta : {} '.format(self.X,self.Y,self.THETA))
        elif cmd == 'gs':
            self.VISION_SERVER.send_list(['V','gs'])
            self.show_vision_status()
        elif cmd == 'sv':
            self.VISION_SERVER.send_list(['V','sv'])
        elif cmd == 'rs':
            self.VISION_SERVER.send_list(['V','rs'])
            print('reset vision , please wait 3 second')
            time.sleep(5)
        elif cmd == 'bm':
            if cmd_list[1] != None:
                self.VISION_SERVER.send_list(['V','bm',int(cmd_list[1])])
                self.show_vision_data()
            else:
                print('Please specify mapid (bm mapid). Ex : bm 1 ')
        elif cmd == 'um':
            if cmd_list[1] != None:
                self.VISION_SERVER.send_list(['V','um',int(cmd_list[1])])
                self.show_vision_data()
            else:
                print('Please specify mapid (bm mapid). Ex : bm 1 ')
        elif cmd == 'kbm':
            if cmd_list[1] != None:
                self.VISION_SERVER.send_list(['V','kbm',int(cmd_list[1])])
                self.show_vision_data()
            else:
                print('Please specify mapid (bm mapid). Ex : bm 1 ')


    def end(self):
        self.VISION_SERVER.close()


    def end_background_thread(self):
        self.VISION_THREAD_SERVER.close()
        self.THREAD.join()
        self.VISION_THREAD_SERVER_STATUS = self.THREAD.is_alive()


    def vision_protocol(self,receive):
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
                print('status : {} | x : {} | y : {} | theta : {} | Use Ctrl+C to terminate'.format(self.STATUS,self.X,self.Y,self.THETA))
                time.sleep(0.2)
            except:
                run = False

    def show_vision_status(self):
        if self.STATUS == 0:
            print("Vision module status : {} | Vision module is booting".format(self.STATUS))
        elif self.STATUS == 1:
            print("Vision module status : {} | Vision module is waiting for 'st $mapid' command".format(self.STATUS))
        elif self.STATUS == 2:
            print("Vision module status : {} | Vision module is loading data ".format(self.STATUS))
        elif self.STATUS == 3:
            print('Vision module status : {} | Please move slowly, fp-slam is searching a set of best images to initialize'.format(self.STATUS))
        elif self.STATUS == 4:
            print('Vision module status : {} | System is working normaaly'.format(self.STATUS))
        elif self.STATUS == 5:
            print('Vision module status : {} | Lost Lost Lost'.format(self.STATUS))
        else:
            print('Unknown status code : {}'.format(self.STATUS))

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





'''

# Initial parameters
vision_module = None
vision_client = None
vision_run = False

def init():
    global vision_module , vision_client , vision_run
    try:
        logging.basicConfig(filename='Vision_main.log',filemode = 'w',level =logging.INFO)
        vision_module =  xmlrpclib.ServerProxy("http://192.168.5.100:8080") 
        if vision_module.alive() == [0,'Alive']:
            logging.info('Connection to Vision module establiished , Vision module status : {}\n'.format(vision_module.alive()))
            vision_client = TCN_socket.TCP_client(50001)
            vision_client.send_list(['V','status','Alive'])
            vision_run = True
        else:
            logging.info('Vision module is not Alive\n')
            raise KeyboardInterrupt
    except:
        vision_client.close()
        traceback.print_exc()
        logging.exception('Got error : ')
        sys.exit(0)

        

def vision_portocol(vision_receive):
    global vision_module , vision_client , vision_run
    if vision_receive[0] == 'V':
        if vision_receive[1] == 'exit':
            vision_run = False
            logging.info(" 'exit' command received, start terminating program\n")

    else:
        print(str(vision_receive)+" received by vision module. Wrong potorcol ! ")





def main():
    global vision_module , vision_client , vision_run
    while vision_run:
        try:
            vision_receive = vision_client.recv_list()
            logging.info('Command in : {} \n'.format(vision_receive))
            vision_portocol(vision_receive)
        except:
            traceback.print_exc()
            vision_run = False
            logging.exception('Got error : \n')

def end():
    global vision_client
    vision_client.close()
    logging.info(" Vision module is off \n")






def manual_mode(proxy):
    print("# type h to refer command usage.")
    
    while True:
        command = input('command：')
        cmd_list = command.lower().split() #splits the input string on spaces
        cmd = cmd_list[0]
        try:
            if (cmd == 'h') or (cmd == 'help') :
                help_manual()
            elif cmd == 'al':
                alive_resp = proxy.alive()
                print( 'Proxy.alive(), response: {}'.format(alive_resp) )
            elif cmd == 'cc':
                cc_resp = proxy.check_cpu_speed()
                print( 'Proxy.get_att(), response: {}'.format(cc_resp) )                    
            elif cmd == 'gp':
                pose_resp = proxy.get_pose()
                print( 'Proxy.get_pose(), response: {}'.format(pose_resp) )
            elif cmd == 'gs':
                status_resp = proxy.get_status()
                print( 'Proxy.get_status(), response: {}'.format(status_resp) )         
            
            elif cmd == 's1':
                scenario1(proxy)
            
            elif cmd == 'sc1':
                if len(cmd_list)<6:
                    print("Error: wrong st arguments, uasge: sc1 <standard> <length1> <length2> <length3>  <length4> ")
                else:
                    print( 'Request fp-slam to make 1st correction.' )
                    itercmd = iter(cmd_list)
                    next(itercmd)
                    length_array = [int(ii) for ii in itercmd] 
                    start_resp = proxy.set_correct1(length_array)
                    print( 'Proxy.set_start(), response: {}'.format(start_resp) )       
            
            elif cmd == 'sd':
                print( 'Request fp-slam to shutdown.' )
                proxy.system.shutdown("")
            
            elif cmd == 'st':
                if len(cmd_list)<3:
                    print("Error: wrong st arguments, uasge: st <mode> <map id> <map id> ... ")
                else:
                    smode = int(cmd_list[1])
                    itercmd = iter(cmd_list)
                    next(itercmd)
                    next(itercmd)
                    mapids = [int(ii) for ii in itercmd] 
                    
                    print(mapids)
                    
                    start_resp = proxy.set_start(smode,mapids)
                    print( 'Proxy.set_start(), response: {}'.format(start_resp) )   



            elif cmd == 'sv':
                save_resp = proxy.save_db()
                print( 'Proxy.save_db(), response: {}'.format(save_resp) )
            

            elif (cmd == 'qi') or (cmd == 'ex'):
                print( 'Quit now.' )
                print("")
                break
            

            elif (cmd == 'rs'):
                reset_resp = proxy.reset()
                print( 'Proxy.reset(), response: {}'.format(reset_resp) )
            

            elif (cmd == 'hasd'):
                reset_resp = proxy.hardware_shutdown()
                print( 'Proxy.hardware_shutdown(), response: {}'.format(reset_resp) )



            # elif cmd == 'gpio':
            #     try:
            #         joy = test_relay()
            #     except IOError as e:
            #         print(e+'\n')
            #         tcng.relay_off()
            #         #print('Please retry again')
            #         print("Automaticly retry in 1 second or use Ctrl+C to halt"+'\n')
            #         time.sleep(1)
            #         joy = test_relay()
            #     except KeyboardInterrupt:
            #         print('Back to command mode')
            #         tcng.relay_off()
            #         joy.close()

                


            else:
                print( 'Unknown command, please type help.' )
        except xmlrpclib.Fault as err:
            print("A fault occurred")
            print("Fault code: %d" % err.faultCode)
            print("Fault string: %s" % err.faultString)
        except KeyboardInterrupt:
            print('Quit by KeyboardInterrupt')

        except Exception as e:
            print(e)
            print("# Command error: please check your format or check if server is not alive.")     
            print("  You can type gs to check slam's status.")  

    return

def scenario1(proxy):
    msgb=""
    while True:
        try:
            time.sleep(0.1)
            pose_resp = proxy.get_pose()
            status_resp = proxy.get_status()
            msg1 = "status:" + format(status_resp[0]) + ", "
            msg2 = "mapid:" + format(pose_resp[1]) + ", "
            msg3 = "(x,y):(" + format(pose_resp[2]) + "," + format(pose_resp[3]) + "), "
            msg4 = "thida: " + format(pose_resp[4]) + ", " 
            msg5 = "conf: " + format(pose_resp[5]) 
            msg6 = " ############################### "
            if status_resp[0]==5:
                msga = msg1 + msg2 + msg3 + msg4 + msg5 + msg6
            else:
                msga = msg1 + msg2 + msg3 + msg4 + msg5

            # Don't show message if current data is same with previous data 
            if msgb!=msga:
                print(msga)
                msgb=msga
        except KeyboardInterrupt:
            break


def help_manual():
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
'''

if __name__ == "__main__":
    Vision()

