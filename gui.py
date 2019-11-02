'''import pip
def install(package):
    if hasattr(pip, 'main'):
        pip.main(['install', package])
    else:
        pip._internal.main(['install', package])

try:
    import keyboard #used for toggle shortcut
except ImportError as e:
    install("keyboard")'''

import keyboard #used for toggle shortcut
from tkinter import * #used for the user interface
import platform #for platform check (keyboard need root on unix)
import os #needed for user id check
import threading

class GuiEntry:
    '''GuiEntrys represent the data blocks in the cheatsheet, including the style'''
    def __init__(self, entry, isHeadline, root, settings, x, mRow = 0, mCol=0):
        bgColors = settings["bgColors"]
        self.entry = entry
        self.isHeadline = isHeadline
        #self.frame = Frame(root, bg=bgColors[2], bd=2, relief=SOLID)
        self.frame = Frame(root, width=x, bg=bgColors[2], bd=2)
        self.cells = []

        colWidth  = int(x/len(self.entry))
        labelFont = settings["HeadlineFont"] if isHeadline else settings["Font"]
        for colNr, colEntry in enumerate(self.entry):
            self.frame.grid_columnconfigure(colNr, minsize=colWidth)
            bgColor = bgColors[2] if isHeadline else bgColors[colNr%2]
            self.cells.append(Label(self.frame, text=colEntry, bg=bgColor, bd = 1, anchor=W, font=labelFont, wraplength=colWidth))

            if settings["multiLineEntry"]:
                self.cells[-1].grid(column=0, row=colNr, sticky=E+W)
            else:
                self.cells[-1].grid(column=colNr, row=0, sticky=E+W)
        self.frame.pack(fill=X)

    def __del__(self):
        self.frame.destroy()

    def hide(self):
        self.frame.pack_forget()
    
    def show(self):
        self.frame.pack(fill=X)

class ListEntry:
    '''List Entrys are used to fill the cheatsheet selection listView'''
    def __init__(self, entry, eId, root):
        self.entry = entry
        text = entry[0]
        self.root = root    
        root.insert(END,  text)
        self.id = eId
        root.selection_set(first=0)
    
    def __del__(self):
        self.root.delete(self.id)
        self.root.selection_clear(0, END)
        self.root.selection_set(first=0)
        self.root.activate(0)

    def hide(self):
        pass
    
    def show(self):
        pass

class Gui:
    def __init__(self, finder, settings = {}, isSheetSelector = False):
        self.settings = settings
        self.entrys = []
        self.loadedFrames = {}
        self.visibleFrames = {}
        self.mainFrames = []
        self.headlines = []
        self.sheet = ""
        self.isSheetSelector = isSheetSelector
        self.finder = finder
        self.createMainWindow()
        self.createSearchBar(self.root, self.windowWidth, int(self.windowHeight/10), 0)

        self.frameWidth = self.windowWidth/self.settings["columns"]
        self.mainFrame = Frame(self.root, width=self.windowWidth, height=int(9*self.windowHeight/10) , bg="white")
        self.mainFrame.grid(row=1)

        if isSheetSelector:
            self.mainFrame = Listbox(self.mainFrame, selectmode=SINGLE)
            self.mainFrame.pack()
            self.root.bind(self.settings["selectKey"], self.execute)
            self.root.bind(self.settings["selectionUp"], self.changeSelection)
            self.root.bind(self.settings["selectionDown"], self.changeSelection)
        else:
            colNr = self.settings["columns"]
            for i in range(0, colNr):
                self.mainFrames.append(Frame(self.mainFrame, width=self.frameWidth, height=int(9*self.windowHeight/10) , bg="white"))
                self.mainFrames[-1].grid(row = 1, column=i)
                if not self.settings["multiLineEntry"]:
                    self.headlines.append(GuiEntry(self.finder.order, True, self.mainFrames[-1], self.settings, self.frameWidth))

        self.root.grid()
        self.vis = True
        self.worker = threading.Thread()

        if ("cleanKey" in self.settings.keys()):
            self.root.bind(self.settings["cleanKey"], lambda x: self.searchBar.delete(0, 'end'))        
        #self.root.bind(self.settings["backKey"], del self)


        if ("shortcut" in self.settings.keys()):
            if platform.system() == "Windows" or os.getuid() == 0: 
                if self.settings["Debug"]:
                    print("Shortcut set to: " + self.settings["shortcut"])
                keyboard.add_hotkey(self.settings["shortcut"], self.toggle)
            else:
                print("Shortcut assignment need root priviliges on Unix! No toggle Key assigned.")



    def execute(self, event):
        for i, key in enumerate(self.loadedFrames.keys()):
            if i == self.mainFrame.curselection()[0]:
                if self.settings["Debug"]:
                    print(self.loadedFrames[key].entry)
                self.sheet = self.loadedFrames[key].entry[0]
                self.root.destroy()

    def changeSelection(self, event):
        if(self.settings["selectionUp"] == ("<" + event.keysym + ">")):
                direction = -1
        elif(self.settings["selectionDown"] == ("<" + event.keysym + ">")):
                direction = 1
        newSelection = self.mainFrame.curselection()[0] + direction
        self.mainFrame.select_clear(0,END)
        self.mainFrame.selection_set(first = newSelection)
        self.mainFrame.activate(newSelection)

    def toggle(self):
        print(getProcessName())
        self.root.update()
        if self.vis == True:
            self.root.withdraw()
            self.vis = False
        else:
            self.root.deiconify()
            self.root.focus_force()
            if platform.system() == "Linux":
                self.searchBar.focus_force() #TODO check if needed on mac/win
            else:
                self.searchBar.focus_set()
            self.vis = True


    def createMainWindow(self):
        self.root = Tk()
        self.root.title("Cheatssheets")
        self.root.config(bg="white")

        # Gets the requested values of the height and widht.
        # Set window positon, width and heigth
        position = self.settings["position"]
        self.windowWidth = int(self.root.winfo_screenwidth()*(1-2*position[0]))
        self.windowHeight = int(self.root.winfo_screenheight()*(1-position[1]))
        self.positionX = int(position[0]*self.root.winfo_screenwidth())
        self.positionY = int(position[1]*self.root.winfo_screenheight())

        if (self.settings["Debug"] == True):
            print("W: {} H: {}".format(self.root.winfo_screenwidth(), self.root.winfo_screenheight()))
            print("X: {} Y: {} Height: {} Width: {}".format(self.positionX, self.positionY, self.windowHeight, self.windowWidth))

        #OS specific window self.settings
        if platform.system() == "Windows": 
            self.root.wm_attributes("-transparentcolor", "white")
            self.root.overrideredirect(True)
        elif platform.system() == "Linux":
            self.root.geometry("{}x{}".format(self.windowWidth, self.windowHeight))
            #self.root.wm_attributes('-type', 'splash')
            self.root.wait_visibility(self.root)
        else:
            self.root.wait_visibility(self.root)

        # Positions the window in the center of the page.
        self.root.geometry("+{}+{}".format(self.positionX, self.positionY))
        self.root.grid_columnconfigure(0, minsize=self.windowWidth)
        self.root.wm_attributes("-topmost", True)
        self.root.attributes('-alpha', self.settings["opacity"])

    def createSearchBar(self, root, x, y, mRow = 0, mCol = 0):
        '''Create the top line of the window including the text edit where the text to search comes from.'''
        self.searchFrame = Frame(self.root, bg="white", height=y)
        self.searchFrame.grid(row=mRow, column=mCol)
        self.searchBar = Entry(self.searchFrame, bg="grey", justify=CENTER)
        self.searchBar.bind("<KeyRelease>", self.update)

        if platform.system() == "Linux":
            self.searchBar.focus_force() #TODO check if needed on mac/win
        else:
            self.searchBar.focus_set()
        self.searchBar.grid()
        return self.searchBar

    def update(self, event = 0):
        del self.worker
        self.worker = threading.Thread(target=self.updateGui)
        self.worker.start()

    def createEntry(self, key, hits):
        if (self.isSheetSelector):
            self.loadedFrames[key] = ListEntry(hits[key], key, self.mainFrame)
        else:
            frame = self.mainFrames[len(self.loadedFrames.keys())%self.settings["columns"]]
            self.loadedFrames[key] = GuiEntry(hits[key], False, frame, self.settings, self.frameWidth)

    def updateGui(self):
        hits = self.finder.find(self.searchBar.get())

        keys = list(filter(lambda x: x not in hits.keys(), self.visibleFrames.keys()))
        for key in keys:
            self.visibleFrames[key].hide()
            del self.visibleFrames[key]
            if self.isSheetSelector:
                del self.loadedFrames[key] 

        for key in filter(lambda x: x not in self.visibleFrames.keys(), hits.keys()):
            if len(self.visibleFrames) >= self.settings["maxEntrys"]:
                break;
            if key not in self.loadedFrames.keys():
                self.createEntry(key, hits)
            self.visibleFrames[key] = self.loadedFrames[key]
            self.visibleFrames[key].show()

    def run(self):
        self.update()
        self.root.mainloop()
