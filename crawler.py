import os

class Crawler:
    def __init__(self, settings):
        self.settings = settings
        self.sheets = {}

    def getSheets(self):
        for path in self.settings["directories"]:
            self.searchFiles(path)
        return self.sheets


    def searchFiles(self, path):
        result = []
        for subdir, dirs, files in os.walk(path):
            for filename in files:
                if (filename.endswith(self.settings["extension"])):
                    filepath = os.path.join(subdir, filename)
                    self.sheets[filename.replace(self.settings["extension"],"")] = os.path.join(subdir, filename)
            if self.settings["recrusive"] == False:
                break
        return result

if __name__ == '__main__':
    settings = {}
    settings['recrusive'] = False
    settings['extension'] = '.csh'
    settings['directories'] = ['./tests/data/', './tests/data/subdata/']
    crawler = Crawler(settings)
    print(crawler.getSheets())