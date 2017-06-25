#! /usr/bin/env python3

import os
import shutil
import re
import hashlib
import ctypes
import inspect
from glob import iglob
from data.filegroups import typeGroups, typeList
from data.settings import SORTER_IGNORE_FILENAME
from pathlib import Path

def has_signore_file(path, filename=SORTER_IGNORE_FILENAME):
	try:
		open(os.path.join(path, filename), 'r').close()
	except FileNotFoundError:
		return False
	else:
		return True

class RelativePathException(Exception):
	pass

class EmptyNameException(Exception):
	pass

class Directory(object):

	def __init__(self, path):
		if not os.path.isabs(path):
			raise RelativePathException('relative paths cannot be used')
		self.Path = Path(path)
		self._path = self.Path.absolute().__str__()
		self._parent = self.Path.parent.absolute().__str__()
		self._name = self.Path.name
		self._hidden_path = self.in_hidden_path(self._path)
		self._suffix = self.Path.suffix
		self._stem = self.Path.stem
		#for item in inspect.getmembers(self.Path, predicate=inspect.ismethod):
		#   setattr(self, item[0], item[1])

	def __str__(self):
		return self.path

	@property
	def path(self):
		return self._get_path()

	@path.setter
	def path(self, value):
		self._set_path(value)

	@property
	def parent(self):
		return self._parent

	@property
	def name(self):
		return self._name

	@property
	def hidden_path(self):
		return self._hidden_path

	@property
	def suffix(self):
		return self._suffix

	@property
	def stem(self):
		return self._stem

	def _get_path(self):
		return self._path

	def _set_path(self, value):
		self.__init__(value)

	def in_hidden_path(self, full_path):
		paths = full_path.split(os.sep)

		if os.name == 'nt':
			get_hidden_attribute = ctypes.windll.kernel32.GetFileAttributesW
			for i in range(len(paths) + 1):
				path = os.sep.join(paths[:i])
				try:
					attrs = get_hidden_attribute(path)
					result = bool(attrs & 2)
				except AttributeError:
					result = False
				finally:
					if result:
						return True
		else:
			for i in range(len(paths) + 1):
				path = str(os.sep).join(paths[:i])
				base_name = os.path.basename(path)
				if base_name.startswith('.') or base_name.startswith('__'):
					return True

		return False


class File(Directory):

	default_category = 'UNDEFINED'
	filename_pattern = re.compile(r'\-\sdup[\s\(\d\)]+')

	def __init__(self, path):
		super(File, self).__init__(path)
		extension = self.Path.suffix[1:]
		self._extension = extension
		self._category = self.get_category(extension)
		self._exists = self.Path.is_file

	@property
	def extension(self):
		return self._extension

	@property
	def category(self):
		return self._category

	@property
	def exists(self):
		return self._exists()

	def get_category(self, extension):
		"""Return the category of the file instance as determined by its extension.

		Categories are determined in filegroups.py
		"""
		if extension:
			file_extension = set([extension.upper()])
			for key in typeGroups.keys():
				common = set(typeGroups[key]) & file_extension
				if common:
					return key
		return self.default_category

	def find_suitable_name(self, file_path):
		"""Validate whether a file with the same name exists, return a name
		indicating that it is a duplicate, else return the given file name.

		A fix is provided in case file renaming errors occur. Check comments.
		"""
		dirname = os.path.dirname(file_path)
		new_filename = os.path.basename(file_path)
		count = 1

		while os.path.isfile(file_path):
			new_filename = '{0} - dup ({1}){2}'.format(
				self.stem, count, self.suffix)
			file_path = os.path.join(dirname, new_filename)
			count += 1

		return new_filename

	def move_to(self, dst_root_path, group=False, by_extension=False, group_folder_name=None):
		"""Move the file instance to a location relative to the 
		specified dst_root_path.

		dst_root_path is the root folder from where files will be organised
		by their extension.

		If dst_root_path = '/home/User/'
		final destination may be 

			'/home/User/<extension>/<filename>'
			- group=False, ignore other options

			or

			'/home/User/<category>/<filename>'  
			- group=True, by_extension=False, group_folder_name=None

			or

			'/home/User/<category>/<extension>/<filename>' 
			- group=True, by_extension=True, group_folder_name=None

			or 

			'/home/User/<group_folder_name>/<filename>' 
			- group=True,by_extension=False,group_folder_name=<some name>

			or 

			'/home/User/<group_folder_name>/<extension>/<filename>' 
			- group=True,by_extension=True,group_folder_name=<some name>
		"""
		if group:
			if group_folder_name is None:
				final_dst = self._set_category_filename_dst(dst_root_path, by_extension)
			else:
				final_dst = self._set_group_folder_dst(dst_root_path, by_extension, group_folder_name)
		else:
			final_dst = self._set_extension_filename_dst(dst_root_path)

		if not os.path.dirname(self.path) == os.path.dirname(final_dst):
			try:
				shutil.move(self.path, final_dst)
			except PermissionError as e:
				print('Could not move "{0}": {1}'.format(self.path, e))
			else:
				self.path = final_dst

	def _set_group_folder_dst(self, root_path, by_extension, group_folder_name):
		if by_extension:
			group_folder_dst = os.path.join(root_path, os.path.join(
				group_folder_name, self.extension.upper()))
		else:
			group_folder_dst = os.path.join(root_path, group_folder_name)
		return self._set_final_destination(group_folder_dst)

	def _set_category_filename_dst(self, root_path, by_extension):
		if by_extension:
			category_dst = os.path.join(root_path, os.path.join(
				self.category, self.extension.upper()))
		else:
			category_dst = os.path.join(root_path, self.category)
		return self._set_final_destination(category_dst)

	def _set_extension_filename_dst(self, root_path):
		extension_dst = os.path.join(root_path, self.extension.upper())
		return self._set_final_destination(extension_dst)

	def _set_final_destination(self, parent_path):
		os.makedirs(parent_path, exist_ok=True)
		dst = os.path.join(parent_path, self.name)
		suitable_name = self.find_suitable_name(dst)
		return os.path.join(parent_path, suitable_name)
