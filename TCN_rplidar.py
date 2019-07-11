import rplidar
import traceback
import time
import logging

class Lidar(object):

    def __init__(self):
        self.lidar_scanning = True
        self.initial_scanning_port_num = 0
        logging.basicConfig(filename='LiDAR_main.log',filemode = 'a',level =logging.INFO)
        logging.info('Scanning RPLidar port')
        
        while self.lidar_scanning:
            try:
                self.lidar_USB_port = '/dev/ttyUSB'+str(self.initial_scanning_port_num)
                logging.info('Scanning '+self.lidar_USB_port)
                self.lidar = rplidar.RPLidar(self.lidar_USB_port)
                self.lidar_state = self.lidar.get_health()
                if self.lidar_state[0] == 'Good':
                    logging.info(self.lidar_state)
                    self.lidar_scanning = False
                else:
                    print(self.lidar_state)
                    print('1 or more undefined problems ')


            except rplidar.RPLidarException:
                # print(re)
                logging.info('Not this one , system continue scanning')
                

    def stop(self):
        self.lidar.stop()  
        self.lidar.disconnect()
        logging.info("RPLidar disconnect")  



        