def artag(size, art, type="getphoto"):
    def fromhex_getphoto(art):
        for i in range(len(art)):
            v = art[i] / (256 * 256) + art[i] / 256 % 256 + art[i] % 256
            if v > 300:
                art[i] = 1
            else:
                art[i] = 0
        return art

    def fromhex(s):  # текущая граница 300 по сумме трех каналов
        rez = int(s, 16)
        rez = rez // (256 * 256) + rez // 256 % 256 + rez % 256
        if rez > 300:
            return 0
        else:
            return 1

    def obnulenie_kraya(m):  # обнулим края
        gr = 10
        for i in range(160):
            for j in range(gr):
                m[160 * j + i] = 0
                m[(119 - j) * 160 + i] = 0
        gr = 10
        for i in range(120):
            for j in range(gr):
                m[i * 160 + j] = 0
                m[i * 160 + 159 - j] = 0

    art = open(art)
    if type == "no_getphoto":
        m1 = []
        for line in art:
            line = line.replace("\\n", " ")
            m1 += line.strip().split()

        for i in range(120 * 160):
            m1[i] = fromhex(m1[i])

        obnulenie_kraya(m1)
    else:
        m1 = art
        for i in range(120 * 160):
            m1 = fromhex_getphoto(art)

    def corners(m):
        k = 0
        i = 0
        x0 = -1
        y0 = -1
        for k in range(160):
            for i in range(k):
                if i >= 120:
                    break
                if (k - i < 160) and (m[i * 160 + k - i] > 0):
                    x0 = i
                    y0 = k - i
                    break
                if x0 >= 0:
                    break
        x3 = -1
        y3 = -1
        for k in range(x0 + y0, 280):
            fl = True
            for i in range(k):
                if i >= 120:
                    break
                if (0 <= k - i < 160) and m[i * 160 + k - i] > 0:
                    x3 = i
                    y3 = k - i
                    fl = False
            if fl:
                break

        x2 = -1
        y2 = -1
        for k in range(-119, 60):
            for i in range(120):
                if 0 <= i + k and i + k < 160 and m[i * 160 + i + k] > 0:
                    x2 = i
                    y2 = i + k
                    break
            if x2 >= 0:
                break

        x1 = -1
        y1 = -1
        for k in range(y2 - x2, 280):
            fl = True
            for i in range(120):
                if 0 <= i + k and i + k < 160 and m[i * 160 + i + k] > 0:
                    x1 = i
                    y1 = i + k
                    fl = False
            if fl:
                break

        return [x0, y0, x1, y1, x2, y2, x3, y3]

    def col(m, i, j, corn):
        x0 = corn[0]
        x1 = corn[2]
        x2 = corn[4]
        x3 = corn[6]
        y0 = corn[1]
        y1 = corn[3]
        y2 = corn[5]
        y3 = corn[7]

        x4 = (x0 * (9 - 2 * i) + x1 * (2 * i + 1)) / 10
        y4 = (y0 * (9 - 2 * i) + y1 * (2 * i + 1)) / 10
        x5 = (x2 * (9 - 2 * i) + x3 * (2 * i + 1)) / 10
        y5 = (y2 * (9 - 2 * i) + y3 * (2 * i + 1)) / 10

        x = int((x4 * (9 - 2 * j) + x5 * (2 * j + 1)) / 10)
        y = int((y4 * (9 - 2 * j) + y5 * (2 * j + 1)) / 10)
        return m[x * 160 + y]

    c1 = corners(m1)
    ar1 = []
    for j in range(size):
        for i in range(size):
            ar1.append(col(m1, i, j, c1))
    return ar1
