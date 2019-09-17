import math
import time
import threading
import logging
import tcn_socket

class MoveAlgorithm:
    def __init__(self):
        self.algorithm_run = True
        self.algorithm_udp_client = None
        
        # Data from bridge
        self.recorded_vision_coordinate = []
        self.lidar_data = []
        self.vision_data = []


