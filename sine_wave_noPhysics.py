from math import *
import os,ctypes,sys,random,time # wait for it
from direct.showbase.ShowBase import ShowBase
from panda3d.core import *
from direct.showbase import DirectObject
from skybox import skybox

user32=ctypes.windll.user32
user32.SetProcessDPIAware()

loadPrcFileData('','fullscreen true')
loadPrcFileData('','win-size '+str(user32.GetSystemMetrics(0))+' '+str(user32.GetSystemMetrics(1)))

loadPrcFileData('','window-title WaveSim')
#antialiasing presets
loadPrcFileData('','framebuffer-multisample 1')
loadPrcFileData('','multisamples 2') 


'''
as we want the simulation to represent a perfect sine wave, we don't need a third dimension,
which means we can make the calculations a bit easier as if all particles on the z-axis were behaving in the same way 
(y displacement only)
'''
MAINDIR=Filename.from_os_specific(os.getcwd())

# MAIN PARAMETERS -- CHANGE THOSE TO MODIFY THE WAVE
AMPLITUDE=0.1
PULSE=4        # in this case, equals to the speed of displacement of the wave
PHASE_SHIFT=4


class wave:
    def __init__(self,path,resolution): #path to model
        self.res=resolution # default resolution
        self.components = [loader.loadModel(path) for x in range(self.res)]
        for c in range(len(self.components)):
            self.components[c].setPos(0.06*c+0.02,1,0)
            self.components[c].reparentTo(render)
        self.is_running = True # by default, the wave is moving
    def toggle(self):
        self.is_running = not(self.is_running)
    def update(self,time):
        if self.is_running:
            for c in self.components:
                temp=tuple(c.getPos())
                c.setPos(temp[0],1,AMPLITUDE*sin(PULSE*time+temp[0]*PHASE_SHIFT))
        return None



class MainApp(ShowBase):
    def __init__(self):
        super().__init__(self)

        # variables
        self.frame_counter = 0 
        lenght=130
        self.sine = wave(str(MAINDIR)+"/wave_part.egg",lenght)

        '''
        # axis
        self.draw_axis()
        '''
        # task manager
        self.task_mgr.add(self.mainloop,'FrameUpdater')

        # key bindings
        self.accept('escape',sys.exit,[0])
        self.accept('space',self.sine.toggle)

        # lighting
        p = PointLight('main_plight')
        p.setColor(VBase4(1,1,1,1))
        plight = render.attachNewNode(p)
        plight.setHpr(60,-30,0)
        plight.setPos(6.5,-4,3)
        render.setLight(plight)

        a = AmbientLight('main_alight')
        a.setColor(VBase4(0.2,0.2,0.2,1))
        alight = render.attachNewNode(a)
        render.setLight(alight)


        # antialiasing
        render.setAntialias(AntialiasAttrib.MAuto)

        # camera
        self.cam.setPos(LPoint3f(12.9715, -7.79632, 3.11914)) # donnees empiriques
        self.cam.setHpr(LVecBase3f(45.6769, -16.8087, 6.02517)) # idem

        # background
        self.setBackgroundColor(0,0,0)

        # draw light indicator:
        self.light_bulb=self.loader.loadModel(str(MAINDIR)+"/light_bulb.egg")
        bufferPos=plight.getPos()
        self.light_bulb.setPos(bufferPos)
        self.light_bulb.setScale(0.25,0.25,0.25)
        self.light_bulb.reparentTo(render)

        '''
        # skybox 
        Environment=skybox(render)
        '''

    def mainloop(self,task):
        self.sine.update(self.frame_counter) 
        if self.sine.is_running: self.frame_counter+=0.017
        return task.cont
    
    def draw_axis(self): #axis drawing routine
        coord = [(3,0,0),(0,2,0),(0,0,2)]
        axis = []
        for c in range(3): 
            axis.append(LineSegs())
            axis[c].moveTo(0,0,0)
            axis[c].drawTo(coord[c])
            axis[c].setThickness(3)
            temp=NodePath(axis[c].create())
            temp.reparent_to(render)
        return None
App = MainApp()
App.run()