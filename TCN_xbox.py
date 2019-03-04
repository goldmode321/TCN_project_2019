import xbox
import TCN_socket
import time


def xbox_main():
    xbox_client = TCN_socket.UDP_client()
    try:
        joy = xbox.Joystick()
    except Exception as e:
        joy = xbox.Joystick()
        print(e)

    step = 0

    while not joy.Back():
        try:

            if int(joy.A()) and step <= 131:
                step = step + 1
                print(step)
            if int(joy.B()) and step > 0:
                step = step - 1
                print(step)
            x = int(step*round(joy.leftX(),2)) 
            y = int(step*round(joy.leftY(),2))
            z = int(step*round(joy.rightX(),2)) 
            print([x,y,z],step)
            xbox_client.send_list([x,y,z])
            time.sleep(0.1)
        except Exception as e:
            xbox_client.close()
            joy.close()
            print(e)


if __name__ == "__main__":
    xbox_main()    
