#! /usr/bin/python3
# sorter.py - A Python script that sorts files in a folder
# into folders which are named by type.

import os
import shutil
import argparse
import sys
import glob
import re
from filegroups import fileGroups, typeList


def move_file(source_path, destination_path, extension_dir, filename):
    source_file = os.path.join(source_path, filename)
    if destination_path:
        extension_destination = os.path.join(destination_path, extension_dir)
    else:
        extension_destination = os.path.join(source_path, extension_dir)

    if os.path.isdir(extension_destination):
        destination_file = os.path.join(
            extension_destination, os.path.basename(filename))
        if not os.path.dirname(source_file) == os.path.dirname(destination_file):
            suitable_name = find_suitable_name(destination_file)
            new_destination = os.path.join(
                extension_destination, suitable_name)
            try:
                shutil.move(source_file, new_destination)
            except OSError:
                pass
    else:
        os.makedirs(extension_destination)
        move_file(source_path, destination_path, extension_dir, filename)


def move_dir(source_path, destination_path):
    source_dir = os.path.basename(source_path)
    destination_dir = os.path.join(destination_path, source_dir)
    folders = [os.path.abspath(folder_name) for folder_name in glob.glob(os.path.join(
        source_path, '*')) if os.path.basename(folder_name) in typeList and os.path.isdir(folder_name)]

    for folder in folders:
        for file_ in glob.glob(os.path.join(folder, '*')):
            extension_dir = os.path.basename(folder)
            move_file(source_path, destination_path, extension_dir, file_)
        try:
            os.rmdir(folder)
        except OSError:
            print('The directory "%s" contains some files and cannot be moved' % folder)


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


def group_folders(path, found_extensions):
    for key in fileGroups.keys():
        common = set(found_extensions) & set(fileGroups[key])
        if common:
            common_list = list(common)
            key_folder = os.path.join(path, key)
            if not os.path.isdir(key_folder):
                os.makedirs(key_folder)

            if is_writable(key_folder):
                for extension in common_list:
                    extension_path = os.path.join(path, extension)
                    new_extension_path = os.path.join(key_folder, extension)
                    if not os.path.isdir(new_extension_path):
                        os.makedirs(new_extension_path)

                    dirs = [dir_ for dir_ in glob.glob(
                        os.path.join(extension_path, '*'))]
                    for file_ in dirs:
                        source_path = os.path.join(
                            extension_path, os.path.basename(file_))
                        dst = os.path.join(
                            new_extension_path, os.path.basename(file_))
                        suitable_name = find_suitable_name(dst)
                        final_dst = os.path.join(
                            new_extension_path, suitable_name)
                        shutil.move(source_path, final_dst)
                    try:
                        os.rmdir(extension_path)
                    except OSError:
                        print(
                            'The directory "%s" contains some files and cannot be moved.' % extension_path)


def find_suitable_name(file_path, count=1):
    filename = os.path.basename(file_path)
    fix_filename = re.sub(r'copy[\s\(\d\)\-]+\s', '', filename)
    filename = fix_filename
    if os.path.exists(file_path):
        split_data = os.path.splitext(filename)
        new_filename = ''
        if count == 1:
            new_filename = '{0} - dup ({1}){2}'.format(
                split_data[0], count, split_data[1])
        else:
            sub_value = '- dup (%s)' % count
            new_filename = re.sub(filename_pattern, sub_value, filename)

        new_file_path = os.path.join(os.path.dirname(file_path), new_filename)
        count += 1
        filename = find_suitable_name(new_file_path, count)
    return filename


def group_misc_folders(path):
    sorter_folders = list(fileGroups.keys()) + ['UNDEFINED']
    folders = [folder for folder in glob.glob(os.path.join(path, '*')) if os.path.basename(
        folder) not in sorter_folders and os.path.isdir(folder) and is_writable(folder)]
    if folders:
        destination_folder = os.path.join(path, 'FOLDERS')
        for folder in folders:
            try:
                shutil.move(os.path.join(path, folder), destination_folder)
            except shutil.Error:
                print('Could not move "{0}". A folder with the same name already exists in the destination "{1}". Rename then try again.'.format(
                    folder, destination_folder))


def get_grouping_variables(source, destination):
    variables = {}
    if destination:
        variables['path'] = destination
    else:
        variables['path'] = source

    variables['extensions'] = [os.path.basename(folder_name) for folder_name in glob.glob(os.path.join(
        variables['path'], '*')) if os.path.basename(folder_name).isupper() and len(os.path.basename(folder_name).split()) == 1 and os.path.isdir(folder_name)]
    return variables


def in_hidden_path(path):
    if not os.path.basename(path):
        return False
    else:
        hidden_path = False
        path_base = os.path.basename(path)
        if path_base.startswith('.') or path_base.startswith('__'):
            return True
        else:
            hidden_path = in_hidden_path(
                os.path.abspath(os.path.dirname(path)))
        return hidden_path


def initiate_transfer(source_path, destination_path, file_types=[]):
    if file_types:
        choose = lambda x: glob.glob(os.path.join(source_path, '*.' + x))
        files = []
        for item in map(choose, file_types):
            files += item

        if files:
            for file_ in files:
                extension = os.path.splitext(file_)[1][1:].upper()
                extension_dir = get_extension_path(
                    destination_path, extension)
                move_file(source_path, destination_path,
                          extension_dir, file_)

    else:
        found_extensions = []
        files = [file_ for file_ in glob.glob(os.path.join(
            source_path, '*')) if os.path.isfile(os.path.join(source_path, file_)) and not in_hidden_path(file_)]

        if files:
            for file_ in files:
                extension = os.path.splitext(file_)[1][1:].upper()

                if extension:
                    if extension not in found_extensions and not file_types:
                        found_extensions.append(extension)

                    extension_dir = get_extension_path(
                        destination_path, extension)
                    move_file(source_path, destination_path,
                              extension_dir, file_)

                else:
                    extension_dir = get_extension_path(
                        destination_path, 'UNDEFINED')
                    move_file(source_path, destination_path,
                              extension_dir, file_)


parser = argparse.ArgumentParser()
parser.add_argument('source', help='Source directory', nargs=1)
parser.add_argument('-d', '--destination',
                    help='Destination directory. Full path required.', nargs=1)
parser.add_argument(
    '--sort-folders', help='Sort folders into categories', action='store_true')
parser.add_argument('-r', '--recursive',
                    help='Recursively look into folders in the specified source directory.', action='store_true')
parser.add_argument(
    '-t', '--types', help='File formats to sort.', nargs='+')
options = vars(parser.parse_args())

source_path = os.path.abspath(options['source'][0])
filename_pattern = re.compile(r'\-\sdup[\s\(\d\)]+')
proceed = True

if options['destination']:
    destination_path = os.path.abspath(options['destination'][0])
else:
    destination_path = ''

if options['types']:
    file_types = options['types']
else:
    file_types = []

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
            if files:
                dir_path = os.path.abspath(root)
                if not in_hidden_path(dir_path):
                    initiate_transfer(root, source_path, file_types)

    else:
        initiate_transfer(source_path, destination_path, file_types)

    if destination_path:
        move_dir(source_path, destination_path)

    if options['sort_folders']:
        group_variables = get_grouping_variables(
            source_path, destination_path)
        group_folders(group_variables['path'],
                      group_variables['extensions'])
        group_misc_folders(group_variables['path'])

    print('Done.')
    print('\n{:-^80}\n'.format('END'))

else:
    parser.print_help()
