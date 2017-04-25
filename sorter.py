#! /usr/bin/env python3

import argparse
import os
from glob import glob
from sdir import File, Folder
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


def sort_files(source_path, destination_path, file_types, glob_pattern):
    glob_files = []
    for item in file_types:
        for i in glob(os.path.join(source_path, glob_pattern + item)):
            if os.path.isfile(i):
                glob_files.append(i)

    if glob_files:
        for file_ in glob_files:
            file_instance = File(os.path.join(source_path, file_))
            file_instance.move_to(
                destination_path, options['sort_folders'])


parser = argparse.ArgumentParser()
parser.add_argument('source', help='Source directory', nargs=1)
parser.add_argument('-d', '--destination',
                    help='Destination directory. Full path required.', nargs=1)
parser.add_argument(
    '--sort-folders', help='Sort folders into categories', action='store_true')
parser.add_argument('-r', '--recursive',
                    help='Recursively check into folders in the specified source directory.', action='store_true')
parser.add_argument(
    '-t', '--types', help='File formats to sort.', nargs='+')
options = vars(parser.parse_args())

source_path = os.path.abspath(options['source'][0])
proceed = True

if options['destination']:
    destination_path = os.path.abspath(options['destination'][0])
else:
    destination_path = source_path

if options['types']:
    file_types = options['types']
    glob_pattern = '*.'
else:
    file_types = ['*']
    glob_pattern = ''

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
    print('\n{:-^80}\n'.format('START'))

    if options['recursive']:
        for root, dirs, files in os.walk(source_path):
            sort_files(root, destination_path, file_types, glob_pattern)

    else:
        sort_files(source_path, destination_path, file_types, glob_pattern)

    if options['sort_folders']:
        folders = [folder for folder in glob(os.path.join(
            source_path, '*')) if os.path.isdir(folder) and os.path.basename(folder) not in typeGroups.keys()]

        if folders:
            for folder in folders:
                folder_instance = Folder(os.path.join(source_path, folder))
                folder_instance.group(source_path)

    print('Done.')
    print('\n{:-^80}\n'.format('END'))

else:
    parser.print_help()
