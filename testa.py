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

# import time
# def ppp():
#     pass
# start_time = time.time()
# dic = {'1':'123', '2':321, 'a':321, 'b':321, '2c':321, '2d':321, '2q':321, '3':ppp}
# b = '3'
# for i in range(100000):
#     dic[b]()
# end_time = time.time()
# print('First : {}'.format(end_time - start_time))
# start_time = time.time()
# a = 3
# for i in range(100000):
#     if a == 1:
#         print('123')
#     elif a == 2:
#         print(321)
#     elif a =='b':
#         pass
#     elif a == '2c':
#         pass
#     elif a == '2d':
#         pass
#     elif a =='321':
#         pass
#     elif a ==123:
#         pass
#     elif a == 3:
#         pass
# end_time = time.time()
# print('Second : {}'.format(end_time - start_time))

# import time
# class classB():
#     def __init__(self,a=1, b=10, t = None):
#         self.a = a
#         self.b = b
#         self.t = t

#     def dic(self):
#         return {1:self.b1, 2:222, 3:self.a}

#     def b1(self):
#         self.t.sleep(3)
#         print('b1')



# class classA(classB):
#     def __init__(self):
#         self.a = 100
#         self.b = 200
        
#         super().__init__(self.a, self.b, time)
#         self.d = self.dic()

#     def a1(self):
#         print('a1')

import tcn_socket
import time
import matplotlib.pyplot as plt

sock = tcn_socket.UDP_client(50008, 0, "192.168.5.10")
sock.send_list([123])