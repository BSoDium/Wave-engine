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
    def update(self,progress):
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

    def CreateSimReadingHUD(self,CommandBase,max_frame):
        '''
        create the whole post-rendering HUD (pause, rewind,...).\n
        CommandBase is the name of the application (App)
        '''
        tempMap = loader.loadModel(str(MAINDIR)+"/files/play.egg")
        tempMap2 = loader.loadModel(str(MAINDIR)+"/files/pause.egg")
        tempMap3 = loader.loadModel(str(MAINDIR)+"/files/fforward.egg")
        tempMap4 = loader.loadModel(str(MAINDIR)+"/files/slower.egg")
        tempMap5 = loader.loadModel(str(MAINDIR)+"/files/thumb.egg")
        self.play_button = DirectButton(geom = (tempMap.find('**/play'),
                                                tempMap.find('**/play_on'),
                                                tempMap.find('**/play_out')),
                                                pos = (0,0,-0.85),
                                                command = CommandBase.toggleReading,
                                                extraArgs = [False],
                                                frameColor = (0,0,0,0),
                                                scale = (0.14,1,0.14))
        self.pause_button = DirectButton(geom = (tempMap2.find('**/pause'),
                                                tempMap2.find('**/pause_on'),
                                                tempMap2.find('**/pause_out')),
                                                pos = (0,0,-0.85),
                                                command = CommandBase.toggleReading,
                                                extraArgs = [False],
                                                frameColor = (0,0,0,0),
                                                scale = (0.14,1,0.14))
        self.forward_button = DirectButton(geom = (tempMap3.find('**/fast_forward'),
                                                    tempMap3.find('**/fast_forward_on'),
                                                    tempMap3.find('**/fast_forward_out')),
                                                    pos = (0.2,0,-0.85),
                                                    command = CommandBase.changeSpeed,
                                                    extraArgs = [2],
                                                    frameColor = (0,0,0,0),
                                                    scale = (0.11,1,0.11))
        self.slower_button = DirectButton(geom = (tempMap4.find('**/slower'),
                                                    tempMap4.find('**/slower_on'),
                                                    tempMap4.find('**/slower_out')),
                                                    pos = (-0.2,0,-0.85),
                                                    command = CommandBase.changeSpeed,
                                                    extraArgs = [0.5],
                                                    frameColor = (0,0,0,0),
                                                    scale = (0.11,1,0.11))
        sliderMap = loader.loadModel(str(MAINDIR)+"/files/slider.egg")
        self.stateSlider = DirectSlider(thumb_geom = (tempMap5.find('**/thumb'),
                                                tempMap5.find('**/thumb_on'),
                                                tempMap5.find('**/thumb_out')),
                                        scale = 0.07,
                                        frameSize = (-20, 20, -0.2, 0.2),
                                        range = (0,max_frame-1),
                                        thumb_frameColor = (0,0,0,0),
                                        pos = (0,0,-0.7),
                                        value = 0)
        if CommandBase.is_paused: # check the initial state and display the correct button accordingly
            self.pause_button.hide()
        else:
            self.play_button.hide()
        return None
    def HUDcom(self,CommandBase,current_state,max_state):
        '''
        whenever this command is executed, the position of the slider is updated, and sent to the reading routine
        It "communicates" with the HUD
        '''
        buffer = round(self.stateSlider.getValue())
         
        self.stateSlider.setValue(current_state)
        return None