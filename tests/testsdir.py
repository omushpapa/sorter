#! /usr/bin/env python3.4

import unittest
import os
import ctypes
from sdir import Directory, File
from testfixtures import TempDirectory, compare


def windows_only(cls_or_func):
    """Return function or class if OS is Windows."""
    if os.name == 'nt':
        return cls_or_func
    else:
        pass


class TestDirectoryCommon(object):
    """Test common sdir.Directory attributes."""

    def setUp(self):
        self.tempdir = TempDirectory(encoding='utf-8')
        self.dirname = 'abc.txt'
        self.tempdir.write(self.dirname, '123')
        self.dir = Directory(self.tempdir.path)

    def tearDown(self):
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
        TestDirectoryCommon.tearDown(self)

    def test_returns_true_if_path_hidden(self):
        pass


class TestDirectoryUnix(unittest.TestCase, TestDirectoryCommon):
    """Test sdir.Directory attributes for UNIX systems."""

    def setUp(self):
        TestDirectoryCommon.setUp(self)

    def tearDown(self):
        TestDirectoryCommon.tearDown(self)

    def test_returns_false_if_path_not_hidden(self):
        """Return False if file is in a path where the directory,
        including the file itself, is hidden."""
        compare(self.dir.hidden_path, False)


class TestFile(unittest.TestCase):
    """Test sdir.File."""

    def setUp(self):
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

if __name__ == '__main__':
    unittest.main()
