import frame

class player(object):
	def __init__(self, m, chain = False):
		self.m = m
		self.chain = chain
		self.alive = True
		self.safeList = []
		self.startList = [(0, 0), (self.m.rows-1, 0), (0, self.m.cols-1), (self.m.rows-1, self.m.cols-1), (0, self.m.cols//2), (self.m.rows//2, 0), (self.m.rows//2, self.m.cols-1), (self.m.rows-1, self.m.cols//2)]
		return


	#if (row, col) no warn or no left, all neighbor are conclusive
	def updateChain(self, row, col, iNebr = None):
		print('updateChain %d, %d' %(row, col))
		print('warn %d, left %d' %(self.m.warn[row, col], self.m.left[row, col]))
		if self.alive:
			chainFlag = False
			if self.m.warn[row, col] == 0: #no warn, all unexplored neighbor safe
				chainFlag = self.setNeighborSafe(row, col, iNebr)
				chainFlag = True
			elif self.m.left[row, col] == self.m.hint[row, col]: #no inconclusive, all unexplored neighbor flag
				chainFlag = self.setNeighborFlag(row, col, iNebr)
				chainFlag = True
			return chainFlag

		else: #dead
			return False

	#empty function, chain to check new flag block's  neighbor's warns
	def updateFlagBlock(self, row, col, iNebr = None):
		print('updateFlagBlock %d, %d' %(row, col))
		if self.alive:
			flagCount, neighbor = self.m.count(row, col, 'flag', iNebr = iNebr, oNebr = True)
			self.m.warn[row, col] = self.m.hint[row, col] - flagCount

			chainFlag = False
			if self.m.left[row, col] == 0: #all neighbor explored or flaged, done
				self.m.done[row, col] = True

			else: #still neighbor
				if self.chain:
					neighbor = self.checkInNeighbor(row, col, iNebr)
					for pos in neighbor:
						chainFlag = chainFlag or self.updateChain(row, col, iNebr = neighbor)
			return chainFlag

		else: #dead
			return False

	#update new hint block's warn
	def updateHintBlock(self, row, col, iNebr = None):
		print('updateHintBlock %d, %d' %(row, col))
		if self.alive:
			flagCount, neighbor = self.m.count(row, col, 'flag', iNebr = iNebr, oNebr = True)
			self.m.warn[row, col] = self.m.hint[row, col] - flagCount
		
			chainFlag = False
			if self.m.left[row, col] == 0: #all neighbor explored or flaged, done
				self.m.done[row, col] = True

			else: #still neighbor, update this block's warn
				if self.chain:
					chainFlag = self.updateChain(row, col, iNebr = neighbor)
					for pos in neighbor:
						chainFlag = self.updateChain(pos[0], pos[1])
			return chainFlag

		else: #dead
			return False

	#set (row, col) flag
	def setBlockFlag(self, row, col, iNebr = None):
		print('setBlockFlag %d, %d' %(row, col))
		# print((row, col))
		# print(p.m.hint)
		# print(p.m.warn)
		# p.m.visualize()
		if self.alive:
			self.m.flag[row, col] = True
			self.m.flagCount = self.m.flagCount + 1
			chainFlag = False
			neighbor = self.checkInNeighbor(row, col, iNebr)
			for pos in neighbor:
				if not self.m.covered[pos]: #decreas explored neighbor's warn
					if self.chain:
						neighbor = self.updateFlagBlock(pos[0], pos[1])
					else:
						self.m.warn[pos] = self.m.warn[pos] - 1
			return chainFlag

		else: #dead
			return False


	#set (row, col) safe
	def setBlockSafe(self, row, col, iNebr = None):
		print('setBlockSafe %d, %d' %(row, col))
		# print((row, col))
		# print(p.m.hint)
		# print(p.m.warn)
		# p.m.visualize()
		if self.alive:
			self.m.safe[row, col] = True

			chainFlag = False
			if self.chain: #explore this block and update this block
				hint, neighbor = self.exploreBlock(row, col, iNebr = iNebr, oNebr = True)
				if hint is False: #dead
					return False
				else:
					chainFlag = chainFlag or self.updateHintBlock(row, col, iNebr = neighbor)
			else: #add to safeList waiting to be explored
				self.safeList.append((row, col))
			return chainFlag

		else: #dead
			return False

	def setNeighborFlag(self, row, col, iNebr = None):
		print('setNeighborFlag %d, %d' %(row, col))
		if self.alive:
			neighbor = self.checkInNeighbor(row, col, iNebr)
			chainFlag = False
			for pos in neighbor:
				if self.m.covered[pos] and not self.m.flag[pos]: #set unexplored block flag
					chainFlag = chainFlag or self.setBlockFlag(pos[0], pos[1])
			return chainFlag
		else: #dead
			return False

	#set all unexplored neighbor of (row, col) safe
	def setNeighborSafe(self, row, col, iNebr = None):
		print('setNeighborSafe %d, %d' %(row, col))
		if self.alive:
			neighbor = self.checkInNeighbor(row, col, iNebr)
			chainFlag = False
			for pos in neighbor:
				if self.m.covered[pos] and not self.m.flag[pos]: #set unexplored block safe
					chainFlag = chainFlag or self.setBlockSafe(pos[0], pos[1])
			return chainFlag
		else: #dead
			return False

	#explore (row, col) and update neighbor's left
	def exploreBlock(self, row, col, iNebr = None, oNebr = False):
		print('explore %d, %d' %(row, col))
		if self.alive:
			tempHint = self.m.explore(row, col, blind = self.m.blind, optimistic = self.m.optimistic, cautious = self.m.cautious)
			if tempHint is False:
				print('E: solution.player.exploreBlock. What a Terrible Failure!')
				self.alive = False
			#	self.m.visualize(cheat = False)
			#	self.m.visualize(cheat = True)
				neighbor = iNebr

			else: #get a new hint, update neighbor left #TODO: blind return process
				self.m.hint[row, col] = tempHint
				neighbor = self.checkInNeighbor(row, col, iNebr)
				for pos in neighbor:
					self.m.left[pos] = self.m.left[pos] - 1

		else: #dead
			tempHint = False
			neighbor = iNebr
		
		#return
		if oNebr:
			return (tempHint, neighbor)
		else:
			return tempHint


	#tool function
	def checkInNeighbor(self, row, col, iNebr):
		if iNebr is None:
			neighbor = self.m.getNeighbor(row, col)
		else:
			neighbor = iNebr
		return neighbor

def makeAMove(p):
	startPos = p.startList.pop()
	tempHint = p.m.start(*startPos)
	chainFlag = p.updateChain(startPos[0], startPos[1])

	while not chainFlag:
		tempPos = p.startList.pop()
		tempHint, neighbor = p.exploreBlock(*tempPos, oNebr = True)
		if tempHint is False:
			return False
		else:
			chainFlag = chainFlag or p.updateHintBlock(*tempPos, iNebr = neighbor)


if __name__ == '__main__':
	m = frame.board(10, 10, 10)
	p = player(m, chain = True)
	res = makeAMove(p)
	print(res)
	m.visualize()
	m.visualize(cheat = True)
	print(m.hint)
	print(m.warn)
	print(m.left)