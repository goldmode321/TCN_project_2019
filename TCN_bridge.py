import TCN_socket
import time
import traceback

'''Portocol'''
''' "C" to Main , "L" to LiDAR , "S" to STM32 , "G" to GPIO , "X" to xbox, "V" to Vision , "M" to motion '''

try:
    commander_server = TCN_socket.UDP_client(50000)
    time.sleep(1)
    commander_server.send_string('C')
    C_connection_test = commander_server.recv_string()
    if C_connection_test == 'C':
        print('close')
        commander_server.close()
        

except:
    traceback.print_exc()
    commander_server.close()

# stm_server = TCN_socket.UDP_server(50001,1)
# xbox_server = TCN_socket.UDP_server(50002,1)




