# БИБЛИОТЕКА
import maze_module


class Robot:
    '''
    Позволяет создать объект Robot, хранящий в себе скрипты, необходимые для передвижения робота
    Имеет основные свойства ml, mr, encl, encr (левые и правые моторы/энкодеры соотв) итд
    '''

    def __init__(self, ml="M3", mr="M4", encl="E3", encr="E4", sens_left='',
                 sens_right='', sens_front='', sens_back=''):

        self.ml = brick.motor(ml).setPower
        self.mr = brick.motor(mr).setPower
        self.encl = brick.encoder(encl)
        self.encr = brick.encoder(encr)
        if sens_left: self.sens_left = brick.sensor(sens_left)
        if sens_right: self.sens_right = brick.sensor(sens_right)
        if sens_front: self.sens_front = brick.sensor(sens_front)
        if sens_back: self.sens_back = brick.sensor(sens_back)
        self.gyro = brick.gyroscope()

    def start(self, time_calib=1000):
        self.gyro.calibrate(time_calib)
        script.wait(time_calib)
        self.encl.reset()
        self.encr.reset()
        return self.gyro.getCalibrationValues()

    def turn_l(self):
        abs_angl = (360000 + self.gyro.read()[6]) % 360000
        err = -90000 + ((360000 + self.gyro.read()[6]) % 360000 - abs_angl)
        while abs(err) > 100:
            err = -90000 + (abs_angl - (360000 + self.gyro.read()[6]) % 360000)
            if err < -270000:
                err = -90000 + ((360000 + abs_angl) - (360000 + self.gyro.read()[6]) % 360000)
            elif err > 270000:
                err = -90000 + (abs_angl - (360000 + ((360000 + self.gyro.read()[6]) % 360000)))
            move = err * 0.0005
            self.ml(-move)
            self.mr(move)
            script.wait(1)
        self.ml(0)
        self.mr(0)
        script.wait(1000)

    def turn_r(self):
        abs_angl = (360000 + self.gyro.read()[6]) % 360000
        err = (((360000 + self.gyro.read()[6]) % 360000 - abs_angl) - 90000)
        while abs(err) > 100:
            err = (((360000 + self.gyro.read()[6]) % 360000 - abs_angl) - 90000)
            if err < -270000:
                err = (((((360000 + self.gyro.read()[6]) % 360000) + 360000) - abs_angl) - 90000)
            elif err > 270000:
                err = ((((360000 + self.gyro.read()[6]) % 360000) - (360000 + abs_angl)) - 90000)
            move = err * 0.0005
            self.ml(move)
            self.mr(-move)
            script.wait(1)
        self.ml(0)
        self.mr(0)
        script.wait(1000)

    def front(self, enc):
        abs_angl = (360000 + self.gyro.read()[6]) % 360000
        now_angl = abs_angl
        s = 0
        err0 = (now_angl - abs_angl)
        self.encl.reset()
        self.encr.reset()
        while self.encl.read() < enc:
            err = (now_angl - abs_angl)
            if err > 270000:
                abs_angl += 360000
                err = (now_angl - abs_angl)
            elif err < -270000:
                now_angl += 360000
                err = (now_angl - abs_angl)
            p = err * 0.004
            i = s * 0.000
            d = (err - err0) * 0.008
            move = p + d
            self.ml(40 + move)
            self.mr(40 - move)
            s += err
            s *= 0.8
            err0 = err
            script.wait(10)
            now_angl = (360000 + self.gyro.read()[6]) % 360000

    def check_left(self, clear_left=35):
        if self.sens_left.read() > clear_left:
            return True
        return False

    def check_right(self, clear_right=35):
        if self.sens_right.read() > clear_right:
            return True
        return False

    def check_front(self, clear_front=35):
        if self.sens_front.read() > clear_front:
            return True
        return False

    def check_back(self, clear_back=35):
        if self.sens_back.read() > clear_back:
            return True
        return False

    def rovn(self, clear_front=20, clear_back=30):
        if self.sens_front.read() < clear_front + 10:
            while abs(self.sens_front.read() - clear_front) > 1:
                err = (self.sens_front.read() - clear_front) * 2
                self.ml(err)
                self.mr(err)
                script.wait(1)

        if self.sens_back.read() < clear_back + 10:
            while abs(self.sens_back.read() - clear_back) > 1:
                err = (self.sens_back.read() - clear_back) * 2
                self.ml(-err)
                self.mr(-err)
                script.wait(1)

    def just_left_hand(self, go_enc, mode="jlh"):
        if self.check_left():
            self.turn_l()
            self.rovn()
            if mode == "sal":
                return ["F"]
            self.front(go_enc)
            self.rovn()
        elif self.check_front():
            self.front(go_enc)
            self.rovn()
        else:
            self.turn_r()
            self.rovn()
        return []

    def check_preg(self, maze, ret="maze+clear"):
        decode_direct = [[(-1, 0), (0, -1), (1, 0), (0, 1)],
                         [(0, 1), (-1, 0), (0, -1), (1, 0)],
                         [(1, 0), (0, 1), (-1, 0), (0, -1)],
                         [(0, -1), (1, 0), (0, 1), (-1, 0)]]

        clear = ["u", "l", "d", "r"]
        if not self.check_front():
            clear.remove("u")
            if ret != "clear":
              if (maze.now_y + decode_direct[maze.now_direct][0][0],
                  maze.now_x + decode_direct[maze.now_direct][0][1]) not in maze.preg:
                  maze.preg.append((maze.now_y + decode_direct[maze.now_direct][0][0],
                                  maze.now_x + decode_direct[maze.now_direct][0][1]))
        if not self.check_left():
            clear.remove("l")
            if ret != "clear":
              if (maze.now_y + decode_direct[maze.now_direct][1][0],
                  maze.now_x + decode_direct[maze.now_direct][1][1]) not in maze.preg:
                  maze.preg.append((maze.now_y + decode_direct[maze.now_direct][1][0],
                                  maze.now_x + decode_direct[maze.now_direct][1][1]))
        if not self.check_back():
            clear.remove("d")
            if ret != "clear":
              if (maze.now_y + decode_direct[maze.now_direct][2][0],
                  maze.now_x + decode_direct[maze.now_direct][2][1]) not in maze.preg:
                  maze.preg.append((maze.now_y + decode_direct[maze.now_direct][2][0],
                                  maze.now_x + decode_direct[maze.now_direct][2][1]))
        if not self.check_right():
            clear.remove("r")
            if ret != "clear":
              if (maze.now_y + decode_direct[maze.now_direct][3][0],
                  maze.now_x + decode_direct[maze.now_direct][3][1]) not in maze.preg:
                  maze.preg.append((maze.now_y + decode_direct[maze.now_direct][3][0],
                                  maze.now_x + decode_direct[maze.now_direct][3][1]))

        if ret != "maze":
            return "".join(clear)

    def go_commands(self, commands, go_enc, clear_front=20, clear_back=30):
        for command in commands:
            if command == "F":
                self.front(go_enc)
                self.rovn(clear_front, clear_back)
            elif command == "R":
                self.turn_r()
                self.rovn(clear_front, clear_back)
            elif command == "L":
                self.turn_l()
                self.rovn(clear_front=20, clear_back=30)

    def unknow_localize(self, maze, go_enc):
        while True:
            self.check_preg(maze)
            if maze.search_way((maze.now_y, maze.now_x, maze.now_direct),
                               ((maze.local_size) - 1, (maze.local_size) - 1), "direct", size=maze.local_size):
                com = maze.search_way((maze.now_y, maze.now_x, maze.now_direct),
                                      ((maze.local_size) - 1, (maze.local_size) - 1), "direct", size=maze.local_size)
                self.go_commands([com[0]], go_enc)
                maze.now_y, maze.now_x, maze.now_direct = maze.search_way((maze.now_y, maze.now_x, maze.now_direct), (
                    (maze.local_size) - 1, (maze.local_size) - 1), size=maze.local_size)[1]
                if maze.now_y > maze.max_y: maze.max_y = maze.now_y
                if maze.now_y < maze.min_y: maze.min_y = maze.now_y
                if maze.now_x > maze.max_x: maze.max_x = maze.now_x
                if maze.now_x < maze.min_x: maze.min_x = maze.now_x
                if maze.max_x - maze.min_x == maze.size - 1 and maze.max_y - maze.min_y == maze.size - 1:
                    break
            else:
                maze.min_x = maze.max_x - maze.size
                maze.min_y = maze.max_y - maze.size
                break


# КОД ПРОГРАММЫ

mapp = [["r", "ld", "n", "n", "d", "n"],
        ["n", "udr", "ldr", "ldr", "uldr", "l"],
        ["r", "uldr", "uldr", "uldr", "uld", "n"],
        ["n", "udr", "uldr", "uldr", "uldr", "ld"],
        ["dr", "ulr", "uldr", "ulr", "uldr", "uld"],
        ["u", "n", "u", "n", "ur", "ul"]]
robot = Robot(ml="M3", mr="M4", encl="E3", encr="E4", sens_left="A1", sens_right="A2", sens_back="D2", sens_front="D1")
maze = maze_module.Know_maze(mapp)

robot.start()
mb_sectors = []
n = []
while True:
    n = robot.just_left_hand(990, "sal")
    sit = robot.check_preg(maze, "clear")
    mb_sectors = maze.localise(sit, mb_sectors)
    print(mb_sectors)
    if len(mb_sectors) == 1:
      print("-----------")
      print(mb_sectors)
      break
    robot.go_commands(n, 990)
    sit = robot.check_preg(maze, "clear")
    mb_sectors = maze.localise(sit, mb_sectors)
    print(mb_sectors)
    if len(mb_sectors) == 1:
      print("-----------")
      print(mb_sectors)
      break
    
