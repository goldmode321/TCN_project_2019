#from TCN_STM32_protocol import STM32_command

# stmc = STM32_command()

# from TCN_socket import UDP_client
# import time


# udpc = UDP_client()
# while True:
#     start = time.time()
#     udpc.send_list([ 1 for x in range(4000)])
#     end = time.time()
#     print(end - start)


import socket
import sys
import time

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = ('localhost', 10000)
print('starting up on {} port {}'.format(*server_address))
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)

while True:
    # Wait for a connection
    print('waiting for a connection')
    connection, client_address = sock.accept()
    try:
        print('connection from', client_address)

        # Receive the data in small chunks and retransmit it
        while True:
            data = connection.recv(16)
            print('received {!r}'.format(data))
            if data:
                print('sending data back to the client')
                connection.sendall(data)
            else:
                print('no data from', client_address)
                break
            time.sleep(1)

    except:
        # Clean up the connection
        connection.close()