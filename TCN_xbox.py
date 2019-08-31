import xbox
import time
import traceback



class Xbox_controller(object):
    
    def __init__(self):
        try:
            self.step = 0
            self.joy = xbox.Joystick()
        except IOError:
            print('Xbox connect error, auto retry again ; Please move joystick or press any button')
            self.__init__()
        except:
            traceback.print_exc()
        
    def xbox_control(self):

        # Key A means accelerate
        if int(self.joy.A()) and self.step <= 131:
            self.step = self.step + 1
            print(self.step)
            time.sleep(0.05)
        # Key B means deaccelerate
        if int(self.joy.B()) and self.step > 0:
            self.step = self.step - 1
            print(self.step)
            time.sleep(0.05)
        
        x = int(self.step*round(self.joy.leftX(),2)) 
        y = int(self.step*round(self.joy.leftY(),2))
        z = int(self.step*round(self.joy.rightX(),2))
        
        return [x,y,z]

    def close(self):
        self.joy.close()

    def xbox_test(self):
        while not self.joy.Back(): # When key "back" is pushed, Back() return True.
            try:
                # Key A means accelerate
                if int(self.joy.A()) and self.step <= 131:
                    self.step = self.step + 1
                    print(self.step)
                    time.sleep(0.05)
                # Key B means deaccelerate
                if int(self.joy.B()) and self.step > 0:
                    self.step = self.step - 1
                    print(self.step)
                    time.sleep(0.05)
                
                x = int(self.step*round(self.joy.leftX(),2)) 
                y = int(self.step*round(self.joy.leftY(),2))
                z = int(self.step*round(self.joy.rightX(),2)) 
                print([x,y,z],self.step)
                time.sleep(0.006)
            except:
                self.joy.close()
                traceback.print_exc()



'''
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
'''

if __name__ == "__main__":
    pass
    # xbox_main()    
