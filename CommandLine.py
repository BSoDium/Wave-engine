from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.DirectGui import *
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import *
import sys,os

MAINDIR = Filename.from_os_specific(os.getcwd())


class Console:
    def __init__(self):
        return None
        
    def create(self,base,renderBase,CommandDictionary):
        self.hidden = False
        textscale = 0.04
        self.Lines = 20
        self.background = OnscreenImage(image = str(MAINDIR)+"/files/bg.png",pos = (-1.14,0,0))
        self.background.setTransparency(TransparencyAttrib.MAlpha)
        self.SavedLines = [OnscreenText(text = '', pos = (-1.76, -0.9 + x*textscale), scale = textscale, align = TextNode.ALeft, fg = (1,1,1,1)) for x in range(self.Lines)]
        self.entry = DirectEntry(text = "", scale=textscale,command=self.ConvertToFunction,initialText="Type Something", numLines = 1, focus=1, focusInCommand=self.clearText, width = 40)
        self.entry.setPos(-1.76, 0, -0.97) # needs to be automated sooner or later
        self.commands = CommandDictionary
        #self.entry.reparent_to(App)
        base.accept('f1',self.toggle)
        self.toggle()
        return None
    
    def toggle(self):
        if self.hidden:
            for i in self.SavedLines:
                i.show()
            self.entry.show()
            self.background.show()
        else:
            for i in self.SavedLines:
                i.hide()
            self.entry.hide()
            self.background.hide()
        self.hidden = not(self.hidden)
        return None
    
    def clearText(self):
        self.entry.enterText('')
        return None
    
    def ConvertToFunction(self,data):
        Buffer = [""]
        for x in range(len(data)):
            if data[x] == "(":
                Buffer.append("(")
                Buffer.append("")
            elif data[x] == ")":
                Buffer.append(")")
                Buffer.append("")
            elif data[x] == ",":
                Buffer.append(",")
                Buffer.append("")
            else:
                Buffer[len(Buffer)-1] += data[x]
        try:
            ChosenCommand = self.commands[Buffer[0]] # check if the command exists
            
        except:
            self.Error(Buffer[0])
        
        return None

    def Error(self,report):
        self.ConsoleOutput("Traceback (most recent call last):")
        self.ConsoleOutput("SyntaxError: command "+str(report)+" is not defined")
    
    def ConsoleOutput(self,output):
        for x in range(self.Lines-1,0,-1):
            self.SavedLines[x].text = self.SavedLines[x-1].text
        self.SavedLines[0].text = output
        return None