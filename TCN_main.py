import TCN_socket
import time
import subprocess

def initialize():
    command_client = TCN_socket.UDP_server(50000,1)
    print('Initializing communicaiton bridge')
    subprocess.Popen('python TCN_bridge.py')
    connection_test = command_client.recv_string()
    print(connection_test)
    if connection_test == 'C':
        print('Bridge connection established successfully')
        command_client.send_string('C')
    
    command_client.close()






if __name__ == "__main__":
    initialize()