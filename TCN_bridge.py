#!/usr/bin/python3
import TCN_socket
import time
import traceback
import subprocess
import sys

'''Portocol'''
''' "C" to Main , "L" to LiDAR , "S" to STM32 , "G" to GPIO , "X" to xbox, "V" to Vision , "M" to motion '''




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






# time.sleep(5)
commander_server.close()
stm32_server.close()












class bridge_portocol(object):

    def Command_potorcol(self,command):
        if type(command) == str:
            pass


