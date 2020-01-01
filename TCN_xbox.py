'''
 Require library from https://github.com/FRC4564/Xbox
 to run this module.
 Use "sudo apt-get install xboxdrv" to intall module.
'''
import time
import traceback
import threading
import xbox

class XboxController():

    def __init__(self, SharedVariable_Xbox):
        self.XBOX = SharedVariable_Xbox

    def init(self):
        try:
            self.XBOX.max_speed = 0
            self.joy = xbox.Joystick()
            self.XBOX.xbox_on = True
            self.xbox_thread = None
        except IOError:
            print('Xbox connect error, auto retry again ; Please move joystick or press any button')
            self.init()
        except:
            traceback.print_exc()

    def start(self):
        self.xbox_thread = XboxController_Thread(self.joy, self.XBOX)

    def stop(self):
        self.XBOX.xbox_thread_on = False

    def end(self):
        self.XBOX.xbox_thread_on = False
        if self.xbox_thread is not None:
            self.xbox_thread.join()
        self.joy.close()
        self.XBOX.xbox_on = False






class XboxController_Thread(threading.Thread):
    def __init__(self, joy, SharedVariable_Xbox, daemon=True):
        super().__init__(daemon)
        self.joy = joy
        self.XBOX = SharedVariable_Xbox

    def run(self):
        self.XBOX.xbox_thread_on = True
        while self.XBOX.xbox_on and self.XBOX.xbox_thread_on and not self.joy.Back():
            self.xbox_control()
            time.sleep(0.025)
        self.XBOX.xbox_thread_on = False

    def xbox_control(self):
        '''which return left stick position and right stick x-direction position'''
        # Key A means accelerate
        if int(self.joy.A()) and self.XBOX.max_speed <= 131:
            self.XBOX.max_speed = self.XBOX.max_speed + 1
            print(self.XBOX.max_speed)
            time.sleep(0.05)
        # Key B means deaccelerate
        if int(self.joy.B()) and self.XBOX.max_speed > 0:
            self.XBOX.max_speed = self.XBOX.max_speed - 1
            print(self.XBOX.max_speed)
            time.sleep(0.05)

        x = int(self.XBOX.max_speed*round(self.joy.leftX(),2)) 
        y = int(self.XBOX.max_speed*round(self.joy.leftY(),2))
        z = int(self.XBOX.max_speed*round(self.joy.rightX(),2))

        return [x, y, z, self.XBOX.max_speed]

    # def xbox_test(self):
    #     while not self.joy.Back(): # When key "back" is pushed, Back() return True.
    #         try:
    #             # Key A means accelerate
    #             if int(self.joy.A()) and self.XBOX.max_speed <= 131:
    #                 self.XBOX.max_speed = self.XBOX.max_speed + 1
    #                 print(self.XBOX.max_speed)
    #                 time.sleep(0.05)
    #             # Key B means deaccelerate
    #             if int(self.joy.B()) and self.XBOX.max_speed > 0:
    #                 self.XBOX.max_speed = self.XBOX.max_speed - 1
    #                 print(self.XBOX.max_speed)
    #                 time.sleep(0.05)

    #             x = int(self.XBOX.max_speed*round(self.joy.leftX(),2)) 
    #             y = int(self.XBOX.max_speed*round(self.joy.leftY(),2))
    #             z = int(self.XBOX.max_speed*round(self.joy.rightX(),2)) 
    #             print([x, y, z], self.XBOX.max_speed)
    #             time.sleep(0.006)
    #         except:
    #             self.joy.close()
    #             traceback.print_exc()


# if __name__ == "__main__":
#     x = XboxController()
#     x.xbox_test()
    # xbox_main()    
