import TCN_socket
import time
import subprocess

def initialize():
    command_server = TCN_socket.UDP_server(50000,1)
    print('Initializing communicaiton bridge')
    subprocess.Popen('python TCN_bridge.py',shell=True)
    connection_test = command_server.recv_string()
    if connection_test == 'C':
        print('Bridge connection established successfully')
    
    print('Initializing STM32')
    # subprocess.Popen('python TCN_STM32_main.py',shell=True)
    command_server.send_string('S')
    connection_test = command_server.recv_string()
    if connection_test == 'S':
        print('STM32 connection established successfully')
    
    # time.sleep(5)
    command_server.send_string('E')
    time.sleep(1)
    command_server.close()
    print('TCN_main off')







if __name__ == "__main__":
    initialize()