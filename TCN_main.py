import TCN_socket
import time

xbox_ser = TCN_socket.UDP_server()

while True:
    start = time.time()
    xbox_data = xbox_ser.recv_list()
    end = time.time()
    print(xbox_data , end-start)
    #time.sleep(0.1)
