#!/usr/bin/python3
import TCN_socket
import time
import traceback
import subprocess
import sys
import threading
import logging

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
logging.basicConfig(filename='Bridge.log',filemode = 'w',level =logging.INFO)


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
    bridge_init()
    bridge_main()
    end_bridge()


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


