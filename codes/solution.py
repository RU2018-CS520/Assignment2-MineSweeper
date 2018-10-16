import numpy as np

import frame

class player(object):
	#player view
	def __init__(self, m, chain = False):
		self.m = m
		self.chain = chain
		self.alive = True
		self.startList = [(0, 0), (self.m.rows-1, 0), (0, self.m.cols-1), (self.m.rows-1, self.m.cols-1), (0, self.m.cols//2), (self.m.rows//2, 0), (self.m.rows//2, self.m.cols-1), (self.m.rows-1, self.m.cols//2)]
		self.prob = np.full((self.m.rows, self.m.cols, 9), np.nan, dtype = np.float16)

		self.safeWaiting = set()
		self.flagWaiting = set()

		return

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
				self.m.left[pos[0], pos[1]] = self.m.left[pos[0], pos[1]] - 1
				if not self.m.covered[pos]:
					self.updateFlagBlock(pos[0], pos[1])
					self.updateNeighborP(pos[0], pos[1])
			return True
		else:
			return False


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
					self.m.left[pos] = self.m.left[pos] - 1

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
		if self.m.left[row, col] == 0:
			self.m.done[row, col] = True
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

#stat the game
def firstStep(p):
	startPos = p.startList.pop()
	tempHint = p.m.start(*startPos)
	p.updateNeighborP(*startPos)

	while p.startList and not (p.safeWaiting or p.flagWaiting):
		tempPos = p.startList.pop()
		p.hintSafeBlock(*tempPos)
	return

#keep looping with bookkeeping
def stepByStep(p):
	while p.alive and (p.safeWaiting or p.flagWaiting):
		while p.alive and p.safeWaiting:
			tempPos = p.safeWaiting.pop()
			p.hintSafeBlock(*tempPos)
		while p.alive and p.flagWaiting:
			tempPos = p.flagWaiting.pop()
			p.flagMineBlock(*tempPos)
	return p.alive
		


if __name__ == '__main__':
	m = frame.board(64, 64, 512)
	p = player(m, chain = True)
	res = firstStep(p)
	res = stepByStep(p)
	print(res)
	print(m.hint)
	print(m.warn)
	print(m.left)
	print(m.blockCount)
	print(m.flagCount)
	m.visualize()
	m.visualize(cheat = True)