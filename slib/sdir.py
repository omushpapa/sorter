#! /usr/bin/env python3

import os
import shutil
import re
import hashlib
import ctypes
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

PathObject = type(Path())

class RelativePathException(Exception):
	pass

class Directory(PathObject):

	def __init__(self, path):
		if not os.path.isabs(path):
			raise RelativePathException('absolute path required')
		self._path = path
		self._parent = super(Directory, self).parent.resolve().__str__()
		self._name = os.path.basename(self._path)
		self._hidden_path = self.in_hidden_path(self._path)

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

	def _get_path(self):
		return self._path

	def _set_path(self, value):
		d = Directory(value)
		self._path = d.path
		self._parent = d.parent
		self._name = d.name
		self._hidden_path = d.hidden_path

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

