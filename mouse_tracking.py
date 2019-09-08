from panda3d.core import * # I know it's not the best way to optimize algorithm loading, but fuck it

class MouseTracker:
    def __init__(self,camerabase):
        self.camerabase = camerabase # temporary reminder
        self.sensitivity = 2

        self.keyMap = [["mouse2",False]]
        base.accept("mouse2",self.activate,[0])
        base.accept("mouse2-up",self.deactivate,[0])
        base.task_mgr.add(self.CheckLoop,"MouseUpdateLoop")
        return None

    def activate(self,rank):
        self.keyMap[rank][1] = True
        #self.toggleCursor(True) 

        mwn = base.mouseWatcherNode # initializing the pos
        self.bufferPos = (mwn.getMouseX(),mwn.getMouseY())
        return None
    
    def deactivate(self,rank):
        self.keyMap[rank][1] = False
        #self.toggleCursor(False) # enable cursor
        return None

    def toggleCursor(self,is_hidden):
        wp = WindowProperties()
        wp.setCursorHidden(is_hidden)
        base.win.requestProperties(wp)
        return None
    
    def getDelta(self):
        mwn = base.mouseWatcherNode
        self.Pos = (mwn.getMouseX(),mwn.getMouseY())
        delta = (self.sensitivity*(self.Pos[0] - self.bufferPos[0]),self.sensitivity*(self.Pos[1] - self.bufferPos[1]))
        self.bufferPos = self.Pos
        return delta

    def center_mouse(self):
        base.win.movePointer(0,
          int(base.win.getProperties().getXSize() / 2),
          int(base.win.getProperties().getYSize() / 2)) 
    

    def CheckLoop(self,task):
        if self.keyMap[0][1]: # orbit mode enabled
            delta = self.getDelta()
            self.camerabase.OCam.HorizontalDisplace(delta[0]) # the use of the name Ocam comes from main.py
            self.camerabase.OCam.VerticalDisplace(-delta[1]) # - reverse controls
        return task.cont