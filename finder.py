import pip

def install(package):
    if hasattr(pip, 'main'):
        pip.main(['install', package])
    else:
        pip._internal.main(['install', package])

try:
    import fuzzyfinder #Used as backend search tool for searchbar
except ImportError as e:
    install("fuzzyfinder")


class Finder:
    def __init__(self, data, isSheetSelector = False):
        if isSheetSelector:
            self.entrys = []
            self.order = ["name", "path"]
            i = 0
            for key, val in data.items():
                self.entrys.append({"name": key, "path": val, "tosearch": " ".join([key, val]), "id": i})
                i = i + 1
        else:
            self.entrys = data["common"]
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


if __name__ == '__main__':
    SettingsPath = "configuration.json"
    settings = {}
    print("Test finder")
    import json

    with open(SettingsPath, 'rb') as f:
        configJson = json.load(f)
    sheetSelector = Finder(configJson["sheets"], True)
    print(sheetSelector.find(""))
