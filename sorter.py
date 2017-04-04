#! /usr/bin/python3
# sorter.py - A Python script which checks file types in a folder and
# sorts them into folders named by type

import os
import ntpath
import shutil
import argparse
import sys
from filegroups import fileGroups


def move_file(source_path, extension_dir, filename):
    source_file = os.path.join(source_path, filename)
    destination_file = os.path.join(
        os.path.join(source_path, extension_dir), filename)

    if os.path.isdir(os.path.join(source_path, extension_dir)):
        shutil.move(source_file, destination_file)
    else:
        os.makedirs(os.path.join(source_path, extension_dir))
        move_file(source_path, extension_dir, _file)


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


def get_extension_path(destination_path, extension):
    if destination_path:
        extension_dir = os.path.join(destination_path, extension.upper())
    else:
        extension_dir = extension.upper()

    return extension_dir


def sort_folders(path, found_extensions):
    for key in fileGroups.keys():
        ans = set(found_extensions) & set(fileGroups[key])
        if ans:
            new_ans = list(ans)
            key_folder = os.path.join(path, key)
            if not os.path.isdir(key_folder):
                os.makedirs(key_folder)
            if is_writable(key_folder):
                for item in new_ans:
                    shutil.move(os.path.join(path, item), key_folder)


parser = argparse.ArgumentParser()
parser.add_argument('--source', help='Source directory', nargs=1)
parser.add_argument('-d', '--destination',
                    help='Destination directory. Full path required.', nargs=1)
parser.add_argument(
    '--sort-folders', help='Sort folders into categories', action='store_true')
options = vars(parser.parse_args())

found_extensions = []
proceed = True
if options['source']:
    source_path = options['source'][0]
else:
    source_path = os.getcwd()

if options['destination']:
    destination_path = options['destination'][0]
else:
    destination_path = ''

if not os.path.isdir(source_path):
    proceed = False
    print('Given source folder is NOT a folder.')
else:
    if not is_writable(source_path):
        proceed = False

if destination_path:
    if not os.path.isdir(destination_path):
        proceed = False
        print('Given destination folder is NOT a folder.')
    else:
        if not is_writable(destination_path):
            proceed = False


if proceed:
    files = [_file for _file in os.listdir(
        source_path) if os.path.isfile(os.path.join(source_path, _file))]

    if files:
        for _file in files:
            extension = os.path.splitext(_file)[1][1:].upper()

            if extension:
                if extension not in found_extensions:
                    found_extensions.append(extension)

                extension_dir = get_extension_path(destination_path, extension)
                # print(extension_dir)

                move_file(source_path, extension_dir, _file)

            else:
                extension_dir = get_extension_path(
                    destination_path, 'UNDEFINED')
                move_file(source_path, extension_dir, _file)
        if options['sort_folders']:
            sort_folders(source_path, found_extensions)
    else:
        print('No files found.')

else:
    parser.print_help()
