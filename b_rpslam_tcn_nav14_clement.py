#!/usr/bin/python
# -*- coding: UTF-8 -*-
from __future__ import division
import rplidar
import TCN_rplidar_2 as tcnrplidar
from breezyslam.algorithms import RMHC_SLAM
from breezyslam.sensors import RPLidarA1 as LaserModel
import matplotlib.pyplot as plt
import multiprocessing as mp
from multiprocessing import Queue, Pool

import TCN_position as tcnp 
import TCN_xbox_velocity as tcnx
import TCN_gpio as tcng
import xbox
import sys, time,readline
# import xmlrpclib
import math
import numpy as np
import a_star_test as twa

import threading
import traceback
import inspect
import ctypes

# LIDAR parameters
port = '/dev/ttyUSB0'
MAP_SIZE_PIXELS  = 500
MAP_SIZE_METERS  = 10
MIN_SAMPLES      = 100

THREAD_OR_PROCESS = 2

np.set_printoptions(precision=2,suppress=True,linewidth=200)

class LidarProcess(mp.Process):
    def __init__(self,shared_variable, lidar_port='/dev/ttyUSB0', new_section=True):
        super(mp.Process, self).__init__(daemon=True)
        self.shared_variable = shared_variable
        self.lidar_port = lidar_port
    def run(self):
        data = np.array([[0,0]])
        try:
            lidar = tcnrplidar.init(self.lidar_port)
            lidar_generator = lidar.iter_measurments()
            for m in lidar_generator:
                try:
                    m = np.asarray([[m[2],m[3]]])
                    data = np.concatenate((data, m), axis=0) # Combin it into nparray([x, y], [x1, y1] ...) form
                    if len(data) >=360:
                        if shared_variable.empty():
                            shared_variable.put(data)
                            data = np.array([[0,0]])
                        # print("clean data")
                except rplidar.RPLidarException:
                    tcnrplidar.stopping(lidar)
                    self.run()
                except KeyboardInterrupt: # When enter Ctrl+C , conduct the code below
                    pass
        except rplidar.RPLidarException:
            # traceback.print_exc()
            tcnrplidar.stopping(lidar)
            self.run()




def lidar_get_data_in_backgounrd(need360data = False,length = 20 , lidar_port = '/dev/ttyUSB0' ):
    global data, lidar, lidar_generator
    data = np.array([[0,0]])
    try:
        lidar = tcnrplidar.init(lidar_port)
        lidar_generator = lidar.iter_measurments()
        for m in lidar_generator:
            try:
                m = np.asarray([[m[2],m[3]]])
                # angle = m[:, 1]
                # distance = m[:, 2]
                # data = np.stack((angle, distance), axis=1)
                # lidar.clean_input()
                data = np.concatenate((data, m), axis=0)
                # print("lidar data  {}".format(len(data)))
                if len(data) >=360:

                    data = np.array([[0,0]])
                    # print("clean data")
            except rplidar.RPLidarException:
                # traceback.print_exc()
                tcnrplidar.stopping(lidar)
                lidar_get_data_in_backgounrd()
            except KeyboardInterrupt: # When enter Ctrl+C , conduct the code below
                # tcnrpldiar.stopping(lidar)
                pass
    except rplidar.RPLidarException:
        # traceback.print_exc()
        tcnrplidar.stopping(lidar)
        lidar_get_data_in_backgounrd()
if THREAD_OR_PROCESS == 1:
    lidar_thread = threading.Thread(target=lidar_get_data_in_backgounrd, daemon=True)
else:
    shared_variable = Queue()
    lidar_thread = LidarProcess(shared_variable)
# class lidar_position(threading.Thread):
#     # def __init__(self):
#     #     threading.Thread.__init__(self)
#     #     self.signal = False

#     def run(self):        
#         self.signal = True
#         while self.signal==True:

#             lidar = init(port)
#             # Create an RMHC SLAM object with a laser model and optional robot model
#             slam = RMHC_SLAM(LaserModel(), MAP_SIZE_PIXELS, MAP_SIZE_METERS)
#             # Initialize an empty trajectory
#             trajectory = []
#             # Initialize empty map
#             mapbytes = bytearray(MAP_SIZE_PIXELS * MAP_SIZE_PIXELS)
#             # We will use these to store previous scan in case current scan is inadequate
#             previous_distances = None
#             previous_angles    = None
#             # First scan is crap, so ignore it
#             # next(iterator)
#             x_position = []
#             y_position = []
#             theta_list = []
#             while True:
#                 data = tcnrplidar.evade_all_dir_main()
#                 if len(data) > 2 :
#                     # Extract (quality, angle, distance) triples from current scan
#                     scan = data[1]                                ### data = [[a],[b],[c]] , member of b is max  
#                     distances = [meas[1] for meas in scan if meas[1] > 300]   ### mm
#                     angles    = [meas[0] for meas in scan if meas[1] > 300]
#                     # Update SLAM with current Lidar scan and scan angles if adequate
#                     if len(distances) > MIN_SAMPLES:
#                         slam.update(distances, scan_angles_degrees=angles)
#                         previous_distances = distances
#                         previous_angles    = angles
#                     # If not adequate, use previous
#                     elif previous_distances is not None:
#                         slam.update(previous_distances, scan_angles_degrees=previous_angles)
#                     # Get current robot position
#                     x, y, theta = slam.getpos()

#                     x_t = x-5000
#                     y_t = y-5000

#                     x_mir = x_t*math.cos(math.radians(270)) + y_t*math.sin(math.radians(270)) 
#                     y_mir = x_t*math.sin(math.radians(270)) - y_t*math.cos(math.radians(270)) 

#                     x_position.append(float('%.2f'%(x_mir/10)))
#                     y_position.append(float('%.2f'%(y_mir/10)))

#                     if theta > 360:
#                         theta_list.append(theta-360+4)
#                     elif theta < -360:
#                         theta_list,append(theta+360-4)
#                     elif 360 > theta >0:
#                         theta_list.append(theta+4)
#                     elif -360 < theta < 0:
#                         theta_list.append(theta-4)
#                     elif theta == 0:
#                         theta_list.append(theta)

#                     print('x_position: %.2f y_position: %.2f ang:%.2f' %(x_position[-1],y_position[-1],theta_list[-1]))
#                     # Get current map bytes as grayscale
#                     slam.getmap(mapbytes)
#                 else:
#                     print('x_position: %.2f y_position: %.2f ang:%.2f' %(x_position[-1],y_position[-1],theta_list[-1]))
#                     time.sleep(1)

    # def stop(self):
    #     self.signal = False
    #     x_position = []
    #     y_position = []
    #     theta_list = []
    #     print('Threading STOP !!!')

def main():

    global proxy

    try:
        # proxy =  xmlrpclib.ServerProxy("http://192.168.5.100:8080") 
        # alive_resp = proxy.alive() #check rpc sever is up
        tcng.init()
    except:
        print("# Server is not alive")
        print("")
        return 1

    if len(sys.argv) < 2:
        manual_mode()
    else:
        auto_mode(sys.argv[1])
    #manual_mode(proxy)
    #manual_mode(proxy,joy)

def manual_mode():
    print("# type h to refer command usage.")
    # joy = xbox.Joystick()
    global lidar_generator, lidar
    lidar_thread.start()
    while True:
        command = input('command：')
        cmd_list = command.lower().split()     #splits the input string on spaces
        cmd_list1 = command.split(",")
        cmd = cmd_list[0]
        cmd1 = cmd_list1[0]
        try:
            if cmd == 's1':
                scenario1()

            elif cmd == 'tr_a':
                try:
                    print('Target mode !!!')
                    set_target_ang()

                except Exception as e:
                    print( 'tr error !!!' )
                    print(e)

            elif cmd == 'tr_b':
                try:
                    print('Target mode !!!')
                    set_target_board()

                except Exception as e:
                    print( 'tr error !!!' )
                    print(e)

            elif cmd == 'tr_x':
                try:
                    print('Target mode !!!')
                    set_target_xbox()

                except Exception as e:
                    print( 'tr error !!!' )
                    print(e)

            elif cmd == 'oa':
                try:
                    print('Obstacle Aviod !!!')
                    pathAvoid()
                
                except Exception as e:
                    traceback.print_exc()
                    print( 'oa error !!!' )
                    print(e)

            elif cmd == 'gpio':
                try:
                    joy = xbox.Joystick()
                    print(joy)
                    print('push rightTrigger')
                    onflag = 1
                    gpioflag = True
                    while gpioflag:
                        if joy.rightTrigger() and onflag == 1:
                            tcng.relay_on()
                            onflag = -onflag
                            print('on')
                            time.sleep(0.2)
                        if joy.rightTrigger() and onflag == -1:
                            tcng.relay_off()
                            onflag = -onflag
                            print('off')
                            time.sleep(0.2)
                        if joy.Back():
                            tcng.relay_off()
                            gpioflag = False
                            print('Back to command mode')
                            joy.close()

                except IOError as e:
                    print(e)
                    tcng.relay_off()
                    print('Please retry again')
                except KeyboardInterrupt:
                    print('Back to command mode')
                    tcng.relay_off()
                    # joy.close()

            elif (cmd == 'qi') or (cmd == 'ex'):
                print( 'Quit now.' )
                print("")
                # joy.close()

                break

            else:
                print( 'Unknown command, please type help.' )


        except KeyboardInterrupt:
            print('Quit by KeyboardInterrupt')
            # joy.close()

        except Exception as e:
            print(e)
            # joy.close()
            print("# Command error: please check your format or check if server is not alive.")


    return



def stopping(lidar):
    print('stopping !!!')
    lidar.stop()
    lidar.disconnect()

def rplidar_RMHC_SLAM():

    global x_mir, y_mir, theta_lidar, data, previous_angles, previous_distances
    old_data = np.array([])
    while True:
        if THREAD_OR_PROCESS == 1:
            if len(data) >=360:
                temp_data = data
            # print(temp_data)
        elif THREAD_OR_PROCESS ==2:
            data = temp_data = shared_variable.get()

        if len(data) > 1:
            distances = [meas[1] for meas in temp_data if meas[1] > 275]   ### mm
            angles    = [meas[0] for meas in temp_data if meas[1] > 275]
            # print(len(distances))
            # Update SLAM with current Lidar scan and scan angles if adequate
            if len(distances) > MIN_SAMPLES:
                slam.update(distances, scan_angles_degrees=angles)
                previous_distances = distances
                previous_angles    = angles

            elif previous_distances is not None:
                slam.update(previous_distances, scan_angles_degrees=previous_angles)

            x_lidar, y_lidar, theta_lidar = slam.getpos()
            x_t = x_lidar-5000
            y_t = y_lidar-5000

            x_mir = x_t*math.cos(math.radians(270)) + y_t*math.sin(math.radians(270)) 
            y_mir = x_t*math.sin(math.radians(270)) - y_t*math.cos(math.radians(270)) 

            slam.getmap(mapbytes)
            # end_time_lidar = time.time()
            # print('LIDAR time : %s'%(end_time_lidar-start_time_lidar))
            return x_mir, y_mir, theta_lidar, temp_data




def scenario1():
    
    global x_lidar_position, y_lidar_position, lidar_theta_list, slam, mapbytes, x_mir, y_mir

    lidar = tcnrplidar.init(port)
    print('lidar OK!')
    slam = RMHC_SLAM(LaserModel(), MAP_SIZE_PIXELS, MAP_SIZE_METERS)
    trajectory = []
    mapbytes = bytearray(MAP_SIZE_PIXELS * MAP_SIZE_PIXELS)
    previous_distances = None
    previous_angles    = None

    # x_difs = []
    # y_difs = []
    x_lidar_position = []
    y_lidar_position = []
    lidar_theta_list = []

    car = tcnp.init()
    print('car')
    try:
        # joy = xbox.Joystick()
        # print('joy')
        # joy.connected()
        print(joy)
    except Exception as e:
        print(e)

    mapping_flag = True

    while mapping_flag:
        try:
            # print('try')
            tcnx.xbox_velocity_vision(joy,car)                #################
            # print('xbox is good')
            tt1 = time.clock()
            # x_lidar_position, y_lidar_position, lidar_theta_list = rplidar_RMHC_SLAM()
            x_mir, y_mir, theta_lidar, lidar_data = rplidar_RMHC_SLAM()
            tt2 = time.clock()
            # print('Lidar data:     %s'%(x_lidar_position))
            print('x_lidar_position:   %.2f' %(x_mir/10))
            print('y_lidar_position:   %.2f' %(y_mir/10))
            print('t               :   %.2f' %(tt2-tt1))
            print ('='*35)

            if joy.Back():
                print('come back command!!!')
                mapping_flag = False
                print(joy.Back())
                joy.close()
                tcng.relay_off()

        except KeyboardInterrupt:
            joy.close()
            tcng.relay_off()
            #print( 'Reset fp-slam start, please wait a moment ...' )
            break
        except Exception as e:
            tcng.relay_off()
            joy.close()
            print('error:',e)

def set_target_xbox():

    global x_lidar_position, y_lidar_position, lidar_theta_list, slam, mapbytes, x_mir, y_mir

    try:
        joy = xbox.Joystick()
        # print('joy')
        # joy.connected()
        print('joy')
    except IOError as ioe:
        print(ioe)
        print('reconnect to xbox in 1 second')
        time.sleep(1)

    car = tcnp.init('/dev/ttyUSB1')
    recorded_position = []
    x=[]

    lidar = tcnrplidar.init(port)
    print('lidar OK!')
    slam = RMHC_SLAM(LaserModel(), MAP_SIZE_PIXELS, MAP_SIZE_METERS)
    print('slam ok !!!')
    trajectory = []
    mapbytes = bytearray(MAP_SIZE_PIXELS * MAP_SIZE_PIXELS)
    previous_distances = None
    previous_angles    = None

    try:
        while True:

            forflag = True
            lidarflag = True

            tcnx.xbox_velocity_vision(joy,car) # Turn on XBOX control mode
            x_mir, y_mir,  theta_lidar, lidar_data= rplidar_RMHC_SLAM()
            print('x_position: %.2f   y_position:%.2f   theta:%.2f'%(x_mir/10, y_mir/10,theta_lidar))

            # The behavier when push button 'x'
            if joy.X():
                print('Add new way point')
                car[0] = 0 # Make car stop
                car[1] = 0
                car[2] = 0
                tcnp.move_to_coordinate(car)                
                time.sleep(0.5)
                recorded_position.append([round(x_mir/10),round(y_mir/10)]) # Remove the last element of recorded_position
                print(recorded_position)
                time.sleep(0.1)
                
            # The behavier when push button 'y'
            if joy.Y():
                print('Delet last generated way point')
                car[0] = 0 # Make car stop
                car[1] = 0
                car[2] = 0
                tcnp.move_to_coordinate(car)
                time.sleep(0.5)
                recorded_position.pop(len(recorded_position) - 1) # Remove the last element of recorded_position
                print(recorded_position)
                time.sleep(0.1)

            # The behavier when push button 'start'
            if joy.Start():
                if len(recorded_position) != 0: # If no position was recorded , then pass
                    for i in range(len(recorded_position)): 
                        print('len of recorded_position: %s'%(len(recorded_position)))
                        print(recorded_position[i])
                        position = recorded_position[i]
                        print('Target X : {} Y : {} '.format(position[0],position[1]))
                        forflag,lidarflag =  vision_to_target_position(car,joy,position[0],position[1]) # Move to target according to the camera
                        time.sleep(1)
                        if forflag == False:
                            break
                        if lidarflag == False:
                            break
                        #     car[0] = 0 
                        #     car[1] = 0
                        #     car[2] = 0
                        #     time.sleep(3)
                    recorded_position = [] # Wipe out recording file after execution
                else:
                    print('no recorded position')

            # The behavier when push button 'Back'
            if joy.Back():
                joy.close() # Kill xbox process 
                tcng.relay_off() # Make GPIO pin 4 off
                print('Closing tr mode')
                break

    except KeyboardInterrupt:
        tcng.relay_off()
        joy.close()
        print( 'Reset fp-slam start, please wait a moment ...' )

    except Exception as e:
        tcng.relay_off()
        print(e)   
        joy.close()
        print( 'Reset fp-slam start, please wait a moment ...' )

def set_target_board():

    global x_lidar_position, y_lidar_position, lidar_theta_list, slam, mapbytes, x_mir, y_mir
    joy = xbox.Joystick()
    car = tcnp.init('/dev/ttyUSB1')
    recorded_position = []

    lidar = tcnrplidar.init(port)
    print('lidar OK!')
    slam = RMHC_SLAM(LaserModel(), MAP_SIZE_PIXELS, MAP_SIZE_METERS)
    print('slam ok !!!')
    trajectory = []
    mapbytes = bytearray(MAP_SIZE_PIXELS * MAP_SIZE_PIXELS)
    previous_distances = None
    previous_angles    = None

    try:
        while True:

            forflag = True
            lidarflag = True
            tcnx.xbox_velocity_vision(joy,car)

            x_mir, y_mir,  theta_lidar, lidar_data= rplidar_RMHC_SLAM()
            print('x_position: %.2f   y_position: %.2f'%(x_mir/10, y_mir/10))
            recorded_position.append([0,0])
            x = int(input('enter x'))
            y = int(input('enter y'))
            recorded_position.append([x,y])
            if len(recorded_position) != 0: # If no position was recorded , then pass
                print(recorded_position[0])
                position = recorded_position[1]
                print('Target X : {} Y : {} '.format(position[0],position[1]))
                forflag,lidarflag =  vision_to_target_position(car,joy,position[0],position[1],step=40) # Move to target according to the camera
                time.sleep(1)
                if forflag == False:
                    break
                if lidarflag == False:
                    break
                joy.close()

    except KeyboardInterrupt:
        tcng.relay_off()
        joy.close()
        print( 'tr_b error, please wait a moment ...' )

    except Exception as e:
        tcng.relay_off()
        joy.close()
        print(e)   
        print( 'tr_b error, please wait a moment ...' )

def set_target_ang():

    global x_lidar_position, y_lidar_position, lidar_theta_list, slam, mapbytes, x_mir, y_mir

    car = tcnp.init('/dev/ttyUSB1')
    recorded_position = []

    lidar = tcnrplidar.init(port)
    print('lidar OK!')
    slam = RMHC_SLAM(LaserModel(), MAP_SIZE_PIXELS, MAP_SIZE_METERS)
    print('slam ok !!!')
    trajectory = []
    mapbytes = bytearray(MAP_SIZE_PIXELS * MAP_SIZE_PIXELS)
    previous_distances = None
    previous_angles    = None

    try:
        while True:

            forflag = True
            lidarflag = True

            x = 0
            y = 0
            ang = int(input('enter ang'))                

            print('Thread Starting!!!!!!!!')
            thread = lidar_position()
            thread.setDaemon(True)
            thread.start()

            if ang > 0:
                z = -10
                t = (57.2*ang/360)
                print('GO!!! x:%s y:%s ang:%s'%(x,y,ang))
                car = tcnp.set_target_position(car,x,y,z)
                time.sleep(t)
            elif ang < 0:
                z = 10
                t = (57.2*ang/360)*-1
                print('GO!!! x:%s y:%s ang:%s'%(x,y,ang))
                car = tcnp.set_target_position(car,x,y,z)
                time.sleep(t)
            elif ang == 0:
                print( 'Quit now.' )
                print("")
                thread.stop()
                thread.join()
                print('Thread Stoping!!!!!!!!')
                break

            car[0] = 0
            car[1] = 0
            car[2] = 0
            car = tcnp.move_to_coordinate(car)
            time.sleep(1)

            print('Car move STOP!!!')
            thread.stop()
            thread.join()
            # break

    except KeyboardInterrupt:
        tcng.relay_off()
        thread.stop()
        print( 'tr_a error, please wait a moment ...' )

    except Exception as e:
        tcng.relay_off()
        thread.stop()
        print(e)   
        print( 'tr_a error, please wait a moment ...' )

def help_manual():
    print("al: chekc fp-slam is alive.")
    print("cc: check cpu speed.")
    print("gp: get pose from fp-slam.")
    print("gs: get state from fp-slam.")
    print("qi: quit client program.")
    print("s1: scenario1")
    print("sc1 <standard> <length1> <length2> <length3>  <length4> : to correct initial corridation.")
    print("rs: reset the fp-slam system. before re-start another system mode.")
    print("sd: shutdown the fp-slam system.")
    print("sn <nfs address> : set nfs address")
    print("st <system mode> <map id> <map id> ....<map id>: set fp-slam to start.")
    print("sv: save database.")
    print("cr: control coordinate mode.")
    print("tr: tracking mode")
    print("gpio:test if relay alive")
    print("pr:keep moving at 2 position")
    return

#step = 20 ,turn_step = 2 ,error_range = 3 ,deacc_range = 150
def vision_to_target_position(car,joy,tx,ty,step = 15 ,turn_step = 2 ,error_range = 5 ,deacc_range = 30,msgb = ""):

    runflag = True 
    i = 0
    j = 0
    deacc_limit = step - 2

    t6 = time.clock()

    while runflag:
        x_mir, y_mir,  theta_lidar, lidar_data= rplidar_RMHC_SLAM()
        #print(pose_resp)
        x = x_mir/10
        y = y_mir/10   
        angle = theta_lidar 
        dx = tx - x
        dy = ty - y
        print('x: %.2f\ty: %.2f\t'%(x,y))                      
        vxy = move_to_coordinate_speed(dx,dy,angle,step,error_range,deacc_range)
        # print("v: {} dxdy: {} {}".format(vxy, dx, dy))
        if angle > 0:
            car[2] =  turn_step
        if angle < 0:
            car[2] = - turn_step
        # show_mesflag = True
        # Auto mode
        car[0] = vxy[0]
        car[1] = vxy[1]
        #car[2] = vz
        tcnp.move_to_coordinate(car)
        #time.sleep(0.1)
        if vxy[2] == True:
            t7 = time.clock()
            print('Target reached!!! x: %.2f y: %.2f move_t: %.2f'%(x, y, (t7-t6)))
            # car[0] = 0
            # car[1] = 0
            # car[2] = 0
            # tcnp.move_to_coordinate(car)
            # time.sleep(1)
            break

        if joy.Back():
            print('Cancel Moving')
            print("Back to 'tr' mode ")
            car[0] = 0
            car[1] = 0
            car[2] = 0
            tcnp.move_to_coordinate(car)
            # time.sleep(1)
            return False

# This function adjusts the speed when moving to target .
# Input argument : dx - the delta x to target ( dx = target_x - map_x )
#                  dy - the delta y to target ( dy = target_y - map_y )
#                  step
#                  error_range
#                  deacc_range - when car's position is whinin deacc_range , adjust speed depends on distance
# Output argument : vx,vy - velocity of x,y
def move_to_coordinate_speed(dx,dy,angle,step,error_range,deacc_range):
        

        angle = (math.degrees(math.atan2(dy,dx))%360+angle)%360

        check_reach_target= False

        dis = ( dx**2 + dy**2 )**0.5

        if error_range < abs(dis):
            if abs(dis) < deacc_range:
                vx = step * dis/deacc_range * math.cos(math.radians(angle))
                vy = step * dis/deacc_range * math.sin(math.radians(angle))
                if 0 <= vx < 1 :
                    vx = 1
                elif -1 < vx < 0 :
                    vx = -1
                if 0 <= vy < 1 :
                    vy = 1
                elif -1 < vy < 0 :
                    vy = -1

            else:
                vx = step* math.cos(math.radians(angle))
                vy = step* math.sin(math.radians(angle))
            # vx = step* math.cos(math.radians(angle))
            # vy = step* math.sin(math.radians(angle))

        else:
            vx = step* math.cos(math.radians(angle))
            vy = step* math.sin(math.radians(angle))
            #vx = 0
            #vy = 0
            check_reach_target = True

        # vx = -vx if dx > 0 else vx
        # vy = -vy if dy > 0 else vy
        return vx, vy, check_reach_target

def move_to_coordinate_angle(d_thida,step,modify_angle):
        
        check_reach_target= False
        
        if abs(d_thida) < abs(modify_angle):
            
            vz = -step* d_thida*0.1
            check_reach_target = True
        else:
            
            vz = -step* d_thida*0.1
            
        return vz,check_reach_targetd

def Round(n):       #自定义四舍五入函数
    n=round(n,2)
    xs=(n-math.floor(n))*10
    if (xs>=5):
        new=round(n)+1
    else:
        new=round(n)
 
    return new

def round_up(number,power=0):
    """
    实现精确四舍五入，包含正、负小数多种场景
    :param number: 需要四舍五入的小数
    :param power: 四舍五入位数，支持0-∞
    :return: 返回四舍五入后的结果
    """
    digit = 10 ** power
    num2 = float(int(number * digit))
    # 处理正数，power不为0的情况
    if number>=0 and power !=0:
        tag = number * digit - num2 + 1 / (digit * 10)
        if tag>=0.5:
            return (num2+1)/digit
        else:
            return num2/digit
    # 处理正数，power为0取整的情况
    elif  number>=0 and power==0 :
        tag = number * digit - int(number)
        if tag >= 0.5:
            return (num2 + 1) / digit
        else:
            return num2 / digit
    # 处理负数，power为0取整的情况
    elif power==0 and number<0:
        tag = number * digit - int(number)
        if tag <= -0.5:
            return (num2 - 1) / digit
        else:
            return num2 / digit
    # 处理负数，power不为0的情况
    else:
        tag = number * digit - num2 - 1 / (digit * 10)
        if tag <= -0.5:
            return (num2-1)/digit
        else:
            return num2/digit

def caculatebeta(s,e):  #角度计算，一到四象限
    dy=e[1]-s[1]
    dx=e[0]-s[0]
    if dx==0:
        beta=(math.pi)/2
    else:
        beta=math.atan(dy/dx)
        if(dx<0):
            if(dy>0):
                beta=(math.pi)-abs(beta)
            else:
                beta=(math.pi)+abs(beta)
        else:
            if (dy<0):
                beta=2*(math.pi)-abs(beta)
    return beta
 
def howmany(c1,c2):   #扇区数目
    n=36
    dif=min([abs(c1-c2),abs(c1-c2-n),abs(c1-c2+n)])
    return dif

def expansion_obstacle(data,expansion = 1):
    obstacle_exp = []
    # con = 0

    for n in data:
        # print('expansion_obstacle: %s'%(n))
        # con = con + 1
        n[0] = round(n[0])
        n[1] = round(n[1])
        # print('n[0]: %s n[1]: %s'%(n[0],n[1]))
        r1 = n[0] + expansion #  1 X
        r2 = n[0] - expansion # -1 X
        r3 = n[1] + expansion #  1 Y
        r4 = n[1] - expansion # -1 Y

        obstacle_exp.append([r1,n[1]])
        obstacle_exp.append([r2,n[1]])
        obstacle_exp.append([n[0],r3])
        obstacle_exp.append([n[0],r4])

    # except KeyboardInterrupt:
    #     sys.exit()

    return obstacle_exp

def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")
 
 
def stop_thread(thread):
    _async_raise(thread.ident, SystemExit)

def pathAvoid():

    global x_lidar_position, y_lidar_position, lidar_theta_list, slam, mapbytes, x_mir, y_mir, data, previous_distances, previous_angles
    try:
        joy = xbox.Joystick()
        print('joy')
        # joy.connected()
        # print(joy)
    except IOError as ioe:
        print(ioe)
        print('reconnect to xbox in 1 second')
        time.sleep(1)
        joy = xbox.Joystick()

    car = tcnp.init('/dev/ttyUSB1')
    mainflag = True
    recorded_position = []

    obdata_orign_x = []
    obdata_orign_y = []
    # map_unit = 1           

    # start and goal position
    # sx = 100  # [cm]     # start
    # sy = 1350  # [cm]
    # gx = 175  # [cm]     # goal
    # gy = 38  # [cm]
    # grid_size = 40  # [cm]
    # robot_radius = 40  # [cm]

    print('lidar OK!')
    slam = RMHC_SLAM(LaserModel(), MAP_SIZE_PIXELS, MAP_SIZE_METERS)
    print('slam ok !!!')
    trajectory = []
    mapbytes = bytearray(MAP_SIZE_PIXELS * MAP_SIZE_PIXELS)
    previous_distances = None
    previous_angles    = None

    ######################################## VFH
    obstacle = []

    step=45             #步伐大小
    f=10                 #單一扇區大小,角分辨率
    dmax=110             #激光超声波最大范围 200
    smax=5             #扇区最大个数
    b=2.5               #参数b
    a=b*(dmax)          #参数a 1+b*(dmax**2)
    C=15                #cv值
    alpha=np.deg2rad(f) #換算成弧度 ****
    # alpha=5
    n=360/f             #划分扇区,72個
    threshold=1300      #
    rsafe=40             #擴大半徑 r(r+s)
    kb=90/f             #最優方向
     
    ffff=np.zeros(37)

    ##########################################
    # plt.ion()
    # plt.figure()
    # plt.title("VFH path planning")
    # plt.grid(True)
    # figure = plt.plot()
    print('Please locate 2 position')
    while mainflag:
        try:
            pathflag = True
            lidarflag = True

            tcnx.xbox_velocity_vision(joy,car)
            x_mir, y_mir,  theta_lidar, lidar_data = rplidar_RMHC_SLAM()
            print('x_position: %.2f   y_position: %.2f   angle:%.2f'%(x_mir/10, y_mir/10, theta_lidar))
            # print(len(data))

            if  len(data) > 1:
                    # power = mea[0]
                deg = lidar_data[:, 0]   # 度
                dis = lidar_data[:, 1]   # mm
                # print(dis[0])

            # obstacle = [[x_mir + j*math.cos(math.radians(450 - i)), x_mir + j*math.sin(math.radians(450 - i))] for i, j in zip(deg, dis) if j >= 275 and j <= 1400]
                    # obdata_orign_y.append(y1/10)
                obstacle = [[dis[i]*np.cos(deg[j]), dis[i]*np.sin(deg[j])] for i, j in zip(range(len(dis)), range(len(deg)))]
                # print(deg)
                # figure.clear()
                # figure.plot(obstacle)
                # plt.pause(0.001)
                # print(lidar_data)
                # print(obstacle)
            # The behavier when push button 'x'
            if joy.X():
                print('Add new way point')
                car[0] = 0 # Make car stop
                car[1] = 0
                car[2] = 0
                tcnp.move_to_coordinate(car)                
                time.sleep(0.5)
                recorded_position.append([round(x_mir/10),round(y_mir/10)]) # Remove the last element of recorded_position
                print(recorded_position)
                time.sleep(0.1)
                
            # The behavier when push button 'y'
            if joy.Y():
                print('Delet last generated way point')
                car[0] = 0 # Make car stop
                car[1] = 0
                car[2] = 0
                tcnp.move_to_coordinate(car)
                time.sleep(0.5)
                recorded_position.pop(len(recorded_position) - 1) # Remove the last element of recorded_position
                print(recorded_position)
                time.sleep(0.1)

            if joy.Start():
                
                print('Going to start point !!!')
                # print(recorded_position)
                # obstacle_exp = obstacle
                # obstacle_exp = expansion_obstacle(obstacle,22)
                obstacle_exp = np.asarray(obstacle)
                # print(obdata_orign_x)
                # print(obdata_orign_y)

                while pathflag:

                    if recorded_position == []:
                        car[0] = 0 # Make car stop
                        car[1] = 0
                        car[2] = 0
                        tcnp.move_to_coordinate(car)
                        print('No goal !!! please add point!!!')
                        print('Back to setting mode')
                        time.sleep(2)
                        pathflag = False

                    elif recorded_position != []:
                        circle = len(recorded_position)
                        for i in range(circle-1):
                            start_position = [int(j) for j in recorded_position[i+1]]
                            goal_position = [int(j) for j in recorded_position[i]]
                            # obdata_orign_x2 = [int(k) for k in obdata_orign_x]
                            # obdata_orign_y2 = [int(k) for k in obdata_orign_y]
                            robot = start_position
                            robottotal = [robot]
                            kt=round_up(caculatebeta(robot,goal_position)/alpha)   #定義目標方向
                            if(kt==0):
                                kt = n
                            print('start_position :  %s\t %s'%(start_position[0],start_position[1]))
                            print('goal_position  :  %s\t %s'%(goal_position[0],goal_position[1]))
                            t0=time.time()
                            thread = None

                            while True:          #機器人不到終點
                                if (np.linalg.norm(np.array(robot)-np.array(goal_position),2)>step*0.8):     #機器人位置與終點位置差距大於step
                                    i=0                                                               #初值
                                    mag=np.zeros(int(n+2))
                                    his=np.zeros(int(n+2))
                                    print('\033[0;32;40mVFH star\033[0m !!!')
                                    print('RobotX: %.2f RobotY:%.2f'%(robot[0],robot[1]))

                                    t1=time.time()

                                    while(i<len(obstacle_exp)):
                                        d=np.linalg.norm(obstacle_exp[i,:]-robot)                         #障礙物柵格與機器人之間距離
                                        if((d<dmax) and (d>rsafe) ):
                                            beta = caculatebeta(robot,obstacle_exp[i,:])                    #障礙物柵格向量的方向
                                            rangle = math.asin(rsafe/d)                                          #擴大角度, rij
                                            k = int(round_up(beta/alpha))                                      #逆時針數,第K個扇區區域
                                            if(k==0):
                                                k=int(n)
                                            h = np.zeros(int(n+2))

                                            if((f*(k) > (np.rad2deg(beta) - np.rad2deg(rangle))) and (f*(k) < (np.rad2deg(beta) + np.rad2deg(rangle)))):  # kf 屬於[beta-rangle,beta+rangle] 之間
                                                h[int(k)] = 1
                                            else:
                                                h[int(k)] = 0
                    
                                            m = (C**2)*(a - b * d)                                             #障礙物柵格的幅度值(向量值) (a-b*(d**2))
                                            mag[k] = max(mag[k], m * h[k])                                    #mag為zero(n),mag的第k個算為m
                                            i = i + 1
                                        else:
                                            i = i + 1
                                    his = mag                                                              #his是一個含72元素的向量
                                    # print('his: %s'%(his))

                                    j = 1
                                    q = 1
                                    c = np.zeros(int(n + 2))

                                    while(q <= n):
                                        if(his[q] < threshold):
                                            kr = q                                                      #找到了波谷的左端
                                            while ((q <= n) and (his[q] < threshold)):                    #這一小段找到了波谷的右端
                                                kl = q
                                                q = q + 1
                                            if (kl-kr>smax):                                          #寬波谷
                                                print('kl : %s\tkr : %s\tkt : %s\t'%(kl,kr,(kl+kr)/2))
                                                # c[j]=Round(kl-smax/2)                                 #朝向左側, cl
                                                # c[j+1]=Round(kr+smax/2)                               #朝向右側, cr
                                                c[j]=(kr+kl)/2
                                                j=j+1

                             
                                            elif (smax>=kl-kr>=1):     # smax/5                           #窄波谷
                                                print('kl : %s\tkr : %s\tkt : %s\t'%(kl,kr,(kl+kr)/2))
                                                c[j]=(kr+kl)/2
                                                # print('c:%s'%(c[j]))
                                                j=j+1
                                        else:
                                            q=q+1                                                     #his(q)不為0,直接下一個
                                    g=np.zeros(j)
                                    how=[]
                                    for i in range(1,j):
                                        g[i]=c[i]                                                          # g中不含目標向量
                                        howtemp=5*howmany(g[i],kt)+2*howmany(g[i],kb)+2*howmany(g[i],kb)   # how為差距向量   g(c) = u1*d(c,kt) + u2*d(c,theta/alpha) + u3*d(c,kni-1) , u1=5, u2=u3=2, u1>u2+u3
                                        how.append(howtemp)
                                        print('h:%.2f u1:%.2f u2:%.2f u3:%.2f'%(howtemp,5*howmany(g[i],kt),2*howmany(g[i],kb),2*howmany(g[i],kb)))
                             
                                    ft=how.index(min(how))
                                    print('g:%s'%(g))
                                    print('how:%s'%(how))
                                    fk=ft+1
                                    kb=g[int(fk)]                                                      #前進向量
                             
                                    robot[0]=robot[0]+step*(math.cos(kb*alpha))
                                    robot[1]=robot[1]+step*(math.sin(kb*alpha))
                                    robottotal.append(robot)

                                    t2=time.time()

                                    print('kb : %.2f  \tkb*alpha : \033[0;36;40m%.2f\033[0m'%(kb,kb*alpha/6.28*360))
                                    print('tarX: %.2f \ttarY: %.2f tarD: %.2f VFH_T: %.2f'%(robot[0],robot[1],np.linalg.norm(np.array(robot)-np.array(goal_position),2),(t2-t1)))
                                    # forflag =  vision_to_target_position(car,joy,robot[0],robot[1]) # Move to target according to the camera
                                    if thread is not None:
                                        print('Thread \033[0;33;40mWaiting\033[0m !!!!!')
                                        # stop_thread(thread)
                                        thread.join()
                                        thread = None
                                        print(thread)
                                    thread = threading.Thread(target=vision_to_target_position, args=[car, joy, robot[0], robot[1]])
                                    print('Thread Starting!!!!!!!!')
                                    thread.setDaemon(True)
                                    thread.start()
                                    # time.sleep(1)
                             
                                    kt=(caculatebeta(robot,goal_position)/alpha)
                                    if(kt==0):
                                        kt=n
                                    time.sleep(4)
                                else:
                                    if thread is not None:
                                        print('Thread Waiting !!!!!')
                                        thread.join()
                                        thread = None
                                    thread = threading.Thread(target=vision_to_target_position, args=[car, joy, goal_position[0], goal_position[1]])
                                    print('Thread Starting!!!!!!!! @@@@@@@@@@@@@@@@@@@@@@@')
                                    thread.setDaemon(True)
                                    thread.start()
                                    thread.join()
                                    mainflag = False
                                    car[0] = 0 # Make car stop
                                    car[1] = 0
                                    car[2] = 0
                                    tcnp.move_to_coordinate(car)
                                    t3=time.time()
                                    print('Reach endpoint !!! T: %.3f @@@@@@@@@@@@@@@@@'%(t3-t0))
                                    recorded_position = []
                                    obstacle = []
                                    # stop_thread(thread)
                                    break  

                            # robottotal=np.asarray(robottotal)
                            else:
                                t3=time.time()
                                stop_thread(thread)
                                car[0] = 0 # Make car stop
                                car[1] = 0
                                car[2] = 0
                                tcnp.move_to_coordinate(car)
                                print('Reach endpoint !!! total_T: %.3f'%(t3-t0))
                                time.sleep(5)
                                recorded_position = []
                                obstacle = []
                                mainflag = False
                                break

                            if joy.Back():
                                mainflag = False
                                car[0] = 0 # Make car stop
                                car[1] = 0
                                car[2] = 0
                                tcnp.move_to_coordinate(car)
                                print('Back to command mode')
                                recorded_position = []
                                obstacle = []


                        if joy.Back():
                                mainflag = False
                                car[0] = 0 # Make car stop
                                car[1] = 0
                                car[2] = 0
                                tcnp.move_to_coordinate(car)
                                print('Back to command mode')
                                recorded_position = []
                                obstacle = []

                        recorded_position = []
                        obstacle = []

                    if joy.Back():
                        joy.close()
                        mainflag = False
                        car[0] = 0 # Make car stop
                        car[1] = 0
                        car[2] = 0
                        tcnp.move_to_coordinate(car)
                        print('Back tooa command mode')
                        recorded_position = []
                        obstacle = []

            if joy.Back():
                mainflag = False
                print('Back to command mode')
                tcng.relay_off()
                joy.close()

        except KeyboardInterrupt:
            mainflag = False
            tcng.relay_off()
            print( 'Reset rp-slam start, please wait a moment ...' )
            joy.close()
            break  

        except Exception as e:
            traceback.print_exc()
            mainflag = False
            print(e)   
            tcng.relay_off()
            print( 'Obstacle Aviod error !!! Closing Joystick' )
            joy.close()

if __name__ == "__main__":
    sys.exit(main())
