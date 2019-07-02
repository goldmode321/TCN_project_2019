import TCN_STM32_protocol
import TCN_socket
import threading
import traceback
import sys
import time


try:
    stm32 = TCN_STM32_protocol.STM32_command()
    stm32_client = TCN_socket.TCP_client(50001)
    stm32_client.send_list(['S',1,2,3])

    
except:
    traceback.print_exc()
    stm32_client.close()


stm32_client.close()
stm32.off()
