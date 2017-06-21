#! /usr/bin/env python3.4

import os
import logging
from gui.tkgui import TkGui
from gui.loader import Loader
from slib.operations import SorterOps
from slib.helpers import DatabaseHelper
from data.settings import DATABASES, LOG_FILE

DB_NAME = DATABASES['default']['NAME']

if __name__ == '__main__':
    # Initialise logger
    logging.basicConfig(filename=LOG_FILE,
                        format='%(asctime)s %(message)s', level=logging.INFO)
    logging.info('Logger ready')

    sorter_loader = Loader(logger=logging)

    # Load database helper
    sorter_loader.report_progress(
        30, 'Loading database helper with database file at "{}"'.format(DB_NAME))
    db_helper = DatabaseHelper(DB_NAME)
    sorter_loader.report_progress(40, 'Database helper loaded.')

    # Create database tables
    sorter_loader.report_progress(
        50, 'Connecting to database and checking tables...')
    db_helper.initialise_db()
    sorter_loader.report_progress(60, 'Database initalised.')

    # Initialise operations
    sorter_loader.report_progress(70, 'Loading operations...')
    operations = SorterOps(db_helper)
    sorter_loader.report_progress(
        90, 'Operations initialised. Database helper configured.')

    # Close loader
    sorter_loader.report_progress(100, 'Initialising UI.')
    sorter_loader.tk_run()

    # Initialise GUI
    app = TkGui(operations=operations, logger=logging)

    # Show window
    app.tk_run()
