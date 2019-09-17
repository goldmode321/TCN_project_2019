
import matplotlib.pyplot as plt
import time

class LVMap:
    def __init__(self):
        self.SHOW_ANIMATION = True
        self.lidar_data = []
        self.vision_coord = []
        self.robot_x = 0
        self.robot_y = 0
        self.robot_coord = [0, 0]
        self.end_X = 50
        self.end_y = 50
        self.start_coord = [0, 0]
        self.target_coord = [50, 50]
        self.global_obstacle = [[i, 10] for i in range(10, 31)] + [[i, 25] for i in range(0, 15)] \
            + [[i, 50] for i in range(15, 35)] + [[25, j] for j in range(20, 40)] + [[45, j] for j in range(35, 60)]
        self.global_obstacle_x = [i[0] for i in self.global_obstacle]
        self.global_obstacle_y = [i[1] for i in self.global_obstacle]

        self.local_obstacle = []
        self.local_obstacle_x = []
        self.local_obstacle_y = []
        self.local_obstacle_range = 10

        plt.xlim(self.start_coord[0] - 10, self.target_coord[0] + 10)
        plt.ylim(self.start_coord[1] - 10, self.target_coord[1] + 10)
        plt.scatter(self.global_obstacle_x, self.global_obstacle_y, c='b')
        plt.pause(0.0001)
        self.main()


    def lidar(self):
        self.local_obstacle = [[i, j] for i in range(self.robot_x - self.local_obstacle_range, self.robot_x + self.local_obstacle_range) \
            for j in range(self.robot_y - self.local_obstacle_range, self.robot_y + self.local_obstacle_range) if [i,j] in self.global_obstacle]
        self.local_obstacle_x = [i[0] for i in self.local_obstacle]
        self.local_obstacle_y = [i[1] for i in self.local_obstacle]
        plt.scatter(self.local_obstacle_x, self.local_obstacle_y, c='r', zorder=10)


    def main(self):
        run = True
        while run:
            try:
                command = input('Enter wasd : ')
                if command == 'd':
                    self.robot_x += 1
                elif command == 'a':
                    self.robot_x -= 1
                elif command == 's':
                    self.robot_y -= 1
                elif command == 'w':
                    self.robot_y += 1
                plt.cla()
                plt.scatter(self.robot_x, self.robot_y, c='g', zorder = 5)
                self.lidar()
                plt.xlim(self.start_coord[0] - 10, self.target_coord[0] + 10)
                plt.ylim(self.start_coord[1] - 10, self.target_coord[1] + 10)
                plt.scatter(self.global_obstacle_x, self.global_obstacle_y, c='b', zorder=0)
                plt.pause(0.00001)
            except KeyboardInterrupt:
                run = False



if __name__ == '__main__':
    LVMap()