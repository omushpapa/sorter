SHORT_DESCRIPTION = "Sorter organises/sorts files in a folder into folders which are grouped by type e.g pdf, docx. It (optionally) groups/sorts the folders created in the first sorting into categories e.g audio, video."
SOURCE_DESCRIPTION = "SOURCE (required)\nThis is the folder in which the sorting should be done i.e the folder containing the disorganised files."
DESTINATION_DESCRIPTION = "DESTINATION (optional)\nAn optional destination (a folder) where the user would want the sorted files/folders to be moved to."
RECURSIVE_DESCRIPTION = "LOOK INTO SUB-FOLDERS (optional)\nChecks into every child folder, starting from the source folder, and groups/sorts the files accordingly."
TYPES_DESCRIPTION = "\SELECT FILE TYPES (optional)\nSelect the specific file types/formats to be sorted."
SEARCH_DESCRIPTION = "SEARCH FOR (optional)\nDirects Sorter to search and only group files with names containing this value. If this is enabled then, by default, Sort Folders option is enabled to enable the sorted files to be moved to a folder whose name will be the value provided here."
GROUP_FOLDER_DESCRIPTION = "GROUP INTO FOLDER (optional)\nMoves all files (and folders) fitting the search descriptions into a folder named by the value provided in this option."
BY_EXTENSION_DESCRIPTION = "GROUP BY FILE TYPE (optional)\nGroups files in the destination and according to their file type. That is, all JPGs different from PDFs different from DOCXs."
HELP_MESSAGE = "How it Works \n" + SHORT_DESCRIPTION + "\n\n" + SOURCE_DESCRIPTION + "\n\n" + DESTINATION_DESCRIPTION + \
    "\n\n" + SEARCH_DESCRIPTION + "\n\n" + RECURSIVE_DESCRIPTION + \
    "\n\n" + TYPES_DESCRIPTION + "\n\n" + GROUP_FOLDER_DESCRIPTION + "\n\n" + BY_EXTENSION_DESCRIPTION
COPYRIGHT_MESSAGE = "Copyright \u00a9 2017\n\nAswa Paul\nAll rights reserved.\n\nFor more information click"
HOMEPAGE = "https://giantas.github.io/sorter"