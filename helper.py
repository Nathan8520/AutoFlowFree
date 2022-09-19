from ctypes import windll
from pynput.mouse import Controller as Mouse, Listener, Button
import time

class queue:
    def __init__(self, data=[]):
        self.data = data

    def enqueue(self, x):
        self.data.append(x)

    def dequeue(self):
        i = self.data [0]
        self.data = self.data [1:]
        return i

    def front(self):
        return self.data [0]

    def empty(self):
        return len(self.data) == 0

def printBoard(board):
    for row in board:
        s = ""
        for element in row:
            if element == 0:
                s += " "
            else:
                s += str(element [0]) if len(element) == 1 else " "
            s += " "
        print(s)
    print()

def rgba(colorref):
    mask = 0xff
    return [(colorref & (mask << (i * 8))) >> (i * 8) for i in range(4)]

def getCol(x, y):
    hdc = windll.user32.GetDC(0)
    col = windll.gdi32.GetPixel(hdc, int(x), int(y))
    return rgba(col), col


def getClick():
    global X, Y

    def on_click(x, y, button, pressed):
        global X, Y
        X = x
        Y = y
        return False

    with Listener(on_click=on_click) as l:
        l.join()
    with Listener(on_click=on_click) as l:
        l.join()

    return X, Y

def drag(mouse, x1, y1, x2, y2, t, steps=100):
    for i in range(steps):
        x = x1 + (x2-x1)*i/steps
        y = y1 + (y2-y1)*i/steps

        mouse.position = (x, y)
        time.sleep(t/steps)

