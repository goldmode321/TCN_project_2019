import TCN_STM32_protocol
import TCN_socket
import threading

def stm32_main():
    stm32 = TCN_STM32_protocol.STM32_command()
    tcns = TCN_socket.UDP_client(50001)

    pin_check = stm32.on()

    while pin_check:
        command = tcns.recv_list()
