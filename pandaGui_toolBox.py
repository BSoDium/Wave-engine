import os
from panda3d.core import *
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.DirectGui import *

MAINDIR = Filename.from_os_specific(os.getcwd())

class loadingscreen:
    def __init__(self):
        self.progress = 0 # percentage
        self.bg = OnscreenImage(image = str(MAINDIR)+"/files/loading_screen_waveengine.png", pos = (0,0,0), scale = (1.77777778,1,1))
        self.loading_bar_bg_c = OnscreenImage(image = str(MAINDIR)+"/files/loading_bar_bg_c.png", pos = (0,0,-0.7), scale = (0.8,1,0.02))
        # this is the only pic that will evolve with time
        self.loading_bar = OnscreenImage(image = str(MAINDIR)+"/files/loading_bar.png", pos = (-0.8+self.progress*0.77,0,-0.7),scale = (self.progress*0.77,1,0.02))
        # --
        self.loading_bar_bg = OnscreenImage(image = str(MAINDIR)+"/files/loading_bar_bg.png", pos = (0,0,-0.7), scale = (0.8745,1,0.1))
        self.loading_bar_bg.setTransparency(TransparencyAttrib.MAlpha)
        return None
    def update (self,progress):
        try:
            assert progress <= 1
            self.progress = progress
            self.loading_bar.setScale(self.progress*0.77,1,0.01)
            self.loading_bar.setPos(-0.8+self.progress*0.77,0,-0.7)
        except:
            print("update_loading_bar: request failed\nwrong progress value")
        return None
    def delete(self):
        '''
        delete the loading page, and all of its components 
        (including the moving ones, like the loading bar)
        '''
        self.bg.destroy()
        self.loading_bar_bg_c.destroy()
        self.loading_bar_bg.destroy()
        self.loading_bar.destroy()
    def CreateSimReadingHUD(self,CommandBase):
        '''
        create the whole post-rendering HUD (pause, rewind,...).\n
        CommandBase is the name of the application (App)
        '''
        tempMap = loader.loadModel(str(MAINDIR)+"/files/play.egg")
        tempMap2 = loader.loadModel(str(MAINDIR)+"/files/pause.egg")
        tempMap3 = loader.loadModel(str(MAINDIR)+"/files/fforward.egg")
        tempMap4 = loader.loadModel(str(MAINDIR)+"/files/slower.egg")
        self.play_button = DirectButton(geom = (tempMap.find('**/play'),
                                                tempMap.find('**/play_on'),
                                                tempMap.find('**/play_out')),
                                                pos = (0,0,-0.85),
                                                command = CommandBase.toggleReading,
                                                frameColor = (0,0,0,0),
                                                scale = (0.187,1,0.187))
        self.pause_button = DirectButton(geom = (tempMap2.find('**/pause'),
                                                tempMap2.find('**/pause_on'),
                                                tempMap2.find('**/pause_out')),
                                                pos = (0,0,-0.85),
                                                command = CommandBase.toggleReading,
                                                frameColor = (0,0,0,0),
                                                scale = (0.187,1,0.187))
        self.forward_button = DirectButton(geom = (tempMap3.find('**/fast_forward'),
                                                    tempMap3.find('**/fast_forward_on'),
                                                    tempMap3.find('**/fast_forward_out')),
                                                    pos = (0.2,0,-0.85),
                                                    command = CommandBase.changeSpeed,
                                                    extraArgs = [2],
                                                    frameColor = (0,0,0,0),
                                                    scale = (0.14,1,0.14))
        self.slower_button = DirectButton(geom = (tempMap4.find('**/slower'),
                                                    tempMap4.find('**/slower_on'),
                                                    tempMap4.find('**/slower_out')),
                                                    pos = (-0.2,0,-0.85),
                                                    command = CommandBase.changeSpeed,
                                                    extraArgs = [0.5],
                                                    frameColor = (0,0,0,0),
                                                    scale = (0.14,1,0.14))
        sliderMap = self.loader.loadModel(str(MAINDIR)+"/files/slider.egg")
        self.stateSlider = DirectSlider(range = (0,5),pos = (0,0,-0.7),value = 1.5)
        if CommandBase.is_paused: # check the initial state and display the correct button accordingly
            self.pause_button.hide()
        else:
            self.play_button.hide()
        return None