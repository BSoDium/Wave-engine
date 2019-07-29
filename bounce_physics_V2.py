import os,ctypes,sys,random,time # I definitely won't use those
from math import *
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
RIGIDCONST=1.2
TIMESCALE=0.005
FRICTIONCONST=0.99
GLOBALSCALE=2
BLOCKINTERVAL=0.06

class harmosc:
    def __init__(self,pos,id):
        self.mass=0.1 # 100 g = 0.1 kg USI
        self.speed = 0 # speed over Z axis only, obviously
        self.model = loader.loadModel(str(MAINDIR)+"/wave_part_small.egg")
        self.model.reparentTo(render)
        self.model.setPos(pos)
        self.model.setScale(GLOBALSCALE)
        return None
    

class PhysicalArray:
    def __init__(self,x,y,DynamicMesh):
        self.is_running=True
        self.LinkedBlocks=DynamicMesh
        InitialZ = 0 # the array starts with all blocks at 0, use the override function to change one of the blocks pos
        self.content = [[harmosc((BLOCKINTERVAL*GLOBALSCALE*a,BLOCKINTERVAL*GLOBALSCALE*b,InitialZ),(a,b)) for a in range(x)] for b in range(y)]
        return None

    def GetSize(self):
        return (len(self.content),len(self.content[0]))

    def toggle(self):
        self.is_running=not(self.is_running)

    def update(self):
        self.create_buffer(self.content)
        for i in range(len(self.content)):
            for j in range(len(self.content[i])):
                AppliedForce = self.scan_neighbors(i,j,self.content)
                PositionalData = self.get_next_pos(AppliedForce,(i,j))
                self.write_buffer((i,j),PositionalData)
        self.blit()

    def create_buffer(self,content):
        self.BufferData = [[content[i][j].model.getPos() for j in range(len(content[i]))] for i in range(len(content))]
        # we create this buffer in order to be able to write the new positions, without modifying the data we need to make the calculations
        return None

    def write_buffer(self,id,data): # id must be tuple
        self.BufferData[id[0]][id[1]]=data
        return None
    
    def blit(self):
        for x in range(len(self.BufferData)):
            for y in range(len(self.BufferData[x])):
                self.content[x][y].model.setPos(self.BufferData[x][y])
                return None
    
    def get_next_pos(self,Force,id): # id must be tuple
        i,j=id[0],id[1]
        LocalMass = self.content[i][j].mass
        accel = Force/LocalMass
        self.content[i][j].speed += accel*TIMESCALE # we can already update the speed, that doesn't actually change anything to our further calculations
        lastPos = self.content[i][j].model.getPos() # save the last known position
        bufferPos = LPoint3f(lastPos[0],lastPos[1],lastPos[2] + self.content[i][j].speed) 
        return bufferPos

    def scan_neighbors(self,i,j,content):
        ScanList=[   (i-1,j),   
        (i,j-1),                  (i,j+1),
                     (i+1,j)]
        centralPos=content[i][j].model.getPos() # centralPos is the position of the central block
        ResultingForce=0
        for x in ScanList:
            try:
                bufferPos = content[x[0]][x[1]].model.getPos()
                dist = (bufferPos-centralPos).lenght() # now we know the distance of the central block to the scanned one
                alpha = asin(BLOCKINTERVAL*GLOBALSCALE/dist) # angle between Z axis and block to block link
                GlobalForce = RIGIDCONST*(dist-BLOCKINTERVAL*GLOBALSCALE) # basically F=k*(l-l0)
                ZForce = GlobalForce*cos(alpha) # projection over Z axis (on ignore les forces sur les axes X et Y)
                ResultingForce+=ZForce
            except: # if the neighbor does not exist (the block is on an edge), then act as if there was a stable block connected to it
                temp = (x[0]-i,x[1]-j) # get an idea of the position in the array
                bufferPos = LPoint3f(centralPos[0]+temp[0]*BLOCKINTERVAL*GLOBALSCALE,centralPos[1]+temp[1]*BLOCKINTERVAL*GLOBALSCALE,0) # not completely accurate: instead of taking a different cube, I use the same one as anchor
                #dist = (bufferPos - centralPos).length() # we can't use the command .length() because of round errors
                '''
                at this point I had some trouble making things work because python would take panda3d's data as enormous floats, instead of
                signed ones (0.11999999 instead of 12), which could lead to mathematical nonsenses. The solution I found ws making my own 
                aprox system.
                '''
                vec = list( bufferPos - centralPos )
                for x in range(3):
                    vec[x] = round(float(str(vec[x])[:6])*100)/100   # here it goes
                dist = sqrt(vec[0]**2 + vec[1]**2 + vec[2]**2)
                alpha = asin(BLOCKINTERVAL*GLOBALSCALE/dist)
                GlobalForce = RIGIDCONST*(dist-BLOCKINTERVAL*GLOBALSCALE)
                ZForce = GlobalForce*cos(alpha)
                ResultingForce += ZForce
        return ResultingForce
        
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
        self.ground = PhysicalArray(20,20,True)
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