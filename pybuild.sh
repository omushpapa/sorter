#! /usr/bin/env bash
pyinstaller --clean --windowed --icon=assets/sorter.ico --hidden-import=http.cookies --hidden-import=html.parser sorter.py