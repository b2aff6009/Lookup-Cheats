from tkinter import * #used for the user interface
import json 
import codecs 
import fuzzyfinder #Used as backend search tool for searchbar
import keyboard #used for toggle shortcut
import platform #for platform check (keyboard need root on unix)
import os #needed for user id check
 
SettingsPath = "CheatSheets.json"
settings = {}

class FinderCs:
    def __init__(self, key, data):

        entrys = data[key]
        self.order = data["visible"]
        self.entrys = entrys
        self.entryDict = {}
        for i,entry in enumerate(entrys):
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
        results = fuzzyfinder.fuzzyfinder(text, self.entrys, accessor=lambda x: x["tosearch"])
        return self.orderResults(list(results))

class GuiEntry:
    def __init__(self, entry, isHeadline, root, x, mRow = 0, mCol=0):
        self.entry = entry
        self.isHeadline = isHeadline
        self.frame = Frame(root, width=x, bg="yellow")
        self.cells = []

        colWidth  = int(x/len(self.entry))
        for colNr, colEntry in enumerate(self.entry):
            self.frame.grid_columnconfigure(colNr, minsize=colWidth)
            if self.isHeadline:
                self.cells.append(Label(self.frame, text=colEntry, bg="lightblue", bd = 5, anchor=W, font=settings.get("HeadlineFont", 'Helvetica 15 bold')))
            else:
                self.cells.append(Label(self.frame, text=colEntry, bg="lightblue", anchor=W))
            self.cells[-1].grid(column=colNr, row=0)
        self.frame.pack()

    def __del__(self):
        if settings.get("Debug", False):
            print("Called del")
        self.frame.destroy()


class Gui:
    def __init__(self, finder):
        self.entrys = []
        self.visbleDict = {}
        self.finder = finder
        self.createMainWindow()
        self.createSearchBar(self.root, self.windowWidth, int(self.windowHeight/10), 0)
        self.mainFrame = Frame(self.root, width=self.windowWidth, height=int(9*self.windowHeight/10) , bg="white")
        self.mainFrame.grid(row=1)
        self.headline = GuiEntry(self.finder.order, True, self.mainFrame, self.windowWidth)
        self.root.grid()
        self.vis = True

        if ("shortcut" in settings.keys()):
            if platform.system() == "Windows" or os.getuid() == 0: 
                if settings.get("Debug", False):
                    print("Shortcut set to: " + settings["shortcut"])
                keyboard.add_hotkey(settings["shortcut"], self.toggle)
            else:
                print("Shortcut assignment need root priviliges on Unix! No toggle Key assigned.")


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
        self.root.grid_columnconfigure(0, minsize=self.windowWidth)
        self.root.wm_attributes("-topmost", True)

        if ("cleanKey" in settings.keys()):
            self.root.bind(settings["cleanKey"], lambda x: self.searchBar.delete(0, 'end'))

        if platform.system() == "Windows": 
            self.root.wm_attributes("-transparentcolor", "white")
            self.root.overrideredirect(True)
        else:
            self.root.attributes('-type', 'normal')
            self.root.wait_visibility(self.root)
        self.root.attributes('-alpha', settings.get("opacity", 1))


    def createSearchBar(self, root, x, y, mRow = 0, mCol = 0):
        self.searchFrame = Frame(self.root, bg="white", width=x, height=y)
        self.searchFrame.grid(row=mRow, column=mCol)
        self.searchFrame.grid_columnconfigure(0, minsize=int(x))
        self.searchBar = Entry(self.searchFrame, bg="grey", justify=CENTER)
        self.searchBar.bind("<KeyRelease>", self.update)
        self.searchBar.focus_set()
        self.searchBar.grid()
        return self.searchBar

    def update(self, event = 0):
        hits = self.finder.find(self.searchBar.get())
        
        for eId in self.visbleDict.keys():
            if eId not in hits.keys():
                del self.visbleDict[eId] 

        for eId in hits.keys():
            if eId not in self.visbleDict.keys():
                self.visbleDict[eId] = GuiEntry(hits[eId], False, self.mainFrame, self.windowWidth)

    def run(self):
        self.update()
        self.root.mainloop()

def LoadSettings(name):
    global settings
    with open(SettingsPath, 'rb') as f:
        configJson = json.load(f)
    settings = configJson["settings"]

    with open(configJson["sheets"][name], 'rb') as f:
        data = json.load(f)
    #Overwrite global settings with specific sheet settings
    if settings.get("AllowOverwrite", True):
        for key in data["settings"] :
            settings[key] = data["settings"][key]
    return FinderCs(name, data)

if __name__ == "__main__":
    finder = LoadSettings("vim")
    Ui = Gui(finder)
    Ui.run()
