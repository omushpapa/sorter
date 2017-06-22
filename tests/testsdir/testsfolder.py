#! /usr/bin/env python3.4

import unittest
import os
import ctypes
import shutil
from slib.sdir import Folder, CustomFolder, CustomFolderWithoutExtension
from testfixtures import TempDirectory, compare


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
        with self.subTest(1):
            compare(False, os.path.exists(path_4))
        with self.subTest(2):
            compare(False, folder.exists)
        folder.recreate()
        with self.subTest(3):
            compare(True, os.path.exists(path_4))
        with self.subTest(4):
            compare(True, folder.exists)

    def test_returns_false_if_folder_not_moved(self):
        temp = self.tempdir
        temp_path = self.tempdir.path
        path_1 = temp.makedir('one/two/three/four')
        path_2 = temp.makedir('one/six/ten')
        folder_1 = self.FolderClass(path_1)
        folder_2 = self.FolderClass(path_2)
        with self.subTest(1):
            compare([folder_1.exists, folder_2.exists],
                    [True, True])
        final_dst = os.path.join(path_2, os.path.join('FOLDERS', 'four'))
        folder_1.group(path_2)
        with self.subTest(2):
            compare(True, os.path.exists(os.path.join(path_2, 'FOLDERS')))
        with self.subTest(3):
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
        with self.subTest(1):
            compare(True, folder_1.exists)
        folder_1.group(path_2)
        final_path = os.path.join(path_2, self.group_folder_name.title())
        with self.subTest(2):
            compare(final_path, folder_1.path)
        with self.subTest(3):
            compare(True, folder_1.exists)


class TestCustomFolderWithoutExtension(unittest.TestCase, TestFolderCommon):

    def setUp(self):
        """Initialise temporary directory."""
        self.tempdir = TempDirectory(encoding='utf-8')
        self.group_folder_name = 'my name is a small guy'
        self.FolderClass = lambda path, group_folder_name=self.group_folder_name: CustomFolderWithoutExtension(
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
        with self.subTest(1):
            compare(True, folder_1.exists)
        folder_1.group(path_2)
        final_path = os.path.join(path_2, self.group_folder_name.title())
        with self.subTest(2):
            compare(final_path, folder_1.path)
        with self.subTest(3):
            compare(True, folder_1.exists)
