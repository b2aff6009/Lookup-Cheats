import pytest

import os
import sys
import inspect
current_dir = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
from crawler import Crawler

settings = {}


def test_wrong_extension():
    settings['recrusive'] = False
    settings['extension'] = '.cs'
    settings['directories'] = ['./tests/data/', './tests/data/subdata/']
    test_crawler = Crawler(settings)
    sheets = test_crawler.getSheets()
    assert len(sheets.keys()) == 0, "extension test failed"


def test_multiple_folders():
    settings['recrusive'] = False
    settings['extension'] = '.csh'
    settings['directories'] = ['./tests/data/', './tests/data/subdata/']
    test_crawler = Crawler(settings)
    sheets = test_crawler.getSheets()
    assert len(sheets.keys()) == 5, "multiple folders test failed"


def test_recrusive():
    settings['recrusive'] = True
    settings['extension'] = '.csh'
    settings['directories'] = ['./tests/data/']
    test_crawler = Crawler(settings)
    sheets = test_crawler.getSheets()
    assert len(sheets.keys()) == 5, "recrusive test failed"


def test_non_recrusive():
    settings['recrusive'] = False
    settings['extension'] = '.csh'
    settings['directories'] = ['./tests/data/']
    test_crawler = Crawler(settings)
    sheets = test_crawler.getSheets()
    assert len(sheets.keys()) == 3, "recrusive test failed"
