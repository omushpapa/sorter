#! /usr/bin/env python3

import argparse
import os
import sqlite3
import hashlib
from glob import glob, iglob
from sdir import File, Folder, CustomFolder, CustomFile, has_signore_file
from filegroups import typeGroups

# Database variables
DB_NAME = 'operations.db'

# Configure files table
FILES_TABLE = 'file'
FILE_ID_FIELD_NAME = 'file_id'
FILE_ID_FIELD_CONF = 'INTEGER PRIMARY KEY'
FILE_ID_FIELD = FILE_ID_FIELD_NAME + ' ' + FILE_ID_FIELD_CONF
FILENAME_FIELD_NAME = 'filename'
FILENAME_FIELD_CONF = 'TEXT NOT NULL'
FILENAME_FIELD = FILENAME_FIELD_NAME + ' ' + FILENAME_FIELD_CONF
FILEPATH_HASH_FIELD_NAME = 'path_hash'
FILEPATH_HASH_FIELD_CONF = FILENAME_FIELD_CONF
FILEPATH_HASH_FIELD = FILEPATH_HASH_FIELD_NAME + ' ' + FILEPATH_HASH_FIELD_CONF
FILE_LAST_MODIFIED_FIELD_NAME = 'last_modified'
FILE_LAST_MODIFIED_FIELD_CONF = 'REAL NOT NULL'
FILE_LAST_MODIFIED_FIELD = FILE_LAST_MODIFIED_FIELD_NAME + \
    ' ' + FILE_LAST_MODIFIED_FIELD_CONF

# Configure paths table
PATHS_TABLE = 'path'
PATH_ID_FIELD_NAME = 'path_id'
PATH_ID_FIELD_CONF = 'INTEGER PRIMARY KEY'
PATH_ID_FIELD = PATH_ID_FIELD_NAME + ' ' + PATH_ID_FIELD_CONF
#FILE_ID_FIELD_NAME = FILE_ID_FIELD_NAME
SRC_FIELD_NAME = 'src_path'
SRC_FIELD_CONF = 'TEXT NOT NULL'
SRC_FIELD = SRC_FIELD_NAME + ' ' + SRC_FIELD_CONF
DST_FIELD_NAME = 'dst_path'
DST_FIELD_CONF = 'TEXT NOT NULL'
DST_FIELD = DST_FIELD_NAME + ' ' + DST_FIELD_CONF
IS_OKAY_FIELD_NAME = 'is_okay'
IS_OKAY_FIELD_CONF = 'INTEGER DEFAULT 1'
IS_OKAY_FIELD = IS_OKAY_FIELD_NAME + ' ' + IS_OKAY_FIELD_CONF
TIMESTAMP_FIELD_NAME = 'time'
TIMESTAMP_FIELD_CONF = 'DATE DEFAULT (datetime(\'now\',\'localtime\')),'
TIMESTAMP_FIELD = TIMESTAMP_FIELD_NAME + ' ' + TIMESTAMP_FIELD_CONF


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


def initialise_db(db_cursor, db_connect):
    """Create tables if they do not exist."""
    # Create table
    query = 'CREATE TABLE IF NOT EXISTS {0} ({1}, {2}, {3}, {4})'.format(
        FILES_TABLE, FILE_ID_FIELD, FILENAME_FIELD,
        FILEPATH_HASH_FIELD, FILE_LAST_MODIFIED_FIELD)
    db_cursor.execute(query)
    query = 'CREATE TABLE IF NOT EXISTS {tn} ({pif}, {fif}, {sf}, {df}, {ok}, {tf} {fk})'.format(
        tn=PATHS_TABLE,
        pif=PATH_ID_FIELD,
        fif=(FILE_ID_FIELD_NAME + ' INTEGER '),
        sf=SRC_FIELD,
        df=DST_FIELD,
        ok=IS_OKAY_FIELD,
        tf=TIMESTAMP_FIELD,
        fk=('FOREIGN KEY(' + FILE_ID_FIELD_NAME + ') REFERENCES ' +
            FILES_TABLE + '(%s)' % FILE_ID_FIELD_NAME))
    db_cursor.execute(query)
    db_connect.commit()

    # Get last row
    query = 'SELECT MAX({0}) FROM {1}'.format(FILE_ID_FIELD_NAME, FILES_TABLE)
    result = db_cursor.execute(str(query))
    return result.fetchone()[0]


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


def sort_files(source_path, destination_path, search_string, string_pattern, file_types, glob_pattern, sort_folders, db_cursor):
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
    db_cursor - the cursor to use in loggin operations to the database.
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
                quote = lambda x: '"' + str(x) + '"'
                hash_path = hashlib.md5(
                    initial_path.encode('utf-8')).hexdigest()
                query = 'INSERT INTO {tn} ({fn}, {fp}, {lm}) VALUES ({fnv}, {fpv}, {lmv}) '.format(
                    tn=FILES_TABLE,
                    fn=FILENAME_FIELD_NAME,
                    fp=FILEPATH_HASH_FIELD_NAME,
                    lm=FILE_LAST_MODIFIED_FIELD_NAME,
                    fnv=quote(initial_name),
                    fpv=quote(hash_path),
                    lmv=quote(last_modified))
                db_cursor.execute(query)

                num = db_cursor.lastrowid
                query = 'INSERT INTO {tn} ({fif}, {sfn}, {dfn}, {tfn}) VALUES ({fifv}, {sfnv}, {dfnv}, {tfnv})'.format(
                    tn=PATHS_TABLE,
                    fif=FILE_ID_FIELD_NAME,
                    sfn=SRC_FIELD_NAME,
                    dfn=DST_FIELD_NAME,
                    tfn=TIMESTAMP_FIELD_NAME,
                    fifv=quote(num),
                    sfnv=quote(initial_path),
                    dfnv=quote(new_path),
                    tfnv='DATETIME("NOW")')
                db_cursor.execute(query)


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
    else:
        status.config(foreground="black")
    status.config(text=text)


def initiate_operation(src='', dst='', search_string='', sort=False, recur=False, types=None, status=None, parser=None):
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
        display_message('START', status=status)
        CONN = sqlite3.connect(DB_NAME)
        CONN.row_factory = sqlite3.Row
        CURSOR = CONN.cursor()

        start_value = initialise_db(db_cursor=CURSOR, db_connect=CONN)

        if recur:
            for root, dirs, files in os.walk(source_path):
                sort_files(root, destination_path, search_string, search_string_pattern,
                           file_types, glob_pattern, sort, db_cursor=CURSOR)
                if not dirs and not files:
                    try:
                        os.rmdir(root)
                    except PermissionError as e:
                        display_message('Could not move "{0}": {1}'.format(
                            root, e), status=status, mtype='warning')

        else:
            sort_files(source_path, destination_path, search_string, search_string_pattern,
                       file_types, glob_pattern, sort, db_cursor=CURSOR)

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

        # Generate report
        if start_value is None:
            start_value = 0
        query = 'SELECT {ftn}.{ffn},{ptn}.{pap},{ptn}.{sfn} FROM {ftn} INNER JOIN {ptn} ON {ftn}.{ffi} = {ptn}.{ffi} WHERE {ftn}.{ffi} > {sv}'.format(
            ftn=FILES_TABLE,
            ffn=FILENAME_FIELD_NAME,
            ptn=PATHS_TABLE,
            sfn=SRC_FIELD_NAME,
            pap=DST_FIELD_NAME,
            ffi=FILE_ID_FIELD_NAME,
            sv=str(start_value))
        result = CURSOR.execute(query)
        rows = result.fetchall()
        report = []
        for row in rows:
            row_tup = (row['filename'], row['src_path'],
                       row['dst_path'], 'Moved')
            report.append(row_tup)

        CONN.commit()
        CONN.close()
        display_message('FINISH', status=status)
        return report

    if status is None and not proceed:
        parser.print_help()
