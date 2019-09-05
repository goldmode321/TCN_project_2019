'''
 Require library from https://github.com/FRC4564/Xbox
 to run this module.
 Use "sudo apt-get install xboxdrv" to intall module.
'''
import time
import traceback
import xbox



class XboxController():

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
        '''which return left stick position and right stick x-direction position'''
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

        return [x, y, z, self.step]

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
                print([x, y, z], self.step)
                time.sleep(0.006)
            except:
                self.joy.close()
                traceback.print_exc()


if __name__ == "__main__":
    x = XboxController()
    x.xbox_test()
    # xbox_main()    
