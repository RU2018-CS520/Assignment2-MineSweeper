import numpy as np
import itertools

import frame

class player(object):
    #player view
    def __init__(self, m):
        self.m = m
        self.alive = True
        self.startList = [(0, 0), (self.m.rows-1, 0), (0, self.m.cols-1), (self.m.rows-1, self.m.cols-1), (0, self.m.cols//2), (self.m.rows//2, 0), (self.m.rows//2, self.m.cols-1), (self.m.rows-1, self.m.cols//2)]
        self.subStartList = [(x, 0) for x in range(2, self.m.rows-2)] + [(x, self.m.cols-1) for x in range(2, self.m.rows-2)] + [(0, y) for y in range(2, self.m.rows-2)] + [(self.m.rows-1, y) for y in range(2, self.m.rows-2)]
        self.prob = np.full((self.m.rows, self.m.cols, 9), np.nan, dtype = np.float16)

        self.safeWaiting = set()
        self.flagWaiting = set()
        self.override = []
        self.twin = set()
        self.bros = set()
        self.pigeon = set()

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
            if not self.m.covered[row, col]:
                return True
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
            if self.m.flag[row, col]:
                return True
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
#       print('explore %d, %d' %(row, col))
        if self.alive:
            tempHint = self.m.explore(row, col)
            if tempHint is False:
                print('E: solution.player.exploreBlock. What a Terrible Failure!')
                self.alive = False
            #   self.m.visualize(cheat = False)
            #   self.m.visualize(cheat = True)
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
        #return: True: there is a new block waiting for hint or flag; False: no new hint or flag block
        if self.m.done[row, col]:
            return False
        
        neighbor = self.checkInNeighbor(row, col, iNebr = iNebr)
        tempProb = self.m.warn[row, col] / self.m.left[row, col]
        updateFlag = False
        for pos, index in neighbor:
            if self.m.covered[pos] and not self.m.flag[pos]:
                self.prob[pos][8-index] = tempProb
                if tempProb == 1:
                    self.flagWaiting.add(pos)
                    updateFlag = True
                elif tempProb == 0:
                    self.safeWaiting.add(pos)
                    updateFlag = True
        return updateFlag

    #override function
    #a block's effective neighbors are all his parent's effective neighbors
    def checkOverride(self):
        #return override relation
        self.override = []
        #for each inconclusive hint block
        for row in range(self.m.rows):
            for col in range(self.m.cols):
                if self.m.done[row, col] or self.m.covered[row, col]:
                    continue
                childList = []
                #check 5*5 neighbor inconclusive hint blocks
                for childRow in range(row-2, row+3):
                    if childRow > self.m.rows-1 or childRow < 0:
                        continue
                    for childCol in range(col-2, col+3):
                        if childCol > self.m.cols-1 or childCol < 0:
                            continue
                        if childRow == row and childCol == col:
                            continue
                        if self.m.done[childRow, childCol] or self.m.covered[childRow, childCol]:
                            continue
                        #if this block % neighbor == 0, neighbor's neighbor is in this neighbor
                        if self.m.nebr[row, col] % self.m.nebr[childRow, childCol] == 0:
                            childList.append((childRow, childCol))
                if childList:
                    self.override.append((len(childList), (row, col), childList))
        return self.override

    #solve override based on copy prob from child
    def solveOverride(self, tempLenLim, pPos, cPosList):
        #return: True: new blocks solved; False: nothing
        for cPosListLim in itertools.combinations(cPosList, tempLenLim):
            prob = np.zeros((3,3), dtype = np.float16)
            mark = np.zeros((3,3), dtype = np.bool)
            conflictFlag = False
            pLeftNebr = []
            sumProb = 0.
            #copy prob
            for cPos in cPosListLim:
                conflictFlag, prob, mark = self.fillCProb(pPos, cPos, prob, mark)
                if conflictFlag:
                    break
            if conflictFlag:
                continue
            #calculate new left prob
            pNeighbor = self.m.getNeighbor(*pPos)
            for pos, index in pNeighbor:
                relativeRow = pos[0] - pPos[0] + 1
                relativeCol = pos[1] - pPos[1] + 1
                if self.m.covered[pos] and not self.m.flag[pos]:
                    if mark[relativeRow, relativeCol]:
                        sumProb = sumProb + prob[relativeRow, relativeCol]
                    else: #not marked, p's unique neighbor
                        pLeftNebr.append(pos)
            if pLeftNebr:
                pLeftWarn = self.m.warn[pPos] - sumProb
                pLeftProb = pLeftWarn / len(pLeftNebr)
                if pLeftProb >= 1: #TODO: could pLeftProb > 1?
                    self.flagWaiting.update(pLeftNebr)
                    return True
                elif pLeftProb <= 0: #TODO: could pLeftProb < 0?
                    self.safeWaiting.update(pLeftNebr)
                    return True
            else: #p have the same neighbor with childs, maybe useful for blind, optimistc, cautious
                continue
        return False

    #fill child's prob
    def fillCProb(self, pPos, cPos, prob, mark):
        #return: True: there is a conflict prob; False: no conflick
        cProb = self.m.warn[cPos] / self.m.left[cPos]
        cNeighbor = self.m.getNeighbor(*cPos)
        for pos, index in cNeighbor:
            relativeRow = pos[0] - pPos[0] + 1
            relativeCol = pos[1] - pPos[1] + 1
            if self.m.covered[pos] and not self.m.flag[pos]:
                if mark[relativeRow, relativeCol]:
                    if cProb != prob[relativeRow, relativeCol]:
                        return True, prob, mark
                prob[relativeRow, relativeCol] = cProb
                mark[relativeRow, relativeCol] = True
        return False, prob, mark


    #twin function
    #a block's hint is equal or something to its neighbor's
    def checkTwin(self):
        self.twin = set()
        self.bros = set()
        self.pigeon = set()
        for row in range(self.m.rows):
            for col in range(self.m.cols):
                if self.m.done[row, col] or self.m.covered[row, col]:
                    continue
                neighbor = self.m.getNeighbor(row, col)
                for bPos, index in neighbor:
                    if self.m.done[bPos] or self.m.covered[bPos]:
                        continue
                    if self.m.hint[row, col] == self.m.hint[bPos]:
                        tempTwin = frozenset([(row, col), bPos])
                        self.twin.add(tempTwin)
                    elif (self.m.hint[row, col] == self.m.hint[bPos] + 1) or (self.m.hint[row, col] == self.m.hint[bPos] + 2):
                        tempBros = ((row, col), bPos)
                        self.bros.add(tempBros)
                    elif self.m.hint[row, col] == self.m.hint[bPos] + 5:
                        tempPigeon = ((row, col), bPos)
                        self.pigeon.add(tempPigeon)
                    elif self.m.hint[row, col] == self.m.hint[bPos] + 3:
                        if row == bPos[0] or col == bPos[1]:
                            tempPigeon = ((row, col), bPos)
                            self.pigeon.add(tempPigeon)
        return bool(self.twin) or bool(self.bros) or bool(self.pigeon)

    #solve twin relation based on symmetric
    def solveTwin(self, oPos, yPos):
        oNeighbor = self.m.getNeighbor(*oPos)
        yNeighbor = self.m.getNeighbor(*yPos)
        oNeighbor = set([pos[0] for pos in oNeighbor]) - {yPos}
        yNeighbor = set([pos[0] for pos in yNeighbor]) - {oPos}
        #compensate border blocks
        oSafe = 8 - len(oNeighbor)
        ySafe = 8 - len(yNeighbor)
        overComp = min(oSafe, ySafe)
        oSafe = oSafe - overComp
        ySafe = ySafe - overComp
        #get unique neighbor
        oUniqNebr = list(oNeighbor - yNeighbor)
        yUniqNebr = list(yNeighbor - oNeighbor)
        #count safe flag and inconclusive blocks WARN: do not use self.m.cound because uniqNebr can be empty
        oFlag = 0
        yFlag = 0
        oInconclusive = []
        yInconclusive = []
        solveFlag = False

        for oNebrPos in oUniqNebr:
            if self.m.safe[oNebrPos]:
                oSafe = oSafe + 1
            elif self.m.flag[oNebrPos]:
                oFlag = oFlag + 1
            else:
                oInconclusive.append(oNebrPos)
        
        for yNebrPos in yUniqNebr:
            if self.m.safe[yNebrPos]:
                ySafe = ySafe + 1
            elif self.m.flag[yNebrPos]:
                yFlag = yFlag + 1
            else:
                yInconclusive.append(yNebrPos)
        
        if not oInconclusive and not yInconclusive: # not this case
            return False
        #symmetric
        safeCount = max(oSafe, ySafe)
        flagCount = max(oFlag, yFlag)
        if safeCount + flagCount == max(len(oUniqNebr), len(yUniqNebr)):
            if oInconclusive:
                if oSafe == safeCount:
                    self.flagWaiting.update(oInconclusive)
                    solveFlag = True
                elif oFlag == flagCount:
                    self.safeWaiting.update(oInconclusive)
                    solveFlag = True
            if yInconclusive:
                if ySafe == safeCount:
                    self.flagWaiting.update(yInconclusive)
                    solveFlag = True
                elif yFlag == flagCount:
                    self.safeWaiting.update(yInconclusive)
                    solveFlag = True
        return solveFlag
        #fill 4*4 board
        #check unique neighbor
        #compare unique neighbor

    #solve bros relation based on symmetric
    def solveBros(self, oPos, yPos):
        oNeighbor = self.m.getNeighbor(*oPos)
        yNeighbor = self.m.getNeighbor(*yPos)
        oNeighbor = set([pos[0] for pos in oNeighbor]) - {yPos}
        yNeighbor = set([pos[0] for pos in yNeighbor]) - {oPos}
        #compensate border blocks
        oSafe = 8 - len(oNeighbor)
        ySafe = 8 - len(yNeighbor)
        overComp = min(oSafe, ySafe)
        oSafe = oSafe - overComp
        ySafe = ySafe - overComp
        #get unique neighbor
        oUniqNebr = list(oNeighbor - yNeighbor)
        yUniqNebr = list(yNeighbor - oNeighbor)
        #count safe flag and inconclusive blocks WARN: do not use self.m.cound because uniqNebr can be empty
        oFlag = 0
        yFlag = 0
        oInconclusive = []
        yInconclusive = []
        solveFlag = False

        for oNebrPos in oUniqNebr:
            if self.m.safe[oNebrPos]:
                oSafe = oSafe + 1
            elif self.m.flag[oNebrPos]:
                oFlag = oFlag + 1
            else:
                oInconclusive.append(oNebrPos)
        
        for yNebrPos in yUniqNebr:
            if self.m.safe[yNebrPos]:
                ySafe = ySafe + 1
            elif self.m.flag[yNebrPos]:
                yFlag = yFlag + 1
            else:
                yInconclusive.append(yNebrPos)
        
        if not oInconclusive and not yInconclusive: # not this case
            return False
        #symmetric
        #TODO: control difference
        diff = self.m.hint[oPos] - self.m.hint[yPos] #older bro has a larger hint
        safeCount = max(oSafe, ySafe - diff)
        flagCount = max(oFlag, yFlag + diff)
        if safeCount + flagCount == max(len(oUniqNebr), len(yUniqNebr)):
            if oInconclusive:
                if oSafe == safeCount:
                    self.flagWaiting.update(oInconclusive)
                    solveFlag = True
                elif oFlag == flagCount:
                    self.safeWaiting.update(oInconclusive)
                    solveFlag = True
            if yInconclusive:
                if ySafe - diff == safeCount:
                    self.flagWaiting.update(yInconclusive)
                    solveFlag = True
                elif yFlag + diff == flagCount:
                    self.safeWaiting.update(yInconclusive)
                    solveFlag = True
        return solveFlag

    #solve pigeon pairs relation based on symmetric
    def solvePigeon(self, oPos, yPos):
        oNeighbor = self.m.getNeighbor(*oPos)
        yNeighbor = self.m.getNeighbor(*yPos)
        oNeighbor = set([pos[0] for pos in oNeighbor]) - {yPos}
        yNeighbor = set([pos[0] for pos in yNeighbor]) - {oPos}
        oUniqNebr = list(oNeighbor - yNeighbor)
        yUniqNebr = list(yNeighbor - oNeighbor)
        solveFlag = False
        for oNebrPos in oUniqNebr:
            if not self.m.flag[oNebrPos]:
                self.flagWaiting.add(oNebrPos)
                solveFlag = True
        for yNebrPos in yUniqNebr:
            if not self.m.safe[yNebrPos]:
                self.safeWaiting.add(yNebrPos)
                solveFlag = True
        return solveFlag


    #leap of faith function
    #get a safer next block to open
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
            self.leapOfFaith()
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
    def stepAside(self):
        solveFlag = False
        #get override relation
        if self.checkOverride():
            self.override.sort() #from simple to complex
            effectiveLen = 25
            #solve override relation
            while self.override:
                tempLen, pPos, cPosList = self.override.pop(0)
                if effectiveLen < tempLen: #discard more complex override
                    break
                #if conflict, try subset
                for tempLenLim in range(tempLen, 0, -1):
                    solved = self.solveOverride(tempLenLim, pPos, cPosList)
                    if solved:
                        print('stepAside (%d, %d) %d' %(pPos[0], pPos[1], tempLenLim))
                        # self.m.visualize()
                        # self.m.visualize(cheat = True)
                        effectiveLen = tempLen #no more complex relation need to do
                        solveFlag = True
                        break
        return solveFlag

    #3rd arm, solve F322F
    def keepInStep(self):
        solveFlag = False
        if self.checkTwin():
            while self.twin:
                tempTwin = self.twin.pop()
                oPos, yPos = tuple(tempTwin)
                solved = self.solveTwin(oPos, yPos)
                if solved:
                    print('keepInStep twin (%d, %d), (%d, %d)' %(oPos[0], oPos[1], yPos[0], yPos[1]))
                    solveFlag = True
            while self.bros:
                tempBros = self.bros.pop()
                oPos, yPos = tempBros
                solved = self.solveBros(oPos, yPos)
                if solved:
                    print('keepInStep bros (%d, %d), (%d, %d)' %(oPos[0], oPos[1], yPos[0], yPos[1]))
                    solveFlag = True
            while self.pigeon:
                tempPigeon = self.pigeon.pop()
                oPos, yPos = tempPigeon
                solved = self.solvePigeon(oPos, yPos)
                if solved:
                    print('keepInStep pigeon (%d, %d), (%d, %d)' %(oPos[0], oPos[1], yPos[0], yPos[1]))
                    solveFlag = True
        return solveFlag

    #final arm, ready to die
    def leapOfFaith(self):
        # self.m.visualize()
        # self.m.visualize(cheat = True)
        step, prob = self.getNext()
        print('W: solution.player.leapOfFaith. risk (%d, %d)' %(step[0], step[1]))
        if prob * 2 < 1:
            self.hintSafeBlock(*step)
        else:
            self.flagMineBlock(*step)
        return self.alive





if __name__ == '__main__':
    m = frame.board(64, 64, 820)
    p = player(m)
    res = p.firstStep()
    while p.alive and ((p.m.blockCount + p.m.flagCount) < (p.m.rows * p.m.cols)) and (p.m.flagCount < p.m.mines):
        res = p.stepByStep()
        res = p.stepAside()
        if res:
            continue
        res = p.keepInStep()
        if res:
            continue
        while p.alive and ((p.m.blockCount + p.m.flagCount) < (p.m.rows * p.m.cols)) and (p.m.flagCount < p.m.mines) and not (p.safeWaiting or p.flagWaiting):
            p.leapOfFaith()
            if p.alive:
                res = p.stepAside()
                if res:
                    break
                res = p.keepInStep()
                if res:
                    break
    # print(res)
    # print(m.hint)
    # print(m.warn)
    # print(m.left)
    # print(m.nebr)
    # print(m.done)
    print(m.blockCount)
    print(m.flagCount)
    print('%.2f%%' %((p.m.blockCount + p.m.flagCount)*100 / (p.m.rows * p.m.cols),))
    m.visualize()
    m.visualize(cheat = True)