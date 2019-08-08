#!/bin/bash

WORKPATH=./tmp
OUTPUTPATH=./output
SOURCE=./CheatSheet.py

rm -rf $OUTPUTPATH
pyinstaller --workpath $WORKPATH --distpath $OUTPUTPATH -F $SOURCE
cp configuration.json $OUTPUTPATH
