#! /usr/bin/env python3.4

import os
import sqlite3
from datetime import datetime

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "data.settings")


from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

from data.models import File as DB_FILE, Path as DB_PATH
from django.db.utils import OperationalError


class InterfaceHelper(object):
    """Handles the messaging to the user."""

    def __init__(self, progress_bar, progress_var, update_idletasks, status_config):
        progress_bar.configure(maximum=100)
        self.progress_bar = progress_bar
        self.progress_var = progress_var
        self.update_idletasks = update_idletasks
        self.status_config = status_config

    def message_user(self, through='status', msg='Ready', weight=0, value=0):
        """Show a message to the user."""
        if through == 'status':
            self._use_status(msg, weight)
        if through == 'progress_bar':
            self._use_progress_bar(weight, value)
        if through == 'both':
            self._use_status(msg, weight)
            self._use_progress_bar(weight, value)

    def _use_status(self, msg, weight):
        if weight == 0:
            self.status_config(foreground='black', text=' {}'.format(str(msg)))
        if weight == 1:
            self.status_config(foreground='blue', text=' {}'.format(str(msg)))
        if weight == 2:
            self.status_config(foreground='red',
                               text=' {}'.format(str(msg)))

    def _use_progress_bar(self, weight, value):
        color = 'blue'
        if weight == 1:
            color = 'green'
        self.progress_var.set(value)
        self.progress_bar.configure(
            style="{}.Horizontal.TProgressbar".format(color))
        self.update_idletasks()


class DatabaseHelper(object):

    def __init__(self, db_name):
        self.DB_NAME = db_name
        self.db_file_objects = DB_FILE.objects
        self.db_path_objects = DB_PATH.objects
        self.db_ready = False

    def initialise_db(self):
        """Initialise database, set self.db_ready to True."""
        if not self.db_ready:
            connection = sqlite3.connect(self.DB_NAME)
            cursor = connection.cursor()
            # Create tables
            # Do not alter the queries, may not work with subsequent database
            # operations
            query1 = """CREATE TABLE IF NOT EXISTS "data_file" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "filename" text NOT NULL, "filepath_hash" text NOT NULL, "last_modified" datetime NOT NULL, "added_at" datetime NOT NULL);"""
            query2 = """CREATE TABLE IF NOT EXISTS "data_path" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "source" text NOT NULL, "destination" text NOT NULL, "accepted" bool NOT NULL, "added_at" datetime NOT NULL, "filename_id" integer NOT NULL REFERENCES "data_file" ("id"));"""
            query3 = """CREATE INDEX IF NOT EXISTS "data_path_filename_id_1d40e5f2" ON "data_path" ("filename_id");"""
            cursor.execute(query1)
            cursor.execute(query2)
            cursor.execute(query3)
            connection.commit()
            connection.close()
            self.db_ready = True

        return self.db_ready

    def get_start_value(self):
        try:
            start_value = self.db_file_objects.last().id
        except AttributeError:
            start_value = 0
        finally:
            return start_value

    def get_report(self, start_value):
        paths = self.db_path_objects.filter(
            id__gte=start_value).order_by('-pk')

        report = []
        for path in paths:
            row_tup = (path.filename.filename, path.source,
                       path.destination, path.added_at)
            report.append(row_tup)
        return report

    def update(self, database_dict):
        now = datetime.now()
        item_count = len(database_dict)

        run_list = []
        for filename in database_dict.keys():
            filename_dict = database_dict[filename]
            this_file = DB_FILE(added_at=now, **filename_dict['file'])
            run_list.append(this_file)
        self.db_file_objects.bulk_create(run_list)

        file_objects = self.db_file_objects.filter(added_at=now)

        for file_ in file_objects:
            this_path = self.db_path_objects.create(
                filename=file_, added_at=now, **database_dict[file_.filename]['path'])

    def alter_path(self, alter_value, finders):
        updated = self.db_path_objects.filter(**finders).update(**alter_value)

    def get_history(self, count):
        files = self.db_file_objects.all().order_by(
            '-pk').select_related().filter(filename_path__accepted=True)[:count]

        try:
            length = len(files)
        except OperationalError:
            pass
        finally:
            return files