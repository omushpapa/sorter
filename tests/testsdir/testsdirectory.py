#! /usr/bin/env python3.4

import unittest
import os
import ctypes
import shutil
from testfixtures import TempDirectory, compare
from slib.sdir import Directory, RelativePathError


class TestDirectoryTestCase(unittest.TestCase):

    def setUp(self):
        """Initialise temporary directory."""
        self.tempdir = TempDirectory(encoding='utf-8')

    def tearDown(self):
        self.tempdir.cleanup()

    def test_returns_false_if_path_not_provided(self):
        self.assertRaises(TypeError, Directory)

    def test_returns_false_if_path_provided_is_relative(self):
        self.assertRaises(RelativePathError, Directory, '.')

    @unittest.skipIf(os.name == 'nt', 'Test meant to work on UNIX systems')
    def test_returns_false_if_path_provided_is_not_windows_style(self):
        self.assertRaises(RelativePathError, Directory, 'C:/users/')

    @unittest.skipIf(os.name != 'nt', 'Test meant to work on Windows systems')
    def test_returns_false_if_path_provided_is_not_unix_style(self):
        self.assertRaises(RelativePathError,
                          Directory, '/home/User/helper/')

    def test_returns_false_if_path_not_set(self):
        d = Directory(self.tempdir.path)
        compare(self.tempdir.path, d.path)

    def test_returns_false_if_parent_path_not_returned(self):
        path = self.tempdir.path
        d = Directory(path)
        compare(os.path.dirname(path), d.parent)

    def test_returns_false_if_name_not_returned(self):
        d = Directory(self.tempdir.path)
        compare(os.path.basename(self.tempdir.path), d.name)

    def test_returns_false_if_path_not_changed(self):
        d = Directory(self.tempdir.path)
        with self.subTest(1):
            compare(self.tempdir.path, d.path)
        new_path = self.tempdir.makedir('abc')
        with self.subTest(2):
            d.path = new_path
            compare(new_path, d.path)

    def test_returns_false_if_parent_is_changed(self):
        new_parent = self.tempdir.makedir('one/one/')
        d = Directory(self.tempdir.path)
        self.assertRaises(TypeError, d.parent, new_parent)

    def test_returns_false_if_name_changed(self):
        d = Directory(self.tempdir.path)
        self.assertRaises(TypeError, d.name, 'new_name.pdf')

    @unittest.skipIf(os.name != 'nt', 'Test hidden path on Windows systems only')
    def test_returns_false_if_hidden_values_not_match_windows(self):
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
        try:
            os.makedirs(path_4)
        except FileExistsError:
            pass

        dir_1 = Directory(path_4)
        with self.subTest(1):
            compare([dir_1.path, dir_1.hidden_path], [path_4, False])

        ctypes.windll.kernel32.SetFileAttributesW(os.path.dirname(path_4), 2)
        dir_1.path = dir_1.path    # Trigger re-evaluation of instance
        with self.subTest(2):
            compare([dir_1.path, dir_1.hidden_path], [path_4, True])

        ctypes.windll.kernel32.SetFileAttributesW(os.path.dirname(path_4), 0)
        dir_1.path = dir_1.path    # Trigger re-evaluation of instance
        with self.subTest(3):
            compare([dir_1.path, dir_1.hidden_path], [path_4, False])

        ctypes.windll.kernel32.SetFileAttributesW(os.path.dirname(path_2), 2)
        dir_1.path = dir_1.path    # Trigger re-evaluation of instance
        with self.subTest(4):
            compare([dir_1.path, dir_1.hidden_path], [path_4, True])

        shutil.rmtree(path_1)

    @unittest.skipIf(os.name == 'nt', 'Test meant to run on unix systems only')
    def test_returns_false_if_hidden_values_not_match_unix(self):
        path_1 = self.tempdir.makedir('abc/.kin/one')
        path_1 = self.tempdir.write(os.path.join(path_1, 'one.docx'), '')

        path_2 = self.tempdir.makedir('abc/kin')
        path_2 = self.tempdir.write(os.path.join(path_2, '.two.tar.gz'), '')

        path_3 = self.tempdir.makedir('.yabc/kin/one')
        path_4 = self.tempdir.makedir('yabc/too/many/.paths/here/kin/one')
        path_5 = self.tempdir.makedir('typo/too/many/paths/here/kin/one')
        dir_1 = Directory(path_1)
        with self.subTest(1):
            compare(True, dir_1.hidden_path)
        dir_2 = Directory(path_2)
        with self.subTest(2):
            compare(True, dir_2.hidden_path)
        dir_3 = Directory(path_3)
        with self.subTest(3):
            compare(True, dir_3.hidden_path)
        dir_4 = Directory(path_4)
        with self.subTest(4):
            compare(True, dir_4.hidden_path)
        dir_5 = Directory(path_5)
        with self.subTest(5):
            compare(False, dir_5.hidden_path)

    @unittest.skipIf(os.name == 'nt', 'Hidden path tests for UNIX systems')
    def test_returns_false_if_attributes_are_not_reevaluated(self):
        d = Directory(self.tempdir.path)
        with self.subTest(1):
            compare(self.tempdir.path, d.path)
        with self.subTest(2):
            compare(os.path.dirname(self.tempdir.path), d.parent)
        with self.subTest(3):
            compare(False, d.hidden_path)
        new_path = self.tempdir.makedir('.abc')
        d.path = new_path
        with self.subTest(4):
            compare(new_path, d.path)
        with self.subTest(5):
            compare('.abc', d.name)
        with self.subTest(6):
            compare(True, d.hidden_path)
        with self.subTest(7):
            compare(os.path.dirname(new_path), d.parent)

    def test_returns_false_if_path_change_is_relative(self):
        d = Directory(self.tempdir.path)
        with self.subTest(1):
            compare(self.tempdir.path, d.path)
        with self.subTest(2):
            compare(False, d.hidden_path)

        def call(x):
            d.path = x
        self.assertRaises(RelativePathError, call, '.')

    def test_returns_false_if_pathlib_methods_fail(self):
        with self.subTest(1):
            path = self.tempdir.makedir('abc/fig/last')
            d = Directory(path)
            compare('', d.suffix)
            compare('last', d.stem)

        with self.subTest(2):
            path = self.tempdir.makedir('abc/fig/my awesome cat.txt')
            d = Directory(path)
            compare('.txt', d.suffix)
            compare('my awesome cat', d.stem)
