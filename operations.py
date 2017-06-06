#! /usr/bin/env python3

import os
import sqlite3
import hashlib
import django
from glob import glob, iglob
from sdir import File, Folder, CustomFolder, CustomFile, has_signore_file
from filegroups import typeGroups
from datetime import datetime

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")


from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()


from django.conf import settings
from data.models import File as DB_FILE, Path as DB_PATH


DB_NAME = settings.DATABASES['default']['NAME']


def initialise_db(db_name=DB_NAME):
    """Create database tables if they do not exist."""
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()
    # Create tables
    # Do not alter the queries, may not work with subsequent database
    # operations
    query1 = """CREATE TABLE IF NOT EXISTS "data_file" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "filename" text NOT NULL, "filepath_hash" text NOT NULL, "last_modified" datetime NOT NULL);"""
    query2 = """CREATE TABLE IF NOT EXISTS "data_path" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "source" text NOT NULL, "destination" text NOT NULL, "accepted" bool NOT NULL, "timestamp" datetime NOT NULL, "filename_id" integer NOT NULL REFERENCES "data_file" ("id"));"""
    query3 = """CREATE INDEX IF NOT EXISTS "data_path_filename_id_1d40e5f2" ON "data_path" ("filename_id");"""
    cursor.execute(query1)
    cursor.execute(query2)
    cursor.execute(query3)
    connection.commit()
    connection.close()


def recreate_path(full_path):
    """Create folders (and parents) in the path if they do not exist."""
    paths = []

    def get_paths(full_path):
        dir_path = os.path.dirname(full_path)
        if dir_path != full_path:
            paths.append(dir_path)
            get_paths(dir_path)
    get_paths(full_path)
    for path in paths[::-1]:
        if not os.path.isdir(path):
            os.mkdir(path)


def is_writable(folder_path, status, mtype):
    """Return True if user has write permission on given path, else False."""
    try:
        permissions_dir = os.path.join(folder_path, 'sorter_dir')
        os.makedirs(permissions_dir)
        os.rmdir(permissions_dir)
    except PermissionError:
        display_message(
            '"{0}" is not writable. Check folder and try again.'.format(
                os.path.basename(folder_path)),
            status=status, mtype=mtype)
        return False
    return True


def sort_files(source_path, destination_path, search_string, string_pattern, file_types, glob_pattern, sort_folders):
    """Move file in relation to its extension and category.

    source_path - path of origin
    destination_path - destined root path
    search_string - only include file names with this value. Defaults to ''.
    string_pattern -  the compiled pattern to utilise in searching using 
        the search_string value.
    file_types - the file extensions or formats to include in the sorting.
    glob_pattern - the pattern to utilise to include (or exclude) certain file
        extensions.
    sort_folders - boolean value determining whether to also group folders 
        according to their categories - as defined in filegroups.py.
    """
    glob_files = []
    if search_string:
        string_pattern = '*' + string_pattern
    for item in file_types:
        for i in glob(os.path.join(source_path, string_pattern + glob_pattern + item)):
            if os.path.isfile(i):
                glob_files.append(i)

    if glob_files:
        for file_ in glob_files:
            if search_string:
                file_instance = CustomFile(os.path.join(
                    source_path, file_), search_string)
            else:
                file_instance = File(os.path.join(source_path, file_))
            initial_path = file_instance.path
            initial_name = file_instance.name
            last_modified = os.path.getmtime(initial_path)
            file_instance.move_to(destination_path, sort_folders)
            new_path = file_instance.path
            if initial_path != new_path:
                # Write to DB
                hash_path = hashlib.md5(
                    initial_path.encode('utf-8')).hexdigest()

                f = DB_FILE.objects.create(
                    filename=initial_name, filepath_hash=hash_path, last_modified=datetime.fromtimestamp(last_modified))
                f.save()

                path = DB_PATH.objects.create(filename=f, source=initial_path,
                                              destination=new_path, timestamp=datetime.now())
                path.save()


def insensitize(string):
    """Return a case-insensitive pattern of the provided string."""
    def either(c):
        return '[{0}{1}]'.format(c.lower(), c.upper()) if c.isalpha() else c
    return ''.join(map(either, string))


def form_search_pattern(search_string):
    """Return a search pattern if search_string is provided."""
    if search_string:
        insensitive_string = insensitize(search_string)
        return '?'.join(insensitive_string.split())
    else:
        return search_string


def display_message(text, status, mtype='info'):
    """Configure the GUI status bar message."""
    if mtype == 'warning':
        status.config(foreground="red")
    elif mtype == 'update':
        status.config(foreground="blue")
    else:
        status.config(foreground="black")
    status.config(text=' %s' % text)


def update_progress(instance, value, status, mtype='update', colour=None):
    instance.progress_var.set(value)
    if colour is not None:
        instance.progress_bar.configure(
            style="{}.Horizontal.TProgressbar".format(colour))
    display_message('{}%'.format(value), status=status, mtype=mtype)
    instance.update_idletasks()


def initiate_operation(src='', dst='', search_string='', sort=False, recur=False, types=None, status=None, parser=None, instance=None):
    proceed = True
    search_string_pattern = form_search_pattern(search_string)

    if src:
        source_path = os.path.abspath(src)
    else:
        proceed = False
        display_message('Source folder is REQUIRED.',
                        status=status, mtype='warning')

    if proceed:
        if dst:
            destination_path = os.path.abspath(dst)
        else:
            destination_path = source_path

    if proceed:
        if types is not None:
            file_types = types or ['*']  # types should be list
            glob_pattern = '*.'
        else:
            file_types = ['*']
            glob_pattern = ''

    if proceed:
        if not os.path.isdir(source_path):
            proceed = False
            display_message(
                'Given Source folder is NOT a folder.', status=status, mtype='warning')
        else:
            if not is_writable(source_path, status=status, mtype='warning'):
                proceed = False

    if proceed:
        if destination_path:
            if not os.path.isdir(destination_path):
                proceed = False
                display_message(
                    'Given Destination folder is NOT a folder.', status=status, mtype='warning')
            else:
                if not is_writable(destination_path, status=status, mtype='warning'):
                    proceed = False

    if proceed:
        if instance is not None:
            instance.progress_bar.configure(maximum=100)

        display_message('START', status=status)
        initialise_db()

        if instance is not None:
            update_progress(instance=instance, value=10, colour='blue',
                            status=status)

        # Get last row in database
        try:
            start_value = DB_FILE.objects.last().id
        except AttributeError:
            start_value = 0

        if instance is not None:
            update_progress(instance=instance, value=25, status=status)

        if recur:
            for root, dirs, files in os.walk(source_path):
                sort_files(root, destination_path, search_string, search_string_pattern,
                           file_types, glob_pattern, sort)
                if not dirs and not files:
                    try:
                        os.rmdir(root)
                    except PermissionError as e:
                        display_message('Could not move "{0}": {1}'.format(
                            root, e), status=status, mtype='warning')

        else:
            sort_files(source_path, destination_path, search_string, search_string_pattern,
                       file_types, glob_pattern, sort)

        if instance is not None:
            update_progress(instance=instance, value=50, status=status)

        if sort:
            folders = [folder for folder in glob(os.path.join(
                source_path, '*')) if os.path.isdir(folder) and os.path.basename(folder) not in typeGroups.keys() and not has_signore_file(folder)]

            if folders:
                for folder in folders:
                    folder_path = os.path.join(source_path, folder)
                    if list(iglob(os.path.join(source_path, '*' + search_string_pattern + '*'))):
                        folder_instance = CustomFolder(
                            folder_path, search_string)
                    else:
                        folder_instance = Folder(folder_path)
                    folder_instance.group(source_path)

        display_message('Done.', status=status)

        if instance is not None:
            update_progress(instance=instance, value=75, status=status)

        paths = DB_PATH.objects.filter(id__gt=start_value)

        report = []
        for path in paths:
            row_tup = (path.filename.filename, path.source,
                       path.destination, 'Moved')
            report.append(row_tup)

        if instance is not None:
            update_progress(instance=instance, value=100, colour='green',
                            status=status)

        display_message('FINISH', status=status)

        return report

    if status is None and not proceed:
        parser.print_help()
