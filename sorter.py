#! /usr/bin/env python3

import os
import django
from gui.tkgui import TkGui
from operations import SorterOps

# Django configuration
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

from django.conf import settings

DB_NAME = settings.DATABASES['default']['NAME']


if __name__ == '__main__':
	operations = SorterOps(DB_NAME)

	# Create database and tables
	initialised = operations.initialise_db()
	app = TkGui(operations=operations)

	# Show window
	app.tk_run()
