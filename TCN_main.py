#!/usr/bin/python3
import TCN_socket
import time
import subprocess
import traceback
import threading


###                                                             ###
###    Run TCN_bridge.py (so called "Communication center")     ###
###                                                             ###

try:
    p_bridge = subprocess.Popen('python TCN_bridge.py',shell = True)
    print('Initializing communication center')
    time.sleep(1)
    
    print('Establish TCP connection to communication center')
    commander_client = TCN_socket.TCP_client(50000)
except:
    commander_client.close()
    traceback.print_exc()
    print('\n Commander communication fail')


    # p_bridge = subprocess.Popen('python TCN_STM32_main.py',shell = True)
    # print('Initializing STM32 motor controller')



commander_client.send_list(['C',1,2,3])
time.sleep(1)
commander_client.recv_list()
time.sleep(5)
commander_client.send_list(['C','end'])
commander_client.close()



