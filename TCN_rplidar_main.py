import TCN_rplidar
import time
import traceback
import logging
import TCN_socket
import threading

lidar = None 
lidar_client = None
lidar_run_flag = False
logging.basicConfig(filename='LiDAR_main.log',filemode = 'w',level =logging.INFO)
lidar_data = []


def init():
    global lidar_client, lidar , lidar_run_flag 
    try:
        logging.info("Initializing Lidar_client")
        lidar_client = TCN_socket.TCP_client(50002)
        logging.info("Initializing RPLidar")
        lidar = TCN_rplidar.Lidar()
        lidar_status = lidar.get_status()
        logging.info("lidar initialize successuflly")
        lidar_client.send_list(['L','status',str(lidar_status[0])])
        lidar_run_flag = True

    except:
        traceback.print_exc()
        logging.exception("Got error\n")
        lidar_client.close()

def main():
    global lidar_run_flag
    while lidar_run_flag:
        try:
            lidar_receive = lidar_client.recv_list()
            logging.info("lidar received : {} ".format(lidar_receive))
            lidar_protocol(lidar_receive)

        except:
            traceback.print_exc()
            logging.exception('Got error : ')
            lidar_run_flag = False

def end():
    lidar_client.close()
    lidar.stop()
    logging.info('Lidar closed successfully')


def lidar_protocol(lidar_receive):
    global lidar_run_flag , lidar_data
    try:
        if lidar_receive[0] == 'L':
            if lidar_receive[1] == 'exit':
                lidar_run_flag = False
                
            if lidar_receive[1] == 'gld':
                logging.debug("lidar data {}".format(lidar_data))
                if lidar_data != None:
                    lidar_client.send_list(['L','gld',lidar_data])
                    
                else:
                    lidar_client.send_list(['L','gld',"No lidar data"])

        else:
            logging.warning("Wrong portocol to Lidar communication , please check lidar_portocol or bridge protocol")
    except:
        logging.exception("lidar_protocol Got error : ")



def lidar_run_background():
    global lidar_data , lidar
    def get_lidar_data():
        global lidar_data , lidar
        lidar_object = lidar.get_lidar_object()
        try:
            logging.info('lidar run in background')
            for i in lidar_object.iter_scans():
                lidar_data = i 
        except:
            
            lidar.reconnect()
            get_lidar_data()
    
    thread = threading.Thread(target = get_lidar_data)
    thread.daemon = True
    thread.start()
    # logging.info('lidar run in background')


# def lidar_run(exit=0):
#     global lidar

#     try:
#         if exit != 0:
#             lidar.get_lidar_data()
#         else:
#             raise KeyboardInterrupt

#     except:
#         if exit !=0:
#             lidar.stop()
#             lidar.reconnect()
#             lidar_run()

def get_data():
    global lidar_data
    return lidar_data

if __name__ == "__main__":
    init()
    lidar_run_background()
    main()
    end()    

