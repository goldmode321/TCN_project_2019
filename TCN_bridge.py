#!/usr/bin/python3
import TCN_socket
import time
import traceback
import subprocess
import sys
import threading

'''Portocol'''
''' "C" to Main , "L" to LiDAR , "S" to STM32 , "G" to GPIO , "X" to xbox, "V" to Vision , "M" to motion '''

'''Initialize'''
commander_server = None
stm32_server = None
bridge_run = True

def commander_init():
    global commander_server
    try:
        commander_server = TCN_socket.TCP_server(50000,1)
        commander_data = commander_server.recv_list()
        if commander_data == ['C',1,2,3]:
            print('Commander communication successfully established ! \ncommunication center get : {}'.format(commander_data))
        else:
            print('Undefined communication error of commander, please check test message')
            raise KeyboardInterrupt
    except:
        commander_server.close()
        traceback.print_exc()
        print('Communication center fail at commander ')

def stm32_init():
    global stm32_server
    try:
        stm32_server = TCN_socket.TCP_server(50001,1)
        stm32_data = stm32_server.recv_list()
        if stm32_data == ['S',1,2,3]:
            print("STM32 communication successfully established !\ncommunication center get : {}".format(stm32_data) )
            stm32_server.send_list(['S','T','M',3,2])
            print("Send back ['S','T','M',3,2] for double check")
        else:
            print('Undefined communication error of STM32, please check test message')
            raise KeyboardInterrupt      
    except:
        stm32_server.close()
        traceback.print_exc()
        print('Communication center fail at STM32 ')


###                                                                   ###
###    Portocol                                                       ###
###                                                                   ###
def bridge_potorcol(commander_data):
    global commander_server,stm32_server,bridge_run
    '''First, get commander command (TCN_main.py)'''
    try:
        commander_data = commander_server.recv_list()
        if commander_data[0] == 'C':
            if commander_data[1] == 'exit':
                stm32_server.send_list(['S',commander_data[1]])
                print('All server will be close in 3 second')
                time.sleep(3)
                commander_server.close()
                stm32_server.close()
                bridge_run = False
            elif commander_data[1] == 'move':
                stm32_server.send_list(['S','move',[ commander_data[2],commander_data[3],commander_data[4] ] ])

        else:
            print('Wrong potorcol from commander ')

    except:
        commander_server.close()
        stm32_server.close()
        traceback.print_exc()

    




###                                                                   ###
###    Waiting for command from TCN_main.py                           ###
###                                                                   ###
def main():
    bridge_run = True
    commander_server.send_list(['C',0])
    while bridge_run:
        try:
            commander_data = commander_server.recv_list()
            bridge_potorcol(commander_data)

        except:
            commander_server.close()
            stm32_server.close()
            traceback.print_exc()
            



if __name__ == "__main__":
    commander_init()
    stm32_init()
    main()


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


