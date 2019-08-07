import json 
import os #needed for user id check
import psutil
import platform

import finder
import gui
 
SettingsPath = "configuration.json"
settings = {}

def osName():
    Names = {"Windows" : "Windows", "Linux" : "Linux", "darwin" : "Mac"}
    return Names[platform.system()]

def getProcessName():
    p = psutil.Process(os.getpid())
    return p.name()

def parseShortSheet(cheatSheet):
    keyList = cheatSheet["entry"]
    valueList = cheatSheet["common"]
    data = {}
    data["visible"] = cheatSheet["visible"]
    data["common"] = []
    for value in valueList:
        entry = {}
        for i,key in enumerate(keyList,0):
            entry[key] = value[i]
        data["common"].append(entry)
    return data

def LoadSettings(name):
    global settings
    with open(SettingsPath, 'rb') as f:
        configJson = json.load(f)
    settings = configJson["settings"]
    print(getProcessName())
    if  name == "":
        selector = finder.Finder("sheets", configJson, True)
        selectGui = gui.Gui(selector, settings,  True)
        selectGui.run()
        return LoadSettings(selectGui.sheet)
    else:
        with open(configJson["sheets"][name], 'rb') as f:
            data = json.load(f)
        data["common"].extend(data.get(osName(), []))

    #Overwrite global settings with specific sheet settings
    if settings.get("AllowOverwrite", True):
        for key in data["settings"] :
            settings[key] = data["settings"][key]

    if (settings.get("shortSheet", False)):
        data = parseShortSheet(data)
    return finder.Finder(data)

if __name__ == "__main__":
    finder = LoadSettings("python")
    Ui = gui.Gui(finder, settings)
    Ui.run()
