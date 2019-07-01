import TCN_STM32_protocol
import TCN_socket
import threading
import traceback
import sys


try:
    stm32 = TCN_STM32_protocol.STM32_command()
    stm32_client = TCN_socket.UDP_client(50001)
    stm32_client.send_string('S')

    
except:
    traceback.print_exc()



# while stm32.pin_check:
    
#     command = tcns.recv_list()
#     stm32.move(command)


end = stm32_client.recv_string()
print(end)
if end == 'E':
    stm32_client.send_string('E')
    stm32_client.close()
    stm32.off()
    print(stm32.pin_check)


sys.exit()