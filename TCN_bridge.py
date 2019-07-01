import TCN_socket
import time
import traceback
import subprocess

'''Portocol'''
''' "C" to Main , "L" to LiDAR , "S" to STM32 , "G" to GPIO , "X" to xbox, "V" to Vision , "M" to motion '''

try:
    commander_client = TCN_socket.UDP_client(50000)
    commander_client.send_string('C')

    stm32_server = TCN_socket.UDP_server(50001,1)
    stm32_connection = stm32_server.recv_string()
    if stm32_connection == 'S':
        commander_client.send_string('S')
    
    # xbox_server = TCN_socket.UDP_server(50002,1)
    # xbox_connection = xbox_server.recv_string()
    # if xbox_connection == 'X':
    #     commander_client.send_string('X')
        

        

except:
    traceback.print_exc()
    commander_client.close()

end = commander_client.recv_string()
if end == 'E':
    stm32_server.send_string('E')
    stm32_server.close()










class bridge_portocol(object):

    def Command_potorcol(self,command):
        if type(command) == str:
            pass


