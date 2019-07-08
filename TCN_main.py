#!/usr/bin/python3
import TCN_socket
import time
import subprocess
import traceback
import threading
import TCN_xbox


process_bridge = None
commander_client = None
commander_run = False
process_stm32 = None
xbox = None
###                                                                   ###
###    Preview function                                               ###
###                                                                   ###

def help_menu():
    print(" exit : Quit software ")                 # [ 'C' , 'exit ']
    print(" xt : Xbox test ")                       # None
    print(" mwx : Xbox remote control ")            # [ 'C' , 'xbox' , [x,y,z] ]
    print(" xtg : Xbox test, gpio ")
    


###                                                                   ###
###    Portocol for commander                                         ###
###                                                                   ###
'''
['C' , 'next' ]

'''
def commander_portocol(commander_receive):
    global commander_client,commander_run,xbox,process_bridge,process_stm32
    if commander_receive[0] == 'C':
        if commander_receive[1] == 'next':
            pass



###                                                                   ###
###    Initialize xbox. See TCN_xbox.py                               ###
###                                                                   ###
def xbox_init():
    global xbox
    xbox = TCN_xbox.xbox_controller()


###                                                                   ###
###    Run TCN_bridge.py (so called "Communication center (CC) ")     ###
###                                                                   ###
def commander_init():
    try:
        global process_bridge, commander_client,commander_run,process_stm32
        
        process_bridge = subprocess.Popen('python3 TCN_bridge.py',shell = True)
        print('##### Initializing communication center #####')
        time.sleep(1)    # Wait some time for assuming Communication center(CC) work  稍微delay，以確保CC正常運作
        print("Establish TCP connection to communication center\nSend test data ['C',1,2,3]")
        commander_client = TCN_socket.TCP_client(50000)
        commander_receive = commander_client.recv_list()
        commander_portocol(commander_receive) # Waiting for [ 'C' , 'next' ]

        


        print('\n\n##### Initializing STM32 #####')
        process_stm32 = subprocess.Popen('python3 TCN_STM32_main.py',shell = True)
        commander_receive = commander_client.recv_list() # Waiting for [ 'C' , 'next' ]
        commander_portocol(commander_receive)



        commander_run = True
        # if commander_receive == (['C',0]):
        #     commander_run = True
            


    except:
        commander_client.close()
        traceback.print_exc()
        print('\n Commander communication fail')




    # p_bridge = subprocess.Popen('python TCN_STM32_main.py',shell = True)
    # print('Initializing STM32 motor controller')


###                                                                   ###
###     Waiting for User Command                                      ###
###                                                                   ###
def main():
    global process_bridge, commander_client,commander_run,process_stm32
    print('\n\n @@@ Program is all set, now is ready to run @@@')

    while commander_run:
        try:
            command = input('\nPlease enter command (Enter "h" for help menu)')
            if command == 'h':
                help_menu()

            elif command == 'exit':
                commander_client.send_list(['C','exit'])
                commander_run = False

            elif command == 'xt':
                xbox.xbox_test()

            elif command == 'mwx':
                while not xbox.joy.Back():
                    move_command = xbox.xbox_control()
                    commander_client.send_list(['C','mwx',move_command])
                    commander_receive = commander_client.recv_list()
                    commander_portocol(commander_receive)
                commander_client.send_list(['C','stop_motor'])


            else:
                commander_client.send_list(['C',command])
        
        except:
            commander_client.send_list(['C','exit'])
            commander_run = False
            
    commander_client.close()
    time.sleep(6)
    print('All program terminated')








if __name__ == "__main__":
    xbox_init()
    commander_init()
    main()
