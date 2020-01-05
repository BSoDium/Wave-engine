from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.DirectGui import *
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import *
import sys,os

MAINDIR = Filename.from_os_specific(os.getcwd())


class Console:
    def __init__(self):
        return None
        
    def create(self,renderBase,CommandDictionary):
        base.a2dBottomLeft.set_bin('background', 123) # avoid drawing order conflict
        self.CommandDictionary = {**CommandDictionary,**{"usage":self.helper,"help":self.showCommands}} #copy for further use in other methods
        self.hidden = False
        self.textscale = 0.04
        self.Lines = 43
        self.background = OnscreenImage(image = str(MAINDIR)+"/files/bg.png",pos = (0.65,0,1), parent = base.a2dBottomLeft)
        self.background.setTransparency(TransparencyAttrib.MAlpha)
        self.SavedLines = [OnscreenText(text = '', pos = (0.02, 0.1 + x*1.1*self.textscale), scale = self.textscale, align = TextNode.ALeft, fg = (1,1,1,1), parent = base.a2dBottomLeft) for x in range(self.Lines)]
        self.loadConsoleEntry()
        self.commands = self.CommandDictionary
        #self.entry.reparent_to(App)
        base.accept('f1',self.toggle,[base])
        self.toggle(base) # initialize as hidden
        return None
    
    def loadConsoleEntry(self): #-1.76, 0, -0.97
        self.entry = DirectEntry(scale=self.textscale,
                                    frameColor=(0,0,0,1),
                                    text_fg = (1,1,1,1),
                                    pos = (0.025, 0, 0.03),
                                    overflow = 1,
                                    command=self.ConvertToFunction,
                                    initialText="",
                                    numLines = 1,
                                    focus=True,
                                    width = 40,
                                    parent = base.a2dBottomLeft)
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
        self.ConsoleOutput(" ")
        self.ConsoleOutput(str(MAINDIR)+">  "+data)
        self.ConsoleOutput(" ")
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
                    self.ConsoleOutput('This command requires (at least) one argument')

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
        maxsize = 73
        discretized = [output[i:i+maxsize] for i in range(0,len(output),maxsize)]
        for i in discretized:
            for x in range(self.Lines-1,0,-1):
                self.SavedLines[x].text = self.SavedLines[x-1].text
            self.SavedLines[0].text = i
        return None
    
    def helper(self,index):
        i = self.CommandDictionary[index]
        self.ConsoleOutput("Help concerning command '"+str(index)+"':")
        self.ConsoleOutput("    associated function name is "+str(i.__name__))
        self.ConsoleOutput("Documentation provided: ")
        doc = self.TextToLine(str(i.__doc__))
        self.ConsoleOutput("    "+doc)
        self.ConsoleOutput("Known arguments: ")
        self.ConsoleOutput("    "+str(i.__code__.co_varnames))
        return None
    
    def showCommands(self):
        self.ConsoleOutput("List of available commands: ")
        for i in self.CommandDictionary:
            self.ConsoleOutput("- "+str(i))
        self.ConsoleOutput(" ")
        self.ConsoleOutput("Use usage(command) for more details on a specific command")
        return None

    def TextToLine(self,text):
        try:
            text = text.replace("\n","")
        except:
            pass
        return text