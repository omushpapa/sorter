SHORT_DESCRIPTION = "Sorter organises/sorts files using a customised search function to group those that have similar characteristics into a single folder. Similar characteristics include file type, file name or part of the name and file category. You can put all letters documents into one folder, all images with the word home into another, all music by one artist in yet another folder, etc."
SOURCE_DESCRIPTION = "SOURCE (required)\nThis is the folder in which the sorting should be done i.e the folder containing the disorganised files."
DESTINATION_DESCRIPTION = "DESTINATION (optional)\nAn optional destination (a folder) where the user would want the sorted files/folders to be moved to."
RECURSIVE_DESCRIPTION = "LOOK INTO SUB-FOLDERS (optional)\nChecks into every child folder, starting from the source folder, and groups/sorts the files accordingly."
TYPES_DESCRIPTION = "SELECT FILE TYPES (optional)\nSelect the specific file types/formats to be sorted."
SEARCH_DESCRIPTION = "SEARCH FOR (optional)\nDirects Sorter to search and only group files with names containing this value. If this is enabled then, by default, Sort Folders option is enabled to enable the sorted files to be moved to a folder whose name will be the value provided here. The search is case-insensitive but the final folder will adopt the case styles."
GROUP_FOLDER_DESCRIPTION = "GROUP INTO FOLDER (optional)\nMoves all files (and folders) fitting the search descriptions into a folder named by the value provided in this option."
BY_EXTENSION_DESCRIPTION = "GROUP BY FILE TYPE (optional)\nGroups files in the destination and according to their file type. That is, all JPGs different from PDFs different from DOCXs."
CLEANUP_DESCRIPTION = "PERFORM CLEANUP (optional)\nLooks into the child folders of the source folder and removes those which are empty."
NOTE = "Note:\nIf you want a folder and its contents to be left as is (i.e. not to be sorted or affected in any way), just add a file named `.signore` (no extension) into the folder."
HELP_MESSAGE = "How it Works \n" + SHORT_DESCRIPTION + "\n\nBelow is a description of the fields required to achieve results using Sorter:\n\n" + SOURCE_DESCRIPTION + "\n\n" + DESTINATION_DESCRIPTION + \
    "\n\n" + SEARCH_DESCRIPTION + "\n\n" + RECURSIVE_DESCRIPTION + \
    "\n\n" + TYPES_DESCRIPTION + "\n\n" + \
    GROUP_FOLDER_DESCRIPTION + "\n\n" + BY_EXTENSION_DESCRIPTION + "\n\n" + CLEANUP_DESCRIPTION + \
    "\n\n" + NOTE
COPYRIGHT_MESSAGE = "Copyright \u00a9 2017\n\nAswa Paul\nAll rights reserved.\n\n"
HOMEPAGE = "https://giantas.github.io/sorter"
SOURCE_CODE = "https://github.com/giantas/sorter"
LICENSE = """BSD 3-Clause License

Copyright (c) 2017, Aswa Paul
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* Neither the name of the copyright holder nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
