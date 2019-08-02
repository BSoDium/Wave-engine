# Wave Engine V0.3
# Dependencies : pandaGui_toolBox.py, SaveTools.py

try:
    import os,ctypes,sys,random,time # I definitely won't use those
    from math import *
    from copy import deepcopy
except:
    print("[WARNING]: One of the following libraries is missing\n","os, ctypes, sys, random, time, math, copy")
    sys.exit(0)
try:
    from direct.showbase.ShowBase import ShowBase
    from panda3d.core import *
    from direct.gui.OnscreenImage import OnscreenImage
except:
    print("[WARNING]: The panda3d engine is missing\n","Try installing it using 'pip install panda3d'")
    sys.exit(0)
try:
    error = 0
    from skybox import skybox #e0
    error+=1
    from pandaGui_toolBox import loadingscreen #e1
    error+=1
    from SaveTools import SaveSim
except:
    print("[WARNING]: Some internal program files seem to be missing\n","error code:",error)
    sys.exit(0)

# fullscreen routine
user32 = ctypes.windll.user32
user32.SetProcessDPIAware()
loadPrcFileData('','fullscreen true')
loadPrcFileData('','win-size '+str(user32.GetSystemMetrics(0))+' '+str(user32.GetSystemMetrics(1)))

loadPrcFileData('','window-title SomeFunnyShit')

# antialias
adv_Gfx = True # turn off if your computer can't handle it
if adv_Gfx:
    loadPrcFileData('','framebuffer-multisample 1')
    loadPrcFileData('','multisamples 2') 

# flat-shading is enabled

MAINDIR = Filename.from_os_specific(os.getcwd())
RIGIDCONST = 4
TIMESCALE = 0.01
FRICTIONCONST = 0.98 # 0.98 = Pizza dough, 0.90 = slow mo kevlar, 0.99 is too high, there is a major risk of structural instability
GLOBALSCALE = 3
BLOCKINTERVAL = 0.06
GLOBALMASS = 0.1 # kg USI

HOLDING_FRAME = True # this defines whether there is a stable frame holding the moving surface or not. Try turning it off to see what happens ;)


TOGGLE_LIVE_DISPLAY = True # when switched off, the calculation process isn't rendered in 3d, and only returns a list of positions, which can be read later, without doing the maths
PRESIMULATION_TIME = 50 # in frames

class VirtualMeshAttribute: # used during non rendered calculations
    def __init__(self):
        self.position = None
        self.Hpr = (0,0,0)
        self.scale = None
        self.color_scale = None
    def __copy__(self):
        return VirtualMeshAttribute(position = self.position, Hpr = self.Hpr, scale = self.scale)

    def setPos(self,pos): # for tuple position entries only !!!
        self.position = LPoint3f(pos) 
        return None

    def setHpr(self,Hpr): # we don't actually need this one
        self.Hpr = Hpr
        return None

    def setScale(self,Scale):
        self.scale = Scale
        return None
    
    def setColorScale(self,ColorScale):
        self.color_scale = ColorScale
        #return "fuck you"
        return None

    def getPos(self):
        return self.position

class harmosc:
    def __init__(self,pos,id):
        self.movable = True
        self.law = None
        self.mass = GLOBALMASS 
        self.falling = (False,None) # by default, gravity is disabled (None here stands for the acceleration applied to the block, undefined here)
        self.speed = 0 # speed over Z axis only, obviously
        if TOGGLE_LIVE_DISPLAY:
            self.model = loader.loadModel(str(MAINDIR)+"/wave_part_small.egg")
            self.model.reparentTo(render)
        else:
            self.model = VirtualMeshAttribute()
        self.model.setPos(pos)
        self.model.setScale(GLOBALSCALE)
        return None

    def follow(self,law,data): # this makes the block follow a law at any time, without being affected by neighbor blocks
        self.law = law # Warning !! self.law is now a fully callable function !
        self.movable = False
        self.law_counter = 0 # this is the x variable for the law, it will evolve with time, making the block change position
        self.law_speed = data
    

class PhysicalArray:
    def __init__(self,x,y,DynamicMesh): # DynamicMesh var deprecated
        self.is_running=True
        self.LinkedBlocks=DynamicMesh
        InitialZ = 0 # the array starts with all blocks at 0, use the override function to change one of the blocks pos
        self.content = [[harmosc((BLOCKINTERVAL*GLOBALSCALE*a,BLOCKINTERVAL*GLOBALSCALE*b,InitialZ),(a,b)) for a in range(x)] for b in range(y)]
        return None

    def GetSize(self): # actually only used for debugging purposes
        return (len(self.content),len(self.content[0]))

    def toggle(self):
        self.is_running=not(self.is_running)

    def update(self):
        if self.is_running:
            self.create_buffer(self.content)
            for i in range(len(self.content)):
                for j in range(len(self.content[i])):
                    AppliedForce = self.scan_neighbors(i,j,self.content)
                    PositionalData = self.get_next_pos(AppliedForce,(i,j))
                    self.write_buffer((i,j),PositionalData)
            
            if not(TOGGLE_LIVE_DISPLAY):
                colorScaleBuffer = self.blit() # update and save (preloading process)
                App.Saved.AddFrameData(self.BufferData,colorScaleBuffer)
            else:
                self.blit() # just update, don't save


    def create_buffer(self,content):
        self.BufferData = [[content[i][j].model.getPos() for j in range(len(content[i]))] for i in range(len(content))]
        # we create this buffer in order to be able to write the new positions, without modifying the data we need to make the calculations
        return None

    def write_buffer(self,id,data): # id must be tuple
        self.BufferData[id[0]][id[1]]=data
        return None
    
    def blit(self):
        if not(TOGGLE_LIVE_DISPLAY):
            colorScaleBuffer = [] # this list gives us the color state of each cube, every frame
        for x in range(len(self.BufferData)):

            if not(TOGGLE_LIVE_DISPLAY):
                colorScaleBuffer.append([])
            
            for y in range(len(self.BufferData[x])):
                if self.content[x][y].movable: # check if the block isn't anchored
                    self.content[x][y].model.setPos(self.BufferData[x][y])
                    tempSpeed = abs(self.content[x][y].speed)*255/10
                    blue_red = (tempSpeed,(1-tempSpeed)/2,(1-tempSpeed),1)
                    black_red = (tempSpeed,0.2,0.2,1)
                    self.content[x][y].model.setColorScale(black_red)
                    self.apply_friction((x,y))
                    if not(TOGGLE_LIVE_DISPLAY):
                        # save the color to the buffer
                        colorScaleBuffer[x].append(black_red)

                elif self.content[x][y].law:
                    LocalSpeed = self.content[x][y].law_speed
                    bufferPos = self.content[x][y].model.getPos()
                    self.content[x][y].model.setPos((bufferPos[0],bufferPos[1],self.content[x][y].law(self.content[x][y].law_counter)))
                    self.content[x][y].law_counter+=TIMESCALE*LocalSpeed
                    if not(TOGGLE_LIVE_DISPLAY):
                        # save the color for non simulated blocks (controlled by defined law)
                        colorScaleBuffer[x].append((1,1,1,1))
                
                elif not(self.content[x][y].movable) and not(TOGGLE_LIVE_DISPLAY):
                    colorScaleBuffer[x].append((1,1,1,1))

        if not(TOGGLE_LIVE_DISPLAY):
            return colorScaleBuffer # return the list so that we can get save it into the SaveSim object 
        else:
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
        centralPos = content[i][j].model.getPos() # centralPos is the position of the central block
        ResultingForce = 0
        for x,y in ScanList:
            try:
                assert x >= 0 # prevents the list from reading negative x and y values ( when scanning edge points )
                assert y >= 0
                bufferPos = content[x][y].model.getPos()
                # calculating the distance between central and scanned object
                dist = (bufferPos - centralPos).length() 
                if dist < BLOCKINTERVAL*GLOBALSCALE: # computer architecture sucks
                    dist = BLOCKINTERVAL*GLOBALSCALE
                # ----
                alpha = asin(BLOCKINTERVAL * GLOBALSCALE/dist) # angle between Z axis and block to block link
                try:
                    force_sign = int(( bufferPos - centralPos )[2]/abs(( bufferPos - centralPos )[2])) # get the sign (pos or neg) of the delta
                except: # if bufferPos[2] == 0
                    force_sign = 1
                GlobalForce =  force_sign * RIGIDCONST * (dist - BLOCKINTERVAL * GLOBALSCALE) # basically F=k*(l-l0)
                ZForce = GlobalForce*cos(alpha) # projection over Z axis (on ignore les forces sur les axes X et Y)
                ResultingForce+=ZForce
            except: # if the neighbor does not exist (the block is on an edge), then act as if there was a stable block connected to it
                if HOLDING_FRAME:
                    temp = (x-i,y-j) # get an idea of the position in the array
                    bufferPos = LPoint3f(centralPos[0]+temp[0]*BLOCKINTERVAL*GLOBALSCALE,centralPos[1]+temp[1]*BLOCKINTERVAL*GLOBALSCALE,0) 
                    dist = (bufferPos - centralPos).length() 
                    if dist < BLOCKINTERVAL*GLOBALSCALE: 
                        dist = BLOCKINTERVAL*GLOBALSCALE
                    alpha = asin(BLOCKINTERVAL*GLOBALSCALE/dist)
                    try:
                        force_sign = int(( bufferPos - centralPos )[2]/abs(( bufferPos - centralPos )[2]))
                    except: 
                        force_sign=1
                    GlobalForce = force_sign * RIGIDCONST * (dist - BLOCKINTERVAL * GLOBALSCALE)
                    ZForce = GlobalForce*cos(alpha)
                    ResultingForce += ZForce
                else:
                    pass
        if content[i][j].falling[0]:
            ResultingForce -= content[i][j].mass * content[i][j].falling[1] * TIMESCALE
        return ResultingForce
    
    def apply_friction(self,id):
        x,y=id[0],id[1]
        self.content[x][y].speed *= FRICTIONCONST+(1-FRICTIONCONST)*TIMESCALE # compensate the fact that in slow mo, the friction is too high
        return None
    
    def toggle_gravity(self,accel):
        for i in self.content:
            for j in i:
                j.falling = (not(j.falling[0]),accel)
        return None

    def single_override(self,state,i,j,new_Z_pos):
        try:
            if state == "initial":
                bufferPos = tuple(self.content[i][j].model.getPos())
                self.content[i][j].model.setPos((bufferPos[0],bufferPos[1],new_Z_pos))
            elif state == "controlled":
                bufferPos = tuple(self.content[i][j].model.getPos())
                self.content[i][j].model.setPos((bufferPos[0],bufferPos[1],new_Z_pos))
                self.content[i][j].movable=False
            elif state[:4] == "sine": # the sine option ignores new_Z_pos, so just add a few zeros to make it work
                data = float(state[4:])
                self.content[i][j].follow(sine,data)
        except:
                warn("[single_override request] override coordinates out of bounds","operation terminated, moving on...")
        return None

    def line_override(self,state,i,new_Z_pos):
        try:
            if state == "initial":
                bufferPos = [tuple(a.model.getPos()) for a in self.content[i]]
                for a in range(len(self.content[i])):
                    self.content[i][a].model.setPos((bufferPos[a][0],bufferPos[a][1],new_Z_pos))
            elif state == "controlled":
                bufferPos = [tuple(a.model.getPos()) for a in self.content[i]]
                for a in range(len(self.content[i])):
                    self.content[i][a].model.setPos((bufferPos[a][0],bufferPos[a][1],new_Z_pos))
                    self.content[i][a].movable=False
            elif state[:4] == "sine":
                data = float(state[4:])
                for a in range(len(self.content[i])):
                    self.content[i][a].follow(sine,data)
        except:
            warn("[line_override request] override coordinates out of bounds","operation terminated, moving on...")
        return None
        

    def column_override(self,state,j,new_Z_pos):
        try:
            if state == "initial":
                bufferPos = [tuple(a[j].model.getPos()) for a in self.content]
                for a in range(len(self.content)):
                    self.content[a][j].model.setPos((bufferPos[a][0],bufferPos[a][1],new_Z_pos))
            elif state == "controlled":
                bufferPos = [tuple(a[j].model.getPos()) for a in self.content]
                for a in range(len(self.content)):
                    self.content[a][j].model.setPos((bufferPos[a][0],bufferPos[a][1],new_Z_pos))
                    self.content[a][j].movable=False
            elif state[:4] == "sine":
                data = float(state[4:])
                for a in range(len(self.content)):
                    self.content[a][j].follow(sine,data)
        except:
                warn("[column_override request] override coordinates out of bounds","operation terminated, moving on...")



class MainApp(ShowBase):
    def __init__(self):
        super().__init__(self)

        if not(TOGGLE_LIVE_DISPLAY):
            self.Gui2d = loadingscreen()
            self.Saved = SaveSim()

        # vars
        self.ground = PhysicalArray(21,21,True)


        '''
        insert all the override commands between the two commented lines
        '''
        #self.ground.toggle_gravity(9.81)
        self.ground.single_override("sine8",10,10,-2) # max is 21-1=20 (depends on the PhysicalArray definition)
        #self.ground.column_override("sine8",0,-1)
        #self.ground.line_override("controlled",0,-1)
        '''
        Using the override commands is pretty simple:
        you can choose between a single_override, which will take control of only one block at a time,
        a column_override for column displacement and/or distorsion,
        or a line_override for the same purposes, on lines instead of columns
        The arguments are: 
        single_override("name_of_the_law/state"+"speed_of_execution",i,j,Z_position) where i,j are the coordinates of the 
        block in the content list, and the Z_position, used only in "controlled" and "initial" states, is the pos you
        want the block to be overridden to
        same idea for the other commands, with column and line coordinates
        States:
        "initial" --> the block is placed at this position at the beginning, but is still able to move freely during simulation
        "controlled" --> the block is maintained at a constant position during the whole simulation process, it is not
        affected by physics. Other surrounding blocks are though
        "name_of_law" --> insert the name of the law you want your block(s) to follow, and they will move accordingly. 
        The name of the law must be followed by the playing speed (directly in the same string, like "sine5")
        Warning: currently, only the sine law is supported
        '''
        # antialias
        if adv_Gfx:
            render.setAntialias(AntialiasAttrib.MAuto)

        # key bindings
        self.accept('escape',sys.exit,[0])
        if TOGGLE_LIVE_DISPLAY:
            self.accept('space',self.ground.toggle)
        self.accept('g',self.ground.toggle_gravity,[9.81])

        # task manager
        self.task_mgr.add(self.mainloop,"FrameUpdateTask")

        # background
        DarkGray = (0.145, 0.149, 0.145, 1)
        LightYellow = (0.996 ,0.996, 0.953, 1)
        self.setBackgroundColor(DarkGray)

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
        
        '''
        # camera
        empirical1 = (12.7973, 3.6711, 4.36375)
        empirical2 = (107.397, -8.29886, -0.55216)
        self.cam.setPos(empirical1)
        self.cam.setHpr(empirical2)
        '''
        '''
        # skybox setup (disabled because it is completely useless in means of simulation. It makes the developer happy tho)
        environment = skybox(render)
        '''

    def mainloop(self,task): #  *ravioli architecture intensifies*
        if TOGGLE_LIVE_DISPLAY:
            self.ground.update()
            return task.cont
        elif task.frame < PRESIMULATION_TIME and not(TOGGLE_LIVE_DISPLAY):
            self.ground.update()
            self.Gui2d.update(task.frame/PRESIMULATION_TIME)
            return task.cont
        elif task.frame == PRESIMULATION_TIME and not(TOGGLE_LIVE_DISPLAY): 
            self.postMainloopTransition()
            return task.cont
        else: # actually there is no such option
            print("weeeeee")
            return task.cont 

    def postMainloopTransition(self): # def thefunctionImadeat1amfuckyouIhadnoideas(self):
        self.Gui2d.delete()
        self.Saved.CreateScene(render,GLOBALSCALE)
        self.task_mgr.add(self.PostRendering,"DataDisplayTask")
        self.task_mgr.remove("FrameUpdateTask")

        # *shit*
        self.FramePosition = 0 # this the frame number (the position of the reading algorithm in our data lists)
        self.is_paused = True # the post rendered simulation starts by default as paused
        self.Gui2d.CreateSimReadingHUD(App)
        return None

    
    def PostRendering(self,task):
        if not(self.is_paused) or task.frame == 0: # if we're dealing with the first frame, read it, cause if we don't we'll get an empty render
            self.Saved.read(self.FramePosition)
            self.FramePosition+=1

        if self.FramePosition < PRESIMULATION_TIME:
            return task.cont
        else:
            self.task_mgr.remove("DataDisplayTask")
            return task.done

    def toggleReading(self):
        '''
        allows to pause the reading of the precomputed simulation
        '''
        self.is_paused = not(self.is_paused)
        return None

def warn(content,description):
    print("[Warning]: "+content+"\n"+description)
    return None

def sine(x):
    return sin(x)

App=MainApp()
App.run()