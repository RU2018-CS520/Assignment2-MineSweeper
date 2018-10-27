import numpy as np
import random
import itertools
from matplotlib import pyplot as plt
from PIL import Image, ImageChops

import tile

class board(object):
    #a minesweeper board
    def __init__(self, rows = 10, cols = 10, mines = 10, blind = False, optimistic = False, cautious = False):
        #int rows in [2 : inf]: size of board
        #int cols in [2 : inf]: size of board
        #int mines in [1 : rows*cols-1]: the number of mines
        #bool blind: True: sometimes return 255 instead of clue; False: normal return
        #bool optimistic: True: sometimes return a smaller clue; False: normal return
        #bool cautious: True: sometimes return a bigger clue; False: normal return

        #basic attribute
        self.rows = rows
        self.cols = cols
        self.mines = mines #TODO: maybe there should be a 'if mines > rows*cols:' #actually mines > 0.23 rows*cols will be too hard
        self.newGame = True
        self.blind = blind
        self.optimistic = optimistic
        self.cautious = cautious
        self.tile = tile.tile()

        self.blindRate = 0.1

        #basic board
        self.covered = np.full((self.rows, self.cols), True, dtype = np.bool)
        self._mine = np.zeros((self.rows, self.cols), dtype = np.bool)
        self._clue = np.zeros((self.rows, self.cols), dtype = np.uint8)

        #player attribute
        self.flagCount = 0
        self.blockCount = 0

        #player board
        self.flag = np.zeros((self.rows, self.cols), dtype = np.bool)
        self.safe = np.zeros((self.rows, self.cols), dtype = np.bool)
        self.hint = np.full((self.rows, self.cols), 127, dtype = np.uint8) #clue player got
        self.warn = np.full((self.rows, self.cols), 127, dtype = np.uint8) #clue - neighbor's flag
        self.nebr = np.full((self.rows, self.cols), 1, dtype = np.uint64) #hash of neighbor's covered but not flaged
        self.left = np.full((self.rows, self.cols), 8, dtype = np.uint8) #number of neighbor's covered but not flaged
        self.done = np.zeros((self.rows, self.cols), dtype = np.bool) #all neighbor explored or flaged

        self.hide = np.zeros((self.rows, self.cols), dtype = np.bool)

        #process left
        self.left[0, :] = 5
        self.left[self.rows-1, :] = 5
        self.left[:, 0] = 5
        self.left[:, self.cols-1] = 5

        self.left[0, 0] = 3
        self.left[0, self.cols-1] = 3
        self.left[self.rows-1, 0] = 3
        self.left[self.rows-1, self.cols-1] = 3

        #process nebr
        hashCore = [[ 2,  3,  5, 7,  11],
                    [13, 17, 19, 23, 29],
                    [31, 37, 41, 43, 47],
                    [53, 59, 61, 67, 71],
                    [73, 79, 83, 89, 97]]
        self.hashCore = np.asarray(hashCore, dtype = np.uint8)

        for row in range(self.rows):
            for col in range(self.cols):
                neighbor = self.getNeighbor(row, col)
                for pos, index in neighbor:
                    self.nebr[row, col] = self.nebr[row, col] * self.hashCore[pos[0]%5, pos[1]%5]

        return

    #important functions
    #start at (row, col), NOTE: start block must be safe
    def start(self, row, col):
        #int row in [0 : rows-1]: start position
        #int col in [0 : cols-1]: start position
        #return:
        #int hint in [0 : 8]: hint of start block (row, col)

        #generate board
        self.build(row, col)

        #get feedback
        self.safe[row, col] = True
        tempHint = self.explore(row, col)
        self.hint[row, col] = self._clue[row, col]
        self.warn[row, col] = self.hint[row, col] #- count(neighbor, 'flag')
        for pos, index in self.getNeighbor(row, col):
            self.nebr[pos] = self.nebr[pos] // self.hashCore[row%5, col%5]
            self.left[pos] = self.left[pos] - 1
        return self.hint[row, col]

    #open (row, col)
    def explore(self, row, col):
        #int row in [0 : rows-1]: position x
        #int col in [0 : cols-1]: position y
        #return
        #int hint [0 : 8]: this block's hint. False: dead
        
        self.covered[row, col] = False
        self.blockCount = self.blockCount + 1
        #death check
        if self._mine[row, col]:
            return False
        
        #get clue
        hint = self._clue[row, col]
        #TODO: blind, optimistic, cautious 
        if self.blind:
            if random.random() < self.blindRate:
                hint = None
        if self.optimistic:
            pass
        if self.cautious:
            pass
        return hint

    #print the board
    def visualize(self, beacon = 16, cheat = False):
        #int beacon [1 : inf]: interval of beacons; 0: no beacon
        #bool cheat: True: god view; False: player view
        #return
        #PIL.Image image: board image
        
        image = np.zeros((self.rows*16, self.cols*16, 3), dtype = np.uint8)
        for row in range(self.rows):
            for col in range(self.cols):
                image[row*16 : row*16+16, col*16 : col*16+16] = self.tile(covered = self.covered[row, col], mine = self._mine[row, col], clue = self._clue[row, col], hint = self.hint[row, col], flag = self.flag[row, col], hide = self.hide[row, col], beacon = beacon and not (row%beacon and col%beacon), cheat = cheat)
        img = Image.fromarray(image) 
        img = ImageChops.invert(img)
        plt.imshow(img)
        plt.show()
        return img

    #count neighbor block's key
    def count(self, row, col, key, iNebr = None, oNebr = False):
        #int row in [0 : rows-1]: position x
        #int col in [0 : cols-1]: position y
        #str key in {'covered', '_mine', 'flag', 'safe'}: key to count
        #list iNebr with element ((row, col), index): input processed neighbor. None: auto-generate neighbor
        #bool oNebr: True: also return neighbor; False: only return count

        #check key
        if key == 'covered':
            mat = self.covered
        elif key == '_mine':
            mat = self._mine
        elif key == 'flag':
            mat = self.flag
        elif key == 'safe':
            mat = self.safe
        else:
            print('E: frame.board.count. wrong input key.')
            return 0
        
        #get neighbor
        if iNebr:
            neighbor = iNebr
        else:
            neighbor = self.getNeighbor(row, col)

        #count
        count = 0
        for pos, index in neighbor:
            if mat[pos]:
                count = count + 1
        
        if oNebr:
            return (count, neighbor)
        else:
            return count

    #tool functions
    #construct mine distribution
    def build(self, row = None, col = None):
        #int row in [0 : rows-1]: start position
        #int col in [0 : cols-1]: start position
        
        #get start position
        if row is None or col is None:
            startPos = self.rows * self.cols
        else:
            startPos = self.xy2ord(row, col)

        #init mines
        minePos = random.sample(list(range(self.rows*self.cols - bool(row and col))), self.mines)
        for pos in minePos:
            if pos >= startPos:
                self._mine[self.ord2xy(pos+1)] = True
            else:
                self._mine[self.ord2xy(pos)] = True
        
        #init clue
        for row in range(self.rows):
            for col in range(self.cols):
                self._clue[row, col] = self.count(row, col, '_mine')

        #done
        self.newGame = False
        return

    #transform (x, y) to num
    def xy2ord(self, row, col):
        #int row in [0 : rows-1]: position x
        #int col in [0 : cols-1]: position y
        return row * self.cols + col
    #transform num to (x, y)
    def ord2xy(self, num):
        #int num in [0 : rows*cols-1]: position number
        return (num // self.cols, num % self.cols)

    #generate neighbor of (row, col)
    def getNeighbor(self, row, col):
        #int row in [0 : rows-1]: position x
        #int col in [0 : cols-1]: position y
        #return:
        #list neighbor with element ((row, col), index): this block's neighbor

        #get valid rows
        if row == 0:
            nRow = [(0, 1), (1, 2)]
        elif row == self.rows-1:
            nRow = [(row-1, 0), (row, 1)]
        else:
            nRow = [(row-1, 0), (row, 1), (row+1, 2)]

        #get valid cols
        if col == 0:
            nCol = [(0, 1), (1, 2)]
        elif col == self.cols-1:
            nCol = [(col-1, 0), (col, 1)]
        else:
            nCol = [(col-1, 0), (col, 1), (col+1, 2)]

        #delete itself
        neighbor = list(itertools.product(nRow, nCol))
        neighbor = [((neighbor[i][0][0], neighbor[i][1][0]), neighbor[i][0][1]*3+neighbor[i][1][1]) for i in range(len(neighbor))]
        neighbor.remove(((row, col), 4))
        return neighbor


if __name__ == '__main__':
    m = board(10, 10, 10, blind = True)
    m.start(m.rows-1,m.cols//2)
    print(m.left)
    m.visualize(cheat = False)
    m.visualize(cheat = True)
    print(m.getNeighbor(0,0))