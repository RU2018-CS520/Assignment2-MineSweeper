import sys
import os
import time
import random
import frame
import solution
import numpy as np
import pyqtgraph as pg
import matplotlib.animation as animation

from PyQt5.QtWidgets import (QApplication, QMainWindow, QMenu, QVBoxLayout,
    QSizePolicy, QMessageBox, QWidget, QPushButton, QWidget, QSlider, QLabel,
    QGridLayout, QGroupBox, QLineEdit)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot, Qt, QRectF
from matplotlib.figure import Figure
from PIL import Image, ImageChops
from threading import Thread
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from matplotlib.animation import TimedAnimation
from matplotlib.lines import Line2D
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.animation import FuncAnimation


class Window(QWidget):

    def __init__(self):
        super().__init__()
        self.left = 10
        self.top = 10
        self.title = 'The best minesweeper(we could figure out)'
        self.width = 1280
        self.height = 960
        self.initUI()
        self.cnt = 0

    def initUI(self):
        grid = QGridLayout()

        self.canvas = Canvas(self, width=12.9, height=9.6)
        grid.addWidget(self.canvas, 0, 0, 10, 10)

        grid.addWidget(self.initConfigGroup(), 0, 11)

        self.labelStep = self.initLabel("Current Step: 0")
        grid.addWidget(self.labelStep, 11, 11)

        self.buttonStartAnimation = QPushButton('Start animation', self)
        self.buttonStartAnimation.clicked.connect(self.animate)
        self.buttonStartAnimation.setEnabled(False)
        grid.addWidget(self.buttonStartAnimation, 1, 11)

        self.buttonSave = QPushButton('Save animation to file', self)
        self.buttonSave.clicked.connect(self.save)
        self.buttonSave.setEnabled(False)
        grid.addWidget(self.buttonSave, 2, 11)

        self.slider = self.initSlider()
        self.slider.setEnabled(False)
        grid.addWidget(self.slider, 11, 0)

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setLayout(grid)
        self.show()


    def initLabel(self, text):
        label = QLabel(self)
        label.setText(text)
        return label

    def initConfigGroup(self):
        groupBox = QGroupBox("Configurations")

        grid = QGridLayout()
        grid.addWidget(self.initLabel("Size:"), 0, 0)
        grid.addWidget(self.initLabel("Mines:"), 1, 0)

        self.lineEditX = QLineEdit(self)
        self.lineEditX.setText("10")
        #self.lineEditX.setText("64")
        self.lineEditY = QLineEdit(self)
        #self.lineEditY.setText("64")
        self.lineEditY.setText("10")
        self.lineEditMines = QLineEdit(self)
        #self.lineEditMines.setText("800")
        self.lineEditMines.setText("10")

        grid.addWidget(self.lineEditX, 0, 1)
        grid.addWidget(self.lineEditY, 0, 2)
        grid.addWidget(self.lineEditMines, 1, 1)

        self.buttonStart = QPushButton('Generate and Solve', self)
        self.buttonStart.clicked.connect(self.start)
        grid.addWidget(self.buttonStart, 2, 0, 1, 3)

        groupBox.setLayout(grid)
        return groupBox

    def initSlider(self):
        slider = QSlider(Qt.Horizontal, self)
        slider.setFocusPolicy(Qt.NoFocus)
        slider.setMaximum(10)
        slider.setGeometry(0, 900, self.width, 50)
        slider.valueChanged[int].connect(self.changeValue)
        slider.sliderReleased.connect(self.releaseSlider)
        return slider

    def releaseSlider(self):
        value = self.slider.value()
        self.canvas.plotOne(value)

    def changeValue(self, value):
        self.labelStep.setText("Step: " + repr(value))

    def animate(self, p, beacon = 16, cheat = False):
        if isinstance(p, bool):
            p = self.p
        self.buttonStartAnimation.setEnabled(False)
        self.canvas.start(p)
        self.buttonStartAnimation.setEnabled(True)
        #self.buttonSave.setEnabled(True)

    def start(self):
        self.buttonStart.setEnabled(False)
        self.buttonStart.setText('Solving, please wait')

        rows = int(self.lineEditX.text())
        cols = int(self.lineEditY.text())
        mines = int(self.lineEditMines.text())
        print('Trying to construct a(an) ' + repr(rows) + 'x' + repr(cols) + ' maze with ' + repr(mines) + ' mines')
        m = frame.board(rows, cols, mines)
        #self.canvas.initUI(m)
        #self.initCanvas(m)
        print('Construction completed.')
        self.p = solution.player(m)
        print('Player is ready, trying to sweep mines.')
        self.p.solve()
        print('Done')

        self.slider.setMaximum(len(self.p.history) - 1)
        self.animate(self.p)
        self.buttonStart.setText('Generate and Solve')
        self.buttonStart.setEnabled(True)
        self.slider.setEnabled(True)

    def save(self):
        self.buttonSave.setEnabled(False)
        self.canvas.save()
        self.buttonSave.setEnabled(True)

class Canvas(FigureCanvas):

    def __init__(self, parent = None, width = 12, height = 9, dpi = 100):
        #fig = Figure(figsize=(width, height), dpi=dpi)
        #self.axes = fig.add_subplot(111)

        self.fig = plt.figure(figsize=(width, height), dpi=dpi)
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                QSizePolicy.Expanding,
                QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        #self.initUI()
        #self.plot()

    def start(self, player, _beacon = 16, _cheat = False):
        print('Started plotting')
        global currentStep
        global p
        global beacon
        global cheat
        global anim
        currentStep = 0
        p = player
        beacon = _beacon
        cheat = _cheat
        anim = FuncAnimation(self.fig, self.animate, init_func = self.init, interval =
                             20, blit = True)
        #m = frame.board(p.m.rows, p.m.cols, p.m.mines)
        #self.image = np.zeros((m.rows*16, m.cols*16, 3), dtype = np.uint8)
        #img = Image.fromarray(self.image)
        #img = ImageChops.invert(img)
        #plt.imshow(img)
        ##plt.show()
        self.draw()
        print('Plotting completed')

    def init(self):
        print('Initializing animation')
        global p
        global image
        global beacon
        global cheat
        m = frame.board(p.m.rows, p.m.cols, p.m.mines)
        image = np.zeros((m.rows*16, m.cols*16, 3), dtype = np.uint8)
        for row in range(m.rows):
            for col in range(m.cols):
                image[row*16 : row*16+16, col*16 : col*16+16] = m.tile(covered = m.covered[row, col], mine = m._mine[row, col], clue = m._clue[row, col], hint = m.hint[row, col], flag = m.flag[row, col], beacon = beacon and not (row%beacon and col%beacon), cheat = cheat)
        img = Image.fromarray(image)
        img = ImageChops.invert(img)
        im = plt.imshow(img, animated = True)
        print('Initialization completed')
        return im,

    def plotOne(self, i):
        print('Plotting step ' + repr(i) + ' . Please wait.')
        global currentStep
        global image
        l = 0
        r = i + 1
        if i >= currentStep:
            l = currentStep
        else:
            m = frame.board(p.m.rows, p.m.cols, p.m.mines)
            image = np.zeros((m.rows*16, m.cols*16, 3), dtype = np.uint8)
            for row in range(m.rows):
                for col in range(m.cols):
                    image[row*16 : row*16+16, col*16 : col*16+16] = m.tile(covered = m.covered[row, col], mine = m._mine[row, col], clue = m._clue[row, col], hint = m.hint[row, col], flag = m.flag[row, col], beacon = beacon and not (row%beacon and col%beacon), cheat = cheat)
            img = Image.fromarray(image)
            img = ImageChops.invert(img)
            im = plt.imshow(img, animated = True)
            self.draw()
        for j in range(l ,r):
            print('Drawing step ' + repr(j))
            [x, y], hint = p.history[j]
            if hint == 'safe':
                p.m.hint[x, y] = p.m.explore(x, y)
            elif hint == 'flag':
                p.m.flag[x, y] = True
            image[x*16 : x*16+16, y*16 : y*16+16] = p.m.tile(covered = p.m.covered[x, y], mine = p.m._mine[x, y], clue = p.m._clue[x, y], hint = p.m.hint[x, y], flag = p.m.flag[x, y], beacon = beacon and not (x%beacon and y%beacon), cheat = cheat)
        img = Image.fromarray(image)
        img = ImageChops.invert(img)
        im = plt.imshow(img, animated = True)
        self.draw()

    def animate(*args):
        global currentStep
        global p
        global beacon
        global cheat
        global image
        global anim
        print('Drawing step ' + repr(currentStep))
        [x, y], hint = p.history[currentStep]
        if hint == 'safe':
            p.m.hint[x, y] = p.m.explore(x, y)
        elif hint == 'flag':
            p.m.flag[x, y] = True
        image[x*16 : x*16+16, y*16 : y*16+16] = p.m.tile(covered = p.m.covered[x, y], mine = p.m._mine[x, y], clue = p.m._clue[x, y], hint = p.m.hint[x, y], flag = p.m.flag[x, y], beacon = beacon and not (x%beacon and y%beacon), cheat = cheat)
        img = Image.fromarray(image)
        img = ImageChops.invert(img)
        im = plt.imshow(img, animated = True)
        print('Finished')
        currentStep += 1
        if currentStep >= len(p.history):
            print('Stop!')
            anim.event_source.stop()
        return im,

    def initUI(self, m = None):
        if m is None:
            m = frame.board(self.rows, self.cols, self.mines)
        self.image = np.zeros((m.rows*16, m.cols*16, 3), dtype = np.uint8)
        self.plot(m, cnt = 0)

    def plot(self, m, cnt, beacon = 16, cheat = False):
        for row in range(m.rows):
            for col in range(m.cols):
                self.image[row*16 : row*16+16, col*16 : col*16+16] = m.tile(covered = m.covered[row, col], mine = m._mine[row, col], clue = m._clue[row, col], hint = m.hint[row, col], flag = m.flag[row, col], beacon = beacon and not (row%beacon and col%beacon), cheat = cheat)
        img = Image.fromarray(self.image)
        img = ImageChops.invert(img)
        plt.imshow(img)
        self.draw()
        #img.save(filePath + "step" + repr(cnt) + '.png')

    def plotFromFile(self, cnt):
        img = Image.open(filePath + "step" + repr(cnt) + '.png')
        plt.imshow(img)
        self.draw()

    def plotFromHistory(self, p, cnt, beacon = 16, cheat = False):
        print('Drawing step ' + repr(cnt))
        [x, y], hint = p.history[cnt]
        p.m.hint[x, y] = p.m.explore(x, y)
        self.image[x*16 : x*16+16, y*16 : y*16+16] = p.m.tile(covered = p.m.covered[x, y], mine = p.m._mine[x, y], clue = p.m._clue[x, y], hint = p.m.hint[x, y], flag = p.m.flag[x, y], beacon = beacon and not (x%beacon and y%beacon), cheat = cheat)
        img = Image.fromarray(self.image)
        img = ImageChops.invert(img)
        plt.imshow(img)
        #plt.pause(0.0001)
        self.draw()
        #plt.draw()
        print('Finished')

    def save(self):
        Writer = animation.writers['ffmpeg']
        writer = Writer(fps=15, metadata=dict(artist='Me'), bitrate=1800)
        global anim
        global currentStep
        currentStep = 0
        anim.save(filePath + 'animation.mp4', writer = writer)

if __name__ == '__main__':
    global filePath
    global fileCnt
    filePath = os.path.dirname(os.path.realpath(__file__))
    filePath = os.path.join(filePath, '../pics/')
    #fileCnt = len([fileName for fileName in os.listdir(filePath) if
    #               os.path.isfile(filePath + fileName)])
    #print(os.listdir(filePath))
    application = QApplication(sys.argv)
    ex = Window()
    sys.exit(application.exec_())
    # test asd
