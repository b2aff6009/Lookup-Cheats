import pytest

import os
import sys
import inspect
current_dir = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
settings = {}
import platform

from AppKit import NSScreen
def test_screens():
    print(platform.system())
    print(NSScreen.mainScreen().frame())
    print(NSScreen.mainScreen().frame().size.width)
    print(NSScreen.mainScreen().frame().size.height)

if __name__ == "__main__":
    test_screens()