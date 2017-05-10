#! /usr/bin/env python3

import argparse
import os
from glob import glob, iglob
from sdir import File, Folder, CustomFolder, CustomFile, has_signore_file
from filegroups import typeGroups


def is_writable(folder_path):
    try:
        permissions_dir = os.path.join(folder_path, 'sorter_dir')
        os.makedirs(permissions_dir)
        os.rmdir(permissions_dir)
    except PermissionError:
        print(
            'Could not write to the folder "%s". Check folder and try again.' % folder_path)
        return False
    return True


def sort_files(source_path, destination_path, search_string, string_pattern, file_types, glob_pattern, sort_folders):
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
                file_instance.move_to(
                    destination_path, sort_folders)
            else:
                file_instance = File(os.path.join(source_path, file_))
                file_instance.move_to(
                    destination_path, sort_folders)


def insensitize(string):
    def either(c):
        return '[{0}{1}]'.format(c.lower(), c.upper()) if c.isalpha() else c
    return ''.join(map(either, string))


def form_search_pattern(search_string):
    if search_string:
        insensitive_string = insensitize(search_string)
        return '?'.join(insensitive_string.split())
    else:
        return search_string


def display_message(text, status, gui):
    if gui is None:
        print(text)
    else:
        text = text.replace('\n', '')
        if gui == 'qt':
            status.showMessage(text)
        if gui == 'tkinter':
            status.config(text=text)


def initiate_operation(src='', dst='', search_string='', sort=False, recur=False, types=None, status=None, parser=None, gui=None):
    proceed = True
    search_string_pattern = form_search_pattern(search_string)

    if src:
        source_path = os.path.abspath(src)
    else:
        proceed = False
        display_message('Source folder is required.', status=status, gui=gui)

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
                'Given source folder is NOT a folder.', status=status, gui=gui)
        else:
            if not is_writable(source_path):
                proceed = False

    if proceed:
        if destination_path:
            if not os.path.isdir(destination_path):
                proceed = False
                display_message(
                    'Given destination folder is NOT a folder.', status=status, gui=gui)
            else:
                if not is_writable(destination_path):
                    proceed = False

    if proceed:
        display_message('\n{:-^80}\n'.format('START'), status=status, gui=gui)

        if recur:
            for root, dirs, files in os.walk(source_path):
                sort_files(root, destination_path, search_string, search_string_pattern,
                           file_types, glob_pattern, sort)
                if not dirs and not files:
                    try:
                        os.rmdir(root)
                    except PermissionError as e:
                        display_message('Could not move "{0}": {1}'.format(
                            root, e), status=status, gui=gui)

        else:
            sort_files(source_path, destination_path, search_string, search_string_pattern,
                       file_types, glob_pattern, sort)

        if sort:
            folders = [folder for folder in glob(os.path.join(
                source_path, '*')) if os.path.isdir(folder) and os.path.basename(folder) not in typeGroups.keys() and not has_signore_file(folder)]

            if folders:
                for folder in folders:
                    folder_path = os.path.join(source_path, folder)
                    if list(iglob(os.path.join(source_path, '*' + search_string_pattern + '*'))):
                        folder_instance = CustomFolder(
                            folder_path, search_string)
                        folder_instance.group(source_path)
                    else:
                        folder_instance = Folder(folder_path)
                        folder_instance.group(source_path)

        display_message('Done.', status=status, gui=gui)
        display_message('\n{:-^80}\n'.format('FINISH'), status=status, gui=gui)

    if gui is None and not proceed:
        parser.print_help()
