from math import *
import os,ctypes,sys,random,time # useless, but I like those libs so I dont't care
from direct.showbase.ShowBase import ShowBase
from panda3d.core import *
from direct.showbase import DirectObject

user32=ctypes.windll.user32
user32.SetProcessDPIAware()

loadPrcFileData('','fullscreen true')
loadPrcFileData('','win-size '+str(user32.GetSystemMetrics(0))+' '+str(user32.GetSystemMetrics(1)))

loadPrcFileData('','window-title WaveSim')



class MainApp(ShowBase):
    def __init__(self):
        super().__init__()
        # model imports
        self.task_mgr.add(self.mainloop,'FrameUpdater')
        
    def mainloop(self):

