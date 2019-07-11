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
        logging.info('Successfully connect to STM32 , port : {} \n'.format(stm32.USB_port_PATH))
        stm32_client = TCN_socket.TCP_client(50003)
        logging.info('STM32 communication established\n')
        # stm32_client.send_list(['S',1,2,3])
        # logging.info("Test connection to communication center,['S',1,2,3'] sent, ['S','T','M',3,2] should be received\n")
        # data_get = stm32_client.recv_list()
        # if data_get == ['S','T','M',3,2]:
        #     keep_running = True
        #     logging.info("['S','T','M',3,2] received , connection test complete. Program start\n")
        # else:
        #     keep_running = False
        #     print('Something wrong for connection check, wrong potorcol')
        #     logging.info(str(data_get)+" . Wrong potorcol, please check TCN_bridge.py , STM32 initial section ; And check TCN_STM32_main.py\n")
        stm32_client.send_list(['S','next'])
    except:
        traceback.print_exc()
        logging.exception("Got error\n")
        stm32_client.close()



'''Portocol function'''

def stm32_portocol(data_get):
    global stm32,stm32_client,keep_running
    if data_get[0] == 'S':
        if data_get[1] == 'exit':
            keep_running = False
            logging.info(" 'exit' command received, start terminating program\n")
        elif data_get[1] == 'move':            
            stm32.move(data_get[2])
            stm32_client.send_list(['S','next'])
            logging.info(" 'move' command received, movie with "+str(data_get[2])+'\n')
        elif data_get[1] == 'stop':
            stm32.move([0,0,0])
            logging.info(" 'stop' command received, movie with "+str([0,0,0])+'\n')
    
    else:
        print(str(data_get)+" received by STM32. Wrong potorcol ! ")
        logging.info(str(data_get)+" received by STM32. Wrong potorcol, please check TCN_bridge.py \n")



'''Running section '''

def main():
    global stm32,stm32_client,keep_running
    while keep_running:
        try:
            data_get = stm32_client.recv_list()
            logging.info('Command in : {} \n'.format(data_get))
            stm32_portocol(data_get)


        except:
            traceback.print_exc()
            logging.exception("Got error \n")
            stm32_client.close()
            keep_running = False



'''Ending section '''

def end():
    stm32_client.close()
    stm32.off()
    logging.info('STM32 is off \n')
    sys.exit(0)

if __name__ == "__main__":
    init()
    main()
    end()
