from panda3d.core import *
from math import *


class OrbitalCamera:
    def __init__(self,base):
        self.focusedPoint = LPoint3f(0,0,0) # orbital center
        self.HGrad = 0 # horizontal angle
        self.VGrad = 0 # vertical angle
        self.zoomDist = 3
        
    def RecomputePosition(self): # internal command, doesn't need to be called (except for debugging purposes)
        localCamPos = LPoint3f( sin(self.HGrad)*cos(self.VGrad)*self.zoomDist,
                                cos(self.HGrad)*cos(self.VGrad)*self.zoomDist,
                                sin(self.VGrad)*self.zoomDist
                                )
        base.camera.setPos(localCamPos)
        base.camera.lookAt(self.focusedPoint)
        return None
    
    def VerticalDisplace(self,delta):
        self.VGrad += delta
        self.RecomputePosition()
        return None
    
    def HorizontalDisplace(self,delta):
        self.HGrad += delta
        self.RecomputePosition()
        return None
