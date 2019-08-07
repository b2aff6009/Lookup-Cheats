import fuzzyfinder #Used as backend search tool for searchbar

class Finder:
    def __init__(self, data, isSheetSelector = False):
        print(data)
        if isSheetSelector:
            self.entrys = []
            self.order = ["name", "path"]
            for i, entry in enumerate(data["common"]):
                self.entrys.append({"name": entry, "id": i, "tosearch" : entry + data["common"][entry], "path": data["common"][entry]})
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
