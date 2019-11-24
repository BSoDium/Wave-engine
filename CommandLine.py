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
        self.CommandDictionary = CommandDictionary #copy for further use in other methods
        self.hidden = False
        self.textscale = 0.04
        self.Lines = 47
        self.background = OnscreenImage(image = str(MAINDIR)+"/files/bg.png",pos = (-1.14,0,0))
        self.background.setTransparency(TransparencyAttrib.MAlpha)
        self.SavedLines = [OnscreenText(text = '', pos = (-1.76, -0.9 + x*self.textscale), scale = self.textscale, align = TextNode.ALeft, fg = (1,1,1,1)) for x in range(self.Lines)]
        self.loadConsoleEntry()
        self.commands = CommandDictionary
        #self.entry.reparent_to(App)
        base.accept('f1',self.toggle,[base])
        self.toggle(base) # initialize as hidden
        return None
    
    def loadConsoleEntry(self):
        self.entry = DirectEntry(scale=self.textscale, frameColor=(1,1,1,1), pos = (-1.76, 0, -0.97),overflow = 1,command=self.ConvertToFunction,initialText="", numLines = 1, focus=True, width = 40)
        return None
    
    def toggle(self,base):
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
        self.entry.destroy()
        self.loadConsoleEntry()
        self.ConsoleOutput(">> "+data)
        Buffer = [""]
        for x in range(len(data)): # I know the way I did this sucks but I didn't want to think a lot
            if data[x] == "(":
                Buffer.append("(")
                if x != len(data) - 1:
                    Buffer.append("")
            elif data[x] == ")":
                Buffer.append(")")
                if x != len(data) - 1:
                    Buffer.append("")
            elif data[x] == ",":
                if x != len(data) - 1:
                    Buffer.append("")
            else:
                Buffer[len(Buffer)-1] += data[x]
        try:
            ChosenCommand = self.commands[Buffer[0]] # check if the command exists
            if len(Buffer)-1 and Buffer[1] == "(" and Buffer[len(Buffer)-1] == ")": # check if the command has some arguments
                args = Buffer[2:len(Buffer)-1]
                for i in range(len(args)):
                    try:
                        args[i] = float(args[i])
                    except:
                        args[i] = str(args[i])
                try:
                    ChosenCommand(*args)
                except:
                    self.ConsoleOutput("Wrong arguments provided")
            elif len(Buffer) - 1 and Buffer[len(Buffer)-1] != ")":
                self.ConsoleOutput('Missing parenthesis ")" in "'+ data + '"')
            else:
                try:
                    ChosenCommand()
                except:
                    self.ConsoleOutput('This command requires (at least) and argument')

        except:
            self.CommandError(Buffer[0])
        
        return None

    def SError(self,report):
        self.ConsoleOutput("Traceback (most recent call last):")
        self.ConsoleOutput("Incorrect use of the "+str(report)+" command")
        return None
    
    def CommandError(self,report):
        self.ConsoleOutput("Traceback (most recent call last):")
        self.ConsoleOutput("SyntaxError: command "+str(report)+" is not defined")
    
    def ConsoleOutput(self,output):
        #maxsize = self.entry['width']
        maxsize = 85
        discretized = [output[i:i+maxsize] for i in range(0,len(output),maxsize)]
        for i in discretized:
            for x in range(self.Lines-1,0,-1):
                self.SavedLines[x].text = self.SavedLines[x-1].text
            self.SavedLines[0].text = i
        return None
    
    def helper(self):
        self.ConsoleOutput("Help concerning available commands:")
        for i in self.CommandDictionary:
            self.ConsoleOutput(str(i))
            self.ConsoleOutput(str(help(self.CommandDictionary[i])))
        return None