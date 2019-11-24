import os
from panda3d.core import *

MAINDIR = Filename.from_os_specific(os.getcwd())

class SaveSim:
    def __init__(self):
        self.PositionalData = [] # empty list, will contain each block's position for each frame
        self.ColorScaleData = [] # empty list, contains the colorScale data (format = r,g,b,a)
        self.ArrayDim = () # empty tuple
    def AddFrameData(self,PositionalData,ColorScaleData):
        '''
        adds all the data contained in one frame to the PositionalData and ColorScaleData lists
        '''
        self.PositionalData.append(PositionalData)
        self.ColorScaleData.append(ColorScaleData)
        self.ArrayDim = (len(self.PositionalData[0]),len(self.PositionalData[0][0]))
        return None
    def CreateScene(self,renderBuffer,scale):
        '''
        Creates the models and components of the scene that will be used later by the read() function
        '''
        self.content = [[loader.loadModel(str(MAINDIR)+"/files/wave_part_small.egg") for x in range(self.ArrayDim[1])] for y in range(self.ArrayDim[0])]
        for i in self.content:
            for j in i:
                j.reparentTo(renderBuffer)
                j.setScale(scale)
    def read(self,frame): # Warning !! CreateScene must be executed first
        '''
        basically reads and renders the requested frame
        '''
        if int(frame) == frame:
            frame = int(frame)
            for i in range(len(self.content)):
                for j in range(len(self.content[i])):
                    self.content[i][j].setPos(self.PositionalData[frame][i][j])
                    self.content[i][j].setColorScale(self.ColorScaleData[frame][i][j])
        else: pass
        return None