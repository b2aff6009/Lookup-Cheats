from finder import *
import pytest

import os
import sys
import inspect
current_dir = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

settings = {}


def search_data():
    data = {"common": [
            {"shourtcut": "ctrl+a", "data": "One", "anOtherEntry": "First"},
            {"shourtcut": "ctrl+b", "data": "two", "anOtherEntry": 2},
            {"shourtcut": "ctrl+c", "data": "tHree", "anOtherEntry": "Third"},
            {"shourtcut": "ctrl+d", "data": "four",
                "anOtherEntry": "This is a sentence"},
            {"shourtcut": "ctrl+e", "data": "five",
                "anOtherEntry": ["Using", "a", "list"]}
            ],
            "visible": ["data"]
            }
    return data


def sheet_data():
    sheets = {
        "sheet1": "FirstCheatSheet.csh",
        "sheet2": "IncludeA0.csh",
        "sheet3": "",
    }
    return sheets


def test_create_finder():
    finder = createFinder("normal", {}, True)
    assert finder.__class__.__name__ == "StandardFinder", "Didn't created a StandardFinder"
    finder = createFinder("lskdjf", {}, True)
    assert finder.__class__.__name__ == "StandardFinder", "Didn't created a StandardFinder"
    finder = createFinder("fuzzy", {}, True)
    assert finder.__class__.__name__ == "FuzzyFinder", "Didn't created a FuzzyFinder"


def test_standard_find_sheets():
    sheets = sheet_data()
    sheetFinder = createFinder("normal", sheets, True)

    assert len(sheetFinder.find("sheet")) == 3, "Faild for sheet"
    assert len(sheetFinder.find("0")) == 1, "Faild for 0"
    assert len(sheetFinder.find("CompleyString")
               ) == 0, "Faild for complex string"
    assert len(sheetFinder.find("FCS")) == 0, "Faild for FCS"


def test_fuzzy_find_sheets():
    sheets = sheet_data()
    sheetFinder = createFinder("fuzzy", sheets, True)

    assert len(sheetFinder.find("sheet")) == 3, "Faild for sheet"
    assert len(sheetFinder.find("0")) == 1, "Faild for 0"
    assert len(sheetFinder.find("CompleyString")
               ) == 0, "Faild for complex string"
    assert len(sheetFinder.find("FCS")) == 1, "Faild for FCS"


def test_search_result_standard():
    data = search_data()
    finder = createFinder("normal", data)

    assert len(finder.find("1")) == 0, "Found a 1"
    assert len(finder.find("2")) == 1, "Didn't found the 2"
    assert len(finder.find("Tia sentence")) == 0, "Found the sentence"
    assert len(finder.find("")) == len(
        data["common"]), "Didn't found all entrys"
    assert len(finder.find("three")) == 1, "Case sensitive issue"
    assert len(finder.find("a list")) == 1, "Didn't handled the list"


def test_search_result_fuzzy():
    data = search_data()
    finder = createFinder("fuzzy", data)

    assert len(finder.find("1")) == 0, "Found a 1"
    assert len(finder.find("2")) == 1, "Didn't found the 2"
    assert len(finder.find("Tia sentence")) == 1, "Didn't found the sentence"
    assert len(finder.find("")) == len(
        data["common"]), "Didn't found all entrys"
    assert len(finder.find("three")) == 1, "Case sensitive issue"
    assert len(finder.find("a list")) == 1, "Didn't handled the list"
