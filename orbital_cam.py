from panda3d.core import *
import os


class OrbitalCamera:
    def __init__(self,baseCam):
        self.camera = baseCam
        self.focusedPoint = LPoint3f(0,0,0) # orbital center
        self.HGrad = 0 # horizontal angle
        self.VGrad = 0 # vertical angle
        self.zoomDist = 3
        
    def RecomputePosition(self):

