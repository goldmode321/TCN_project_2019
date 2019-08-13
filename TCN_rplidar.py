import rplidar
import time
import traceback
import logging
import TCN_socket
import threading

class Lidar(object):

    def __init__(self):
        logging.basicConfig(filename='LiDAR.log',filemode = 'w',level =logging.INFO)
        logging.info("Initializing RPLidar")

        ###############
        self.lidar = None 
        self.lidar_client = None
        self.lidar_thread_client = None
        self.lidar_run_flag = False
        self.lidar_data = []
        ###############
        try:
            logging.info("Initializing Lidar_client")
            self.lidar_client = TCN_socket.TCP_client(50002)
            self.lidar_thread_client = TCN_socket.UDP_client(50004)
            self.lidar_scan_port()
            self.lidar_client.send_list(['L','status',str(self.lidar_state[0])])
            self.lidar_run_flag = True
            self.lidar_main()
            

        except:
            traceback.print_exc()
            logging.exception("Got error\n")
            if self.lidar_client != None:
                self.lidar_client.close()
            if self.lidar_thread_client != None:
                self.lidar_thread_client.close()



    def lidar_main(self):
        self.lidar_run_background()
        while self.lidar_run_flag:
            try:
                lidar_receive = self.lidar_client.recv_list()
                logging.info("lidar received : {} ".format(lidar_receive))
                self.lidar_protocol(lidar_receive)

            except:
                traceback.print_exc()
                logging.exception('Got error : ')
                self.lidar_run_flag = False   
        # self.lidar.stop()
        # self.lidar_client.close()
        # time.sleep(1)        



    def lidar_protocol(self,lidar_receive):
        try:
            if lidar_receive[0] == 'L':
                if lidar_receive[1] == 'exit':
                    self.lidar_run_flag = False
                    self.lidar_client.close()
                    self.lidar.stop()

                    
                elif lidar_receive[1] == 'gld':
                    logging.debug("lidar data {}".format( self.lidar_data))
                    if self.lidar_data != None:
                        self.lidar_client.send_list(['L','gld', self.lidar_data])
                        
                    else:
                        self.lidar_client.send_list(['L','gld',"No lidar data"])
 
            else:
                logging.warning("Wrong portocol to Lidar communication , please check lidar_portocol or bridge protocol")
        except:
            logging.exception("lidar_protocol Got error : ")




    def lidar_run_background(self):
        thread = threading.Thread(target = self.get_lidar_data ,daemon = True)
        thread.start()

#=============================================#
#                   Liberary                  #
#=============================================#

    def lidar_scan_port(self):
        self.lidar_scanning_flag = True
        self.initial_scanning_port_num = 0
        logging.info('Scanning RPLidar port')
        while self.lidar_scanning_flag:
            try:

                self.lidar_USB_port = '/dev/ttyUSB'+str(self.initial_scanning_port_num)
                logging.info('Scanning '+self.lidar_USB_port)
                self.lidar = rplidar.RPLidar(self.lidar_USB_port)
                self.lidar_state = self.get_status()
                if self.lidar_state[0] == 'Good':
                    logging.info(self.lidar_state)
                    self.lidar_scanning_flag = False
                    logging.info("lidar initialize successuflly")
                else:
                    print(self.lidar_state)
                    print('1 or more undefined problems , plase check RPLiDAR')
                    logging.warning(str(self.lidar_state)+' ; 1 or more undefined problems , please check RPLiDAR')


            except rplidar.RPLidarException:
                # print("Not this one , system continue scanning")
                logging.info('Not this one , system continue scanning')
                self.initial_scanning_port_num += 1
                if self.initial_scanning_port_num > 10:
                    self.initial_scanning_port_num = 0
                    logging.warning('Rescanning RPLiDAR port')
            
            except:
                traceback.print_exc()
                logging.exception("Got error\n")

    def get_status(self):
        return self.lidar.get_health()
                

    def stop(self):
        self.lidar.stop()  
        self.lidar.disconnect()
        logging.info("RPLidar disconnect")  

    def reconnect(self):
        self.lidar.stop()
        self.lidar = rplidar.RPLidar(self.lidar_USB_port)

    def get_lidar_object(self):
        return self.lidar

    def get_lidar_data(self):

        try:
            for scan in self.lidar.iter_scans():
                self.lidar_data = scan
                self.lidar_thread_client.send_list(self.lidar_data)
        except:
            self.reconnect()
            self.get_lidar_data()

    
        




class Lidar_test_communication(object):
    
    def __init__(self):
        try:
            self.lidar_server_run_flag = False
            self.lidar_thread_server_run_flag = False
            self.lidar_server = TCN_socket.TCP_server(50002,1)
            self.lidar_thread_server = TCN_socket.UDP_server(50004)
            self.lidar_data = self.lidar_server.recv_list()
            if self.lidar_data == ['L','status','Good']:
                print('Lidar connected')
                self.lidar_server_run_flag = True
                self.lidar_thread_server_run_flag = True
                self.main()
            else:
                print('Undefined communication error of Vision module, please check test message')

                raise KeyboardInterrupt      
        except:
            traceback.print_exc()
            self.lidar_server.close()

    def main(self):
        self.server_run_background()
        while self.lidar_server_run_flag:
            try:
                command = input('Server command : ')
                self.potorcol(command)
            except:
                self.potorcol('exit')
                self.lidar_server_run_flag = False
        
        self.lidar_server.close()
        self.lidar_thread_server.close()
        # time.sleep(1)

    def get_lidar_data_background(self):
        while self.lidar_thread_server_run_flag:
            if self.lidar_thread_server.server_alive:
                self.temp_lidar_data = self.lidar_thread_server.recv_list()
                time.sleep(0.2)

    def server_run_background(self):
        thread = threading.Thread(target = self.get_lidar_data_background ,daemon = True)
        thread.start()

                
    def potorcol(self,command):

        try:
            if command == None:
                print('socket got problem')
  
            elif command == 'gld':
                self.lidar_server.send_list(['L','gld'])
                receive = self.lidar_server.recv_list()
                print(receive[2])

            elif command == 'gld2':
                print(self.temp_lidar_data)

            elif command == 'exit':
                self.lidar_server.send_list(['L','exit'])
                self.lidar_server_run_flag = False
                time.sleep(0.2) # For sure that client close first
                self.lidar_server.close()



            else:
                print('{} received . Wrong potorcol  !'.format(command))
                
                

        except:
            self.lidar_server.close()
            traceback.print_exc()


if __name__ == "__main__":
    Lidar()

        