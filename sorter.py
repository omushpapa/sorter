#! /usr/bin/env python3

import sys
import argparse
import os
from glob import glob
from operations import initiate_operation, is_writable


if __name__ == '__main__':
    if len(sys.argv) > 1:
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

        initiate_operation(src=source_path,
                           dst=destination_path,
                           sort=options['sort_folders'],
                           recur=options['recursive'],
                           types=file_types,
                           status=None,
                           parser=parser)
    else:
        try:
            import PyQt4
            from sorter_gui.qtgui import qt_run
            qt_run()
        except ImportError:
            from sorter_gui.tkgui import TkGui
            app = TkGui()
            app.tk_run()
