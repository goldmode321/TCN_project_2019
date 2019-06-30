import TCN_STM32_protocol
import TCN_socket
import threading
import traceback

def stm32_main():
    try:
        stm32 = TCN_STM32_protocol.STM32_command()
        tcns = TCN_socket.UDP_client(50001,1)
        stm32.on()
        
    except:
        traceback.print_exc()



    while stm32.pin_check:
        
        command = tcns.recv_list()
        stm32.move(command)
