#! /usr/bin/env python3

import os
import django
import logging
from gui.tkgui import TkGui
from operations import SorterOps
from helpers import DatabaseHelper

# Django configuration
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

from django.conf import settings

DB_NAME = settings.DATABASES['default']['NAME']
LOG_FILE = settings.LOG_FILE


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
