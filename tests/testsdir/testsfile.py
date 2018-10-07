#! /usr/bin/env python3.4

import unittest
import os
from testfixtures import TempDirectory, compare
from slib.sdir import File, RelativePathError, EmptyNameError


class TestFileTestCase(unittest.TestCase):

    def setUp(self):
        self.tempdir = TempDirectory(encoding='utf-8')

    def tearDown(self):
        self.tempdir.cleanup()

    def test_returns_false_if_parent_attributes_not_set(self):
        d = File(self.tempdir.path)
        with self.subTest(1):
            compare(self.tempdir.path, d.path)
        with self.subTest(2):
            compare(os.path.basename(self.tempdir.path), d.name)
        with self.subTest(3):
            compare(os.path.dirname(self.tempdir.path), d.parent)

    def test_returns_false_if_path_change_is_relative(self):
        d = File(self.tempdir.path)
        with self.subTest(1):
            compare(self.tempdir.path, d.path)
        if os.name != 'nt':
            with self.subTest(2):
                compare(False, d.hidden_path)
        with self.subTest(3):
            compare('UNDEFINED', d.default_category)

        def call(x):
            d.path = x
        self.assertRaises(RelativePathError, call, '.')

    def test_returns_false_if_attributes_not_set(self):
        file_path = self.tempdir.write('123.txt', '')
        d = File(file_path)
        with self.subTest(1):
            compare(file_path, d.path)
        if os.name != 'nt':
            with self.subTest(2):
                compare(False, d.hidden_path)
        with self.subTest(3):
            compare(os.path.basename(file_path), d.name)
        with self.subTest(4):
            compare(True, d.exists)
        with self.subTest(5):
            compare('document', d.category)
        with self.subTest(6):
            compare('txt', d.extension)
        with self.subTest(7):
            compare(d.path, str(d))

    def test_returns_false_if_names_not_match(self):
        initial_file = self.tempdir.write('123.txt', '')
        for i in range(1, 10):
            filename = '123 - dup ({}).txt'.format(str(i))
            d = File(initial_file)
            with self.subTest(i):
                compare(filename, d.find_suitable_name(initial_file))
            self.tempdir.write(os.path.join(self.tempdir.path, filename), '')

    def test_returns_false_if_pathlib_methods_fail(self):
        path = self.tempdir.makedir('abc/fig/')
        file_ = self.tempdir.write(
            os.path.join(path, 'my awesome cat.txt'), '')
        d = File(file_)
        with self.subTest(1):
            compare('.txt', d.suffix)
        with self.subTest(2):
            compare('my awesome cat', d.stem)

    def test_returns_false_if_file_moving_fails(self):
        dir_1 = self.tempdir.makedir('abc/fig/')
        dir_2 = self.tempdir.makedir('one/twp/')
        dir_3 = self.tempdir.makedir('some/dir/')
        file_ = self.tempdir.write(
            os.path.join(dir_1, 'my awesome cat.txt'), '')
        f = File(file_)
        f.move_to(dir_2, group=False)
        with self.subTest(1):
            compare(os.path.join(dir_2, 'TXT', 'my awesome cat.txt'), f.path)
        with self.subTest(2):
            compare(True, f.exists)
        f.move_to(dir_3, group=True, by_extension=True)
        with self.subTest(3):
            compare(os.path.join(dir_3, 'document',
                                 'TXT', 'my awesome cat.txt'), f.path)
        with self.subTest(4):
            compare(True, f.exists)
        with self.subTest(5):
            compare(False, os.path.isfile(os.path.join(
                dir_2, 'TXT', 'my awesome cat.txt')))

    def test_returns_false_if_grouping_by_category_fails_group_false(self):
        dir_1 = self.tempdir.makedir('abc/fig/')
        dir_2 = self.tempdir.makedir('one/twp/')
        dir_3 = self.tempdir.makedir('some/dir/')
        file_1 = self.tempdir.write(
            os.path.join(dir_1, 'my awesome cat.txt'), '')
        self.tempdir.write(os.path.join(dir_1, 'my awesome cat.txt'), '')
        self.tempdir.write(os.path.join(dir_1, '1.jpeg'), '')

        f1 = File(file_1)
        f1.move_to(dst_root_path=dir_2, group=False, by_extension=False,
                   group_folder_name=None)  # default
        with self.subTest(1):
            final_path = os.path.join(dir_2, 'TXT', 'my awesome cat.txt')
            compare(final_path, f1.path)
        f1.move_to(dst_root_path=dir_3, group=False, by_extension=False,
                   group_folder_name=None)  # default
        with self.subTest(1):
            final_path = os.path.join(dir_3, 'TXT', 'my awesome cat.txt')
            compare(final_path, f1.path)

    def test_returns_false_if_grouping_fails_group_true(self):
        dir_1 = self.tempdir.makedir('abc/fig/')
        dir_2 = self.tempdir.makedir('one/twp/')
        self.tempdir.makedir('some/dir/')
        file_1 = self.tempdir.write(
            os.path.join(dir_1, 'my awesome cat.txt'), '')
        self.tempdir.write(os.path.join(dir_1, 'my awesome cat.txt'), '')
        self.tempdir.write(os.path.join(dir_1, '1.jpeg'), '')

        f1 = File(file_1)
        f1.move_to(dst_root_path=dir_2, group=True, by_extension=False,
                   group_folder_name=None)
        with self.subTest(1):
            final_path = os.path.join(dir_2, 'document', 'my awesome cat.txt')
            compare(final_path, f1.path)

    def test_returns_false_if_grouping_fails_by_extension_true_group_folder_name_none(self):
        dir_1 = self.tempdir.makedir('abc/fig/')
        dir_2 = self.tempdir.makedir('one/twp/')
        self.tempdir.makedir('some/dir/')
        file_1 = self.tempdir.write(
            os.path.join(dir_1, 'my awesome cat.txt'), '')
        self.tempdir.write(os.path.join(dir_1, 'my awesome cat.txt'), '')
        self.tempdir.write(os.path.join(dir_1, '1.jpeg'), '')

        f1 = File(file_1)
        f1.move_to(dst_root_path=dir_2, group=True, by_extension=True,
                   group_folder_name=None)
        with self.subTest(1):
            final_path = os.path.join(
                dir_2, 'document', 'TXT', 'my awesome cat.txt')
            compare(final_path, f1.path)

    def test_returns_false_if_grouping_fails_by_extension_true_group_folder_name_given(self):
        dir_1 = self.tempdir.makedir('abc/fig/')
        dir_2 = self.tempdir.makedir('one/twp/')
        self.tempdir.makedir('some/dir/')
        file_1 = self.tempdir.write(
            os.path.join(dir_1, 'my awesome cat.txt'), '')
        self.tempdir.write(
            os.path.join(dir_1, 'my awesome cat.txt'), '')
        self.tempdir.write(
            os.path.join(dir_1, '1.jpeg'), '')

        f1 = File(file_1)
        f1.move_to(dst_root_path=dir_2, group=True, by_extension=True,
                   group_folder_name='sample dir')
        with self.subTest(1):
            final_path = os.path.join(
                dir_2, 'sample dir', 'TXT', 'my awesome cat.txt')
            compare(final_path, f1.path)

    def test_returns_false_if_grouping_fails_by_extension_false_group_folder_name_given(self):
        dir_1 = self.tempdir.makedir('abc/fig/')
        dir_2 = self.tempdir.makedir('one/twp/')
        dir_3 = self.tempdir.makedir('some/dir/')
        file_1 = self.tempdir.write(
            os.path.join(dir_1, 'my awesome cat.txt'), '')
        file_2 = self.tempdir.write(
            os.path.join(dir_1, 'my awesome cat.txt'), '')
        file_3 = self.tempdir.write(
            os.path.join(dir_1, '1.jpeg'), '')

        f1 = File(file_1)
        f1.move_to(dst_root_path=dir_2, group=True, by_extension=False,
                   group_folder_name='sample dir')
        with self.subTest(1):
            final_path = os.path.join(
                dir_2, 'sample dir', 'my awesome cat.txt')
            compare(final_path, f1.path)

    def test_returns_false_if_relocation_to_existing_child_folder_fails(self):
        dir_1 = self.tempdir.makedir('abc/fig/')
        dir_2 = self.tempdir.makedir('abc/fig/one/two')
        dir_3 = self.tempdir.makedir('abc/fig/one/two/three/')
        file_1 = self.tempdir.write(
            os.path.join(dir_1, 'my awesome cat.txt'), '')

        f1 = File(file_1)
        f1.move_to(dst_root_path=dir_2, group=True, by_extension=True,
                   group_folder_name='sample dir')
        with self.subTest(1):
            final_path = os.path.join(
                dir_2, 'sample dir', 'TXT', 'my awesome cat.txt')
            compare(final_path, f1.path)
        f1.move_to(dst_root_path=dir_3, group=True, by_extension=True,
                   group_folder_name='sample dir')
        with self.subTest(2):
            final_path = os.path.join(
                dir_3, 'sample dir', 'TXT', 'my awesome cat.txt')
            compare(final_path, f1.path)

    def test_returns_false_if_relocation_to_non_existent_folder_fails(self):
        temp_path = self.tempdir.path
        dir_1 = self.tempdir.makedir('abc/fig/')
        dir_2 = os.path.join(temp_path, 'abc', 'fig', 'one', 'two')
        dir_3 = os.path.join(temp_path, 'first', 'fig', 'one', 'two', 'three')
        file_1 = self.tempdir.write(
            os.path.join(dir_1, 'my awesome cat.txt'), '')

        f1 = File(file_1)
        f1.move_to(dst_root_path=dir_2, group=True, by_extension=True,
                   group_folder_name='sample dir')
        with self.subTest(1):
            final_path = os.path.join(
                dir_2, 'sample dir', 'TXT', 'my awesome cat.txt')
            compare(final_path, f1.path)
        f1.move_to(dst_root_path=dir_3, group=True, by_extension=True,
                   group_folder_name='sample dir')
        with self.subTest(2):
            final_path = os.path.join(
                dir_3, 'sample dir', 'TXT', 'my awesome cat.txt')
            compare(final_path, f1.path)

    def test_returns_false_if_relocation_to_parent_folder_fails(self):
        temp_path = self.tempdir.path
        dir_1 = os.path.join(temp_path, 'abc', 'fig', 'one', 'two', 'three')
        dir_2 = os.path.join(temp_path, 'abc', 'fig', 'one', 'two')
        dir_3 = os.path.join(temp_path, 'abc', 'fig')
        self.tempdir.makedir(dir_1)
        file_1 = self.tempdir.write(
            os.path.join(dir_1, 'my awesome cat.txt'), '')

        f1 = File(file_1)
        f1.move_to(dst_root_path=dir_2, group=True, by_extension=True,
                   group_folder_name='sample dir')
        with self.subTest(1):
            final_path = os.path.join(
                dir_2, 'sample dir', 'TXT', 'my awesome cat.txt')
            compare(final_path, f1.path)
        f1.move_to(dst_root_path=dir_3, group=True, by_extension=True,
                   group_folder_name='sample dir')
        with self.subTest(2):
            final_path = os.path.join(
                dir_3, 'sample dir', 'TXT', 'my awesome cat.txt')
            compare(final_path, f1.path)

    def test_returns_false_if_relocation_of_file_without_extension_fails(self):
        temp_path = self.tempdir.path
        dir_1 = os.path.join(temp_path, 'abc', 'fig', 'one', 'two', 'three')
        dir_2 = os.path.join(temp_path, 'abc', 'fig', 'one', 'two')
        dir_3 = os.path.join(temp_path, 'abc', 'fig')
        self.tempdir.makedir(dir_1)
        file_1 = self.tempdir.write(
            os.path.join(dir_1, '146 awesome street $# yea'), '')

        f1 = File(file_1)
        f1.move_to(dst_root_path=dir_2, group=True, by_extension=True,
                   group_folder_name='sample dir')
        with self.subTest(1):
            compare(True, f1.exists)
        with self.subTest(2):
            final_path = os.path.join(
                dir_2, 'sample dir', 'UNDEFINED', '146 awesome street $# yea')
            compare(final_path, f1.path)
        f1.move_to(dst_root_path=dir_3, group=False, by_extension=True,
                   group_folder_name='sample dir')
        with self.subTest(3):
            final_path = os.path.join(
                dir_3, 'UNDEFINED', '146 awesome street $# yea')
            compare(final_path, f1.path)

    def test_returns_false_if_emptynameerror_not_raised(self):
        temp_path = self.tempdir.path
        dir_1 = os.path.join(temp_path, 'abc', 'fig', 'one', 'two', 'three')
        dir_2 = os.path.join(temp_path, 'abc', 'fig', 'one', 'two')
        self.tempdir.makedir(dir_1)
        file_1 = self.tempdir.write(
            os.path.join(dir_1, 'my awesome cat.txt'), '')

        f1 = File(file_1)
        self.assertRaises(EmptyNameError, f1.move_to, dst_root_path=dir_2,
                          group=True, by_extension=True, group_folder_name=' ')

    def test_returns_false_if_file_not_created(self):
        dir_1 = self.tempdir.makedir('abc/fig/one/two/three')
        file_1 = os.path.join(dir_1, 'my awesome cat.txt')

        f1 = File(file_1)
        with self.subTest(1):
            compare(False, f1.exists)
        f1.touch()
        with self.subTest(2):
            compare(True, f1.exists)
        with self.subTest(3):
            self.assertRaises(FileExistsError, f1.touch, exist_ok=False)
