#! /usr/bin/env python3

import os
import shutil
import re
import hashlib
import ctypes
import inspect
from glob import iglob
from data.filegroups import typeGroups, typeList
from data.settings import SORTER_IGNORE_FILENAME, SORTER_FOLDER_IDENTITY_FILENAME
from pathlib import Path


def has_signore_file(path, filename=SORTER_IGNORE_FILENAME):
    try:
        open(os.path.join(path, filename), 'r').close()
    except FileNotFoundError:
        return False
    else:
        return True


def write_identity_file(path):
    identity_file = os.path.join(path, SORTER_FOLDER_IDENTITY_FILENAME)
    open(identity_file, 'w+').close()
    if os.name == 'nt':
        # Hide file - Windows
        ctypes.windll.kernel32.SetFileAttributesW(identity_file, 2)


class RelativePathException(Exception):
    pass


class EmptyNameException(Exception):
    pass


class Directory(object):

    def __init__(self, path):
        if not os.path.isabs(path):
            raise RelativePathException('relative paths cannot be used')
        self.Path = Path(path)
        self._path = self.Path.absolute().__str__()
        self._parent = self.Path.parent.absolute().__str__()
        self._name = self.Path.name
        self._hidden_path = self.in_hidden_path(self._path)
        self._suffix = self.Path.suffix
        self._stem = self.Path.stem

    def __str__(self):
        return self.path

    @property
    def path(self):
        return self._get_path()

    @path.setter
    def path(self, value):
        self._set_path(value)

    @property
    def parent(self):
        return self._parent

    @property
    def name(self):
        return self._name

    @property
    def hidden_path(self):
        return self._hidden_path

    @property
    def suffix(self):
        return self._suffix

    @property
    def stem(self):
        return self._stem

    def _get_path(self):
        return self._path

    def _set_path(self, value):
        self.__init__(value)

    def in_hidden_path(self, full_path):
        paths = full_path.split(os.sep)

        if os.name == 'nt':
            get_hidden_attribute = ctypes.windll.kernel32.GetFileAttributesW
            for i in range(len(paths) + 1):
                path = os.sep.join(paths[:i])
                try:
                    attrs = get_hidden_attribute(path)
                    result = bool(attrs & 2)
                except AttributeError:
                    result = False
                finally:
                    if result:
                        return True
        else:
            for i in range(len(paths) + 1):
                path = str(os.sep).join(paths[:i])
                base_name = os.path.basename(path)
                if base_name.startswith('.') or base_name.startswith('__'):
                    return True

        return False


class File(Directory):

    default_category = 'UNDEFINED'
    filename_pattern = re.compile(r'\-\sdup[\s\(\d\)]+')

    def __init__(self, path):
        super(File, self).__init__(path)
        extension = self.Path.suffix[1:]
        self._extension = extension or self.default_category
        self._category = self.get_category(extension)
        self._exists = self.Path.is_file

    @property
    def extension(self):
        return self._extension

    @property
    def category(self):
        return self._category

    @property
    def exists(self):
        return self._exists()

    def touch(self, **kwargs):
        self.Path.touch(**kwargs)

    def get_category(self, extension):
        """Return the category of the file instance as determined by its extension.

        Categories are determined in filegroups.py
        """
        if extension:
            file_extension = set([extension.upper()])
            for key in typeGroups.keys():
                common = set(typeGroups[key]) & file_extension
                if common:
                    return key
        return self.default_category

    def find_suitable_name(self, file_path):
        """Validate whether a file with the same name exists, return a name
        indicating that it is a duplicate, else return the given file name.

        A fix is provided in case file renaming errors occur. Check comments.
        """
        dirname = os.path.dirname(file_path)
        new_filename = os.path.basename(file_path)
        count = 1

        while os.path.isfile(file_path):
            new_filename = '{0} - dup ({1}){2}'.format(
                self.stem, count, self.suffix)
            file_path = os.path.join(dirname, new_filename)
            count += 1

        return new_filename

    def move_to(self, dst_root_path, group=False, by_extension=False, group_folder_name=None):
        """Move the file instance to a location relative to the
        specified dst_root_path.

        dst_root_path is the root folder from where files will be organised
        by their extension.

        If dst_root_path = '/home/User/'
        final destination may be

                '/home/User/<extension>/<filename>'
                - group=False, ignore other options

                or

                '/home/User/<category>/<filename>'
                - group=True, by_extension=False, group_folder_name=None

                or

                '/home/User/<category>/<extension>/<filename>'
                - group=True, by_extension=True, group_folder_name=None

                or

                '/home/User/<group_folder_name>/<filename>'
                - group=True,by_extension=False,group_folder_name=<some name>

                or

                '/home/User/<group_folder_name>/<extension>/<filename>'
                - group=True,by_extension=True,group_folder_name=<some name>
        """
        if group:
            if group_folder_name is None:
                final_dst, go_back = self._set_category_filename_dst(
                    dst_root_path, by_extension)
            elif not group_folder_name:
                raise EmptyNameException('blank name not allowed')
            else:
                final_dst, go_back = self._set_group_folder_dst(
                    dst_root_path, by_extension, group_folder_name)
        else:
            final_dst, go_back = self._set_extension_filename_dst(
                dst_root_path)

        final_dir = os.path.dirname(final_dst)

        if not os.path.dirname(self.path) == final_dir:
            os.makedirs(final_dir, exist_ok=True)
            try:
                shutil.move(self.path, final_dst)
            except PermissionError:
                pass
            else:
                if go_back == 2:
                    write_identity_file(os.path.dirname(
                        os.path.dirname(final_dst)))
                    write_identity_file(os.path.dirname(final_dst))
                if go_back == 1:
                    write_identity_file(os.path.dirname(final_dst))
                self.path = final_dst

    def _set_group_folder_dst(self, root_path, by_extension, group_folder_name):
        if by_extension:
            group_folder_dst = os.path.join(
                root_path, group_folder_name, self.extension.upper())
            go_back = 2
        else:
            group_folder_dst = os.path.join(root_path, group_folder_name)
            go_back = 1
        return self._set_final_destination(group_folder_dst), go_back

    def _set_category_filename_dst(self, root_path, by_extension):
        if by_extension:
            category_dst = os.path.join(
                root_path, self.category, self.extension.upper())
            go_back = 2
        else:
            category_dst = os.path.join(root_path, self.category)
            go_back = 1
        return self._set_final_destination(category_dst), go_back

    def _set_extension_filename_dst(self, root_path):
        extension_dst = os.path.join(root_path, self.extension.upper())
        go_back = 1
        return self._set_final_destination(extension_dst), go_back

    def _set_final_destination(self, parent_path):
        dst = os.path.join(parent_path, self.name)
        suitable_name = self.find_suitable_name(dst)
        return os.path.join(parent_path, suitable_name)


class Folder(Directory):

    default_category = 'FOLDERS'

    def __init__(self, path):
        super(Folder, self).__init__(path)
        self._exists = self.Path.is_dir
        self._for_sorter = self._is_sorter_folder()
        self._category_folder = self._get_category_folder()

    @property
    def exists(self):
        return self._exists()

    @property
    def for_sorter(self):
        return self._for_sorter

    @property
    def category_folder(self):
        return self._category_folder

    def create(self, **kwargs):
        self.Path.mkdir(**kwargs)

    def glob(self, pattern):
        return self.Path.glob(pattern)

    def _is_sorter_folder(self, path=None):
        """Return True if Folder instance was generated by Sorter, else False.
        The folder has to exist."""
        path = path or self.path
        try:
            sorter_identity = os.path.join(
                path, SORTER_FOLDER_IDENTITY_FILENAME)
            open(sorter_identity, 'r').close()
        except FileNotFoundError:
            # For compatibility
            dirname = self.name
            if dirname.isupper():
                if dirname == self.default_category or dirname in typeList:
                    return True
            else:
                if dirname in typeGroups.keys():
                    return True
        else:
            return True

        return False

    def _get_category_folder(self):
        # category folder is not full path
        if self.for_sorter:
            if self.name.upper() in typeList:
                category = [key for key in typeGroups.keys() if set(
                    typeGroups[key]) & set([self.name])][0]
                return category
            if self.name in typeGroups.keys():
                return None

        return self.default_category

    def move_to(self, dst_root_path, **kwargs):
        """Move the folder to dst_root_path and, if self.for_sorter is True,
        create a sorter identity file if the folder has been generated by the
        current operation i.e. not preexistent."""
        if has_signore_file(self.path):
            return
        if self.path == dst_root_path:
            if kwargs.get('group', False):
                self.group(dst_root_path, **kwargs)
            else:
                return

        if self.category_folder is None:
            category_dst = dst_root_path
            create_category_identity_file = False
        else:
            category_dst = os.path.join(dst_root_path, self.category_folder)
            create_category_identity_file = True

        final_dst = os.path.join(category_dst, self.name)
        self._move_contents(final_dst)
        if self.for_sorter:
            write_identity_file(final_dst)
        if create_category_identity_file:
            write_identity_file(category_dst)
        try:
            os.rmdir(self.path)
        except OSError:
            pass
        self.path = final_dst

    def _move_contents(self, dst, src=None):
        if src is None:
            path_gen = self.glob('*')
            dirname = self.parent
        else:
            path_gen = iglob(os.path.join(src, '*'))
            dirname = os.path.dirname(src)

        contents = (str(i) for i in path_gen if (os.path.isfile(str(i)) and os.path.basename(str(i))
                                                 != SORTER_IGNORE_FILENAME) or (os.path.isdir(str(i)) and not has_signore_file(str(i))))
        os.makedirs(dst, exist_ok=True)

        for i in contents:
            item = str(i)
            if os.path.isfile(item):
                try:
                    open(os.path.join(dst, os.path.basename(item)), 'r').close()
                except FileNotFoundError:
                    shutil.move(item, dst)
            if os.path.isdir(item):
                dir_ = os.path.join(dst, os.path.basename(item))
                try:
                    os.makedirs(dir_)
                except FileExistsError:
                    self._move_contents(dst, src=item)
                else:
                    os.rmdir(dir_)
                    try:
                        shutil.move(item, dst)
                    except shutil.Error:
                        pass

    def group(self, dst_root_path, **kwargs):
        """
        dst_root_path = /home/User/

        /home/User/<this folder>/
        -group=False,ignore the rest

        or

        /home/User/<category>/<this folder>/
        -group=True,group_folder_name=None,ignore the rest

        or 

        /home/User/<group_folder_name>/<this folder>/
        -group=True,group_folder_name=<some name>
        """
        if has_signore_file(self.path):
            return
        if 'group' not in kwargs.keys():
            kwargs['group'] = True
        contents = (str(i) for i in self.glob('*') if os.path.isfile(str(i))
                    and os.path.basename(str(i)) != SORTER_IGNORE_FILENAME)
        for item in contents:
            file_ = File(item)
            file_.move_to(dst_root_path, **kwargs)

        try:
            os.rmdir(self.path)
        except OSError:
            pass
