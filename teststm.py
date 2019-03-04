#from TCN_STM32_protocol import STM32_command

# stmc = STM32_command()

from TCN_socket import UDP_client
import time


udpc = UDP_client()
while True:
    start = time.time()
    udpc.send_list([ 1 for x in range(4000)])
    end = time.time()
    print(end - start)

