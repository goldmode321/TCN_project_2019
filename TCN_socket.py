import socket
import time
import sys


class UDP_server(object):
    ''' Class for socket server '''

    def __init__(self, port = 50000, ip = '127.0.0.1',setblocking = 0):
        self.port = port
        self.ip = ip
        self.setblocking = setblocking

        # Create UDP server
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.setblocking(self.setblocking)
            self.sock.bind(self.ip, self.port)
            print('Server initiate - '+ self.ip+ ' : '+ str(self.port))

        except Exception as e:
            self.sock.close()
            print('Cancel bind process \n\n')
            print(e)

    def listen_string(self, length = 11):
        try:
            self.listen_str = self.sock.recv(length)
            return self.listen_str
        
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

    def send_string(self, port=5000, message = '', ip = '127.0.0.1'):
        ''' Send string to target port (default IP is 127.0.0.1)'''
        try:
            self.sock.sendto(message.encode('utf-8') , (ip,port) ) # Send message ( I forgot what's the return value of sendto() )

        except Exception as e:
            self.sock.close()
            print(e)        



