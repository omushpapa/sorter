#! /usr/bin/env python3

import os
import shutil
import re
import hashlib
from filegroups import typeGroups, typeList
from glob import glob

def has_signore_file(path, filename='.signore'):
    try:
        open(os.path.join(path, filename), 'r').close()
    except FileNotFoundError:
        return False
    else:
        return True


class Directory(object):

    def __init__(self, path):
        self._path = os.path.abspath(path)
        self._name = os.path.basename(self.path)
        self._parent = os.path.dirname(self.path)
        self._hidden_path = self.in_hidden_path(self.path)

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        self._path = value
        self._name = os.path.basename(self.path)
        self._parent = os.path.dirname(self.path)
        self._hidden_path = self.in_hidden_path(self.path)

    @property
    def name(self):
        return self._name

    @property
    def parent(self):
        return self._parent

    @property
    def hidden_path(self):
        return self._hidden_path

    def in_hidden_path(self, path):
        if not os.path.basename(path):
            return False
        else:
            hidden_path = False
            path_base = os.path.basename(path)
            if path_base.startswith('.') or path_base.startswith('__'):
                return True
            else:
                hidden_path = self.in_hidden_path(
                    os.path.abspath(os.path.dirname(path)))
            return hidden_path


class File(Directory):
    filename_pattern = re.compile(r'\-\sdup[\s\(\d\)]+')

    def __init__(self, path):
        super(File, self).__init__(path)
        self._extension = self._get_extension()
        self._category = self.get_category(self.extension)
        self._exists = os.path.isfile(self.path)

    @property
    def extension(self):
        return self._extension

    @property
    def category(self):
        return self._category

    @property
    def exists(self):
        return self._exists

    @property
    def path(self):
        return super(File, self).path

    @path.setter
    def path(self, value):
        super(File, self.__class__).path.fset(self, value)
        self._extension = self._get_extension()
        self._category = self.get_category(self.extension)
        self._exists = os.path.isfile(self.path)

    def _get_extension(self):
        extension = 'undefined'
        result = os.path.splitext(self.name)[1][1:]
        if result:
            extension = result
        return extension

    def get_category(self, extension):
        if extension:
            file_extension = extension.upper()
            for key in typeGroups.keys():
                common = set(typeGroups[key]) & set([file_extension])
                if common:
                    return key
        return 'UNDEFINED'

    def find_suitable_name(self, file_path, count=1):
        filename = os.path.basename(file_path)
        # Fix when renaming errors occusr
        # fix_filename = re.sub(r'[\-\s]*dup[\s\(\d\)\-]+', '', filename)
        # filename = fix_filename
        # Things happen :P
        if os.path.exists(file_path):
            split_data = os.path.splitext(filename)
            new_filename = ''
            if count == 1:
                new_filename = '{0} - dup ({1}){2}'.format(
                    split_data[0], count, split_data[1])
            else:
                sub_value = '- dup (%s)' % count
                new_filename = re.sub(
                    self.filename_pattern, sub_value, filename)

            new_file_path = os.path.join(
                os.path.dirname(file_path), new_filename)
            count += 1
            try:
                filename = self.find_suitable_name(new_file_path, count)
            except RuntimeError:
                filename = hashlib.md5(filename.encode('utf-8')).hexdigest()
        return filename

    def _set_extension_destination(self, root_path, group):
        if group:
            group_dst = os.path.join(root_path, self.category)

            if not os.path.isdir(group_dst):
                os.mkdir(group_dst)
            extension_dst = os.path.join(group_dst, self.extension.upper())
        else:
            extension_dst = os.path.join(root_path, self.extension.upper())

        if not os.path.isdir(extension_dst):
            os.mkdir(extension_dst)
        new_dst = os.path.join(extension_dst, self.name)
        suitable_name = self.find_suitable_name(new_dst)
        final_dst = os.path.join(os.path.dirname(new_dst),
                                 suitable_name)

        return final_dst

    def move_to(self, dst_root_path, group=False):
        # dst_root_path should be root, no file name
        final_destination = self._set_extension_destination(
            dst_root_path, group)
        if not os.path.dirname(self.path) == os.path.dirname(final_destination):
            try:
                shutil.move(self.path, final_destination)
            except PermissionError as e:
                print('Could not move "{0}": {1}'.format(self.path, e))
            self.path = final_destination


class Folder(Directory):

    def __init__(self, path):
        super(Folder, self).__init__(path)
        self._exists = os.path.isdir(self.path)
        self._for_sorter = self.is_sorter_folder(self.path)
        self._category_folder = ''

    @property
    def path(self):
        return super(Folder, self).path

    @path.setter
    def path(self, value):
        super(Folder, self.__class__).path.fset(self, value)
        self._exists = os.path.isdir(self.path)
        self._for_sorter = self.is_sorter_folder(self.path)
        self._category_folder = ''

    @property
    def exists(self):
        return self._exists

    @property
    def for_sorter(self):
        return self._for_sorter

    def is_sorter_folder(self, path):
        if os.path.isdir(path):
            dirname = os.path.basename(path)
            if dirname.isupper():
                if dirname in typeList or dirname == 'FOLDERS':
                    return True
            else:
                if dirname in typeGroups.keys():
                    return True

        return False

    def _get_category_folder(self):
        # category folder is not full path
        if self.for_sorter:
            if self.name.upper() in typeList:
                # folder is file type folder
                category = [key for key in typeGroups.keys() if set(
                    typeGroups[key]) & set([self.name])][0]
                return os.path.join(category, self.name.upper())
            if self.name in typeGroups.keys():
                # folder is category folder
                return os.path.basename(self.parent)

        return 'FOLDERS'

    def create(self):
        try:
            try:
                os.mkdir(self.path)
            except FileExistsError:
                pass
        except NameError:  # For Python2
            pass
        finally:
            self.path = self.path

    def group(self, root_path):
        # root_path is provided by user
        # groups according to root path ie source_path
        # if folder is not a sorter folder
        # eg developer, PDF
        # move to category folder == FOLDERS
        #
        # if folder is a sorter folder
        # eg developer, PDF
        # move to category folder
        dst = os.path.join(root_path, self._get_category_folder())
        self.move_to(dst, root_path, group_content=True)

    def move_to(self, dst, root_path, src=None, group_content=False):
        # dst, src should be absolute paths
        if src is None:
            src = self.path

        if os.path.isdir(dst):
            # if destination exists
            self._move_contents(src, dst, root_path, group_content)
            try:
                os.rmdir(src)
            except OSError:
                print('Could not delete "%s". May contain hidden files.' % src)

        else:
            # if destination does not exists
            shutil.move(src, dst)

    def _move_contents(self, src, dst, root_path, group_content=False):
        # move contents of src to dst
        # ignore folders
        files = [content for content in glob(
            os.path.join(src, '*')) if os.path.isfile(content)]
        if files:
            for file_ in files:
                file_instance = File(os.path.join(src, file_))
                file_instance.move_to(
                    dst_root_path=root_path, group=group_content)


class CustomFolder(Folder):

    def __init__(self, path, group_folder_name):
        self._group_folder = group_folder_name.title()
        super(CustomFolder, self).__init__(path)

    @property
    def group_folder(self):
        return self._group_folder

    def _get_category_folder(self):
        # category folder is not full path
        return self._group_folder

    def _move_contents(self, src, dst, root_path, group_content=False):
        # move contents of src to dst
        # ignore folders
        files = [content for content in glob(
            os.path.join(src, '*')) if os.path.isfile(content)]
        if files:
            for file_ in files:
                file_instance = CustomFile(os.path.join(src, file_), self._group_folder)
                file_instance.move_to(
                    dst_root_path=root_path, group=group_content)
                
    def move_to(self, dst, root_path, src=None, group_content=False):
        # dst, src should be absolute paths
        if src is None:
            src = self.path

        if os.path.isdir(dst):
            # if destination exists
            self._move_contents(src, dst, root_path, group_content)
            if not has_signore_file(dst):
                open(os.path.join(dst,'.signore'), 'w+').close()
            try:
                os.rmdir(src)
            except OSError:
                # TODO: Check if has empty subfolders, then delete
                print('Could not delete "%s". May contain hidden files.' % src)

        else:
            # if destination does not exists
            shutil.move(src, dst)


class CustomFile(File):

    def __init__(self, path, group_folder_name):
        self._group_folder = group_folder_name.title()
        super(CustomFile, self).__init__(path)

    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, value):
        self._category = value

    def get_category(self, extension):
        return self._group_folder
