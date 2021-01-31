class Non_localize_error(EOFError):
    pass


class Maze:
    def neib(self, now, size):
        y, x = now
        now_neib = []
        if y-1 >= 0:
            now_neib.append((y-1, x))
        elif x+1 < size:
            now_neib.append((y, x+1))
        elif y+1 < size:
            now_neib.append((y+1, x))
        elif x-1 >= 0:
            now_neib.append((y, x-1))
        return now_neib

    def change_position(self, now_position):
        self.now_y, self.now_x, self.now_direct = now_position


class Unknow_maze(Maze):
    def __init__(self, size, now_direct=0, preg=list()):
        self.size = size
        self.local_size = size*2 + 1
        self.preg = preg
        self.now_direct = now_direct
        self.min_x = self.local_size//2-1
        self.max_x = self.local_size//2-1
        self.min_y = self.local_size//2-1
        self.max_y = self.local_size//2-1
        self.now_x = self.min_x
        self.now_y = self.min_y
        self.is_localised = False

    def search_way(self, start, finish, ret="way", size=False):
        if not size: size=self.size
        all_maze = {}
        y_start, x_start, d_start = start
        y_finish, x_finish = finish
        if y_start == y_finish and x_start == x_finish:
            return False
        x = x_start
        y = y_start
        fl = 0
        block = self.preg
        n = size
        d = d_start
        q = [(y_start, x_start, d_start)]
        all_maze[(y_start, x_start, d_start)] = 0
        for maze in q:
            now_neib = []
            y, x, d = maze
            now_neib.append((y, x, (d+1) % 4))
            now_neib.append((y, x, (d+3) % 4))
            if d == 0 and y-1 >= 0:
                now_neib.append((y-1, x, d))
            elif d == 1 and x+1 < n:
                now_neib.append((y, x+1, d))
            elif d == 2 and y+1 < n:
                now_neib.append((y+1, x, d))
            elif d == 3 and x-1 >= 0:
                now_neib.append((y, x-1, d))
            for fr in now_neib:
                if (fr[0], fr[1]) not in block and fr not in all_maze:
                    q.append(fr)
                    all_maze[fr] = all_maze[maze] + 1
                    if fr[0] == y_finish and fr[1] == x_finish:
                        d = fr[2]
                        fl = 1
                        break
            if fl:
                break
        x = x_finish
        y = y_finish
        fin = [(y, x, 0), (y, x, 1), (y, x, 2), (y, x, 3)]
        fl_fin = 0
        for elem in fin:
            if elem in all_maze:
                fl_fin = 1
                break
        if not fl_fin:
            return False
        sector = (y_finish, x_finish, d)
        jour = [sector]
        while sector != (y_start, x_start, d_start):
            ret_neib = []
            y0, x0, d0 = sector
            # разворот робота
            ret_neib.append((y0, x0, (d0+1) % 4))
            ret_neib.append((y0, x0, (d0+3) % 4))
            # переход в другую клетку
            if d0 == 0 and y0+1 < n:
                ret_neib.append((y0+1, x0, d0))
            elif d0 == 1 and x0-1 >= 0:
                ret_neib.append((y0, x0-1, d0))
            elif d0 == 2 and y0-1 >= 0:
                ret_neib.append((y0-1, x0, d0))
            elif d0 == 3 and x0+1 < n:
                ret_neib.append((y0, x0+1, d0))
            for fr in ret_neib:
                if fr in all_maze:
                    if all_maze[sector] - all_maze[fr] == 1:
                        sector = fr
                        jour.append(fr)
                        break
        jour.reverse()
        if ret == "way":
            return jour
        elif ret == "length":
            return len(jour)
        elif ret == "direct":
            out = ""
            for k in range(len(jour) - 1):
                y0, x0, d0 = jour[k]
                y1, x1, d1 = jour[k+1]
                if d1 - d0 == 1 or d1 - d0 == -3:
                    out += "R"
                elif d1 - d0 == -1 or d1 - d0 == 3:
                    out += "L"
                else:
                    out += "F"
            return out
        else:
            raise ValueError

    def localize(self, ret="zn"):
        if self.max_x-self.min_x != self.size-1 or self.max_y-self.min_y != self.size-1:
            raise Non_localize_error
        zero_x = self.min_x
        zero_y = self.min_y
        self.now_x -= zero_x
        self.now_y -= zero_y
        new_preg = list()
        if not self.is_localised:
            for k in self.preg:
                new_preg.append((k[0]-zero_y, k[1]-zero_x))
        self.preg = list()
        self.preg = new_preg
        self.is_localised = True
        if ret == "zn":
            return [(zero_y, zero_x), (self.now_y, self.now_x)]
        elif ret == "z":
            return (zero_y, zero_x)
        elif ret == "n":
            return (self.now_y, self.now_x)
        else:
            raise ValueError


class Know_maze(Maze):
    def __init__(self, mapp):
        self.map = mapp
        self.decode_dict = {'u': (-1, 0), 'l': (0, -1), 'd': (1, 0), 'r': (0, 1), 'n': (0, 0)}
        self.decode_direct = ['uldr', 'ruld', 'drul', 'ldru']
        self.size = len(self.mapp)

    def convert_direct(self, old, direct):
        ret = ""
        for d in old:
            if d == "u": d += self.decode_direct[direct][0]
            if d == "l": d += self.decode_direct[direct][1]
            if d == "d": d += self.decode_direct[direct][2]
            if d == "r": d += self.decode_direct[direct][3]
        return ret

    def localise(self, situation, last_neib=[]):
        if last_neib:
            last_neib = last_neib.copy()
            last_neib.reverse()
            may_be_sectors = []
            for i in range(len(self.mapp)):
                for j in range(len(self.mapp)):
                    if situation in [self.convert_direct(self.mapp[i][j], k) for k in range(4)]:
                        i1, j1 = i, j
                        for s in range(len(last_neib)):
                            fl = False
                            now_neib = self.neib((i1, j1), self.size)
                            for neib in now_neib:
                                if last_neib[s] in [self.convert_direct(self.mapp[neib[[0]]][neib[1]], k) for k in range(4)]:
                                    fl = True
                                    i1, j1 = neib[0], neib[1]
                                    break
                            if fl:
                                may_be_sectors.append((i, j))
                                break
        else:
            may_be_sectors = []
            for i in range(len(self.mapp)):
                for j in range(len(self.mapp)):
                    if situation in [self.convert_direct(self.mapp[i][j], k) for k in range(4)]:
                        may_be_sectors.append((i, j))
        return may_be_sectors
