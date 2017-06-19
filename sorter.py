#! /usr/bin/env python3

import os
import logging
from gui.tkgui import TkGui
from operations import SorterOps
from helpers import DatabaseHelper
from settings import DATABASES, LOG_FILE

DB_NAME = DATABASES['default']['NAME']

if __name__ == '__main__':
    db_helper = DatabaseHelper(DB_NAME)
    # Create database and tables
    db_helper.initialise_db()

    # Initialise operations
    operations = SorterOps(db_helper)

    # Initialise logger
    logging.basicConfig(filename=LOG_FILE,
                        format='%(asctime)s %(message)s', level=logging.INFO)

    # Initialise GUI
    app = TkGui(operations=operations, logger=logging)

    # Show window
    app.tk_run()
