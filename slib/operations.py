#! /usr/bin/env python3

import os
import sqlite3
import hashlib
import django
from glob import iglob
from slib.sdir import File, Folder, CustomFolder, CustomFile, has_signore_file
from slib.helpers import DatabaseHelper
from data.filegroups import typeGroups
from datetime import datetime


class SorterOps(object):

    def __init__(self, db_helper):
        self.db_helper = db_helper
        self._set_defaults()

    def _set_defaults(self):
        self.src = ''
        self.dst = ''
        self.search_string = ''
        self.search_string_pattern = ''
        self.glob_pattern = ''
        self.sort_folders = False
        self.recursive = False
        self.file_types = ['*']
        self.status = None
        self.parser = None
        self.database_dict = {}

    @classmethod
    def is_writable(cls, folder_path):
        """Return True if user has write permission on given path, else False."""
        try:
            permissions_dir = os.path.join(folder_path, 'sorter_dir')
            os.makedirs(permissions_dir)
            os.rmdir(permissions_dir)
        except PermissionError:
            return False
        else:
            return True

    @classmethod
    def insensitize(cls, string):
        """Return a case-insensitive pattern of the provided string."""
        def either(c):
            return '[{0}{1}]'.format(c.lower(), c.upper()) if c.isalpha() else c
        return ''.join(map(either, string))

    def form_search_pattern(self, search_string):
        """Return a search pattern if search_string is provided."""
        self.search_string = search_string
        if search_string:
            insensitive_string = self.insensitize(search_string)
            search_string_pattern = '?'.join(insensitive_string.split())
        else:
            search_string_pattern = search_string
        return search_string_pattern

    def sort_files(self, source_path=None, sort_folders=False):
        """Move files in relation to their extensions and categories.

        source_path - path of origin
        sort_folders - boolean value determining whether to also group folders 
            according to their categories - as defined in filegroups.py.
        """
        source_path = source_path or self.src
        destination_path = self.dst
        search_string = self.search_string
        string_pattern = self.search_string_pattern
        file_types = self.file_types
        glob_pattern = self.glob_pattern

        glob_files = []
        if search_string:
            string_pattern = '*' + string_pattern

        string_glob_pattern = string_pattern + glob_pattern

        for item in file_types:
            full_pattern = string_glob_pattern + item
            for i in iglob(os.path.join(source_path, full_pattern)):
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

                    file_dict = {'filename': initial_name, 'filepath_hash': hash_path,
                                 'last_modified': datetime.fromtimestamp(last_modified)}
                    path_dict = {'source': initial_path,
                                 'destination': new_path}

                    this_file_dict = {initial_name: {
                        'file': file_dict, 'path': path_dict}}

                    self.database_dict.update(this_file_dict)

    def _verify_path(self, path, path_name=''):
        if not os.path.isdir(path) or not os.path.isabs(path):
            msg = 'Given {} folder is NOT a folder'.format(path_name)
            return False, msg
        elif not self.is_writable(path):
            msg = '"{0}" is not writable. Check folder and try again.'.format(
                path)
            return False, msg
        else:
            return True, ''

    def _check_source_path(self, src):
        self.src = src
        if not src:
            msg = 'Source folder is NOT optional (required)'
            return False, msg
        else:
            return self._verify_path(src, 'Source')

    def _check_dst_path(self, dst=''):
        if dst:
            self.dst = os.path.abspath(dst)
        else:
            self.dst = self.src
        return self._verify_path(self.dst, 'Destination')

    def _get_glob_pattern(self, types_given):
        if types_given:
            self.glob_pattern = '*.'
        else:
            self.glob_pattern = ''
        return self.glob_pattern

    def _recursive_operation(self, sort_folders=False):
        source_path = self.src

        for root, dirs, files in os.walk(source_path):
            self.sort_files(root, sort_folders=sort_folders)
            if not dirs and not files:
                try:
                    os.rmdir(root)
                except PermissionError as e:
                    display_message('Could not move "{0}": {1}'.format(
                        root, e), status=status, mtype='warning')

    def _sort_folders_operation(self):
        source_path = self.src
        search_string_pattern = self.search_string_pattern
        search_string = self.search_string
        folder_list_matching_pattern = iglob(os.path.join(
            source_path, '*' + search_string_pattern + '*'))
        folders = [folder for folder in folder_list_matching_pattern if os.path.isdir(
            folder) and os.path.basename(folder) not in typeGroups.keys() and not has_signore_file(folder)]

        if folders:
            for folder in folders:
                folder_path = os.path.join(source_path, folder)
                if search_string:
                    folder_instance = CustomFolder(
                        folder_path, search_string)
                else:
                    folder_instance = Folder(folder_path)
                folder_instance.group(source_path)

    def initiate_operation(self, src, dst, send_message, **kwargs):
        """Initiate Sorter operations.

        Execution starts from here once the Run button is clicked.

        src/source_path - path of origin
        dst/destination_path - destined root path
        send_message - method for returning information to the user e.g. through the
            status bar or progress bar.
        kwargs['search_string'] - only include file names with this value. Defaults to ''.
        kwargs['file_types'] - the file extensions or formats to include in the sorting.
            Defaults to ['*'].
        kwargs['types_given'] - boolean value determined to specify whether file_types
            parameter was provided or default was used. Defaults to False.
        kwargs['glob_pattern'] - the pattern to utilise to include (or exclude) certain file
            extensions. Default value is determined by the value of kwargs['types_given'].
        kwargs['sort_folders'] - boolean value determining whether to also group folders 
            according to their categories - as defined in filegroups.py. Defaults to False.
        kwargs['recursive'] - check into folders and their subfolders.
        """
        proceed, msg = self._check_source_path(src)

        if not proceed:
            send_message(msg=msg, weight=2)
        else:
            proceed, msg = self._check_dst_path(dst)

            if not proceed:
                send_message(msg=msg, weight=2)
            else:
                self.search_string_pattern = self.form_search_pattern(
                    kwargs.get('search_string', ''))
                self.file_types = kwargs.get('file_types', ['*'])
                self.glob_pattern = self._get_glob_pattern(
                    kwargs.get('types_given', False))
                self.recursive = kwargs.get('recursive', False)
                self.sort_folders = kwargs.get('sort_folders', False)

                send_message(through='both', msg='10% - running...', value=10)

                # Get last row in database
                start_value = self.db_helper.get_start_value()

                send_message(through='both', msg='25% - running...', value=25)

                if self.recursive:
                    self._recursive_operation(self.sort_folders)
                else:
                    self.sort_files(sort_folders=self.sort_folders)

                send_message(through='both', msg='40% - running...', value=50)

                # Call database helper
                self.db_helper.update(self.database_dict)

                send_message(through='both', msg='60% - running...', value=50)

                if self.sort_folders:
                    self._sort_folders_operation()

                send_message(through='both', msg='75% - running...', value=75)

                report = self.db_helper.get_report(start_value)

                send_message(through='both', msg='Done', weight=1, value=100)

                self._set_defaults()

                return report
