import numpy as np

import frame

class player(object):
	#player view
	def __init__(self, m, chain = False):
		self.m = m
		self.chain = chain
		self.alive = True
		self.startList = [(0, 0), (self.m.rows-1, 0), (0, self.m.cols-1), (self.m.rows-1, self.m.cols-1), (0, self.m.cols//2), (self.m.rows//2, 0), (self.m.rows//2, self.m.cols-1), (self.m.rows-1, self.m.cols//2)]
		self.subStartList = [(x, 0) for x in range(2, self.m.rows-2)] + [(x, self.m.cols-1) for x in range(2, self.m.rows-2)] + [(0, y) for y in range(2, self.m.rows-2)] + [(self.m.rows-1, y) for y in range(2, self.m.rows-2)]
		self.prob = np.full((self.m.rows, self.m.cols, 9), np.nan, dtype = np.float16)

		self.safeWaiting = set()
		self.flagWaiting = set()
		self.override = []

		return

	#basic action
	#update warn
	def updateHintBlock(self, row, col, iNebr = None):
		flagCount, neighbor = self.m.count(row, col, 'flag', iNebr = iNebr, oNebr = True)
		self.m.warn[row, col] = self.m.hint[row, col] - flagCount
		return

	#assume (row, col) is safe, explore it
	def hintSafeBlock(self, row, col, iNebr = None):
		if self.alive:
			self.m.safe[row, col] = True

			hint, neighbor = self.exploreBlock(row, col, iNebr = iNebr, oNebr = True)
			if hint is False: #dead
				return False
			else:
				self.updateHintBlock(row, col, iNebr = neighbor)
				self.updateNeighborP(row, col, iNebr = neighbor)
				for pos, index in neighbor:
					if not self.m.covered[pos]:
						self.updateNeighborP(pos[0], pos[1])
			return True
		else:
			return False

	#update warn
	def updateFlagBlock(self, row, col, iNebr = None):
		self.m.warn[row, col] = self.m.warn[row, col] - 1
		return

	#assume (row, col) is mine, flag it
	def flagMineBlock(self, row, col, iNebr = None):
		if self.alive:
			self.m.flag[row, col] = True
			self.m.flagCount = self.m.flagCount + 1
			self.prob[row, col] = 1 #TODO: should it be set 1? if optimistic/cautious?
			neighbor = self.checkInNeighbor(row, col, iNebr)
			for pos, index in neighbor:
				self.m.nebr[pos] = self.m.nebr[pos] // self.m.hashCore[row%5, col%5]
				self.m.left[pos] = self.m.left[pos] - 1
				if self.m.left[pos] == 0:
					self.m.done[pos] = True
				if not self.m.covered[pos]:
					self.updateFlagBlock(pos[0], pos[1])
					self.updateNeighborP(pos[0], pos[1])
			return True
		else:
			return False

	#tool function
	#return neighbor
	def checkInNeighbor(self, row, col, iNebr):
		if iNebr is None:
			neighbor = self.m.getNeighbor(row, col)
		else:
			neighbor = iNebr
		return neighbor

	#explore (row, col) and update neighbor's left
	def exploreBlock(self, row, col, iNebr = None, oNebr = False):
#		print('explore %d, %d' %(row, col))
		if self.alive:
			tempHint = self.m.explore(row, col)
			if tempHint is False:
				print('E: solution.player.exploreBlock. What a Terrible Failure!')
				self.alive = False
			#	self.m.visualize(cheat = False)
			#	self.m.visualize(cheat = True)
				neighbor = iNebr

			else: #get a new hint, update neighbor's left #TODO: blind return process
				self.m.hint[row, col] = tempHint
				self.prob[row, col] = 0
				neighbor = self.checkInNeighbor(row, col, iNebr)
				for pos, index in neighbor:
					self.m.nebr[pos[0], pos[1]] = self.m.nebr[pos[0], pos[1]] // self.m.hashCore[row%5, col%5]
					self.m.left[pos] = self.m.left[pos] - 1
					if self.m.left[pos] == 0:
						self.m.done[pos] = True

		else: #dead
			tempHint = False
			neighbor = iNebr
		
		#return
		if oNebr:
			return (tempHint, neighbor)
		else:
			return tempHint

	#calculate neighbor's prob
	def updateNeighborP(self, row, col, iNebr = None):
		if self.m.done[row, col]:
			return False
		
		neighbor = self.checkInNeighbor(row, col, iNebr = iNebr)
		tempProb = self.m.warn[row, col] / self.m.left[row, col]
		chainFlag = False
		for pos, index in neighbor:
			if self.m.covered[pos] and not self.m.flag[pos]:
				self.prob[pos][8-index] = tempProb
				if tempProb == 1:
					self.flagWaiting.add(pos)
					chainFlag = True
				elif tempProb == 0:
					self.safeWaiting.add(pos)
					chainFlag = True
		return chainFlag

	#a block's effective neighbors are all his parent's effective neighbors
	def checkOverride(self):
		self.override = []
		for row in self.m.rows:
			for col in self.m.cols:
				if self.m.done[row, col]:
					continue
				childList = []
				for childRow in range(row-2, row+2):
					if childRow > self.m.rows-1 or childRow < 0:
						continue
					for childCol in range(col-2, col+2):
						if childCol > self.m.cols-1 or childCol < 0:
							continue
						if self.m.done[childRow, childCol]:
							continue
						if self.m.nebr[row, col] % self.m.nebr[childRow, childCol] == 0:
							childList.append((childRow, childCol))
				if childList:
					self.override.append((len(childList), (row, col), childList))
		return self.override

	def getNext(self):
		completeRate = (self.m.blockCount + self.m.flagCount) / (self.m.rows * self.m.cols)
		defaultProb = (self.m.mines - self.m.flagCount) / (self.m.rows * self.m.cols - self.m.blockCount)
		tempProb = np.copy(self.prob)
		tempProb[np.isnan(tempProb)] = defaultProb
		meanProb = tempProb.mean(axis = 2)
		#best start block, not bad block before endgame
		if completeRate < 0.33:
			while self.startList:
				pos = self.startList.pop()
				if self.m.covered[pos] and not self.m.flag[pos]:
					return pos, meanProb[pos]
		#better start block, bad block in middle stage
		if completeRate < 0.1:
			while self.subStartList:
				pos = self.subStartList.pop()
				if self.m.covered[pos] and not self.m.flag[pos]:
					return pos, meanProb[pos]
		#best block in middle stage and endgame
		meanProb[(~self.m.covered) | self.m.flag] = 1
		pos = np.unravel_index(np.argmin(meanProb), meanProb.shape)
		return pos, meanProb[pos]


	#hi-level action
	#stat the game
	def firstStep(self):
		startPos = self.startList.pop()
		tempHint = self.m.start(*startPos)
		self.updateNeighborP(*startPos)
	
		while self.alive and not (self.safeWaiting or self.flagWaiting):
			self.stepOut()
		return self.alive
	
	#1st arm, keep looping with bookkeeping
	def stepByStep(self):
		while self.alive and (self.safeWaiting or self.flagWaiting):
			while self.alive and self.safeWaiting:
				tempPos = self.safeWaiting.pop()
				self.hintSafeBlock(*tempPos)
			while self.alive and self.flagWaiting:
				tempPos = self.flagWaiting.pop()
				self.flagMineBlock(*tempPos)
		return self.alive

	#2nd arm, solve A+B=1 A+B+C=2
	def solveOverride(self):
		pass

	#final arm, ready to die
	def stepOut(self):
		step, prob = self.getNext()
		print(step)
		print('W: solution.player.stepOut. risk (%d, %d)' %(step[0], step[1]))
		if prob * 2 < 1:
			self.hintSafeBlock(*step)
		else:
			self.flagMineBlock(*step)
		return self.alive





if __name__ == '__main__':
	m = frame.board(64, 64, 512)
	p = player(m, chain = True)
	res = p.firstStep()
	while p.alive and ((p.m.blockCount + p.m.flagCount) < (p.m.rows * p.m.cols)) and (p.m.flagCount < p.m.mines):
		res = p.stepByStep()
		while p.alive and ((p.m.blockCount + p.m.flagCount) < (p.m.rows * p.m.cols)) and (p.m.flagCount < p.m.mines) and not (p.safeWaiting or p.flagWaiting):
			p.stepOut()
	# print(res)
	print(m.hint)
	print(m.warn)
	print(m.left)
	# print(m.nebr)
	# print(m.done)
	print(m.blockCount)
	print(m.flagCount)
	m.visualize()
	m.visualize(cheat = True)