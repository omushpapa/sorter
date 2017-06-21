#! /usr/bin/env bash
pyinstaller --clean --windowed --icon=sorter.ico --hidden-import=http.cookies sorter.py