import TCN_socket
import time


gui_server = TCN_socket.UDP_server(50000)
stm_server = TCN_socket.UDP_server(50001)
xbox_server = TCN_socket.UDP_server(50002)


while True:
    start = time.time()
    xbox_data = xbox_server.recv_list()
    end = time.time()
    print(xbox_data , end-start)
    #time.sleep(0.1)
