#! /usr/bin/env python3.4

import unittest
import os
import ctypes
import shutil
from slib.sdir import Directory, File, Folder, CustomFolder, CustomFile, CustomFileWithoutExtension
from testfixtures import TempDirectory, compare


def windows_only(cls_or_func):
    """Return function or class if OS is Windows."""
    if os.name == 'nt':
        return cls_or_func


def unix_only(cls_or_func):
    """Return function or class if OS is Windows."""
    if not os.name == 'nt':
        return cls_or_func


class TestDirectoryCommon(object):
    """Test common sdir.Directory attributes."""

    def setUp(self):
        """Initialise temporary directory and file."""
        self.tempdir = TempDirectory(encoding='utf-8')
        self.dirname = 'abc.txt'
        self.tempdir.write(self.dirname, '123')
        self.dir = Directory(self.tempdir.path)

    def tearDown(self):
        """Clean up temporary directory."""
        self.tempdir.cleanup()
        del self.dir

    def test_fails_if_abs_path_not_equal(self):
        """Return False is absolute paths do not match."""
        compare(self.tempdir.path, self.dir.path)

    def test_fails_if_basename_not_equal(self):
        """Return False if file names do not match."""
        compare(os.path.basename(self.tempdir.path), self.dir.name)

    def test_fails_if_parent_not_equal(self):
        """Return False if parent directory names do not match."""
        compare(os.path.dirname(self.tempdir.path), self.dir.parent)


@windows_only
class TestDirectoryWindows(unittest.TestCase, TestDirectoryCommon):
    """Test sdir.Directory attributes for Windows systems."""

    def setUp(self):
        TestDirectoryCommon.setUp(self)

    def tearDown(self):
        """Clean up temporary directory."""
        self.tempdir.cleanup()

    def test_returns_fails_if_hidden_value_not_match(self):
        """Test returns False is Directory.hidden_path returns False
        if Dirctory.path is hidden or has a hidden parent directory,
        True otherwise.

        TestFixtures is not used in this case since Windows temp directory
        is hidden by default.
        """
        path_1 = os.path.join(os.getcwd(), 'one')
        path_2 = os.path.join(path_1, 'two')
        path_3 = os.path.join(path_2, 'three')
        path_4 = os.path.join(path_3, 'three')
        os.makedirs(path_4)

        dir_1 = Directory(path_4)
        compare([dir_1.path, dir_1.hidden_path], [path_4, False])

        a = ctypes.windll.kernel32.SetFileAttributesW(
            os.path.dirname(path_4), 2)
        dir_1.path = dir_1.path    # Trigger re-evaluation of instance
        compare([dir_1.path, dir_1.hidden_path], [path_4, True])

        a = ctypes.windll.kernel32.SetFileAttributesW(
            os.path.dirname(path_4), 0)
        dir_1.path = dir_1.path    # Trigger re-evaluation of instance
        compare([dir_1.path, dir_1.hidden_path], [path_4, False])

        a = ctypes.windll.kernel32.SetFileAttributesW(
            os.path.dirname(path_2), 2)
        dir_1.path = dir_1.path    # Trigger re-evaluation of instance
        compare([dir_1.path, dir_1.hidden_path], [path_4, True])

        shutil.rmtree(path_1)


@unix_only
class TestDirectoryUnix(unittest.TestCase, TestDirectoryCommon):
    """Test sdir.Directory attributes for UNIX systems."""

    def setUp(self):
        """Inherits from TestDirectoryCommon.setUp()."""
        TestDirectoryCommon.setUp(self)

    def tearDown(self):
        """Inherits from TestDirectoryCommon.tearDown()."""
        TestDirectoryCommon.tearDown(self)

    def test_returns_false_if_path_not_hidden(self):
        """Return False if file is in a path where the directory,
        including the file itself, is hidden."""
        compare(self.dir.hidden_path, False)


class TestFolderCommon(object):

    def test_returns_false_if_path_not_equal(self):
        path = self.tempdir.makedir('sampler')
        folder = self.FolderClass(path)
        compare(path, folder.path)

    def test_returns_false_if_path_not_exist(self):
        self.tempdir.makedir('sample')
        folder = self.FolderClass(os.path.join(self.tempdir.path, 'sample'))
        compare(True, folder.exists)

    def test_returns_false_if_folder_not_meant_for_sorter_use(self):
        self.tempdir.makedir('sample')
        self.tempdir.makedir('developer')
        self.tempdir.makedir('FOLDERS')
        self.tempdir.makedir('PDF')
        self.tempdir.makedir('EXIST')
        folder_1 = self.FolderClass(os.path.join(self.tempdir.path, 'sample'))
        folder_2 = self.FolderClass(
            os.path.join(self.tempdir.path, 'developer'))
        folder_3 = self.FolderClass(os.path.join(self.tempdir.path, 'FOLDERS'))
        folder_4 = self.FolderClass(os.path.join(self.tempdir.path, 'PDF'))
        folder_5 = self.FolderClass(os.path.join(self.tempdir.path, 'false'))
        folder_6 = self.FolderClass(os.path.join(self.tempdir.path, 'EXIST'))
        compare([folder_1.for_sorter, folder_2.for_sorter, folder_3.for_sorter,
                 folder_4.for_sorter, folder_5.for_sorter, folder_6.for_sorter],
                [False, True, True, True, False, False])

    def test_returns_false_if_parent_folder_not_match(self):
        self.tempdir.makedir('sample')
        folder_1 = self.FolderClass(os.path.join(self.tempdir.path, 'sample'))
        compare(self.tempdir.path, folder_1.parent)

    def test_returns_false_if_path_not_exists_after_recreate(self):
        """Test declares a non-existent path and returns False
        if still non-existent after operation."""
        temp_path = self.tempdir.path
        path_1 = os.path.join(temp_path, 'one')
        path_2 = os.path.join(path_1, 'two')
        path_3 = os.path.join(path_2, 'three')
        path_4 = os.path.join(path_3, 'three')
        folder = self.FolderClass(path_4)
        compare(False, os.path.exists(path_4))
        compare(False, folder.exists)
        folder.recreate()
        compare(True, os.path.exists(path_4))
        compare(True, folder.exists)

    def test_returns_false_if_folder_not_moved(self):
        temp = self.tempdir
        temp_path = self.tempdir.path
        path_1 = temp.makedir('one/two/three/four')
        path_2 = temp.makedir('one/six/ten')
        folder_1 = self.FolderClass(path_1)
        folder_2 = self.FolderClass(path_2)
        compare([folder_1.exists, folder_2.exists],
                [True, True])
        final_dst = os.path.join(path_2, os.path.join('FOLDERS', 'four'))
        folder_1.group(path_2)
        compare(True, os.path.exists(os.path.join(path_2, 'FOLDERS')))
        compare(True, os.path.isdir(final_dst))


class TestFolder(unittest.TestCase, TestFolderCommon):

    def setUp(self):
        """Initialise temporary directory."""
        self.tempdir = TempDirectory(encoding='utf-8')
        self.FolderClass = Folder

    def tearDown(self):
        self.tempdir.cleanup()


class TestCustomFolder(unittest.TestCase, TestFolderCommon):

    def setUp(self):
        """Initialise temporary directory."""
        self.tempdir = TempDirectory(encoding='utf-8')
        self.group_folder_name = 'my name is a small guy'
        self.FolderClass = lambda path, group_folder_name=self.group_folder_name: CustomFolder(
            path, group_folder_name)

    def tearDown(self):
        self.tempdir.cleanup()

    def test_returns_false_if_group_folder_name_not_match(self):
        """Test returns False if provided group_folder names do not match."""
        f = self.FolderClass(self.tempdir.path)
        compare(f.group_folder, self.group_folder_name.title())

    def test_returns_false_if_folder_not_moved(self):
        """Test returns False if folder not moved to a location with
        the name similar to the group_folder_name value, in title format."""
        temp = self.tempdir
        temp_path = self.tempdir.path
        path_1 = temp.makedir('one/two/three/four')
        path_2 = temp.makedir('one/six/ten')
        folder_1 = self.FolderClass(path_1)
        folder_2 = self.FolderClass(path_2)
        compare(True, folder_1.exists)
        folder_1.group(path_2)
        final_path = os.path.join(path_2, self.group_folder_name.title())
        compare(final_path, folder_1.path)
        compare(True, folder_1.exists)


class TestFileCommon(object):
    """Test sdir.File."""

    def test_returns_false_if_extensions_lists_dont_match(self):
        """Return False if file extensions do not match with list."""
        extensions = [self.file_1_File.extension, self.file_2_File.extension,
                      self.file_3_File.extension, self.file_4_File.extension, self.file_5_File.extension]
        compare(extensions, ['txt', 'c', 'undefined', 'gz', 'undefined'])

    def test_returns_false_if_categories_lists_dont_match(self):
        """Return False if file categories do not match with list."""
        categories = [self.file_1_File.category, self.file_2_File.category,
                      self.file_3_File.category, self.file_4_File.category, self.file_5_File.category]
        compare(categories, ['document', 'developer',
                             'UNDEFINED', 'archive', 'UNDEFINED'])

    def test_returns_false_if_not_file(self):
        """Return False if file does not exist."""
        non_existent = File(os.path.join(self.tempdir.path, 'not here.txt'))
        files = [self.file_1_File.exists, self.file_2_File.exists,
                 self.file_3_File.exists, self.file_4_File.exists,
                 self.file_5_File.exists, non_existent.exists]

        compare(files, [True, True, True, True, True, False])

    def test_returns_false_if_names_dont_match(self):
        """Test returns False if there was an error in renaming the file."""
        dup_file_1_name = 'abc - dup (1).txt'
        compare(self.file_1_File.find_suitable_name(
            self.file_1_File.path), dup_file_1_name)
        self.tempdir.write(dup_file_1_name, '')
        compare(self.file_1_File.find_suitable_name(
            self.file_1_File.path), 'abc - dup (2).txt')
        compare(self.file_3_File.find_suitable_name(
            self.file_3_File.path), 'abc - dup (1)')

    def test_returns_false_if_relocation_without_grouping_failed(self):
        """Test returns False if file relocation failed when 
        File.move_to(group=False)."""
        self.tempdir.makedir('newfolder')
        dst = os.path.join(self.tempdir.path, 'newfolder')

        self.file_1_File.move_to(dst)
        compare(self.file_1_File.path, os.path.join(dst, os.path.join(
            os.path.splitext(self.file_1_name)[1][1:].upper()), self.file_1_name))
        self.file_2_File.move_to(dst)
        compare(self.file_2_File.path, os.path.join(dst, os.path.join(
            os.path.splitext(self.file_2_name)[1][1:].upper()), self.file_2_name))
        self.file_3_File.move_to(dst)
        compare(self.file_3_File.path, os.path.join(
            dst, os.path.join('UNDEFINED', self.file_3_name)))
        self.file_4_File.move_to(dst)
        compare(self.file_4_File.path, os.path.join(dst, os.path.join(
            os.path.splitext(self.file_4_name)[1][1:].upper()), self.file_4_name))
        self.file_5_File.move_to(dst)
        compare(self.file_5_File.path, os.path.join(
            dst, os.path.join('UNDEFINED', self.file_5_name)))

    def test_returns_false_if_relocation_with_grouping_failed(self):
        """Test returns False if file relocation failed when 
        File.move_to(group=True)."""
        self.tempdir.makedir('grouping_folder')
        dst = os.path.join(self.tempdir.path, 'grouping_folder')

        self.file_1_File.move_to(dst, group=True)
        compare(self.file_1_File.path, os.path.join(os.path.join(dst, self.file_1_File.category),
                                                    os.path.join(os.path.splitext(self.file_1_name)[1][1:].upper()), self.file_1_name))
        self.file_2_File.move_to(dst, group=True)
        compare(self.file_2_File.path, os.path.join(os.path.join(dst, self.file_2_File.category),
                                                    os.path.join(os.path.splitext(self.file_2_name)[1][1:].upper()), self.file_2_name))
        self.file_3_File.move_to(dst, group=True)
        compare(self.file_3_File.path, os.path.join(os.path.join(
            dst, self.file_3_File.category), os.path.join('UNDEFINED', self.file_3_name)))
        self.file_4_File.move_to(dst, group=True)
        compare(self.file_4_File.path, os.path.join(os.path.join(dst, self.file_4_File.category),
                                                    os.path.join(os.path.splitext(self.file_4_name)[1][1:].upper()), self.file_4_name))
        self.file_5_File.move_to(dst, group=True)
        compare(self.file_5_File.path, os.path.join(os.path.join(
            dst, self.file_5_File.category), os.path.join('UNDEFINED', self.file_5_name)))


class TestFile(unittest.TestCase, TestFileCommon):

    def setUp(self):
        """Initialise temporary directory and files."""
        self.tempdir = TempDirectory(encoding='utf-8')

        self.file_1_name = 'abc.txt'
        self.file_2_name = 'ay.c'
        self.file_3_name = 'abc'
        self.file_4_name = 'crpart.tar.gz'
        self.file_5_name = 'long file name without extension and with spaces'

        self.file_1_path = self.tempdir.write(self.file_1_name, '')
        self.file_2_path = self.tempdir.write(self.file_2_name, '')
        self.file_3_path = self.tempdir.write(self.file_3_name, '')
        self.file_4_path = self.tempdir.write(self.file_4_name, '')
        self.file_5_path = self.tempdir.write(self.file_5_name, '')

        self.file_1_File = File(self.file_1_path)
        self.file_2_File = File(self.file_2_path)
        self.file_3_File = File(self.file_3_path)
        self.file_4_File = File(self.file_4_path)
        self.file_5_File = File(self.file_5_path)

    def tearDown(self):
        self.tempdir.cleanup()


class TestCustomFile(unittest.TestCase, TestFileCommon):

    def setUp(self):
        """Initialise temporary directory and files."""
        self.tempdir = TempDirectory(encoding='utf-8')

        self.file_1_name = 'abc.txt'
        self.file_2_name = 'ay.c'
        self.file_3_name = 'abc'
        self.file_4_name = 'crpart.tar.gz'
        self.file_5_name = 'long file name without extension and with spaces'

        self.file_1_path = self.tempdir.write(self.file_1_name, '')
        self.file_2_path = self.tempdir.write(self.file_2_name, '')
        self.file_3_path = self.tempdir.write(self.file_3_name, '')
        self.file_4_path = self.tempdir.write(self.file_4_name, '')
        self.file_5_path = self.tempdir.write(self.file_5_name, '')

        self.file_1_File = CustomFile(self.file_1_path, 'sample')
        self.file_2_File = CustomFile(
            self.file_2_path, 'grey hound And an animaL')
        self.file_3_File = CustomFile(self.file_3_path, 'one 1rt 7')
        self.file_4_File = CustomFile(self.file_4_path, 's')
        self.file_5_File = CustomFile(self.file_5_path, '123 556u')

    def tearDown(self):
        self.tempdir.cleanup()

    def test_returns_false_if_categories_lists_dont_match(self):
        """Return False if file categories do not match with list."""
        categories = [self.file_1_File.category, self.file_2_File.category,
                      self.file_3_File.category, self.file_4_File.category, self.file_5_File.category]
        compare(categories, ['Sample', 'Grey Hound And An Animal',
                             'One 1Rt 7', 'S', '123 556U'])

    def test_returns_false_if_relocation_without_grouping_failed(self):
        """Test returns False if file relocation failed when 
        File.move_to(dst) and group argument is not provided."""
        self.tempdir.makedir('newfolder')
        dst = os.path.join(self.tempdir.path, 'newfolder')

        self.file_1_File.move_to(dst)
        compare(self.file_1_File.path, os.path.join(dst, os.path.join(os.path.join('Sample',
                                                                                   os.path.splitext(self.file_1_name)[1][1:].upper()), self.file_1_name)))
        self.file_2_File.move_to(dst)
        compare(self.file_2_File.path, os.path.join(dst, os.path.join(os.path.join('Grey Hound And An Animal',
                                                                                   os.path.splitext(self.file_2_name)[1][1:].upper()), self.file_2_name)))
        self.file_3_File.move_to(dst)
        compare(self.file_3_File.path, os.path.join(dst, os.path.join(os.path.join('One 1Rt 7',
                                                                                   "UNDEFINED"), self.file_3_name)))
        self.file_4_File.move_to(dst)
        compare(self.file_4_File.path, os.path.join(dst, os.path.join(os.path.join('S',
                                                                                   os.path.splitext(self.file_4_name)[1][1:].upper()), self.file_4_name)))
        self.file_5_File.move_to(dst)
        compare(self.file_5_File.path, os.path.join(dst, os.path.join(os.path.join('123 556U',
                                                                                   "UNDEFINED"), self.file_5_name)))


class TestCustomFileWithoutExtension(unittest.TestCase, TestFileCommon):

    def setUp(self):
        """Initialise temporary directory and files."""
        self.tempdir = TempDirectory(encoding='utf-8')

        self.file_1_name = 'abc.txt'
        self.file_2_name = 'ay.c'
        self.file_3_name = 'abc'
        self.file_4_name = 'crpart.tar.gz'
        self.file_5_name = 'long file name without extension and with spaces'

        self.file_1_path = self.tempdir.write(self.file_1_name, '')
        self.file_2_path = self.tempdir.write(self.file_2_name, '')
        self.file_3_path = self.tempdir.write(self.file_3_name, '')
        self.file_4_path = self.tempdir.write(self.file_4_name, '')
        self.file_5_path = self.tempdir.write(self.file_5_name, '')

        self.file_1_File = CustomFileWithoutExtension(
            self.file_1_path, 'sample')
        self.file_2_File = CustomFileWithoutExtension(
            self.file_2_path, 'grey hound And an animaL')
        self.file_3_File = CustomFileWithoutExtension(
            self.file_3_path, 'one 1rt 7')
        self.file_4_File = CustomFileWithoutExtension(self.file_4_path, 's')
        self.file_5_File = CustomFileWithoutExtension(
            self.file_5_path, '123 556u')

    def tearDown(self):
        self.tempdir.cleanup()

    def test_returns_false_if_categories_lists_dont_match(self):
        """Return False if file categories do not match with list."""
        categories = [self.file_1_File.category, self.file_2_File.category,
                      self.file_3_File.category, self.file_4_File.category, self.file_5_File.category]
        compare(categories, ['Sample', 'Grey Hound And An Animal',
                             'One 1Rt 7', 'S', '123 556U'])

    def test_returns_false_if_relocation_without_grouping_failed(self):
        """Test returns False if file relocation failed when 
        File.move_to(dst) and group argument is not provided."""
        self.tempdir.makedir('newfolder')
        dst = os.path.join(self.tempdir.path, 'newfolder')

        self.file_1_File.move_to(dst)
        compare(self.file_1_File.path, os.path.join(
            dst, os.path.join('Sample', self.file_1_name)))
        self.file_2_File.move_to(dst)
        compare(self.file_2_File.path, os.path.join(
            dst, os.path.join('Grey Hound And An Animal', self.file_2_name)))
        self.file_3_File.move_to(dst)
        compare(self.file_3_File.path, os.path.join(
            dst, os.path.join('One 1Rt 7', self.file_3_name)))
        self.file_4_File.move_to(dst)
        compare(self.file_4_File.path, os.path.join(
            dst, os.path.join('S', self.file_4_name)))
        self.file_5_File.move_to(dst)
        compare(self.file_5_File.path, os.path.join(
            dst, os.path.join('123 556U', self.file_5_name)))

    def test_returns_false_if_relocation_with_grouping_failed(self):
        """Test returns False if file relocation failed when 
        File.move_to(group=True)."""
        self.tempdir.makedir('grouping_folder')
        dst = os.path.join(self.tempdir.path, 'grouping_folder')

        self.file_1_File.move_to(dst, group=True)
        compare(self.file_1_File.path, os.path.join(
            dst, os.path.join('Sample', self.file_1_name)))


if __name__ == '__main__':
    unittest.main()
