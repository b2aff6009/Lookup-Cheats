# TODO
## Readme
- complete the installation description
- add a short "usage" gif

## Content
- Add a .csh for vim from dev.to

## Help
- Add a section of "how to use CS"
- Add a description "how to create a cheat sheet"
- create a complete list of settings (mandantory and optional)

## Backend

### Crawler
- ~~Implement a crawler~~
- ~~search for csh files in given directoies (dir's from settings)~~
- Enable the crawler to search in git repos.
   
### Gui
- Add a better multi screen support
- Check if Gui works on all three platform (Linux: done, Windows: <>, Mac: <>)
- Add a way to jump back to sheetSelector
- Add support for icons instead of string in "shortcut" coloumn
- Improve the update performance
  - ~~Hide instead of delete~~
  - ~~Hide/Delete item only if it is not part of the new results~~
 
### Finder
- ~~Add an alternative fuzzyfinder~~
- ~~select finder via settings~~
- in case of a more specific search string us the old results as source for the search
 
### Settings
- implement an exit key
- add "autoselect" sheet if possible (via processName)
- Create a userinterface for handle the settings
- ~~add a "default" sheet to the settings~~

## Misc

### Known issues
- stop worker thread in gui is dirty
- "splash" doesn't work on mac
- reorder of data doesn't work with new gui update
- Cheater doesn't support multi screens.

### Add tests
- ~~Crawler~~
- ~~finder~~
- gui

### Install scripts:
- Windows
- Linux (with service option)
- Mac
### Start scripts:
- Windows
- Linux
- Mac
