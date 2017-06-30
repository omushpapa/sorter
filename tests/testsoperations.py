#! /usr/bin/env python3.4

import unittest
import os
import hashlib
from slib.operations import SorterOps
from slib.helpers import DatabaseHelper
from testfixtures import compare, TempDirectory
from tests.some_files import many_files, few_files
from data.settings import DATABASES, SORTER_FOLDER_IDENTITY_FILENAME, SORTER_IGNORE_FILENAME
from datetime import datetime

DB_NAME = DATABASES['default']['NAME']


class TestOperationsTestCase(unittest.TestCase):

    def setUp(self):
        self.temp = TempDirectory(encoding='utf-8')
        self.tempdir = self.temp.path
        self.DB_NAME = DB_NAME
        self.db_helper = DatabaseHelper(self.DB_NAME)
        self.operations = SorterOps(self.db_helper)

    def tearDown(self):
        self.temp.cleanup()

    def test_returns_false_if_default_not_match(self):
        with self.subTest(1):
            compare('', self.operations.src)
        with self.subTest(1):
            compare('', self.operations.dst)
        with self.subTest(1):
            compare('', self.operations.search_string)
        with self.subTest(1):
            compare('', self.operations.search_string_pattern)
        with self.subTest(1):
            compare('', self.operations.glob_pattern)
        with self.subTest(1):
            compare(False, self.operations.group)
        with self.subTest(1):
            compare(False, self.operations.recursive)
        with self.subTest(1):
            compare(['*'], self.operations.file_types)
        with self.subTest(1):
            compare(None, self.operations.status)
        with self.subTest(1):
            compare(None, self.operations.parser)
        with self.subTest(1):
            compare({}, self.operations.database_dict)

    def test_returns_false_if_search_string_pattern_not_match(self):
        search_string = 'one common 2 $ word'
        pattern = '*[oO][nN][eE]?[cC][oO][mM][mM][oO][nN]?2?$?[wW][oO][rR][dD]'
        with self.subTest(1):
            compare(pattern, self.operations.form_search_pattern(search_string))
        with self.subTest(2):
            compare('', self.operations.form_search_pattern(''))
        with self.subTest(3):
            compare('', self.operations.form_search_pattern('   '))
        with self.subTest(4):
            compare('', self.operations.form_search_pattern([]))

    @unittest.skipIf(os.name == 'nt', 'Windows systems do not have root folder')
    def test_returns_false_if_folder_if_is_writable_fails(self):
        dir_1 = self.temp.makedir('one/two')
        self.temp.makedir('three/two')
        with self.subTest(1):
            compare(True, self.operations.is_writable(dir_1))
        with self.subTest(2):
            compare(False, self.operations.is_writable('/'))

    def add_files_to_path(self, path, choice='few', start=None, end=None):
        if choice == 'few':
            file_list = few_files
        if choice == 'many':
            file_list = many_files
        paths = []
        for file_ in file_list[start:end]:
            file_path = self.temp.write(os.path.join(path, file_), '')
            paths.append(file_path.replace(path + os.sep, ''))
        return paths

    def test_returns_false_if_files_not_sorted(self):
        dir_1 = self.temp.makedir('one/two')
        self.add_files_to_path(dir_1)
        self.operations.src = dir_1
        self.operations.group = False
        self.operations.recursive = False
        with self.subTest(1):
            compare(os.path.join(self.tempdir, 'one', 'two'), dir_1)
        self.operations.sort_files()
        with self.subTest(2):
            self.temp.compare([
                '{}/'.format('JPEG'),
                '{}/'.format('PNG'),
                '{}/'.format('PHP'),
                '{}/'.format('ZIP'),
                '{}/'.format('GZ'),
                '{}/'.format('MP4'),
                '{}/'.format('APK'),
                '{}/'.format('PPTX'),
                '{}/{}'.format('JPEG',
                               'WhatsApp Image 2017-06-10 at 9.53.02 PM.jpeg'),
                '{}/{}'.format('PNG', 'unnamed.png'),
                '{}/{}'.format('PHP', 'index.php'),
                '{}/{}'.format('PHP', 'wp-settings.php'),
                '{}/{}'.format('ZIP', 'WallPaper.zip'),
                '{}/{}'.format('GZ', 'coverage-4.4.1.tar.gz'),
                '{}/{}'.format('MP4', 'Coldplay - The Scientist.mp4'),
                '{}/{}'.format('APK',
                               'GBWAPlus v5.60-2.17.146 @atnfas_hoak.apk'),
                '{}/{}'.format('PPTX',
                               'updates to www.thetruenorth.co.ke 01.pptx'),
                '{}/{}'.format('PNG',
                               'pyinstaller-draft1a-35x35-trans.png'),
                '{}/{}'.format('JPEG', SORTER_FOLDER_IDENTITY_FILENAME),
                '{}/{}'.format('PNG', SORTER_FOLDER_IDENTITY_FILENAME),
                '{}/{}'.format('PHP', SORTER_FOLDER_IDENTITY_FILENAME),
                '{}/{}'.format('ZIP', SORTER_FOLDER_IDENTITY_FILENAME),
                '{}/{}'.format('GZ', SORTER_FOLDER_IDENTITY_FILENAME),
                '{}/{}'.format('MP4', SORTER_FOLDER_IDENTITY_FILENAME),
                '{}/{}'.format('APK', SORTER_FOLDER_IDENTITY_FILENAME),
                '{}/{}'.format('PPTX', SORTER_FOLDER_IDENTITY_FILENAME),
            ], path=dir_1)

    def test_returns_false_if_files_not_sorted_by_category_with_extension(self):
        dir_1 = self.temp.makedir('one/two')
        self.add_files_to_path(dir_1)
        self.operations.src = dir_1
        # self.operations.dst =
        # self.operations.search_string =
        # self.operations.glob_pattern =
        self.operations.group = True
        self.operations.recursive = False
        self.operations.by_extension = True
        # self.operations.file_types =
        # self.operations.status =
        # self.operations.parser =
        with self.subTest(1):
            compare(os.path.join(self.tempdir, 'one', 'two'), dir_1)
        self.operations.sort_files()
        with self.subTest(2):
            self.temp.compare([
                '{}/'.format('image'),
                '{}/'.format('website'),
                '{}/'.format('archive'),
                '{}/'.format('video'),
                '{}/'.format('installer'),
                '{}/'.format('presentation'),
                '{}/{}/'.format('image', 'JPEG'),
                '{}/{}/'.format('image', 'PNG'),
                '{}/{}/'.format('website', 'PHP'),
                '{}/{}/'.format('archive', 'ZIP'),
                '{}/{}/'.format('archive', 'GZ'),
                '{}/{}/'.format('video', 'MP4'),
                '{}/{}/'.format('installer', 'APK'),
                '{}/{}/'.format('presentation', 'PPTX'),
                '{}/{}'.format('image', SORTER_FOLDER_IDENTITY_FILENAME),
                '{}/{}'.format('website',
                               SORTER_FOLDER_IDENTITY_FILENAME),
                '{}/{}'.format('archive',
                               SORTER_FOLDER_IDENTITY_FILENAME),
                '{}/{}'.format('video', SORTER_FOLDER_IDENTITY_FILENAME),
                '{}/{}'.format('installer',
                               SORTER_FOLDER_IDENTITY_FILENAME),
                '{}/{}'.format('presentation',
                               SORTER_FOLDER_IDENTITY_FILENAME),
                '{}/{}'.format('image', SORTER_IGNORE_FILENAME),
                '{}/{}'.format('website',
                               SORTER_IGNORE_FILENAME),
                '{}/{}'.format('archive',
                               SORTER_IGNORE_FILENAME),
                '{}/{}'.format('video', SORTER_IGNORE_FILENAME),
                '{}/{}'.format('installer',
                               SORTER_IGNORE_FILENAME),
                '{}/{}'.format('presentation',
                               SORTER_IGNORE_FILENAME),
                '{}/{}/{}'.format('image', 'JPEG',
                                  'WhatsApp Image 2017-06-10 at 9.53.02 PM.jpeg'),
                '{}/{}/{}'.format('image', 'PNG', 'unnamed.png'),
                '{}/{}/{}'.format('website', 'PHP', 'index.php'),
                '{}/{}/{}'.format('website', 'PHP', 'wp-settings.php'),
                '{}/{}/{}'.format('archive', 'ZIP', 'WallPaper.zip'),
                '{}/{}/{}'.format('archive', 'GZ',
                                  'coverage-4.4.1.tar.gz'),
                '{}/{}/{}'.format('video', 'MP4',
                                  'Coldplay - The Scientist.mp4'),
                '{}/{}/{}'.format('installer', 'APK',
                                  'GBWAPlus v5.60-2.17.146 @atnfas_hoak.apk'),
                '{}/{}/{}'.format('presentation', 'PPTX',
                                  'updates to www.thetruenorth.co.ke 01.pptx'),
                '{}/{}/{}'.format('image', 'PNG',
                                  'pyinstaller-draft1a-35x35-trans.png'),
                '{}/{}/{}'.format('image', 'JPEG',
                                  SORTER_FOLDER_IDENTITY_FILENAME),
                '{}/{}/{}'.format('image', 'PNG',
                                  SORTER_FOLDER_IDENTITY_FILENAME),
                '{}/{}/{}'.format('website', 'PHP',
                                  SORTER_FOLDER_IDENTITY_FILENAME),
                '{}/{}/{}'.format('archive', 'ZIP',
                                  SORTER_FOLDER_IDENTITY_FILENAME),
                '{}/{}/{}'.format('archive', 'GZ',
                                  SORTER_FOLDER_IDENTITY_FILENAME),
                '{}/{}/{}'.format('video', 'MP4',
                                  SORTER_FOLDER_IDENTITY_FILENAME),
                '{}/{}/{}'.format('installer', 'APK',
                                  SORTER_FOLDER_IDENTITY_FILENAME),
                '{}/{}/{}'.format('presentation', 'PPTX',
                                  SORTER_FOLDER_IDENTITY_FILENAME),
            ], path=dir_1)

    def test_returns_false_if_files_not_sorted_by_category_without_extension(self):
        dir_1 = self.temp.makedir('one/two')
        self.add_files_to_path(dir_1)
        self.operations.src = dir_1
        # self.operations.dst =
        # self.operations.search_string =
        # self.operations.glob_pattern =
        self.operations.group = True
        self.operations.recursive = False
        # self.operations.file_types =
        # self.operations.status =
        # self.operations.parser =
        self.operations.group_folder_name = 'sample dir'
        self.by_extension = False
        with self.subTest(1):
            compare(os.path.join(self.tempdir, 'one', 'two'), dir_1)
        self.operations.sort_files()
        with self.subTest(2):
            self.temp.compare([
                '{}/'.format('sample dir'),
                '{}/{}'.format('sample dir',
                               'WhatsApp Image 2017-06-10 at 9.53.02 PM.jpeg'),
                '{}/{}'.format('sample dir', 'unnamed.png'),
                '{}/{}'.format('sample dir', 'index.php'),
                '{}/{}'.format('sample dir', 'wp-settings.php'),
                '{}/{}'.format('sample dir', 'WallPaper.zip'),
                '{}/{}'.format('sample dir', 'coverage-4.4.1.tar.gz'),
                '{}/{}'.format('sample dir',
                               'Coldplay - The Scientist.mp4'),
                '{}/{}'.format('sample dir',
                               'GBWAPlus v5.60-2.17.146 @atnfas_hoak.apk'),
                '{}/{}'.format('sample dir',
                               'updates to www.thetruenorth.co.ke 01.pptx'),
                '{}/{}'.format('sample dir',
                               'pyinstaller-draft1a-35x35-trans.png'),
                '{}/{}'.format('sample dir',
                               SORTER_FOLDER_IDENTITY_FILENAME),
                '{}/{}'.format('sample dir',
                               SORTER_IGNORE_FILENAME),
            ], path=dir_1)

    def test_returns_false_if_database_insert_fails(self):
        path = self.temp.write('one/three/abc.txt', '')
        hash_path = hashlib.md5(path.encode('utf-8')).hexdigest()
        self.operations.db_helper.initialise_db(test=True)
        obj = self.operations.db_helper.db_file_objects.create(
            filename='abc.txt', filepath_hash=hash_path,
            last_modified=datetime.now(), added_at=datetime.now())
        with self.subTest(1):
            compare(1, obj.id)
        count = self.operations.db_helper.db_file_objects.count()
        with self.subTest(2):
            compare(1, count)

    def test_returns_false_false_if_start_fails(self):
        def messenger(*args, **kwargs):
            pass
        dir_1 = self.temp.makedir('one/two')
        paths = self.add_files_to_path(dir_1)
        expected = ['index.php', 'wp-settings.php']
        contents = [i for i in paths if os.path.basename(i) not in expected]
        self.operations.src = dir_1
        self.operations.group = False
        self.operations.recursive = False
        with self.subTest(1):
            compare(os.path.join(self.tempdir, 'one', 'two'), dir_1)
        kwargs = {
            'search_string': '',
            'file_types': ['php'],
            'group': False,
            'recursive': False,
        }
        db_ready = self.db_helper.initialise_db(test=True)
        with self.subTest(3):
            compare(True, db_ready)
        with self.subTest(4):
            compare(True, os.path.exists(self.db_helper.DB_NAME))
        self.operations.start(src=dir_1, dst=dir_1,
                              send_message=messenger, **kwargs)
        with self.subTest(5):
            self.temp.compare([
                '{}/'.format('PHP'),
                '{}/{}'.format('PHP', 'index.php'),
                '{}/{}'.format('PHP', 'wp-settings.php'),
                '{}/{}'.format('PHP', SORTER_FOLDER_IDENTITY_FILENAME),
            ] + contents, path=dir_1)

    def test_returns_false_false_if_operation_fails_group_true(self):
        def messenger(*args, **kwargs):
            pass
        dir_1 = self.temp.makedir('one/two')
        dir_2 = self.temp.makedir('three/two')
        self.add_files_to_path(dir_1, 'many')
        self.operations.src = dir_1
        self.operations.group = False
        self.operations.recursive = False
        with self.subTest(1):
            compare(os.path.join(self.tempdir, 'one', 'two'), dir_1)
        kwargs = {
            'search_string': 'whatsapp image',
            'group': True,
            'recursive': False,
        }
        db_ready = self.db_helper.initialise_db(test=True)
        with self.subTest(3):
            compare(True, db_ready)
        with self.subTest(4):
            compare(True, os.path.exists(self.db_helper.DB_NAME))
        self.operations.start(src=dir_1, dst=dir_2,
                              send_message=messenger, **kwargs)
        with self.subTest(5):
            self.temp.compare([
                '{}/'.format('whatsapp image'),
                '{}/{}'.format('whatsapp image',
                               'WhatsApp Image 2017-06-10 at 9.53.02 PM.jpeg'),
                '{}/{}'.format('whatsapp image',
                               'WhatsApp Image 2017-06-05 at 09.19.55.jpeg'),
                '{}/{}'.format('whatsapp image',
                               'WhatsApp Image 2017-06-14 at 2.26.53 PM.jpeg'),
                '{}/{}'.format('whatsapp image', 'GBWhatsApp Images.zip'),
                '{}/{}'.format('whatsapp image',
                               SORTER_FOLDER_IDENTITY_FILENAME),
                '{}/{}'.format('whatsapp image',
                               SORTER_IGNORE_FILENAME),
            ], path=dir_2)

    def test_returns_false_false_if_operation_fails_group_true_with_matching_folders(self):
        def messenger(*args, **kwargs):
            pass
        dir_1 = self.temp.makedir('one/two')
        dir_2 = self.temp.makedir('three/two')
        self.temp.makedir('one/two/new whatsapp images folder')
        self.add_files_to_path(dir_1, 'many')
        self.operations.src = dir_1
        self.operations.group = False
        self.operations.recursive = False
        with self.subTest(1):
            compare(os.path.join(self.tempdir, 'one', 'two'), dir_1)
        kwargs = {
            'search_string': 'whatsapp image',
            'group': True,
            'recursive': False,
        }
        db_ready = self.db_helper.initialise_db(test=True)
        with self.subTest(3):
            compare(True, db_ready)
        with self.subTest(4):
            compare(True, os.path.exists(self.db_helper.DB_NAME))
        self.operations.start(src=dir_1, dst=dir_2,
                              send_message=messenger, **kwargs)
        with self.subTest(5):
            self.temp.compare([
                '{}/'.format('whatsapp image'),
                '{}/{}/'.format('whatsapp image',
                                'new whatsapp images folder'),
                '{}/{}'.format('whatsapp image',
                               'WhatsApp Image 2017-06-10 at 9.53.02 PM.jpeg'),
                '{}/{}'.format('whatsapp image',
                               'WhatsApp Image 2017-06-05 at 09.19.55.jpeg'),
                '{}/{}'.format('whatsapp image',
                               'WhatsApp Image 2017-06-14 at 2.26.53 PM.jpeg'),
                '{}/{}'.format('whatsapp image', 'GBWhatsApp Images.zip'),
                '{}/{}'.format('whatsapp image',
                               SORTER_FOLDER_IDENTITY_FILENAME),
                '{}/{}'.format('whatsapp image',
                               SORTER_IGNORE_FILENAME),
            ], path=dir_2)

    def test_returns_false_if_recursive_operation_fails(self):
        def messenger(*args, **kwargs):
            pass
        dir_1 = self.temp.makedir('three/two')
        dir_2 = self.temp.makedir('one/two')
        dir_3 = self.temp.makedir('one/two/new whatsapp images folder')
        dir_4 = self.temp.makedir('one/two/new whatsapp images folder/last')
        self.add_files_to_path(dir_2, 'few', start=0, end=3)
        self.add_files_to_path(dir_3, 'few', start=3, end=6)
        self.add_files_to_path(dir_4, 'few', start=6)
        with self.subTest(1):
            compare([True, True, True, True], [os.path.isdir(dir_1),
                                               os.path.isdir(
                                                   dir_2), os.path.isdir(dir_3),
                                               os.path.isdir(dir_4)])

        kwargs = {
            'group_folder_name': 'sample dir',
            'group': True,
            'recursive': True,
        }
        self.operations.start(src=dir_2, dst=dir_1,
                              send_message=messenger, **kwargs)
        with self.subTest(2):
            self.temp.compare([
                '{}/'.format('sample dir'),
                '{}/{}'.format('sample dir',
                               'WhatsApp Image 2017-06-10 at 9.53.02 PM.jpeg'),
                '{}/{}'.format('sample dir', 'unnamed.png'),
                '{}/{}'.format('sample dir', 'index.php'),
                '{}/{}'.format('sample dir', 'wp-settings.php'),
                '{}/{}'.format('sample dir', 'WallPaper.zip'),
                '{}/{}'.format('sample dir', 'coverage-4.4.1.tar.gz'),
                '{}/{}'.format('sample dir',
                               'Coldplay - The Scientist.mp4'),
                '{}/{}'.format('sample dir',
                               'GBWAPlus v5.60-2.17.146 @atnfas_hoak.apk'),
                '{}/{}'.format('sample dir',
                               'updates to www.thetruenorth.co.ke 01.pptx'),
                '{}/{}'.format('sample dir',
                               'pyinstaller-draft1a-35x35-trans.png'),
                '{}/{}'.format('sample dir',
                               SORTER_FOLDER_IDENTITY_FILENAME),
                '{}/{}'.format('sample dir',
                               SORTER_IGNORE_FILENAME),
            ], path=dir_1)
