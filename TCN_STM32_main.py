import TCN_STM32_protocol
import TCN_socket
import threading
import traceback


try:
    stm32 = TCN_STM32_protocol.STM32_command()
    stm32_client = TCN_socket.UDP_client(50001)

    
except:
    traceback.print_exc()



# while stm32.pin_check:
    
#     command = tcns.recv_list()
#     stm32.move(command)


end = stm32_client.recv_string()
if end == 'E':
    stm32_client.send_string('E')
    stm32_client.close()
    stm32.off()