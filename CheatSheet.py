from tkinter import * #used for the user interface
import json 
import codecs 
import fuzzyfinder #Used as backend search tool for searchbar
import keyboard #used for toggle shortcut
import platform #for platform check (keyboard need root on unix)
import os #needed for user id check
import threading
 
SettingsPath = "CheatSheets.json"
settings = {}

class FinderCs:
    def __init__(self, key, data, isSheetSelector = False):
        if isSheetSelector:
            self.entrys = []
            self.order = ["name", "path"]
            for i, entry in enumerate(data[key]):
                self.entrys.append({"name": entry, "id": i, "tosearch" : entry + data[key][entry], "path": data[key][entry]})
        else:
            self.entrys = data[key]
            self.order = data["visible"]
            for i,entry in enumerate(self.entrys):
                entry["tosearch"] = self.createSearchEntry(entry.values())
                entry["id"] = i

    def createSearchEntry(self, entry):
        getType = lambda data :str(type(data)).split("'")[1]
        useConverter = lambda entry : self.converter.get(getType(entry), lambda x : str(x))(entry)
        self.converter = {
            'dict' : lambda cell : "Dict is not yet supported",
            'list' : lambda cell : " ".join([useConverter(entry) for entry in cell])
        }
        tosearch = "".join([useConverter(cell) for cell in entry])
        return tosearch

    def orderResults(self, unorderd):
        results = {}
        for entry in unorderd:
            results[entry["id"]] = [entry[step] for step in self.order]
        return results

    def find(self, text):
        results = self.orderResults(list(fuzzyfinder.fuzzyfinder(text, self.entrys, accessor=lambda x: x["tosearch"])))
        return results

class ListEntry:
    def __init__(self, entry, eId, root):
        self.entry = entry
        text = " ".join(entry)
        self.root = root    
        root.insert(END,  text)
        self.id = eId
        root.selection_set(first=0)
    
    def __del__(self):
        if settings.get("Debug", False):
            print("Called del")
        self.root.delete(self.id)
        self.root.selection_clear(0, END)
        self.root.selection_set(first=0)
        self.root.activate(0)

class GuiEntry:
    def __init__(self, entry, isHeadline, root, x, mRow = 0, mCol=0):
        bgColors = ["SkyBlue1", "SkyBlue2", "SkyBlue3"]
        self.entry = entry
        self.isHeadline = isHeadline
        if(root.widgetName == "listbox"):
            root.insert(END,  entry)
            return
        self.frame = Frame(root, bg=bgColors[2], bd=2, relief=SOLID)
        #self.frame = Frame(root, width=x, bg=bgColors[2], bd=5)
        self.cells = []

        colWidth  = int(x/len(self.entry))
        labelFont = settings.get("HeadlineFont", 'Helvetica 15 bold') if isHeadline else settings.get("Font", 'Helvetica 11')
        for colNr, colEntry in enumerate(self.entry):
            self.frame.grid_columnconfigure(colNr, minsize=colWidth)
            bgColor = bgColors[2] if isHeadline else bgColors[colNr%2]
            self.cells.append(Label(self.frame, text=colEntry, bg=bgColor, bd = 1, anchor=W, font=labelFont))

            if settings.get("multiLineEntry", False):
                self.cells[-1].grid(column=0, row=colNr, sticky=E+W)
            else:
                self.cells[-1].grid(column=colNr, row=0, sticky=E+W)
        self.frame.pack(fill=X)

    def __del__(self):
        if settings.get("Debug", False):
            print("Called del")
        self.frame.destroy()


class Gui:
    def __init__(self, finder, isSheetSelector = False):
        self.entrys = []
        self.visbleDict = {}
        self.mainFrames = []
        self.headlines = []
        self.sheet = ""
        self.finder = finder
        self.createMainWindow()
        self.createSearchBar(self.root, self.windowWidth, int(self.windowHeight/10), 0)

        self.frameWidth = self.windowWidth/settings.get("columns",1)
        self.mainFrame = Frame(self.root, width=self.windowWidth, height=int(9*self.windowHeight/10) , bg="white")
        self.mainFrame.grid(row=1)

        if isSheetSelector:
            self.mainFrame = Listbox(self.mainFrame, selectmode=SINGLE)
            self.mainFrame.pack()
            self.root.bind(settings.get("selectKey",'<Return>'), self.execute)
            self.root.bind(settings.get("selectionUp",'<Up>'), self.changeSelection)
            self.root.bind(settings.get("selectionDown",'<Down>'), self.changeSelection)
        else:
            colNr = settings.get("columns", 1)
            for i in range(0, colNr):
                self.mainFrames.append(Frame(self.mainFrame, width=self.frameWidth, height=int(9*self.windowHeight/10) , bg="white"))
                self.mainFrames[-1].grid(row = 1, column=i)
                if not settings.get("multiLineEntry", False):
                    self.headlines.append(GuiEntry(self.finder.order, True, self.mainFrames[-1], self.frameWidth))

        self.root.grid()
        self.vis = True
        self.worker = threading.Thread()

        if ("cleanKey" in settings.keys()):
            self.root.bind(settings["cleanKey"], lambda x: self.searchBar.delete(0, 'end'))


        if ("shortcut" in settings.keys()):
            if platform.system() == "Windows" or os.getuid() == 0: 
                if settings.get("Debug", False):
                    print("Shortcut set to: " + settings["shortcut"])
                keyboard.add_hotkey(settings["shortcut"], self.toggle)
            else:
                print("Shortcut assignment need root priviliges on Unix! No toggle Key assigned.")


    def execute(self, event):
        for i, key in enumerate(self.visbleDict.keys()):
            if i == self.mainFrame.curselection()[0]:
                if settings.get("Debug", False):
                    print(self.visbleDict[key].entry)
                self.sheet = self.visbleDict[key].entry[0]
                self.root.destroy()

    def changeSelection(self, event):
        if(settings.get("selectionUp",'<Up>') == ("<" + event.keysym + ">")):
                direction = -1
        elif(settings.get("selectionDown",'<Down>') == ("<" + event.keysym + ">")):
                direction = 1
        newSelection = self.mainFrame.curselection()[0] + direction
        self.mainFrame.select_clear(0,END)
        self.mainFrame.selection_set(first = newSelection)
        self.mainFrame.activate(newSelection)

    def toggle(self):
        self.root.update()
        if self.vis == True:
            self.root.withdraw()
            self.vis = False
        else:
            self.root.deiconify()
            self.root.focus_force()
            self.searchBar.focus()
            self.vis = True


    def createMainWindow(self):
        self.root = Tk()
        self.root.title("Cheatssheets")
        self.root.config(bg="white")

        # Gets the requested values of the height and widht.
        # Set window positon, widdth and heigt
        position = settings.get("position", [0.25, 0.25])
        self.windowWidth = int(self.root.winfo_screenwidth()*(1-2*position[0]))
        self.windowHeight = int(self.root.winfo_screenheight()*(1-position[1]))
        self.positionX = int(position[0]*self.root.winfo_screenwidth())
        self.positionY = int(position[1]*self.root.winfo_screenheight())

        # Positions the window in the center of the page.
        if platform.system() != "Linux":
            self.root.geometry("{}x{}".format(self.windowWidth, self.windowHeight))
        self.root.geometry("+{}+{}".format(self.positionX, self.positionY))
        #self.root.grid_columnconfigure(0, minsize=self.windowWidth)
        self.root.wm_attributes("-topmost", True)

        if platform.system() == "Windows": 
            self.root.wm_attributes("-transparentcolor", "white")
            self.root.overrideredirect(True)
        else:
            self.root.attributes('-type', 'normal')
            self.root.wait_visibility(self.root)
        self.root.attributes('-alpha', settings.get("opacity", 1))


    def createSearchBar(self, root, x, y, mRow = 0, mCol = 0):
        self.searchFrame = Frame(self.root, bg="white", height=y)
        #self.searchFrame = Frame(self.root, bg="white", width=x, height=y)
        #self.searchFrame.grid_columnconfigure(0, minsize=int(x))
        self.searchFrame.grid(row=mRow, column=mCol)
        self.searchBar = Entry(self.searchFrame, bg="grey", justify=CENTER)
        self.searchBar.bind("<KeyRelease>", self.update)
        self.searchBar.focus_set()
        self.searchBar.grid()
        return self.searchBar

    def update(self, event = 0):
        del self.worker
        self.worker = threading.Thread(target=self.updateGui)
        self.worker.start()

    def updateGui(self):
        hits = self.finder.find(self.searchBar.get())

        if settings.get("columns", 1) > 1 and self.mainFrame.widgetName == "frame":
            for key in self.visbleDict.keys():
                del self.visbleDict[key]
        
        for eId in self.visbleDict.keys():
            if eId not in hits.keys():
                del self.visbleDict[eId] 

        for eId in hits.keys():
            if len(self.visbleDict) >= settings.get("maxEntrys", 30):
                break;
            if eId not in self.visbleDict.keys():
                if (self.mainFrame.widgetName == "frame"):
                    frame = self.mainFrames[len(self.visbleDict.keys())%settings.get("columns",1)]
                    self.visbleDict[eId] = GuiEntry(hits[eId], False, frame, self.frameWidth)
                else:
                    self.visbleDict[eId] = ListEntry(hits[eId], eId, self.mainFrame)

    def run(self):
        self.update()
        self.root.mainloop()

def parseShortSheet(cheatSheet, valueKey):
    keyList = cheatSheet["entry"]
    valueList = cheatSheet[valueKey]
    data = {}
    data["visible"] = cheatSheet["visible"]
    data[valueKey] = []
    for value in valueList:
        entry = {}
        for i,key in enumerate(keyList,0):
            entry[key] = value[i]
        data[valueKey].append(entry)
    return data

def LoadSettings(name):
    global settings
    with open(SettingsPath, 'rb') as f:
        configJson = json.load(f)
    settings = configJson["settings"]

    if  name == "":
        selector = FinderCs("sheets", configJson, True)
        selectGui = Gui(selector, True)
        selectGui.run()
        return LoadSettings(selectGui.sheet)
    else:
        with open(configJson["sheets"][name], 'rb') as f:
            data = json.load(f)

    #Overwrite global settings with specific sheet settings
    if settings.get("AllowOverwrite", True):
        for key in data["settings"] :
            settings[key] = data["settings"][key]

    if (settings.get("shortSheet", False)):
        data = parseShortSheet(data, name)
    return FinderCs(name, data)

if __name__ == "__main__":
    finder = LoadSettings("")
    Ui = Gui(finder)
    Ui.run()
