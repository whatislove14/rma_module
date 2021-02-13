from trik_var import brick, script


class Robot:
    '''
    Позволяет создать объект Robot
    Основные методы:
        start - стартовая функция (калибровка+сброс)
        turn_l, turn_r, front - функции движения
        check_left, check_right, check_back, check_front - проверка преград
        rovn - выравнивание по стенкам
        just_left_hand - движение по левой руке (с возможными модификациями)
        check_preg - полная проверка преград + операции с ними
        go_commands - езда по заданным командам
        unknow_localize - алгоритм движения для локализации

    Основные параметры:
        ml, mr - моторы (дефолт-M3, M4)
        encl, encr - энкодеры (дефолт-E3, E4)
        sens_left, sens_right, sens_back, sens_front - сенсоры
        gyro - гироскоп (дефолт-задан)
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
        '''
        start - стартовая функция
        производится калибровка гироскопа+сброс энкодеров
        Параметр time_calib - время калибровки в мс (дефолт-1000)
        '''
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
        '''
        Функция движения вперед
        Параметр enc - кол-во энкодеров, на которое соверш. движение
        '''
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
        '''
        Функция движения по левой руке с модификациями
        jlh - стандарт
        sal (stop after left) - прекращение движения после каждой команды\
            если какая-то команда не доделана, то она возвращается в качестве\
            текста
        '''
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

    def check_preg(self, maze=None, ret="maze+clear"):
        '''
        check_preg - полная проверка преград + операции с ними
        Параметр ret - влияет на результат работы:
            maze - изменяет заданный лабиринт
            clear - возвращает список свободных направлений
            maze+clear - оба действия
        '''
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
