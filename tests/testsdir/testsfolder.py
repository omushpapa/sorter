#! /usr/bin/env python3.4

import unittest
import os
import ctypes
import shutil
from testfixtures import TempDirectory, compare
from slib.sdir import Folder, RelativePathException, EmptyNameException
from data.settings import SORTER_FOLDER_IDENTITY_FILENAME, SORTER_IGNORE_FILENAME


class TestFolderTestCase(unittest.TestCase):

    def setUp(self):
        self.tempdir = TempDirectory(encoding='utf-8')

    def tearDown(self):
        self.tempdir.cleanup()

    def test_returns_false_if_parent_attributes_not_set(self):
        d = Folder(self.tempdir.path)
        with self.subTest(1):
            compare(self.tempdir.path, d.path)
        with self.subTest(2):
            compare(os.path.basename(self.tempdir.path), d.name)
        with self.subTest(3):
            compare(os.path.dirname(self.tempdir.path), d.parent)

    def test_returns_false_if_attributes_are_not_equal(self):
        temp_path = self.tempdir.path
        dir_1 = Folder(temp_path)
        dir_2 = Folder(self.tempdir.makedir('abc/123/JPG'))
        dir_3 = Folder(self.tempdir.makedir('abc/&%^/website'))
        d4 = self.tempdir.makedir('abc/123/ghi')
        d5 = Folder(os.path.join(temp_path, 'abc', 'hjig'))
        sorter_identity = self.tempdir.write(
            os.path.join(d4, SORTER_FOLDER_IDENTITY_FILENAME), '')
        dir_4 = Folder(d4)
        with self.subTest(1):
            compare(True, dir_1.exists)
        with self.subTest(2):
            compare(False, dir_1.for_sorter)
        with self.subTest(3):
            compare('FOLDERS', dir_1.category_folder)
        with self.subTest(4):
            compare(True, dir_2.for_sorter)
        with self.subTest(5):
            compare('image', dir_2.category_folder)
        with self.subTest(6):
            compare(True, dir_3.for_sorter)
        with self.subTest(7):
            compare(None, dir_3.category_folder)
        with self.subTest(8):
            compare('FOLDERS', dir_4.category_folder)
        with self.subTest(9):
            compare(True, os.path.isfile(sorter_identity))
        with self.subTest(10):
            compare(True, dir_4.for_sorter)
        with self.subTest(11):
            compare(False, d5.for_sorter)

    def test_returns_false_if_folder_not_exists(self):
        temp_path = self.tempdir.path
        path = os.path.join(temp_path, 'bdk/ksks/a94')
        dir_1 = Folder(path)
        with self.subTest(1):
            compare(False, dir_1.exists)
        with self.subTest(2):
            self.assertRaises(FileNotFoundError, dir_1.create)
        with self.subTest(3):
            compare(False, dir_1.exists)
        dir_1.create(parents=True)
        with self.subTest(4):
            compare(True, dir_1.exists)

    def test_returns_false_if_grouping_failed(self):
        temp_path = self.tempdir.path
        dir_1 = self.tempdir.makedir('abc/for/document')
        dir_2 = self.tempdir.makedir('abc/for/PDF')
        dir_3 = self.tempdir.makedir('abc/for/last')
        dir_ = self.tempdir.makedir('one/two')
        d1 = Folder(dir_1)
        d2 = Folder(dir_2)
        d3 = Folder(dir_3)
        with self.subTest(1):
            compare(dir_1, d1.path)
        d1.move_to(dir_)
        with self.subTest(2):
            compare(os.path.join(dir_, 'document'), d1.path)

        with self.subTest(3):
            compare(dir_2, d2.path)
        d2.move_to(dir_)
        with self.subTest(4):
            compare(os.path.join(dir_, 'document', 'PDF'), d2.path)

        with self.subTest(5):
            compare(dir_3, d3.path)
        d3.move_to(dir_)
        with self.subTest(6):
            compare(os.path.join(dir_, 'FOLDERS', 'last'), d3.path)

    def test_folder_grouping_with_files(self):
        temp_path = self.tempdir.path
        write = lambda path: self.tempdir.write(path, '')
        isfile = os.path.isfile
        dir_ = self.tempdir.makedir('one/two')
        file_1 = write('abc/for/PDF/this long name.pdf')
        file_2 = write('abc/for/DOCX/y.docx')
        file_3 = write('abc/for/DOC/123 54.doc')
        file_4 = write('abc/for/none/xw')
        file_5 = write('abc/for/PDF/second.pdf')

        dir_1 = Folder(os.path.dirname(file_1))
        dir_2 = Folder(os.path.dirname(file_2))
        dir_3 = Folder(os.path.dirname(file_3))
        dir_4 = Folder(os.path.dirname(file_4))
        dir_5 = Folder(os.path.dirname(file_5))
        dir_6 = Folder(dir_)

        with self.subTest(1):
            compare([True, True, True, True],
                    [isfile(file_1), isfile(file_2), isfile(file_3), isfile(file_4)])
        dir_1.move_to(dir_)
        dir_2.move_to(dir_)
        dir_3.move_to(dir_)
        dir_4.move_to(dir_)
        dir_5.move_to(dir_)
        dir_6.move_to(dir_)
        with self.subTest(3):
            self.tempdir.compare([
                '{}/'.format('document'),
                '{}/'.format('FOLDERS'),
                '{}/{}'.format('document', SORTER_FOLDER_IDENTITY_FILENAME),
                '{}/{}'.format('FOLDERS', SORTER_FOLDER_IDENTITY_FILENAME),
                '{}/{}/'.format('document', 'PDF'),
                '{}/{}/'.format('document', 'DOCX'),
                '{}/{}/'.format('document', 'DOC'),
                '{}/{}/'.format('FOLDERS', 'none'),
                '{}/{}/{}'.format('document', 'PDF',
                                              'this long name.pdf'),
                '{}/{}/{}'.format('document', 'PDF', 'second.pdf'),
                '{}/{}/{}'.format('document', 'DOCX', 'y.docx'),
                '{}/{}/{}'.format('document', 'DOC', '123 54.doc'),
                '{}/{}/{}'.format('FOLDERS', 'none', 'xw'),
                '{}/{}/{}'.format('document', 'PDF',
                                  SORTER_FOLDER_IDENTITY_FILENAME),
                '{}/{}/{}'.format('document', 'DOCX',
                                  SORTER_FOLDER_IDENTITY_FILENAME),
                '{}/{}/{}'.format('document', 'DOC',
                                  SORTER_FOLDER_IDENTITY_FILENAME),
            ], path=dir_)
        with self.subTest(4):
            compare(os.path.join(dir_, 'document', 'PDF'), dir_5.path)

    def test_folder_grouping_with_files_and_existing_destinations(self):
        temp_path = self.tempdir.path
        write = lambda path: self.tempdir.write(path, '')
        isfile = os.path.isfile
        dir_ = self.tempdir.makedir('one/two')
        self.tempdir.makedir('one/two/document/PDF/')
        self.tempdir.makedir('one/two/document/DOCX')
        self.tempdir.makedir('one/two/document/DOC')
        file_1 = write('abc/for/PDF/this long name.pdf')
        file_2 = write('abc/for/DOCX/y.docx')
        file_3 = write('abc/for/DOC/123 54.doc')
        file_4 = write('abc/for/none/xw')
        file_5 = write('abc/for/PDF/second.pdf')
        file_6 = write('abc/for/image/JPEG/abc.jpeg')

        dir_1 = Folder(os.path.dirname(file_1))
        dir_2 = Folder(os.path.dirname(file_2))
        dir_3 = Folder(os.path.dirname(file_3))
        dir_4 = Folder(os.path.dirname(file_4))
        dir_5 = Folder(os.path.dirname(file_5))
        dir_6 = Folder(os.path.dirname(os.path.dirname(file_6)))
        dir_7 = Folder(dir_)

        with self.subTest(1):
            compare([True, True, True, True],
                    [isfile(file_1), isfile(file_2), isfile(file_3), isfile(file_4)])
        with self.subTest(2):
            compare('document', dir_1.category_folder)
        dir_1.move_to(dir_)
        dir_2.move_to(dir_)
        dir_3.move_to(dir_)
        dir_4.move_to(dir_)
        dir_5.move_to(dir_)
        dir_6.move_to(dir_)
        dir_7.move_to(dir_)
        with self.subTest(3):
            compare(True, dir_1.for_sorter)

        with self.subTest(4):
            self.tempdir.compare([
                '{}/'.format('document'),
                '{}/'.format('image'),
                '{}/'.format('FOLDERS'),
                '{}/{}/'.format('document', 'PDF'),
                '{}/{}/'.format('document', 'DOCX'),
                '{}/{}/'.format('document', 'DOC'),
                '{}/{}/'.format('image', 'JPEG'),
                '{}/{}/'.format('FOLDERS', 'none'),
                '{}/{}'.format('document', SORTER_FOLDER_IDENTITY_FILENAME),
                '{}/{}'.format('image', SORTER_FOLDER_IDENTITY_FILENAME),
                '{}/{}'.format('FOLDERS', SORTER_FOLDER_IDENTITY_FILENAME),
                '{}/{}/{}'.format('document', 'PDF',
                                              'this long name.pdf'),
                '{}/{}/{}'.format('document', 'PDF', 'second.pdf'),
                '{}/{}/{}'.format('document', 'DOCX', 'y.docx'),
                '{}/{}/{}'.format('document', 'DOC', '123 54.doc'),
                '{}/{}/{}'.format('image', 'JPEG', 'abc.jpeg'),
                '{}/{}/{}'.format('FOLDERS', 'none', 'xw'),
                '{}/{}/{}'.format('document', 'PDF',
                                  SORTER_FOLDER_IDENTITY_FILENAME),
                '{}/{}/{}'.format('document', 'DOCX',
                                  SORTER_FOLDER_IDENTITY_FILENAME),
                '{}/{}/{}'.format('document', 'DOC',
                                  SORTER_FOLDER_IDENTITY_FILENAME),
            ], path=dir_)

        with self.subTest(5):
            compare(os.path.join(dir_, 'document', 'PDF'), dir_5.path)
        with self.subTest(6):
            compare(True, os.path.isdir(dir_1.path))
        with self.subTest(7):
            compare(os.path.join(temp_path, dir_, 'document', 'PDF'), dir_1.path)
        with self.subTest(8):
            compare(True, os.path.isfile(os.path.join(
                dir_1.path, SORTER_FOLDER_IDENTITY_FILENAME)))
        with self.subTest(9):
            compare(False, os.path.exists(os.path.dirname(file_1)))

    def test_retuns_false_folder_with_multiple_subfolders_relocation_failse(self):
        temp_path = self.tempdir.path
        write = lambda path: self.tempdir.write(path, '')
        isfile = os.path.isfile
        dir_ = self.tempdir.makedir('one/two')
        self.tempdir.makedir('one/two/document/PDF/')
        file_1 = write('abc/for/PDF/this long name.pdf')
        file_2 = write(
            'abc/for/PDF/somefolder/another/and another/JPEG/abc.jpeg')

        dir_1 = Folder(os.path.dirname(file_1))
        dir_1.move_to(dir_)
        with self.subTest(1):
            self.tempdir.compare([
                '{}/'.format('document'),
                '{}/{}'.format('document', SORTER_FOLDER_IDENTITY_FILENAME),
                '{}/{}/'.format('document', 'PDF'),
                '{}/{}/{}'.format('document', 'PDF',
                                  SORTER_FOLDER_IDENTITY_FILENAME),
                '{}/{}/{}/'.format('document', 'PDF', 'somefolder'),
                '{}/{}/{}'.format('document', 'PDF', 'this long name.pdf'),
                '{}/{}/{}/{}/'.format('document', 'PDF',
                                      'somefolder', 'another'),
                '{}/{}/{}/{}/{}/'.format('document', 'PDF',
                                         'somefolder', 'another', 'and another'),
                '{}/{}/{}/{}/{}/{}/'.format('document', 'PDF',
                                            'somefolder', 'another', 'and another', 'JPEG'),
                '{}/{}/{}/{}/{}/{}/{}'.format('document', 'PDF', 'somefolder',
                                              'another', 'and another', 'JPEG', 'abc.jpeg'),
            ], path=dir_)

    def test_returns_false_if_folder_relocation_with_ignore_file_succeeds(self):
        temp_path = self.tempdir.path
        write = lambda path: self.tempdir.write(path, '')
        isfile = os.path.isfile
        dir_ = self.tempdir.makedir('one/two')
        dir_2 = self.tempdir.makedir('one/two/document/PDF/')
        file_1 = write('abc/for/PDF/this long name.pdf')
        file_2 = write(
            'abc/for/PDF/somefolder/another/and another/JPEG/abc.jpeg')
        file_3 = write('abc/for/PDF/somefolder/%s' % SORTER_IGNORE_FILENAME)

        with self.subTest(1):
            compare(True, os.path.isfile(file_3))

        with self.subTest(2):
            compare(True, os.path.isdir(os.path.dirname(file_2)))
        dir_1 = Folder(os.path.dirname(file_1))
        dir_1.move_to(dir_)
        with self.subTest(3):
            self.tempdir.compare([
                '{}/'.format('document'),
                '{}/{}'.format('document', SORTER_FOLDER_IDENTITY_FILENAME),
                '{}/{}/'.format('document', 'PDF'),
                '{}/{}/{}'.format('document', 'PDF',
                                  SORTER_FOLDER_IDENTITY_FILENAME),
                '{}/{}/{}'.format('document', 'PDF', 'this long name.pdf'),
            ], path=dir_)

    def test_returns_false_if_original_folder_exists(self):
        temp_path = self.tempdir.path
        write = lambda path: self.tempdir.write(path, '')
        isfile = os.path.isfile
        dir_ = self.tempdir.makedir('one/two')
        dir_2 = self.tempdir.makedir('one/two/document/PDF/')
        file_1 = write('abc/for/PDF/this long name.pdf')

        dir_1 = Folder(os.path.dirname(file_1))
        dir_1.move_to(dir_)
        with self.subTest(1):
            self.tempdir.compare([
                '{}/'.format('document'),
                '{}/{}'.format('document', SORTER_FOLDER_IDENTITY_FILENAME),
                '{}/{}/'.format('document', 'PDF'),
                '{}/{}/{}'.format('document', 'PDF',
                                  SORTER_FOLDER_IDENTITY_FILENAME),
                '{}/{}/{}'.format('document', 'PDF', 'this long name.pdf'),
            ], path=dir_)

        with self.subTest(2):
            compare(False, os.path.isdir(os.path.dirname(file_1)))

    def test_returns_false_if_original_folder_not_exists(self):
        temp_path = self.tempdir.path
        write = lambda path: self.tempdir.write(path, '')
        isfile = os.path.isfile
        dir_ = self.tempdir.makedir('one/two')
        dir_2 = self.tempdir.makedir('one/two/document/PDF/')
        file_1 = write('abc/for/PDF/this long name.pdf')
        file_2 = write(
            'abc/for/PDF/somefolder/another/and another/JPEG/abc.jpeg')
        file_3 = write('abc/for/PDF/somefolder/%s' % SORTER_IGNORE_FILENAME)

        with self.subTest(1):
            compare(True, os.path.isfile(file_3))

        with self.subTest(2):
            compare(True, os.path.isdir(os.path.dirname(file_2)))
        dir_1 = Folder(os.path.dirname(file_1))
        dir_1.move_to(dir_)
        with self.subTest(3):
            self.tempdir.compare([
                '{}/'.format('document'),
                '{}/{}'.format('document', SORTER_FOLDER_IDENTITY_FILENAME),
                '{}/{}/'.format('document', 'PDF'),
                '{}/{}/{}'.format('document', 'PDF',
                                  SORTER_FOLDER_IDENTITY_FILENAME),
                '{}/{}/{}'.format('document', 'PDF', 'this long name.pdf'),
            ], path=dir_)

        with self.subTest(4):
            compare(True, os.path.isdir(dir_2))

    def test_returns_false_if_grouping_in_same_folder_failed(self):
        temp_path = self.tempdir.path
        write = lambda path: self.tempdir.write(path, '')
        isfile = os.path.isfile
        dir_ = self.tempdir.makedir('one/two')
        file_1 = write('one/two/PDF/this long name.pdf')
        file_2 = write(
            'one/two/PDF/somefolder/another/and another/JPEG/abc.jpeg')
        file_3 = write('one/two/PDF/somefolder/%s' % SORTER_IGNORE_FILENAME)

        with self.subTest(1):
            compare(True, os.path.isfile(file_3))

        with self.subTest(2):
            compare(True, os.path.isdir(os.path.dirname(file_2)))
        dir_1 = Folder(os.path.dirname(file_1))
        dir_1.group(dir_, by_extension=True)
        with self.subTest(3):
            compare(True, os.path.isfile(os.path.join(temp_path, 'one',
                                                      'two', 'document', 'PDF', SORTER_FOLDER_IDENTITY_FILENAME)))
        with self.subTest(4):
            self.tempdir.compare([
                '{}/'.format('document'),
                '{}/'.format('PDF'),
                '{}/{}'.format('document', SORTER_FOLDER_IDENTITY_FILENAME),
                '{}/{}/'.format('document', 'PDF'),
                '{}/{}/{}'.format('document', 'PDF',
                                  SORTER_FOLDER_IDENTITY_FILENAME),
                '{}/{}/{}'.format('document', 'PDF', 'this long name.pdf'),
                '{}/{}/'.format('PDF', 'somefolder'),
                '{}/{}/{}'.format('PDF', 'somefolder', SORTER_IGNORE_FILENAME),
                '{}/{}/{}/'.format('PDF', 'somefolder', 'another'),
                '{}/{}/{}/{}/'.format('PDF', 'somefolder',
                                      'another', 'and another'),
                '{}/{}/{}/{}/{}/'.format('PDF', 'somefolder',
                                         'another', 'and another', 'JPEG'),
                '{}/{}/{}/{}/{}/{}'.format('PDF', 'somefolder',
                                           'another', 'and another', 'JPEG', 'abc.jpeg')
            ], path=dir_)

        with self.subTest(5):
            compare(True, os.path.isdir(os.path.dirname(file_1)))
