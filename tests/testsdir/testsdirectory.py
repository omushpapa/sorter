#! /usr/bin/env python3.4

import unittest
import os
import ctypes
import shutil
from slib.sdir import Directory
from testfixtures import TempDirectory, compare


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


@unittest.skipIf(os.name != 'nt', 'Tests can be run on Windows only')
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


@unittest.skipIf(os.name == 'nt', 'Tests can be run on UNIX only')
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
