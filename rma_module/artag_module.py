from trik_var import brick, script, getPhoto


def artag(size, art, type="getphoto", height_width=(120, 160)):
    height, width = height_width

    def fromhex_getphoto(art):
        for i in range(len(art)):
            v = art[i] / (256 * 256) + art[i] / 256 % 256 + art[i] % 256
            if v > 250:
                art[i] = 0
            else:
                art[i] = 1
        return art

    def fromhex(s):  # текущая граница 300 по сумме трех каналов
        rez = int(s, 16)
        rez = rez // (256 * 256) + rez // 256 % 256 + rez % 256
        if rez > 300:
            return 0
        else:
            return 1

    def obnulenie_kraya(m):  # обнулим края
        gr = 20
        for i in range(width):
            for j in range(gr):
                m[width * j + i] = 0
                m[((height-1) - j) * width + i] = 0
        gr = 20
        for i in range(height):
            for j in range(gr):
                m[i * width + j] = 0
                m[i * width + (width-1) - j] = 0

    if type == "no_getphoto":
        art = open(art)
        m1 = []
        for line in art:
            line = line.replace("\\n", " ")
            m1 += line.strip().split()

        for i in range(height * width):
            m1[i] = fromhex(m1[i])

        obnulenie_kraya(m1)
    else:
        m1 = art
        m1 = fromhex_getphoto(art)

        obnulenie_kraya(m1)

    def corners(m):
        k = 0
        i = 0
        x0 = -1
        y0 = -1
        for k in range(width):
            for i in range(k):
                if i >= height:
                    break
                if (k - i < width) and (m[i * width + k - i] > 0):
                    x0 = i
                    y0 = k - i
                    break
                if x0 >= 0:
                    break
        x3 = -1
        y3 = -1
        for k in range(x0 + y0, height+width):
            fl = True
            for i in range(k):
                if i >= height:
                    break
                if (0 <= k - i < width) and m[i * width + k - i] > 0:
                    x3 = i
                    y3 = k - i
                    fl = False
            if fl:
                break

        x2 = -1
        y2 = -1
        for k in range(-height, 60):
            for i in range(height):
                if 0 <= i + k and i + k < width and m[i * width + i + k] > 0:
                    x2 = i
                    y2 = i + k
                    break
            if x2 >= 0:
                break

        x1 = -1
        y1 = -1
        for k in range(y2 - x2, height+width):
            fl = True
            for i in range(height):
                if 0 <= i + k and i + k < width and m[i * width + i + k] > 0:
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
        k1 = size*2 - 1
        k2 = k1+1

        x4 = (x0 * (k1 - 2 * i) + x1 * (2 * i + 1)) / k2
        y4 = (y0 * (k1 - 2 * i) + y1 * (2 * i + 1)) / k2
        x5 = (x2 * (k1 - 2 * i) + x3 * (2 * i + 1)) / k2
        y5 = (y2 * (k1 - 2 * i) + y3 * (2 * i + 1)) / k2

        x = int((x4 * (k1 - 2 * j) + x5 * (2 * j + 1)) / k2)
        y = int((y4 * (k1 - 2 * j) + y5 * (2 * j + 1)) / k2)
        return m[x * width + y]

    c1 = corners(m1)
    ar1 = []
    for j in range(size):
        for i in range(size):
            ar1.append(col(m1, i, j, c1))

    def val(ar):
        for x in range(4):
            if ar[3*5+3] == 0:
                break
            n1 = ar[1*5+1]
            ar[1*5+1] = ar[1*5+3]
            ar[1*5+3] = ar[3*5+3]
            ar[3*5+3] = ar[3*5+1]
            ar[3*5+1] = n1
            n2 = ar[1*5+2]
            ar[1*5+2] = ar[2*5+3]
            ar[2*5+3] = ar[3*5+2]
            ar[3*5+2] = ar[2*5+1]
            ar[2*5+1] = n2
        r = 0
        o = [ar[1*5+2], ar[2*5+1], ar[2*5+3],  ar[3*5+2]]
        for x in range(4):
            r = r*2+o[x]
        return r
    return val(ar1)
