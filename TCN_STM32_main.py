import TCN_STM32_protocol
import TCN_socket
import threading
import traceback
import sys
import time
import logging


'''Initial section of STM32 '''
stm32 = None
stm32_client = None
keep_running = False



def init():
    global stm32,stm32_client,keep_running
    try:
        logging.basicConfig(filename='STM32_main.log',filemode = 'w',level =logging.INFO)
        stm32 = TCN_STM32_protocol.STM32_command()
        logging.info('Successfully connect to STM32')
        stm32_client = TCN_socket.TCP_client(50001)
        logging.info('STM32 communication established')
        stm32_client.send_list(['S',1,2,3])
        logging.info("Test connection to communication center,['S',1,2,3'] sent, ['S','T','M',3,2] should be received")
        data_get = stm32_client.recv_list()
        if data_get == ['S','T','M',3,2]:
            keep_running = True
            logging.info("['S','T','M',3,2] received , connection test complete. Program start")
        else:
            keep_running = False
            print('Something wrong for connection check, wrong potorcol')
            logging.info("Wrong potorcol, please check TCN_bridge.py , STM32 initial section ; And check TCN_STM32_main.py")
    except:
        traceback.print_exc()
        stm32_client.close()


'''Running section '''


def main():
    global stm32,stm32_client,keep_running
    while keep_running:
        try:
            data_get = stm32_client.recv_list()

            ''' Check data flag '''
            if data_get[0] == 'S':
                if data_get[1] != 'end':
                    stm32.move(data_get[1])
                elif data_get[1] == 'end':
                    keep_running = False
        except:
            stm32_client.close()
            keep_running = False



'''Ending section '''

def end():
    stm32_client.close()
    stm32.off()

if __name__ == "__main__":
    init()
    main()
    end()
