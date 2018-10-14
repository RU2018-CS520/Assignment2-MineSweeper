import numpy as np
import random
import itertools
from matplotlib import pyplot as plt
from PIL import Image, ImageChops

import tile

class board(object):
	#a minesweeper board
	def __init__(self, rows = 10, cols = 10, mines = 10):
		#int rows in [2 : inf]: size of board
		#int cols in [2 : inf]: size of board
		#int mines in [1 : rows*cols-1]: the number of mines

		#basic attribute
		self.rows = rows
		self.cols = cols
		self.mines = mines #TODO: maybe there should be a 'if mines > rows*cols:' #actually mines > 0.23 rows*cols will be too hard
		self.newGame = True

		#basic board
		self.covered = np.full((self.rows, self.cols), True, dtype = np.bool)
		self.mine = np.zeros((self.rows, self.cols), dtype = np.bool)
		self.clue = np.zeros((self.rows, self.cols), dtype = np.uint8)

		#player attribute
		self.mineCount = 0
		self.blockCount = 0

		#player board
		self.flag = np.zeros((self.rows, self.cols), dtype = np.bool)
		self.safe = np.zeros((self.rows, self.cols), dtype = np.bool)
		self.hint = np.full((self.rows, self.cols), 255, dtype = np.uint8)
		self.warn = np.full((self.rows, self.cols), 255, dtype = np.uint8)
		self.left = np.full((self.rows, self.cols), 8, dtype = np.uint8)
		self.done = np.zeros((self.rows, self.cols), dtype = np.bool)

		self.tile = tile.tile()

		self.left[0, :] = 5
		self.left[self.rows-1, :] = 5
		self.left[:, 0] = 5
		self.left[:, self.cols-1] = 5

		self.left[0, 0] = 3
		self.left[0, self.cols-1] = 3
		self.left[self.rows-1, 0] = 3
		self.left[self.rows-1, self.cols-1] = 3

		return


	#important functions
	def start(self, row, col):
		#int row in [0 : rows-1]: start position
		#int col in [0 : cols-1]: start position

		#open block
		self.safe[row, col] = True
		self.covered[row, col] = False
		self.blockCount = self.blockCount + 1

		#generate board
		self.build(row, col)

		#get feedback
		self.hint[row, col] = self.explore(row, col)
		self.warn[row, col] = self.hint[row, col] #- count(neighbor, 'flag')
		for index in self.getNeighbor(row, col):
			self.left[index] = self.left[index] - 1
		return warn[row, col]


	def explore(self, row, col, blind = False, optimistic = False, cautious = False):
		#int row in [0 : rows-1]: position x
		#int col in [0 : cols-1]: position y
		#bool blind: True: sometimes return 255 instead of clue; False: normal return
		#bool optimistic: True: sometimes return a smaller clue; False: normal return
		#bool cautious: True: sometimes return a bigger clue; False: normal return
		
		#death check
		if self.mine[row, col]:
			return False
		
		#get clue
		clue = self.clue[row, col]
		#TODO: blind, optimistic, cautious 
		if blind:
			pass
		if optimistic:
			pass
		if cautious:
			pass
		return clue


	def visualize(self, beacon = 16, cheat = False):
		#int beacon [1 : inf]: interval of beacons; 0: no beacon
		#bool cheat: True: god view; False: player view
		
		image = np.zeros((self.rows*16, self.cols*16, 3), dtype = np.uint8)
		for row in range(self.rows):
			for col in range(self.cols):
				image[row*16 : row*16+16, col*16 : col*16+16] = self.tile(covered = self.covered[row, col], mine = self.mine[row, col], clue = self.clue[row, col], hint = self.hint[row, col], flag = self.flag[row, col], beacon = beacon and not (row%beacon and col%beacon), cheat = cheat)
		img = Image.fromarray(image) 
		img = ImageChops.invert(img)
		plt.imshow(img)
		plt.show()
		return img


	def count(self, row, col, key, inNeighbor = None, outNeighbor = False):
		#int row in [0 : rows-1]: position x
		#int col in [0 : cols-1]: position y
		#str key in {'covered', 'mine', 'flag', 'safe'}: key to count

		#check key
		if key == 'covered':
			mat = self.covered
		elif key == 'mine':
			mat = self.mine
		elif key == 'flag':
			mat = self.flag
		elif key == 'safe':
			mat = self.safe
		else:
			print('E: frame.board.count. wrong input key.')
			return 0
		
		#get neighbor
		if inNeighbor:
			neighbor = inNeighbor
		else:
			neighbor = self.getNeighbor(row, col)

		#count
		count = 0
		for index in neighbor:
			if mat[index]:
				count = count + 1
		
		if outNeighbor:
			return (count, neighbor)
		else:
			return count

	#tool functions
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
		for index in minePos:
			if index >= startPos:
				self.mine[self.ord2xy(index+1)] = True
			else:
				self.mine[self.ord2xy(index)] = True
		
		#init clue
		for row in range(self.rows):
			for col in range(self.cols):
				self.clue[row, col] = self.count(row, col, 'mine')

		#done
		self.newGame = False
		return


	def xy2ord(self, row, col):
		#int row in [0 : rows-1]: position x
		#int col in [0 : cols-1]: position y
		return row * self.cols + col
	
	def ord2xy(self, num):
		#int num in [0 : rows*cols-1]: position number
		return (num // self.cols, num % self.cols)


	def getNeighbor(self, row, col):
		#int row in [0 : rows-1]: position x
		#int col in [0 : cols-1]: position y

		#get valid rows
		if row == 0:
			nRow = [0, 1]
		elif row == self.rows-1:
			nRow = [row-1, row]
		else:
			nRow = [row-1, row, row+1]

		#get valid cols
		if col == 0:
			nCol = [0, 1]
		elif col == self.cols-1:
			nCol = [col-1, col]
		else:
			nCol = [col-1, col, col+1]

		#delete itself
		neighbor = list(itertools.product(nRow, nCol))
		neighbor.remove((row, col))
		return neighbor


if __name__ == '__main__':
	m = board(10, 10, 10)
	m.start(m.rows-1,m.cols//2)
	print(m.left)
	m.visualize(cheat = True)