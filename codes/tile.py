import numpy as np
from matplotlib import pyplot as plt
from PIL import Image, ImageChops

class tile(object):
    def __init__(self):
        self.size = 16
        
        #color
        self.backColor = [63, 63, 63]
        self.failedBackColor = [0, 255, 255]
        self.uncoveredGridColor = [127, 127, 127]
        self.coveredGridMainColor = [0, 0, 0]
        self.coveredGridSubColor = [127, 127, 127]

        clue1Color = [255, 255, 0]
        clue2Color = [255, 127, 255]
        clue3Color = [0, 255, 255]
        clue4Color = [255, 255, 127]
        clue5Color = [127, 255, 255]
        clue6Color = [255, 127, 127]
        clue7Color = [255, 255, 255]
        clue8Color = [127, 127, 127]
        self.clueColors = [clue1Color, clue2Color, clue3Color, clue4Color, clue5Color, clue6Color, clue7Color, clue8Color]

        self.mineMainColor = [255, 255, 255]
        self.mineSubColor = [0, 0, 0]
        self.flagMainColor = [0, 255, 255]
        self.flagSubColor = [255, 255, 255]

        self.blockWrongColor = [0, 255, 255]

        self.hideColor = [255, 255, 255]

        #shape
        self.backShape = np.asarray([               [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                                                    [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                                                    [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                                                    [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                                                    [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                                                    [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                                                    [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                                                    [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                                                    [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                                                    [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                                                    [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                                                    [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                                                    [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                                                    [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                                                    [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]], dtype = np.bool)

        self.failedBackShape = np.asarray([         [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                                                    [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                                                    [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                                                    [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                                                    [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                                                    [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                                                    [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                                                    [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                                                    [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                                                    [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                                                    [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                                                    [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                                                    [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                                                    [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                                                    [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]], dtype = np.bool)

        self.uncoveredGridShape = np.asarray([      [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                                                    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]], dtype = np.bool)

        self.coveredGridMainShape = np.asarray([    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                                                    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0],
                                                    [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]], dtype = np.bool)

        self.coveredGridSubShape = np.asarray([     [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
                                                    [0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                                                    [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]], dtype = np.bool)

        clue1Shape = np.asarray([                   [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0],
                                                    [0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0],
                                                    [0,0,0,0,0,1,1,1,1,1,1,1,0,0,0,0],
                                                    [0,0,0,0,0,1,1,1,1,1,1,1,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]], dtype = np.bool)

        clue2Shape = np.asarray([                   [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0],
                                                    [0,0,0,1,1,1,1,1,1,1,1,1,1,0,0,0],
                                                    [0,0,0,1,1,1,0,0,0,0,1,1,1,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0],
                                                    [0,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0],
                                                    [0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0],
                                                    [0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0],
                                                    [0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,1,1,1,1,1,1,1,1,1,1,0,0,0],
                                                    [0,0,0,1,1,1,1,1,1,1,1,1,1,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]], dtype = np.bool)

        clue3Shape = np.asarray([                   [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,1,1,1,1,1,1,1,1,1,0,0,0,0],
                                                    [0,0,0,1,1,1,1,1,1,1,1,1,1,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0],
                                                    [0,0,0,0,0,0,1,1,1,1,1,1,0,0,0,0],
                                                    [0,0,0,0,0,0,1,1,1,1,1,1,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0],
                                                    [0,0,0,1,1,1,1,1,1,1,1,1,1,0,0,0],
                                                    [0,0,0,1,1,1,1,1,1,1,1,1,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]], dtype = np.bool)

        clue4Shape = np.asarray([                   [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,1,1,1,0,1,1,1,0,0,0,0],
                                                    [0,0,0,0,0,1,1,1,0,1,1,1,0,0,0,0],
                                                    [0,0,0,0,1,1,1,0,0,1,1,1,0,0,0,0],
                                                    [0,0,0,0,1,1,1,0,0,1,1,1,0,0,0,0],
                                                    [0,0,0,1,1,1,1,1,1,1,1,1,1,0,0,0],
                                                    [0,0,0,1,1,1,1,1,1,1,1,1,1,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]], dtype = np.bool)

        clue5Shape = np.asarray([                   [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,1,1,1,1,1,1,1,1,1,1,0,0,0],
                                                    [0,0,0,1,1,1,1,1,1,1,1,1,1,0,0,0],
                                                    [0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,1,1,1,1,1,1,1,1,1,0,0,0,0],
                                                    [0,0,0,1,1,1,1,1,1,1,1,1,1,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0],
                                                    [0,0,0,1,1,1,1,1,1,1,1,1,1,0,0,0],
                                                    [0,0,0,1,1,1,1,1,1,1,1,1,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]], dtype = np.bool)

        clue6Shape = np.asarray([                   [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0],
                                                    [0,0,0,1,1,1,1,1,1,1,1,1,0,0,0,0],
                                                    [0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,1,1,1,1,1,1,1,1,1,0,0,0,0],
                                                    [0,0,0,1,1,1,1,1,1,1,1,1,1,0,0,0],
                                                    [0,0,0,1,1,1,0,0,0,0,1,1,1,0,0,0],
                                                    [0,0,0,1,1,1,0,0,0,0,1,1,1,0,0,0],
                                                    [0,0,0,1,1,1,1,1,1,1,1,1,1,0,0,0],
                                                    [0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]], dtype = np.bool)

        clue7Shape = np.asarray([                   [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,1,1,1,1,1,1,1,1,1,1,0,0,0],
                                                    [0,0,0,1,1,1,1,1,1,1,1,1,1,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,1,1,1,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,1,1,1,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]], dtype = np.bool)

        clue8Shape = np.asarray([                   [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0],
                                                    [0,0,0,1,1,1,1,1,1,1,1,1,1,0,0,0],
                                                    [0,0,0,1,1,1,0,0,0,0,1,1,1,0,0,0],
                                                    [0,0,0,1,1,1,0,0,0,0,1,1,1,0,0,0],
                                                    [0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0],
                                                    [0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0],
                                                    [0,0,0,1,1,1,0,0,0,0,1,1,1,0,0,0],
                                                    [0,0,0,1,1,1,0,0,0,0,1,1,1,0,0,0],
                                                    [0,0,0,1,1,1,1,1,1,1,1,1,1,0,0,0],
                                                    [0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]], dtype = np.bool)

        self.clueShapes = [clue1Shape, clue2Shape, clue3Shape, clue4Shape, clue5Shape, clue6Shape, clue7Shape, clue8Shape]

        self.mineMainShape = np.asarray([           [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0],
                                                    [0,0,0,0,1,0,1,1,1,1,1,0,1,0,0,0],
                                                    [0,0,0,0,0,1,1,1,1,1,1,1,0,0,0,0],
                                                    [0,0,0,0,1,1,0,0,1,1,1,1,1,0,0,0],
                                                    [0,0,0,0,1,1,0,0,1,1,1,1,1,0,0,0],
                                                    [0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,0],
                                                    [0,0,0,0,1,1,1,1,1,1,1,1,1,0,0,0],
                                                    [0,0,0,0,1,1,1,1,1,1,1,1,1,0,0,0],
                                                    [0,0,0,0,0,1,1,1,1,1,1,1,0,0,0,0],
                                                    [0,0,0,0,1,0,1,1,1,1,1,0,1,0,0,0],
                                                    [0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]], dtype = np.bool)

        self.mineSubShape = np.asarray([            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]], dtype = np.bool)

        self.flagMainShape = np.asarray([           [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0],
                                                    [0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]], dtype = np.bool)

        self.flagSubShape = np.asarray([            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0],
                                                    [0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0],
                                                    [0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]], dtype = np.bool)

        self.blockWrongShape = np.asarray([         [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,1,1,0,0,0,0,0,0,0,0,0,1,1,0],
                                                    [0,0,0,1,1,0,0,0,0,0,0,0,1,1,0,0],
                                                    [0,0,0,0,1,1,0,0,0,0,0,1,1,0,0,0],
                                                    [0,0,0,0,0,1,1,0,0,0,1,1,0,0,0,0],
                                                    [0,0,0,0,0,0,1,1,0,1,1,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,1,1,0,1,1,0,0,0,0,0],
                                                    [0,0,0,0,0,1,1,0,0,0,1,1,0,0,0,0],
                                                    [0,0,0,0,1,1,0,0,0,0,0,1,1,0,0,0],
                                                    [0,0,0,1,1,0,0,0,0,0,0,0,1,1,0,0],
                                                    [0,0,1,1,0,0,0,0,0,0,0,0,0,1,1,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]], dtype = np.bool)

        self.hideShape = np.asarray([               [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0],
                                                    [0,0,0,0,0,1,1,0,0,1,1,0,0,0,0,0],
                                                    [0,0,0,0,0,1,1,0,0,1,1,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                                                    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]], dtype = np.bool)

    #paint a tile
    def __call__(self, covered, mine, clue, hint, flag, hide, beacon = False, cheat = False):
        
        block = np.zeros((self.size, self.size, 3), dtype = np.uint8)

        if beacon:
            block[self.backShape] = [31, 31, 31]
        else:
            block[self.backShape] = self.backColor

        if covered:
            if flag: #covered flag
                if mine: #covered flag mine, correct
                    block[self.flagMainShape] = self.flagMainColor
                    block[self.flagSubShape] = self.flagSubColor
                else: #covered flag not mine, wrong
                    block[self.mineMainShape] = self.mineMainColor
                    block[self.mineSubShape] = self.mineSubColor
                    block[self.blockWrongShape] = self.blockWrongColor
            elif cheat: #get the whole board
                if mine: #covered cheat mine
                    block[self.mineMainShape] = self.mineMainColor
                    block[self.mineSubShape] = self.mineSubColor
                elif 0 < clue < 9: # covered cheat clue
                    block[self.clueShapes[clue-1]] = self.clueColors[clue-1]
            block[self.coveredGridMainShape] = self.coveredGridMainColor
            block[self.coveredGridSubShape] = self.coveredGridSubColor

        else: #explored
            if mine: #uncovered mine, died
                block[self.failedBackShape]  = self.failedBackColor
                block[self.mineMainShape] = self.mineMainColor
                block[self.mineSubShape] = self.mineSubColor
            elif not cheat and hide:
                block[self.hideShape] = self.hideColor
            elif not cheat and 0 < hint < 9: #covered hint
                block[self.clueShapes[hint-1]] = self.clueColors[hint-1]
            elif cheat and 0 < clue < 9:#cheat clue
                block[self.clueShapes[clue-1]] = self.clueColors[clue-1]
            block[self.uncoveredGridShape] = self.uncoveredGridColor

        return block


if __name__ == '__main__':
    b = tile()
    image = b(covered = True, mine = False, clue = 3, hint = 2, flag = False, beacon = True, cheat = True)
    img = Image.fromarray(image) 
    img = ImageChops.invert(img)
    plt.imshow(img)
    plt.show()