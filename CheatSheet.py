from tkinter import * #used for the user interface
import json 
import codecs 
import fuzzyfinder #Used as backend search tool for searchbar
import keyboard #used for toggle shortcut
import platform #for platform check (keyboard need root on unix)
import os #needed for user id check
 
SettingsPath = "CheatSheets.json"
settings = {}

class CheatSheetTool:

    def getType(self, data):
        return str(type(data)).split("'")[1]

    def __init__(self, key, path):
        self.converter = {
            'dict' : lambda cell : "Dict is not yet supported",
            'list' : lambda cell : "".join([self.converter[self.getType(entry)](entry) for entry in cell]),
            'str' : lambda x : x,
            'int' : lambda x : str(x),
            'unicode' : lambda x : str(x)
        }

        with open(path, 'rb') as f:
            CheatSheet = json.load(f)
        entrys = CheatSheet[key]
        self.order = CheatSheet["entry"]
        self.entrys = entrys
        for entry in entrys:
            entry["tosearch"] = self.createSearchEntry(entry.values())


    def createSearchEntry(self, entry):
        tosearch = ""
        for cell in entry:
            tosearch = "".join(self.converter[self.getType(cell)](cell))
        return tosearch

    def orderResults(self, unorderd):
        results = []
        for entry in unorderd:
            results.append([entry[step] for step in self.order]) 
        return results

    def find(self, text):
        results = fuzzyfinder.fuzzyfinder(text, self.entrys, accessor=lambda x: x["tosearch"])
        return self.orderResults(list(results))

class GuiEntry:
    def __init__(self, entry):
        self.entry = entry

    def __del__(self):
        if settings.get("Debug", False):
            print("Called del")
        self.frame.destroy()

    def AddLine(self, root, x, mRow = 0, mCol=0):
        colWidth  = int(x/len(self.entry))

        self.frame = Frame(root, width=x, bg="yellow")
        self.cells = []
        for colNr, colEntry in enumerate(self.entry):
            self.frame.grid_columnconfigure(colNr, minsize=colWidth)
            self.cells.append(Label(self.frame, text=colEntry, bg="lightblue", anchor=W))
            self.cells[-1].grid(column=colNr, row=0)

        self.frame.grid(row=mRow, column=mCol)
 
class Gui:
    def __init__(self):
        self.entrys = []
        self.createMainWindow()
        self.createSearchBar(self.root, self.windowWidth, int(self.windowHeight/10), 0)
        self.mainFrame = Frame(self.root, width=self.windowWidth, height=int(9*self.windowHeight/10) , bg="white")
        self.mainFrame.grid(row=1)
        self.root.grid()
        if ("shortcut" in settings.keys()):
            if platform.system() == "Windows" or os.getuid() == 0: 
                print("Shortcut set to: " + settings["shortcut"])
                keyboard.add_hotkey(settings["shortcut"], self.toggle)
            else:
                print("Shortcut assignment need root priviliges on Unix! No toggle Key assigned.")
        self.vis = True

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
        self.windowWidth = int(self.root.winfo_screenwidth()/2)
        self.windowHeight = int(self.root.winfo_screenheight()/2)
         
        # Gets both half the screen width/height and window width/height
        self.positionRight = int(self.root.winfo_screenwidth()/2 - self.windowWidth/2)
        self.positionDown = int(self.root.winfo_screenheight()/2 - self.windowHeight/2)
          
        # Positions the window in the center of the page.
        self.root.geometry("{}x{}".format(self.windowWidth, self.windowHeight))
        self.root.geometry("+{}+{}".format(self.positionRight, self.positionDown))
        self.root.grid_columnconfigure(0, minsize=self.positionRight)
        self.root.wm_attributes("-topmost", True)
        if not settings.get("Debug", False):
            self.root.attributes('-alpha', 0.8)
            self.root.wm_attributes("-transparentcolor", "white")
            self.root.overrideredirect(True)

    def createSearchBar(self, root, x, y, mRow = 0, mCol = 0):
        self.searchFrame = Frame(self.root, bg="white", width=x, height=y)
        self.searchFrame.grid(row=mRow, column=mCol)
        self.searchFrame.grid_columnconfigure(0, minsize=int(x))
        self.searchBar = Entry(self.searchFrame, bg="grey", justify=CENTER)
        self.searchBar.bind("<KeyRelease>", self.update)
        self.searchBar.focus_set()
        self.searchBar.grid()
        return self.searchBar

    def update(self, event):
        del self.entrys[:]

        hits = toolSheet.find(self.searchBar.get()) 
        for i, hit in enumerate(hits,0):
            newEntry = GuiEntry(hit)
            newEntry.AddLine(self.mainFrame, self.windowWidth, i, 0)
            self.entrys.append(newEntry)

    def run(self):
        self.root.mainloop()

def LoadSettings(name):
    global settings
    with open(SettingsPath, 'rb') as f:
        configJson = json.load(f)
    settings = configJson["settings"]
    ToolSheet = CheatSheetTool(name, configJson["sheets"][name]) 
    return ToolSheet

if __name__ == "__main__":
    toolSheet = LoadSettings("vim")
    print(settings)
    print(settings.get("Debug", False))
    Ui = Gui()
    Ui.run()
