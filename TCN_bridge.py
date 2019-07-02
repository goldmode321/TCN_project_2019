import TCN_socket
import time
import traceback
import sys

'''Portocol'''
''' "C" to Main , "L" to LiDAR , "S" to STM32 , "G" to GPIO , "X" to xbox, "V" to Vision , "M" to motion '''

try:
    commander_client = TCN_socket.TCP_client(50000)
    time.sleep(1)
    commander_client.send_string('C')
    C_connection_test = commander_client.recv_string(1)
    print(C_connection_test)
    if C_connection_test == 'C':
        print('close')
        time.sleep(1)
        commander_client.send_string('C')
        time.sleep(1)
        commander_client.close()
        sys.exit(0)



except:
    traceback.print_exc()
    commander_client.close()

# stm_server = TCN_socket.UDP_server(50001,1)
# xbox_server = TCN_socket.UDP_server(50002,1)




