# Uncertainty Explanation

There are 3 different cases:
1. Blind: when a cell is selected to be uncovered, if the cell is ‘clear’ you only reveal a clue about the surrounding cells with some probability. 
2. Optimistic: When a cell is selected to be uncovered, the revealed clue is less than or equal to the true number of surrounding mines.
3. Cautious: When a cell is selected to be uncovered, the revealed clue is greater than or equal to the true number of surrounding mines.

Actually, these 3 cases can be divided into 2 cases:
1. Blind: some safe blocks will not return hints, but all returned hints are reliable.
2. Fuzzy: returned hints are not reliable, but all safe blocks will return hints.

There are 2 different strategies to deal with them.

## Blind
Since all returned hints are reliable, we can just ignore those hidden (safe but not returned) blocks when solving minesweeper.

Note that even though we can figure out some hidden blocks' hint by `stepAside` and `keepInStep`, but they will not provide more information. Once we can figure out a block's real hint, we must have known everything about its neighbors. But the hint can only provide the information about its neighbors. Hence, it makes no sense to figure out a hidden block's hint.

Here are some screenshots of this case. (See Fig. 1 and Fig. 2.)

![Fig. 1](https://lh3.googleusercontent.com/WLsIJW0RvxTTgKyw2ypmxgC8u7x5Kb45joCBV-swIBwUtPPUDNBPvt64hURuyQbVY2f_7x7Vitkf "Fig. 1")

Fig. 1: a 64 by 64 board with 820 mines and 0.1 blind rate.

![Fig. 2](https://lh3.googleusercontent.com/iutQICz5AqfCOu2-A03zY8wsipYNydDVjbVFfFnlXVhfo1t2wdoUiEvc-ezr5OC68D4crogtfyb1 "FIg. 2")

Fig. 2: a 64 by 64 board with 512 mines and 0.15 blind rate.

Note that a 64 by 64 board with 512 mines and less than 0.1 blind rate are not interesting because most of them can be solved. (See Fig. 3)

![Fig. 3](https://lh3.googleusercontent.com/iSgJkaPsVNA8XnrAWUWJtUFpfuvmZo7j973KN4jhYke0acIExwXcs7fmvHIMLE1siDo4yQj6JsHK "Fig. 3")

Fig. 3 a 64 by 64 board with 512 mines and 0.1 blind rate.

## Fuzzy
Instead of directly using `clue`, which equals to `hint` , we can calculate `prob` by using $E(clue|hint)$.

Here is how to calculate $E(clue | hint)$:

Say it is the case of "cautious". 

$P(clue | hint) = \frac{P(clue, hint)}{P(hint)}$

Say $P(hint) = \frac{1}{\alpha}$:
$P(clue | hint) = \alpha \sum\limits_{clues}P(hint | clues) P(clues)$

Notice that $P(hint | clue) = \frac{1}{9-clues}$ because of unifrom distribution.
$P(clue | hint) = \alpha \sum\limits_{clues}\frac{1}{9-clues} P(clues)$
$P(clues) = C_{left}^{clues-flag}mineRate^{clues-flag}(1-mineRate)^{left-(clues-flag))}$, where $left$ is the number of uncertain neighbor blocks, $flag$ is the number of neighbor flag blocks, and $mineRate = \frac{mines - flagCount}{rows \times cols - blockCount}$

Therefore, $P(clue | hint) = \alpha \sum\limits_{clues = flag}^{flag+left} \frac{1}{9-clues}C_{left}^{clues-flag}mineRate^{clues-flag}(1-mineRate)^{(left-(clues-flag))}$

$\alpha = \frac{1}{\sum\limits_{clues=flag}^{flag+left}P(clues|hint)}$

Since we can compute $P(clue|hint)$, it is easy to compute $E(clue|hint) = clue \times P(clue|hint)$.

(If it is the case of "optimistic": $P(hint | clue) = \frac{1}{clues}$, and other formulas will not change.)

Since we have $E(clue|hint)$ we can easily use `solution` to solve this board. If we would like to take some risks, instead of waiting for probabilities to become 0 or 1, we can set a margin, say 0.05, to regard those probabilities less than 0.05 as 0, and greater than 0.95 as 1.

However, unfortunately, I do not have enough time to implement this idea and test it. But I believe it will work.