import xbox
import TCN_socket
import time



class xbox_controller():
    
    def __init__(self):
        try:
            self.joy = xbox.Joystick()
        except IOError:
            print('Xbox connect error, auto retry again.')
            self.__init__()
        except Exception as e:
            print(e)
        
        self.xbox_client = TCN_socket.UDP_client(50002)


def xbox_main():
    
    try:
        joy = xbox.Joystick()
    except IOError:
        print('Xbox connect error, auto retry again.')
        xbox_main()
    except Exception as e:
        print(e)

    
    xbox_client = TCN_socket.UDP_client(50002)
    step = 0 # Step represent the speed 

    while not joy.Back(): # When key "back" is pushed, Back() return True.
        try:
            # Key A means accelerate
            if int(joy.A()) and step <= 131:
                step = step + 1
                print(step)
            # Key B means deaccelerate
            if int(joy.B()) and step > 0:
                step = step - 1
                print(step)
            
            x = int(step*round(joy.leftX(),2)) 
            y = int(step*round(joy.leftY(),2))
            z = int(step*round(joy.rightX(),2)) 
            print([x,y,z],step)
            xbox_client.send_list([x,y,z])
            time.sleep(0.006)
        except Exception as e:
            xbox_client.close()
            joy.close()
            print(e)


if __name__ == "__main__":
    xbox_main()    
