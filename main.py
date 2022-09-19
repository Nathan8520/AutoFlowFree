from helper import *
from ctypes import windll
from pynput.mouse import Controller as Mouse, Listener, Button
import time
import numpy as np
from PIL import ImageGrab
import cv2

size = 4

mouse = Mouse()

cx = -1
cy = -1
w = -1

global bcCol, bcx, bcy
bcCol = 0
bcx = 0
bcy = 0

def calibrate(size):
    global bcCol, bcx, bcy
    print("Calibration process:")

    print("Press the top left corner")
    x1, y1 = getClick()
    print(f"Calibrated to ({x1}, {y1})")

    print("Press the bottom right corner")
    x2, y2 = getClick()
    print(f"Calibrated to ({x2}, {y2})")

    print("Calibration complete")

    width = (x2 - x1) / size

    bcx = x2
    bcy = y2
    _, bcCol = getCol(bcx, bcy)

    return x1, y1, width

def getBoard(size, cx, cy, w):
    board = [[0 for x in range(size)] for x in range(size)]

    colMap = {}
    nxtCol = 1

    if cx == -1 or cy == -1 or w == -1:
        cx, cy, w = calibrate(size)

    for x in range(size):
        for y in range(size):
            col, i = getCol(cx + w*x + w/2, cy + w*y + w/2)
            if sum(col) < 100:
                continue
            if i in colMap:
                board [y][x] = colMap [i]
            else:
                colMap [i] = nxtCol
                nxtCol += 1
                board [y][x] = nxtCol - 1

    return cx, cy, w, board

def getEndPoints(board):
    p = []
    for x in range(len(board)):
        for y in range(len(board [x])):
            if board [x][y] != 0:
                p.append([x, y])
    return p


def isReady():
    while True:
        frame = ImageGrab.grab(bbox=(cx + (size-1)*w, cy + (size-1)*w, cx + w * size, cy + w * size))
        frame = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower_green = np.array([36, 25, 25])
        upper_green = np.array([70, 255, 255])

        mask = cv2.inRange(hsv, lower_green, upper_green)

        if cv2.countNonZero(mask) > 0:
            break

def validateBoard(board, endPoints):
    for r in range(size):
        for c in range(size):
            cols = board [r][c]
            if len(cols) > 1:
                continue
            for col in cols:
                board [r][c] = [col]
                count = 0
                cert = 0

                if r > 0 and board[r][c][0] in board[r - 1][c]:
                    count += 1
                    if len(board[r - 1][c]) == 1:
                        cert += 1
                if r < size - 1 and board[r][c][0] in board[r + 1][c]:
                    count += 1
                    if len(board[r + 1][c]) == 1:
                        cert += 1
                if c > 0 and board[r][c][0] in board[r][c - 1]:
                    count += 1
                    if len(board[r][c - 1]) == 1:
                        cert += 1
                if c < size - 1 and board[r][c][0] in board[r][c + 1]:
                    count += 1
                    if len(board[r][c + 1]) == 1:
                        cert += 1

                if [r, c] in endPoints:
                    if cert > 1 or count < 1:
                        return False
                else:
                    if cert > 2 or count < 2:
                        return False
            board [r][c] = cols
    return True

def checkCell(board, endPoints, r, c, col, cr, cc):
    #print(r, c, col, cr, cc)
    if len(board [r][c]) > 1:
        return 0

    if board [r][c][0] != col:
        return 0

    count = 0
    cert = 0

    if r > 0 and r-1 != cr and board [r][c][0] in board [r-1][c]:
        count += 1
        if len(board [r-1][c]) == 1:
            cert += 1
    if r < size-1 and r+1 != cr and board [r][c][0] in board [r+1][c]:
        count += 1
        if len(board [r+1][c]) == 1:
            cert += 1
    if c > 0 and c-1 != cc and board [r][c][0] in board [r][c-1]:
        count += 1
        if len(board [r][c-1]) == 1:
            cert += 1
    if c < size-1 and c+1 != cc and board [r][c][0] in board [r][c+1]:
        count += 1
        if len(board [r][c+1]) == 1:
            cert += 1

    if [r, c] in endPoints:
        if cert >= 1:
            #print("X")
            return -1
        if count == 0:
            return 1
        return 0
    else:
        if cert >= 2:
            #print("Y")
            return -1
        if count < 2:
            return 1
        return 0


def solveBoard(board, endPoints):

    if not validateBoard(board, endPoints):
        return False, []

    #print("-----")
    #printBoard(board)
    change = True

    while change:
        change = False
        for x in range(size):
            for y in range(size):
                #print(f"---{x}, {y}---")
                if len(board [x][y]) == 1:
                    continue

                p = board [x][y]

                cert = []
                pos = []
                for col in board [x][y]:
                    a = checkCell(board, endPoints, x-1, y, col, x, y) if x > 0 else 0
                    b = checkCell(board, endPoints, x+1, y, col, x, y) if x < size-1 else 0
                    c = checkCell(board, endPoints, x, y-1, col, x, y) if y > 0 else 0
                    d = checkCell(board, endPoints, x, y+1, col, x, y) if y < size-1 else 0
                    #print(a, b, c, d)

                    z = 0

                    countx = 0
                    certx = 0

                    if x > 0 and col in board[x - 1][y]:
                        countx += 1
                        if len(board[x - 1][y]) == 1:
                            certx += 1
                    if x < size - 1 and col in board[x + 1][y]:
                        countx += 1
                        if len(board[x + 1][y]) == 1:
                            certx += 1
                    if y > 0 and col in board[x][y - 1]:
                        countx += 1
                        if len(board[x][y - 1]) == 1:
                            certx += 1
                    if y < size - 1 and col in board[x][y + 1]:
                        countx += 1
                        if len(board[x][y + 1]) == 1:
                            certx += 1

                    if [x, y] in endPoints:
                        if certx > 1 or countx < 1:
                            z = -1
                    else:
                        if certx > 2 or countx < 2:
                            z = -1

                    if a < 0 or b < 0 or c < 0 or d < 0 or z < 0:
                        if a > 0 or b > 0 or c > 0 or d > 0:
                            #print(x, y, col, z)
                            return False, []
                    else:
                        if a > 0 or b > 0 or c > 0 or d > 0:
                            #print()
                            #printBoard(board)
                            #print(col, a, b, c, d, x, y)
                            cert.append(col)
                        pos.append(col)

                if len(cert) > 1 or len(pos) == 0:
                    #printBoard(board)
                    #print(x, y, cert)
                    return False, []
                elif len(cert) == 1:
                    board [x][y] = cert
                else:
                    board [x][y] = pos

                if board [x][y] != p:
                    change = True

    #print()
    #printBoard(board)

    minPos = []
    for x in range(size):
        for y in range(size):
            if len(board [x][y]) > 1:
                h = 4*len(board [x][y])

                if x > 0:
                    h += len(board [x-1][y])
                if x < size-1:
                    h += len(board [x+1][y])
                if y > 0:
                    h += len(board [x][y-1])
                if y < size-1:
                    h += len(board [x][y+1])

                minPos.append([h, (x, y)])

    minPos = sorted(minPos)

    if len(minPos) == 0:
        return True, board

    currentBoard = [row [:] for row in board]

    for i in minPos:
        x = i [1][0]
        y = i [1][1]
        cols = board [x][y]

        for j in cols:
            board [x][y] = [j]

            valid, newBoard = solveBoard([row [:] for row in board], endPoints)

            if valid:
                return True, newBoard

            board = currentBoard

    return False, []

for set in range(5):
    size += 1
    w *= (size-1)/size
    for level in range(30):

        cx, cy, w, board = getBoard(size, cx, cy, w)

        endPoints = getEndPoints(board)

        maxCol = max([max(x) for x in board])

        for x in range(size):
            for y in range(size):
                if board [x][y] == 0:
                    board [x][y] = range(1, maxCol+1, 1)
                else:
                    board [x][y] = [board [x][y]]

        printBoard(board)

        valid, board = solveBoard(board, endPoints)

        #print(valid, board)
        printBoard(board)

        if not valid:
            break

        def conv(r, c):
            return cx + w*c + w/2, cy + w*r + w/2

        visited = []
        for x in endPoints:
            if x in visited:
                continue

            visited.append(x)

            p = conv(x [0], x [1])
            mouse.position = (p [0], p [1])
            mouse.press(Button.left)
            time.sleep(0.05)

            r = x [0]
            c = x [1]

            while True:
                if r > 0 and board [r][c] == board [r-1][c] and not [r-1, c] in visited:
                    r -= 1
                elif r < size-1 and board [r][c] == board [r+1][c] and not [r+1, c] in visited:
                    r += 1
                elif c > 0 and board [r][c] == board [r][c-1] and not [r, c-1] in visited:
                    c -= 1
                elif c < size-1 and board [r][c] == board [r][c+1] and not [r, c+1] in visited:
                    c += 1
                else:
                    visited.append([r, c])
                    break

                p = conv(r, c)
                drag(mouse, mouse.position [0], mouse.position [1], p [0], p [1], 0.01, steps=20)
                visited.append([r, c])

            mouse.release(Button.left)
            time.sleep(0.05)

        #time.sleep(1.2)
        #x, y = getCoords()
        mouse.position = (cx + w * size/2 , cy - w * size/5)
        mouse.press(Button.left)
        mouse.release(Button.left)
        time.sleep(0.3)
        mouse.position = (cx + w * size/2, cy + 6.25 * w * size/5)
        mouse.press(Button.left)
        mouse.release(Button.left)

        time.sleep(0.1)
        time.sleep(1)
        time.sleep(0.1)





