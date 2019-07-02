#!/usr/bin/python3
import TCN_socket
import time
import subprocess
import traceback
import threading


###                                                                   ###
###    Run TCN_bridge.py (so called "Communication center (CC) ")     ###
###                                                                   ###

try:
    process_bridge = subprocess.Popen('python3 TCN_bridge.py',shell = True)
    print('##### Initializing communication center #####')
    time.sleep(1)    # Wait some time for assuming Communication center(CC) work  稍微delay，以確保CC正常運作
    print("Establish TCP connection to communication center\nSend test data ['C',1,2,3]")
    commander_client = TCN_socket.TCP_client(50000)
    commander_client.send_list(['C',1,2,3])


    print('\n\n##### Initializing STM32 #####')
    process_bridge = subprocess.Popen('python3 TCN_STM32_main.py',shell = True)

    
except:
    commander_client.close()
    traceback.print_exc()
    print('\n Commander communication fail')




    # p_bridge = subprocess.Popen('python TCN_STM32_main.py',shell = True)
    # print('Initializing STM32 motor controller')




commander_client.close()



