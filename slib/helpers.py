#! /usr/bin/env python3.4

import os
import logging
import sqlite3
from datetime import datetime

logger = logging.getLogger(__name__)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "data.settings")


from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

from data.models import File as DB_FILE, Path as DB_PATH
from django.db.utils import OperationalError as DjangoOperationalError


class InterfaceHelper(object):
    """Handles the messaging to the user.

    data attributes maps:
        progress_bar - ttk.Progressbar instance
        progress_var - IntVar() for progress_bar
        update_idletasks - tkinter.update_idletasks
        status_config - ttk.Label.config
        messagebox - tkinter.messagebox
        progress_text - tkinter.text_widget
        progress_info - StringVar() for progress logs

    methods:
        message_user
    """

    def __init__(self, progress_bar, progress_var, status, messagebox, progress_info):
        progress_bar.configure(maximum=100)
        self.progress_bar = progress_bar
        self.progress_var = progress_var
        self.status = status
        self.messagebox = messagebox
        self.progress_info = progress_info

    def message_user(self, through=None, msg='Ready', weight=0, value=100):
        """Show a message to the user.

        Through:
            status - status bar
            progress_bar - progress bar
            dialog - messagebox
            progress_text - progress info text box
        """
        through = through or ['status']

        if 'status' in through:
            self._use_status(msg, weight)
        if 'progress_bar' in through:
            self._use_progress_bar(weight, value)
        if 'dialog' in through:
            self._use_messagebox(msg, weight)
        if 'progress_text' in through:
            self._update_progress_window(str(msg))

    def _update_progress_window(self, msg):
        prev_text = self.progress_info.get()
        _text = '{}{}  {}\n'.format(prev_text, str(datetime.now()), msg)
        logger.debug(_text)
        self.progress_info.set(_text)

    def _use_status(self, msg, weight):
        _msg = str(msg)[:50]
        if weight == 0:
            self.status.config(foreground='black', text=' {}'.format(_msg))
        if weight == 1:
            self.status.config(foreground='blue', text=' {}'.format(_msg))
        if weight == 2:
            self.status.config(foreground='red',
                               text=' {}'.format(_msg))
        self.status.update()
        self._update_progress_window(str(msg))

    def _use_progress_bar(self, weight, value):
        color = 'blue'
        if weight == 1:
            color = 'green'
        self.progress_var.set(value)
        self.progress_bar.configure(
            style="{}.Horizontal.TProgressbar".format(color))
        self.progress_bar.update()

    def _use_messagebox(self, msg, weight):
        if weight == 2:
            self.messagebox.showwarning(title='Warning', message=msg)
        else:
            self.messagebox.showinfo(title='Info', message=msg)


class DatabaseHelper(object):
    """A helper class that interacts with the database.

    data attributes:
        DB_NAME - the path to the database
        db_path_objects - DB_PATH.objects
        db_file_objects - DB_FILE.objects
        db_ready - True if database table have been created

    methods:
        initialise_db
        get_start_value
        get_report
        update
        alter_value
        get_history
    """

    def __init__(self, db_name):
        self.DB_NAME = db_name
        self.db_file_objects = DB_FILE.objects
        self.db_path_objects = DB_PATH.objects
        self.db_ready = False

    def initialise_db(self, test=False):
        """Initialise database, set self.db_ready to True.

        If test is True (for tests), drop tables first.
        """
        if not self.db_ready:
            connection = sqlite3.connect(self.DB_NAME)
            cursor = connection.cursor()

            if test:
                query1 = 'DROP TABLE IF EXISTS data_file'
                query2 = 'DROP TABLE IF EXISTS data_path'
                query3 = 'DROP TABLE IF EXISTS data_path_filename_id_1d40e5f2'
                cursor.execute(query1)
                cursor.execute(query2)
                cursor.execute(query3)
                connection.commit()
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
        """Return the index of the last database entry in the
        db_file_objects table.

        Return 0 if table has no entry.
        """
        try:
            start_value = self.db_file_objects.last().id
        except (AttributeError, DjangoOperationalError):
            start_value = 0
        return start_value

    def get_report(self, start_value):
        """Return the objects created by the current operations."""
        paths = self.db_path_objects.filter(
            id__gte=start_value).order_by('-pk')

        report = []
        for path in paths:
            row_tup = (path.filename.filename, path.source,
                       path.destination, path.added_at)
            report.append(row_tup)
        return report

    def update(self, database_dict):
        """Insert values of the current operations into the database."""
        now = datetime.now()
        file_list = []
        for filename in database_dict.keys():
            filename_dict = database_dict[filename]
            this_filename = DB_FILE(added_at=now, **filename_dict['file'])
            file_list.append(this_filename)
        self.db_file_objects.bulk_create(file_list)

        file_objects = DB_FILE.objects.filter(added_at=now)
        path_list = []
        for file_ in file_objects:
            this_file = DB_PATH(
                filename=file_, added_at=now, **database_dict[file_.filename]['path'])
            path_list.append(this_file)
        self.db_path_objects.bulk_create(path_list)

    def alter_path(self, alter_value, finders):
        """Alter the value of db_file_objects instance in the database.

        finders - the key,value pairs to use to search for the entry in the
            table
        alter_value - the key,value pair of the value to alter in the database
            table
        """
        self.db_path_objects.filter(**finders).update(**alter_value)

    def get_history(self, count):
        """Return the number of db_file_objects instances as specified by count."""
        try:
            files = self.db_file_objects.all().order_by(
                '-pk').select_related().filter(filename_path__accepted=True)[:count]
        except (DjangoOperationalError, sqlite3.OperationalError):
            files = ''
        return files
