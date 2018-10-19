import sys
import random
import frame
import solution
import numpy as np

from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QVBoxLayout, QSizePolicy, QMessageBox, QWidget, QPushButton
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PIL import Image, ImageChops

class Window(QMainWindow):

    def __init__(self):
        super().__init__()
        self.left = 10
        self.top = 10
        self.title = 'The best minesweeper(we could figure out)'
        self.width = 1024 
        self.height = 768 
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.canvas = Canvas(self, width=5, height=4)
        self.canvas.move(0,0)

        button1 = QPushButton('Reserved position', self)
        button1.setToolTip('This is an example button')
        button1.clicked.connect(self.button1_on_click)
        button1.move(768,0)
        button1.resize(256,100)

        self.show()

    @pyqtSlot()
    def button1_on_click(self):
        self.deal()

    def deal(self):
        m = frame.board(10, 10, 10)
        m.start(m.rows-1, m.cols//2)
        self.canvas.plot(m, cheat = True)


class Canvas(FigureCanvas):

    def __init__(self, parent = None, width = 5, height = 4, dpi = 100):
        #fig = Figure(figsize=(width, height), dpi=dpi)
        #self.axes = fig.add_subplot(111)

        fig = plt.figure()
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                QSizePolicy.Expanding,
                QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.initUI()
        #self.plot()

    def initUI(self):
        m = frame.board(10, 10, 0)
        self.image = np.zeros((m.rows*16, m.cols*16, 3), dtype = np.uint8)
        self.plot(m)

    def plot(self, m, beacon = 16, cheat = False):
        for row in range(m.rows):
            for col in range(m.cols):
                self.image[row*16 : row*16+16, col*16 : col*16+16] = m.tile(covered = m.covered[row, col], mine = m._mine[row, col], clue = m._clue[row, col], hint = m.hint[row, col], flag = m.flag[row, col], beacon = beacon and not (row%beacon and col%beacon), cheat = cheat)
        img = Image.fromarray(self.image) 
        img = ImageChops.invert(img)
        plt.imshow(img)
        self.draw()

if __name__ == '__main__':
    application = QApplication(sys.argv)
    ex = Window()
    sys.exit(application.exec_())
