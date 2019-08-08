#!/bin/bash
rm -rf ./dist
pyinstaller -F ./CheatSheet.py
cp configuration.json ./dist/
