#! /usr/bin/env python3.4

import os
import logging
from gui.tkgui import TkGui
from gui.loader import Loader
from operations import SorterOps
from helpers import DatabaseHelper
from settings import DATABASES, LOG_FILE

DB_NAME = DATABASES['default']['NAME']

if __name__ == '__main__':
    sorter_loader = Loader()

    # Load database
    sorter_loader.report_progress(10, 'Loading database...')
    db_helper = DatabaseHelper(DB_NAME)
    sorter_loader.report_progress(20, 'Database loaded.')

    # Create database and tables
    sorter_loader.report_progress(30, 'Checking tables...')
    db_helper.initialise_db()
    sorter_loader.report_progress(40, 'Database initalised.')

    # Initialise operations
    sorter_loader.report_progress(50, 'Loading operations...')
    operations = SorterOps(db_helper)
    sorter_loader.report_progress(60, 'Operations initialised.')

    # Initialise logger
    sorter_loader.report_progress(80, 'Loading logger...')
    logging.basicConfig(filename=LOG_FILE,
                        format='%(asctime)s %(message)s', level=logging.INFO)
    sorter_loader.report_progress(90, 'Logger set.')

    # Close loader
    sorter_loader.report_progress(100, 'Initialising UI.')
    sorter_loader.tk_run()

    # Initialise GUI
    app = TkGui(operations=operations, logger=logging)

    # Show window
    app.tk_run()
