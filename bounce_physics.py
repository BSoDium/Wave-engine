import os,ctypes,sys,random,time # I definitely won't use those
from direct.showbase.ShowBase import ShowBase
from panda3d.core import *
from copy import deepcopy
from skybox import skybox

# fullscreen routine
user32 = ctypes.windll.user32
user32.SetProcessDPIAware()
loadPrcFileData('','fullscreen true')
loadPrcFileData('','win-size '+str(user32.GetSystemMetrics(0))+' '+str(user32.GetSystemMetrics(1)))

loadPrcFileData('','window-title SomeFunnyShit')

MAINDIR = Filename.from_os_specific(os.getcwd())
TIMESCALE=0.01
FRICTIONCONST=0.99
GLOBALSCALE=2

class harmosc: # the good ol' harmonic oscillator
    def __init__(self,pos,id,RandFric): # initialize harmosc below StableZ to make it react 
        self.id=id
        self.RigidConst = 1.2 # k constant (non-physicists go fuck themselves)
        self.StableZ = 0 # stable position on Z axis
        self.speed = 0 # initialized always at 0, can be changed, that shouldn't cause too many bugs
        self.mass = 0.1 # 100g=0.1kg
        self.freeze = False
        self.is_random=RandFric
        # loading 3d mesh
        self.model = loader.loadModel(str(MAINDIR)+"/wave_part_small.egg")
        self.model.reparentTo(render)
        self.model.setPos(pos)
        self.model.setScale(GLOBALSCALE)
    def toggle(self):
        self.freeze = not(self.freeze)
        return None
    def update(self):
        if not(self.freeze):
            # some nerd shit
            bufferPos = tuple(self.model.getPos())
            bufferForce = -self.RigidConst*(bufferPos[2]-self.StableZ) # F=k*(l-l0)
            bufferaccel = bufferForce/self.mass
            self.speed = self.speed+bufferaccel*TIMESCALE
            self.model.setPos(bufferPos[0],bufferPos[1],bufferPos[2]+self.speed*TIMESCALE)
            self.apply_friction()
            return None
        return None

        return None
    def apply_friction(self):
        # first, check if the speed isn't too small 
        BufferDelta=abs(self.model.getPos()[2]-self.StableZ)
        if 0 < self.speed <= 1e-6 and BufferDelta <= 1e-3:
            self.speed=0
            bufferPos = tuple(self.model.getPos())
            self.model.setPos(bufferPos[0],bufferPos[1],0)
            '''
            print("[DEBUG]: stopped block "+str(self.id))
            '''
        
        # now randomize the friction constant on request from the user
        if self.is_random:
            self.speed*=(FRICTIONCONST+random.random()*0.01)
        else:
            self.speed*=FRICTIONCONST
        return None
    def apply_force(self,name,intensity):
        return None

class PhysicalArray:
    def __init__(self,x,y,randomize_friction,DynamicMesh):
        InitialZ=0 # the array starts with all blocks at 0, use the override function to change one of the blocks pos
        self.LinkedBlocks=DynamicMesh
        self.RandFric = randomize_friction
        self.content = [[harmosc((0.06*GLOBALSCALE*a,0.06*GLOBALSCALE*b,InitialZ),(a,b),self.RandFric) for a in range(x)] for b in range(y)]
        return None

    def GetSize(self):
        return (len(self.content),len(self.content[0]))

    def toggle(self):
        for i in self.content:
            for j in i:
                j.toggle()

    def update(self):
        for i in self.content:
            for j in i:
                j.update()
        
    def single_override(self,i,j,new_Z_pos):
        try:
            bufferPos = tuple(self.content[i][j].model.getPos())
            self.content[i][j].model.setPos(bufferPos[0],bufferPos[1],new_Z_pos)
        except:
            warn("override coordinates out of bounds","operation terminated, moving on...")
            
        return None

    def line_override(self,i,new_Z_pos):
        try:
            bufferPos = [tuple(a.model.getPos()) for a in self.content[i]]
            for a in range(len(self.content[i])):
                self.content[i][a].model.setPos(bufferPos[a][0],bufferPos[a][1],new_Z_pos)
        except:
            warn("override coordinates out of bounds","operation terminated, moving on...")
        return None

    def column_override(self,j,new_Z_pos):
        try:
            bufferPos = [tuple(a[j].model.getPos()) for a in self.content]
            for a in range(len(self.content)):
                self.content[a][j].model.setPos(bufferPos[a][0],bufferPos[a][1],new_Z_pos)
        except:
            warn("override coordinates out of bounds","operation terminated, moving on...")



class MainApp(ShowBase):
    def __init__(self):
        super().__init__(self)

        # vars
        self.ground = PhysicalArray(20,20,False,True)
        #self.ground.single_override(19,19,-1) # max is 20-1=19 (depends on the PhysicalArray definition)
        #self.ground.column_override(2,-1)
        self.ground.line_override(0,-1)
        
        # key bindings
        self.accept('escape',sys.exit,[0])
        self.accept('space',self.ground.toggle)

        # task manager
        self.task_mgr.add(self.mainloop,"FrameUpdateTask")

        # background
        LightYellow=(0.996,0.996,0.953)
        self.setBackgroundColor(LightYellow)

        # lighting
        p = PointLight('main_plight')
        p.setColor(VBase4(1,1,1,1))
        plight = render.attachNewNode(p)
        plight.setPos(-23.9196, 0.779138, 10.6075)
        render.setLight(plight)

        # draw light indicator:
        self.light_bulb=self.loader.loadModel(str(MAINDIR)+"/light_bulb.egg")
        bufferPos=plight.getPos()
        self.light_bulb.setPos(bufferPos)
        self.light_bulb.setScale(0.25,0.25,0.25)
        self.light_bulb.reparentTo(render)

        
        a = AmbientLight('main_alight')
        a.setColor(VBase4(0.3,0.3,0.3,1))
        alight = render.attachNewNode(a)
        render.setLight(alight)
        

        # camera
        empirical1 = (1.29481, -3.75714, 0.925946)
        empirical2 = (1.44023, -13.8639, 0.420943)
        self.cam.setPos(empirical1)
        self.cam.setHpr(empirical2)

        '''
        # skybox setup
        environment = skybox(render)
        '''

    def mainloop(self,task):
        self.ground.update()
        return task.cont


def warn(content,description):
    print("[Warning]: "+content+"\n"+description)
    return None

App=MainApp()
App.run()