# frame
representation of minesweeper
## class board
representation of minesweeper board
### member varibles:
```
basic
	int rows in [2 : inf]: size of board
	int cols in [2 : inf]: size of board
	int mines in [1 : rows*cols-1]: the number of mines
	bool newGame:
		True: board has not been initalized;
		False: board has been built up
	bool blind:
		True: sometimes hint = None, rather than hint = clue;
		False: normal sweeper
	bool optimistic:
		True: hint <= clue;
		False: normal sweeper
	bool cautious:
		True: hint >= clue;
		False: normal sweeper
	class tile.tile tile: rudimentary visualization tool
board:
	np.ndarray covered with dtype = np.bool:
		True: this block is not explored;
		False: this block has been explorerd
	np.ndarray _mine with dtype = np.bool:
		True: this block is a mine;
		False: this block is safe
	np.ndarray _clue with dtype = np.unit8: number of neighbor mines
	np.ndarray flag with dtype = np.bool:
		True: this block is regarded as a mine by agents;
		False: inconclusive or safe
	np.ndarray safe with dtype = np.bool:
		True: this block is regarded as safe block by agents;
		False: inconclusive or flag
	np.ndarray hint with dtype = np.uint8: clue got by agents
	np.ndarray warn with dtype = np.uint8: clue - neighbor's flag
	np.ndarray left with dtype = np.uint8: number of inconclusive neighbor
	np.ndarray nebr with dtype = np.uint64: hash of inconclusive blocks
	np.ndarray done with dtype = np.bool: 
		True: all neighbor explored or flaged
		False: still have inconclusive neighbor
statistic:
	int flagCount in [0 : inf]: number of flaged block
	int blockCount in [0 : inf]: number of explored block
tool:
	np.ndarray hashCore with dtype = np.uint8: compute nebr
```
### member functions:
#### action functions:
```
start(): open the first block (row, col), get returned hint
	in:
		int row: start position
		int col: start position
	out:
		int hint[row, col]
explore(): open (row, col), die or get returned hint
	in:
		int row: position
		int col: position
	out:
		int hint[row, col]
visualize(): print the board
	in:
		int beacon [1 : inf]: interval of beacons; 
			0: no beacon
		bool cheat:
			True: god view;
			False: player view
	out:
		PIL.Image image: board image
count(): get the number of key neighbors
	in:
		int row: position
		int col: position
		str key in {'covered', '_mine', 'flag', 'safe'}: key to count
		list iNebr with element ((row, col), index): input processed neighbor.
			None: auto-generate neighbor
		bool oNebr:
			True: also return neighbor;
			False: only return count
	out:
		int count in [0 : 8]: the number of key neighbors
		list oNebr with element ((row, col), index): this block's neighbor
```
#### tool functions:
```
build(): initalize the board
	in:
		int row: start position
		int col: start position
	out:
		None
getNeighbor(): generate neighbor of (row ,col)
	in:
		int row: position
		int col: position
	out:
		list neighbor with element ((row, col), index): this block's neighbor
xy2ord(): transform (x, y) to num
	in:
		int row: position
		int col: position
	out:
		int num: position
ord2xy(): transform num to (x, y)
	in:
		int num: position
	out:
		int row: position
		int col: position
```
### usage:
build and start a minesweeper
```
import frame
m = frame.board(10, 10, 10)
m.start(m.rows-1,m.cols//2)
m.visualize(cheat = True)
```

# solution
functions to solve minesweeper
## class player:
representation of player view
### member variables
```
basic:
	frame.board m: minesweeper board
	bool alive:
		True: safe, continue;
		False: died, stop sweeping
	list startList with element (row, col): some good start position
	list subStarList with element (row, col): some not bad start postion
	np.ndarray prob with shape = (m.rows, m.cols, 9): mine probablity from this block's neighbor view
waiting list:
	set safeWaiting with element (row, col): blocks must be safe, waiting for explore
	set flagWaiting with element (row, col): blocks must be mine, waiting for flag
	list override with element (pPos, [cPos], cNum): block groups with override relation
	set twin with element frozenset{oPos, yPos}: block pairs with twin relation
	set bros with element (oPos, yPos): block pairs with brother relation
	set pigeon with element (oPos, yPos): block pairs with pigeon twin relation
	set inconclusive with element (row, col): inconclusive block adjacent to a hint
record:
	list history with element (pos, operation): record of each step
```
### member functions:
#### first step:
start the game
```
firstStep(): keep open blocks until find a good start situation
	in:
		None
	out:
		bool alive
```
#### step by step:
main functions to keep sweeping, based on bookkeeping
```
stepByStep(): looping with bookkeeping
	in:
		None
	out:
		bool alive
hintSafeBlock(): assume (row, col) is safe, explore it
	in:
		int row:
		int col:
		list iNebr:
	out:
		bool res:
			True: successfully explored
			False: died
updateHintBlock(): update new explored block's warn
	in:
		int row:
		int col:
		list iNebr:
	out:
		None
flagMineBlock(): assume (row, col) is mine, flag it
	in:
		int row:
		int col:
		list iNebr:
	out:
		bool res:
			True: succefully flaged
			False: died
updateFlagBlock(): update new flaged block's neighbor warn
	in: 
		int row:
		int col:
		list: iNebr:
	out:
		None
```
#### step aside:
functions to solve override relation, like A+B=1 A+B+C=2, based on pattern recognization
```
stepAside(): try to solve override relation
	in:
		None
	out:
		bool solveFlag:
			True: new block has been solved
			False: no new block solved
checkOverride(): find groups of override relation
	in:
		None
	out:
		set override:
solveOverrid(): solve a group of override relation (pPos, [cPos], cNum) with limitation of cNum
	in:
		int tempLenLim in [1 : cNum]: limit of cNum
		tuple pPos = (row, col): parent position
		list cPosList with element (row, col): child position
	out:
		bool solveFlag:
			True: new block has been solved
			False: no new block solved
fillCProb(): fill child's probablity to 
	in:
		tuple pPos = (row, col): parent position
		tuple cPos = (row, col): child position
		np.ndarray prob with shape = (3, 3) dtype = np.float16: probablity of parent's neighbor
		np.ndarray mark with shape = (3, 3) dtype = np.bool:
			True: this block is filled
			False: not filled
	out:
		bool conflict:
			True: a block with 2 different probablity
			False: no conflict, continue
		np.ndarray prob with shape = (3, 3) dtype = np.float16: probablity of parent's neighbor
		np.ndarray mark with shape = (3, 3) dtype = np.bool:
			True: this block is filled
			False: not filled
```
#### keep in step:
functions to solve twin, bros and pigeon relation, like F322F, based on pattern recognization
```
keepInStep(): try to solve twin-like relation
	in:
		None
	out:
		bool solveFlag:
			True: new block has been solved
			False: no new block solved
checkTwin(): find pairs of twin-like relation
	in:
		None
	out:
		bool findFlag:
			True: find pairs of twin-like realtion
			False: no pairs exist
solveTwin(): solve a pair of twin relation
	in:
		tuple oPos: older one's position
		tuple yPos: younger one's position
	out:
		bool soloveFlag:
solveBros(): solve a pair of bros relation
	in:
		tuple oPos:
		tuple yPos:
	out:
		bool soloveFlag:
solvePigeon(): solve a pair of pigeon twin relation
	in:
		tuple oPos:
		tuple yPos:
	out:
		bool soloveFlag:
```
#### elixir:
proof by contradiction. theoretically it can do anything we can do at a given board
```
elixir(): try to solve inconclusive blocks
	in:
		int rangeLim [1 : inf]: max search range of proof by contradiction
			None: auto adapt 
		int iterLim [1 : inf]: max number of trying to solve
			None: no limit
	out:
		bool solveFlag
getInconclusive(): get all inconclusive block adjacent to a hint
	in:
		None
	out:
		set inconclusive:
suppose(): assume (row, col) is blockType, check whether contradict
	in:
		int row:
		int col:
		str blockType in {'flag', 'safe'}: assumed block type
		int rangeLim [1 : inf]: max search range of proof by contradiction
	out:
		bool consistFlag:
			True: consist
			False: contradiction
checkAssumedHint(): check assumedBoard whether consist
	in:
		int row: assumed block position
		int col: assumed block position
		np.ndarray assumedBoard shape = (2*rangeLim+1, 2*rangeLim+1) dtype = np.bool: an assumed distribution of mines
		int rangeLim [1 : inf]: max search range of proof by contradiction
	out:
		bool consistFlag:
			True: consist
			False: contradiction
```
#### leap of faith:
get out of dead end. solve or die
```
leapOfFaith(): last choice, open an inconclusive block at risk
	in:
		None
	out:
		bool alive:
getNext(): find a block worth taking risk to open
	in:
		None
	out:
		tuple pos:
		float prob: probablity of mine
```
#### tool functions:
```
checkInNeighbor(): check iNebr whether valid
	in:
		int row:
		int col:
		list iNebr:
	out:
		neighbor
exploreBlock(): explore (row, col), update neighbor's left
	in:
		int row:
		int col:
		list iNebr:
		bool oNebr:
	out:
		int hint: hint of (row, col)
		list neighbor:
updateNeighborP(): update (row, col) neighbor's probablity
	in:
		int row:
		int col:
		list iNebr:
	out:
		bool updateFlag:
			True: probablity updated
			False: no update
solve(): use first step, step by step, step aside, elixir, leap of faith to solve minesweeper
	in:
		None
	out:
		float completeRate: percentage of completation
```
### usage:
solve a minesweeper
```
import frame
import solution
m = frame.board(64, 64, 820)
p = player(m)
completeRate = p.solve()
```