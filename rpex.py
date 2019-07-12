import sys
import numpy as np
import rplidar as rp


PORT_NAME = '/dev/ttyUSB0'


def run(Number_of_turns=1):

        data=[]
        lidar = rp.RPLidar(PORT_NAME)
        lidar.clear_input()

        info = lidar.get_info()
        data.append(info)

        health = lidar.get_health()
        data.append(health)

        for i,scan in enumerate(lidar.iter_measurments()):
                data.append(scan)
                if i>Number_of_turns-2:
                        break
                lidar.stop()
        lidar.stop_motor()
        lidar.disconnect()

        return data






if __name__ == '__main__':
    data=run()
    print(data[2][2],data[2][3])            #print(angle,distance) 