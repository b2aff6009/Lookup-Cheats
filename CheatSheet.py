
import json 
import os #needed for user id check
import psutil
import platform

import finder
import crawler
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

def SelectSheet(sheets):
    global settings
    selector = finder.createFinder(settings.get("finder", ""), sheets, True)
    selectGui = gui.Gui(selector, settings,  True)
    selectGui.run()
    return selectGui.sheet

def setDefault(data, key, val):
    data[key] = data.get(key, val)

def SetDefaultSettings(config):
    '''Ensure that every config parameter exists, if it doens't it will be set to a default value'''

    #Settings used by crawler
    setDefault(config, "crawler", {})
    setDefault(config["crawler"], "use", True)
    setDefault(config["crawler"], "recrusive", True)
    setDefault(config["crawler"], "extension", ".csh")
    setDefault(config["crawler"], "directories", ["./"])

    setDefault(config, "sheets", {})

    setDefault(config, "settings", {})
    setDefault(config["settings"], "defaultSheet", "")
    setDefault(config["settings"], "AllowOverwrite", True)
    setDefault(config["settings"], "shortSheet", False)

    #Settings used by Gui
    setDefault(config["settings"], "bgColors", ["SkyBlue1", "SkyBlue2", "SkyBlue3"])
    setDefault(config["settings"], "HeadlineFont", 'Helvetica 15 bold') 
    setDefault(config["settings"], "Font", 'Helvetica 11')
    setDefault(config["settings"], "multiLineEntry", False)
    setDefault(config["settings"], "columns",1)
    setDefault(config["settings"], "selectKey",'<Return>')
    setDefault(config["settings"], "position", [0.25, 0.25])
    setDefault(config["settings"], "opacity", 1)
    setDefault(config["settings"], "maxEntrys", 30)
    setDefault(config["settings"], "selectionUp",'<Up>')
    setDefault(config["settings"], "selectionDown",'<Down>')
    setDefault(config["settings"], "Debug", False)


def LoadSettings(name):
    global settings
    with open(SettingsPath, 'rb') as f:
        configJson = json.load(f)
    SetDefaultSettings(configJson)
    settings = configJson["settings"]
    if settings["Debug"]:
        print(configJson)

    if (configJson["crawler"]["use"] == True):
        sheetCrawler = crawler.Crawler(configJson["crawler"])
        configJson["sheets"] = sheetCrawler.getSheets()
    if settings.get("Debug", False) == True:
        print(configJson["sheets"])

    if name == "":
        name = settings["defaultSheet"]
    if name == "" or name not in configJson['sheets']:
        name = SelectSheet(configJson['sheets'])

    with open(configJson["sheets"][name], 'rb') as f:
        data = json.load(f)
    data["common"].extend(data.get(osName(), []))

    #Overwrite global settings with specific sheet settings
    if settings["AllowOverwrite"]:
        for key in data["settings"] :
            settings[key] = data["settings"][key]

    if (settings["shortSheet"]):
        data = parseShortSheet(data)
    return finder.createFinder(settings.get("finder", ""), data)

if __name__ == "__main__":
    finder = LoadSettings("")

    if settings.get("Debug", False) == True:
        print("Finder typ: {}".format(finder.__class__))
    Ui = gui.Gui(finder, settings)
    Ui.run()
