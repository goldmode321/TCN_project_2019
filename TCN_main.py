import TCN_socket
import time
import subprocess
import traceback

try:
    command_server = TCN_socket.TCP_server(50000)
    print('Initializing communicaiton bridge')
    subprocess.Popen('python TCN_bridge.py',shell = True)
    connection_test = command_server.recv_string()
    print(connection_test)
    if connection_test == 'C':
        print('Bridge connection established successfully')
        command_server.send_string('C')
        time.sleep(1)
    connect_test = command_server.recv_string()
    print(connect_test)
    time.sleep(1)
    command_server.close()
except:
    command_server.close()
    traceback.print_exc()





