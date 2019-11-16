from panda3d.core import *
from math import *


class OrbitalCamera:
    def __init__(self,base,focus):
        self.focusedPoint = LPoint3f(focus) # orbital center
        self.HGrad = 0 # horizontal angle
        self.VGrad = 0 # vertical angle
        self.zoomDist = 3
        base.accept('wheel_up',self.Zoom,[0.95])
        base.accept('wheel_down',self.Zoom,[1.05])
        self.RecomputePosition() # initialize
        
    def RecomputePosition(self): # internal command, doesn't need to be called (except for debugging purposes)
        localCamPos = LPoint3f( sin(self.HGrad)*cos(self.VGrad)*self.zoomDist + self.focusedPoint[0],
                                cos(self.HGrad)*cos(self.VGrad)*self.zoomDist + self.focusedPoint[1],
                                sin(self.VGrad)*self.zoomDist + self.focusedPoint[2]
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

    def Zoom(self,percentage):
        self.zoomDist *= percentage
        self.RecomputePosition()
        return None
