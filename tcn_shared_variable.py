import numpy


class SharedVariables():
    def __init__(self):
        self.ROV = Rover()                 # 50012
        self.VI = Vision()                 # 50015
        self.LI = Lidar()                  # 50016
        self.MAP = MapPlotting()           # 50017
        self.CAL = Calibration()           # 50018
        self.STM = STM32()             # 50019
        self.LOBS = LocalObstacle()        # 50020
        self.GOBS = GlobalObstacle()       
        self.GUI = GuiObject()

class Rover:
    def __init__(self):
        self.rover_run = False


class LocalObstacle:
    def __init__(self):
        self.local_obstacle_x = numpy.array([0, 1, 2])
        self.local_obstacle_y = numpy.array([0, 1, 2])
        self.local_obstacle_dict = {
            'local_obstacle_x':self.local_obstacle_x,
            'local_obstacle_y':self.local_obstacle_y
            }

class GlobalObstacle:
    def __init__(self):
        self.global_obstacle_x = numpy.array([])
        self.global_obstacle_y = numpy.array([])
        self.global_obstacle = numpy.array([])
        self.global_obstacle_buffer = list()

class Vision:
    def __init__(self):
        self.vision_ip = "192.168.5.101"
        self.vision_run = False
        self.reset_flag = False
        self.vision_idle = False
        self.vision_x = 0
        self.vision_y = 0
        self.vision_theta = 0
        self.vision_use_map_mode = False
        self.vision_build_map_mode = False
        self.vision_angle_radian = 0
        self.vision_status = -1
        self.vision_data = [0, 0, 0, self.vision_status]


class Lidar:
    def __init__(self):
        self.lidar = None
        self.lidar_thread = None
        self.lidar_USB_port = ""
        self.lidar_run = False
        self.lidar_connect = False
        self.lidar_state = list()
        self.lidar_minimum_radius = 450
        self.lidar_data = [[0,0,0],[1,1,1]]
        self.lidar_angle = [0]
        self.lidar_radius = [0]

class MapPlotting:
    def __init__(self):
        self.arrow_x = [0]
        self.arrow_y = [0]
        self.global_map = numpy.array([])

class STM32:
    def __init__(self):
        self.calibrate_x = 0
        self.calibrate_y = 0
        self.calibrate_angle = 0
        self.calibrate_x_multi = 1
        self.calibrate_y_multi = 1
        self.calibrate_angle_multi = 1
        self.calibrate_difference_between_lidar_and_vision = 130
        self.temp_calibrate_difference_between_lidar_and_vision = 130
        self.calibration_run = False

class CarControl:
    def __init__(self):
        self.car_control_server_run = False
        self.car_control_receive = None
        self.car_control_previous_receive = None
        self.car_control_state = 'stop'
        self.car_control_forward_pwm = 410 # 403
        self.car_control_backward_pwm = 370  # 381
        self.car_control_stop_pwm = 400
        self.car_control_add_speed = 1 # Speed adjust from gui

class GuiObject:
    def __init__(self):
        self.gui = None

if __name__ == "__main__":
   SharedVariables() 