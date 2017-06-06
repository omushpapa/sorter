#! /usr/bin/env python3

from gui.tkgui import TkGui
from operations import initialise_db


if __name__ == '__main__':
    app = TkGui()

    # Create database and tables
    initialise_db()

    # Show window
    app.tk_run()
