#! /usr/bin/env python3.4

import unittest
import os
import ctypes
import shutil
from slib.sdir import File, CustomFile, CustomFileWithoutExtension
from testfixtures import TempDirectory, compare


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
        with self.subTest(1):
            compare(self.file_1_File.find_suitable_name(
                self.file_1_File.path), dup_file_1_name)
        self.tempdir.write(dup_file_1_name, '')
        with self.subTest(2):
            compare(self.file_1_File.find_suitable_name(
                self.file_1_File.path), 'abc - dup (2).txt')
        with self.subTest(3):
            compare(self.file_3_File.find_suitable_name(
                self.file_3_File.path), 'abc - dup (1)')

    def test_returns_false_if_relocation_without_grouping_failed(self):
        """Test returns False if file relocation failed when 
        File.move_to(group=False)."""
        self.tempdir.makedir('newfolder')
        dst = os.path.join(self.tempdir.path, 'newfolder')

        self.file_1_File.move_to(dst)
        with self.subTest(1):
            compare(self.file_1_File.path, os.path.join(dst, os.path.join(
                os.path.splitext(self.file_1_name)[1][1:].upper()), self.file_1_name))
        self.file_2_File.move_to(dst)
        with self.subTest(2):
            compare(self.file_2_File.path, os.path.join(dst, os.path.join(
                os.path.splitext(self.file_2_name)[1][1:].upper()), self.file_2_name))
        self.file_3_File.move_to(dst)
        with self.subTest(3):
            compare(self.file_3_File.path, os.path.join(
                dst, os.path.join('UNDEFINED', self.file_3_name)))
        self.file_4_File.move_to(dst)
        with self.subTest(4):
            compare(self.file_4_File.path, os.path.join(dst, os.path.join(
                os.path.splitext(self.file_4_name)[1][1:].upper()), self.file_4_name))
        self.file_5_File.move_to(dst)
        with self.subTest(5):
            compare(self.file_5_File.path, os.path.join(
                dst, os.path.join('UNDEFINED', self.file_5_name)))

    def test_returns_false_if_relocation_with_grouping_failed(self):
        """Test returns False if file relocation failed when 
        File.move_to(group=True)."""
        self.tempdir.makedir('grouping_folder')
        dst = os.path.join(self.tempdir.path, 'grouping_folder')

        self.file_1_File.move_to(dst, group=True)
        with self.subTest(1):
            compare(self.file_1_File.path, os.path.join(os.path.join(dst, self.file_1_File.category),
                                                        os.path.join(os.path.splitext(self.file_1_name)[1][1:].upper()), self.file_1_name))
        self.file_2_File.move_to(dst, group=True)
        with self.subTest(2):
            compare(self.file_2_File.path, os.path.join(os.path.join(dst, self.file_2_File.category),
                                                        os.path.join(os.path.splitext(self.file_2_name)[1][1:].upper()), self.file_2_name))
        self.file_3_File.move_to(dst, group=True)
        with self.subTest(3):
            compare(self.file_3_File.path, os.path.join(os.path.join(
                dst, self.file_3_File.category), os.path.join('UNDEFINED', self.file_3_name)))
        self.file_4_File.move_to(dst, group=True)
        with self.subTest(4):
            compare(self.file_4_File.path, os.path.join(os.path.join(dst, self.file_4_File.category),
                                                        os.path.join(os.path.splitext(self.file_4_name)[1][1:].upper()), self.file_4_name))
        self.file_5_File.move_to(dst, group=True)
        with self.subTest(5):
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
        with self.subTest(1):
            compare(self.file_1_File.path, os.path.join(dst, os.path.join(os.path.join('Sample',
                                                                                       os.path.splitext(self.file_1_name)[1][1:].upper()), self.file_1_name)))
        self.file_2_File.move_to(dst)
        with self.subTest(2):
            compare(self.file_2_File.path, os.path.join(dst, os.path.join(os.path.join('Grey Hound And An Animal',
                                                                                       os.path.splitext(self.file_2_name)[1][1:].upper()), self.file_2_name)))
        self.file_3_File.move_to(dst)
        with self.subTest(3):
            compare(self.file_3_File.path, os.path.join(dst, os.path.join(os.path.join('One 1Rt 7',
                                                                                       "UNDEFINED"), self.file_3_name)))
        self.file_4_File.move_to(dst)
        with self.subTest(4):
            compare(self.file_4_File.path, os.path.join(dst, os.path.join(os.path.join('S',
                                                                                       os.path.splitext(self.file_4_name)[1][1:].upper()), self.file_4_name)))
        self.file_5_File.move_to(dst)
        with self.subTest(5):
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
        with self.subTest(1):
            compare(self.file_1_File.path, os.path.join(
                dst, os.path.join('Sample', self.file_1_name)))
        self.file_2_File.move_to(dst)
        with self.subTest(2):
            compare(self.file_2_File.path, os.path.join(
                dst, os.path.join('Grey Hound And An Animal', self.file_2_name)))
        self.file_3_File.move_to(dst)
        with self.subTest(3):
            compare(self.file_3_File.path, os.path.join(
                dst, os.path.join('One 1Rt 7', self.file_3_name)))
        self.file_4_File.move_to(dst)
        with self.subTest(4):
            compare(self.file_4_File.path, os.path.join(
                dst, os.path.join('S', self.file_4_name)))
        self.file_5_File.move_to(dst)
        with self.subTest(5):
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
