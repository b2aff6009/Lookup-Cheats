import json

def parseShortSheet(path, valueKey):
    with open(path, 'rb') as f:
        cheatSheet = json.load(f)
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
        


def exportLongSheet(path, data):
    with open(path, 'w') as outfile:
        json.dump(data, outfile, indent = 4)

if __name__ == "__main__":
    data = parseShortSheet("exampleSheet.json", "example")
    exportLongSheet("longExampleSheet.json", data)


