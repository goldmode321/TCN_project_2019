import socket
import time
import sys
import pickle
import struct
from multiprocessing.connection import Listener, Client


class UDP_server(object):
    ''' Class for socket server '''

    def __init__(self, port = 50000, ip = '127.0.0.1',setblocking = 0):
        self.port = port
        self.ip = ip
        self.setblocking = setblocking

        # Send list method ( 'socket' or 'multi')
        self.method = 'socket'

        # Create UDP server
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.setblocking(self.setblocking)
            self.sock.bind((self.ip, self.port))
            print('Server initiate - '+ self.ip+ ' : '+ str(self.port))

        except Exception as e:
            self.sock.close()
            print('Cancel bind process \n\n')
            print(e)

    def recv_string(self, length = 11):
        try:
            receive_str = self.sock.recv(length).decode('utf-8')
            return receive_str
        
        except socket.timeout: # if server didn't get any data in a period of time 
            pass               # Do nothing and pass  , the return data is 'None' 
        except KeyboardInterrupt: 
            self.sock.close() # Unbind socket from the adress
            sys.exit(0) # Exit program
        except socket.error as e:
            #print(e)
            pass
        except Exception as e:
            print(e)
            self.sock.close()

    def recv_list(self, length = 4096):
        try:
            if self.method == 'socket':
                #buf = b''
                #while len(buf) < 4:
                #    buf += self.sock.recv(4-len(buf))
                #print(buf)
                #print(struct.unpack('!I',buf))
                #receive_list = pickle.loads(struct.unpack('!I',buf)[0])
                #receive_list = struct.unpack('!I',buf)[0]
                receive_list = pickle.loads(self.sock.recv(length))
                return receive_list
        
        except socket.timeout: # if server didn't get any data in a period of time 
            pass               # Do nothing and pass  , the return data is 'None' 
        except KeyboardInterrupt: 
            self.sock.close() # Unbind socket from the adress
            sys.exit(0) # Exit program
        except socket.error as e:
            #print(e)
            pass
        except Exception as e:
            print(e)
            self.sock.close()

    def send_string(self, message = '', port=50000, ip = '127.0.0.1'):
        ''' Send string to target port (default IP is 127.0.0.1)'''

        try:
            if port != self.port or ip != self.ip:
                self.sock.sendto(message.encode('utf-8') , (ip,port) ) # Send message ( I forgot what's the return value of sendto() )
            else:
                self.sock.sendto(message.encode('utf-8') , (self.ip ,self.port) )
        except Exception as e:
            self.sock.close()
            print(e)

    def send_list(self, list = [], port=50000, ip = '127.0.0.1'):
        '''send list to target port (default IP is 127.0.0.1)'''
        try:
            #if self.method == 'socket':
            #    packet = pickle.dumps(list)
            #    length = struct.pack('!I', len(packet))
            #    packet = packet + length
            #    self.sock.sendto(packet , (ip,port) )
            self.sock.sendto(pickle.dumps(list) , (ip,port) )
        except Exception as e:
            self.sock.close()
            print(e)

    def close(self):
        ''' Close server '''
        self.sock.close()
        print('Server close without error')


class UDP_client(object):
    ''' Class for UDP_client '''
    def __init__(self, port = 50000, ip='127.0.0.1'):
        self.port = port
        self.ip = ip
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except Exception as e:
            self.sock.close()
            print(e)
            print('socket client fail initialize')
    
    def recv_string(self, length = 11):
        try:
            receive_str = self.sock.recv(length).decode('utf-8')
            return receive_str
        
        except socket.timeout: # if server didn't get any data in a period of time 
            pass               # Do nothing and pass  , the return data is 'None' 
        except KeyboardInterrupt: 
            self.sock.close() # Unbind socket from the adress
            sys.exit(-0) # Exit program
        except socket.error as e:
            print(e)
            pass
        except Exception as e:
            print(e)
            self.sock.close()

    def recv_list(self, length = 4096):
        try:
            receive_list = pickle.loads(self.sock.recv(length))
            return receive_list
        
        except socket.timeout: # if server didn't get any data in a period of time 
            pass               # Do nothing and pass  , the return data is 'None' 
        except KeyboardInterrupt: 
            self.sock.close() # Unbind socket from the adress
            sys.exit(0) # Exit program
        except socket.error as e:
            print(e)
            pass
        except Exception as e:
            print(e)
            self.sock.close()

    def send_string(self, message = '', port=50000, ip = '127.0.0.1'):
        ''' Send string to target port (default IP is 127.0.0.1)'''
        try:
            self.sock.sendto(message.encode('utf-8') , (ip,port) ) # Send message ( I forgot what's the return value of sendto() )

        except Exception as e:
            self.sock.close()
            print(e)

    def send_list(self, list = [], port=50000, ip = '127.0.0.1'):
        '''send list to target port (default IP is 127.0.0.1)'''
        try:
            self.sock.sendto(pickle.dumps(list) , (ip,port) )
        except Exception as e:
            self.sock.close()
            print(e)

    def close(self):
        ''' Close server '''
        self.sock.close()
        print('Server close without error')

    





