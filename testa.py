'''
import socket
import sys

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = ('localhost', 10000)
print('connecting to {} port {}'.format(*server_address))
sock.connect(server_address)

try:

    # Send data
    message = b'This is the message.  It will be repeated.'
    print('sending {!r}'.format(message))
    sock.sendall(message)

    # Look for the response
    amount_received = 0
    amount_expected = len(message)

    while amount_received < amount_expected:

        data = sock.recv(16)
        amount_received += len(data)
        print('received {!r}'.format(data))

finally:
    print('closing socket')
    sock.close()
'''



'''
class cdf:
    def c(self):
        print('c')
    
    def d(self, input):
        print(input)
    
    def f(self):
        print('f')
'''

'''
import threading
import time
import traceback
global b 
b = 0
def printA():
    global b
    runA = True
    
    while runA:
        try:
            b = b + 1
            print('A')
            time.sleep(1)
        except:
            print('printA terminate')
            runA = False


t1 = threading.Thread(target = printA)
t1.daemon = True
t1.start()

run = True

try:
    while run:
        print('B')
        time.sleep(0.5)
        print(b)

except:
    traceback.print_exc()
    run = False
'''




# import TCN_socket
# import time
# import threading

# # client = TCN_socket.TCP_client(55555)
# client = TCN_socket.TCP_server(55555,1)
# # client = TCN_socket.UDP_server(55555,1)
# global i
# i = 0

# def multi():
#     global i 
#     while True:
#         i = i+1
#         time.sleep(0.5)



# thread = threading.Thread(target = multi)
# thread.daemon = True
# thread.start()


# while True:
#     try:
        
#         data = client.recv_list()
#         # data = client.recv_string(1024)
#         print('client get {} '.format(data))
#         time.sleep(1)
#         # client.send_list(['number of receive',i])
#         client.send_list(['thread run',i])
#         # client.send_string(str(['thread run',i]))
#     except:
#         client.close()
#         break


# import TCN_socket
# import time
# import traceback
# client = TCN_socket.TCP_client(50000)
# try:
#     try:
#         time.sleep(10)
#         client.send_list([321])
#     except KeyboardInterrupt:
#         print('keyboard')
# except:
#     traceback.print_exc()
# client.close()



# try:
#     input('enter : ')
#     print(1)
# except:
#     print(2)

# import TCN_socket
# import pickle
# import dill
# import time
# def a():
#     print(1)
# msg = dill.dumps(a)
# print(msg)
# server =TCN_socket.TCP_server(50000)
# server.connection[0].send(msg)
# time.sleep(0.5)
# server.close()

import TCN_socket
server = TCN_socket.UDP_server(55555)
RUN = True
while RUN:
    try:
        cmd = input('321  : ')
        if cmd == 'e':
            break
    except:
        break

