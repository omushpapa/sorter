# Sorter

[![Latest Release](https://img.shields.io/github/release/giantas/sorter.svg?maxAge=2592000)](https://github.com/giantas/sorter/releases/latest)
[![Issues](https://img.shields.io/github/issues-raw/giantas/sorter/website.svg)](https://github.com/giantas/sorter/issues)
[![Say Thanks](https://img.shields.io/badge/Say%20Thanks-!-blue.svg)](https://saythanks.io/to/giantas)
[![Telegram Channel](https://img.shields.io/badge/channel-Telegram-blue.svg)](https://t.me/giantas_sorter)


An application that organises/sorts files in a folder into folder-groups named by type. It (optionally) groups the folders created in the first sorting into categories as defined in [filegroups](filegroups.py)


## Download
[![SourceForge](https://img.shields.io/sourceforge/dm/file-sorter.svg)](http://file-sorter.sourceforge.io)
[![Github Latest Downloads](https://img.shields.io/github/downloads/giantas/sorter/latest/total.svg)](https://github.com/giantas/sorter/releases/latest)


Download from [Sorter - SourceForge](http://file-sorter.sourceforge.io)

For specific OS versions (*recommended visit*), go to [Sorter - Official Releases](https://github.com/giantas/sorter/releases/latest)


## New Features Added
* Search for file with names you only want e.g. enter "letter" into the search box and only files containing the word "letter" will be organised. What's more is that they will all be moved to a folder named "Letter".
	__This is an advantage for organising your songs, movies, etc__
* Undo (reverse) is now possible. You can undo any unwanted file relocation!
* Check for updates. Automatically check for updates any time your are connected to the Internet.
* And many [more](releases/latest)...


## Usage

Launch [Sorter GUI](releases/latest)

![main screen](screenshots/Screenshot_20170523_101454.png)


Choose source folder - folder in which files should be organised

![Choose source folder - New Screen](screenshots/Screenshot_20170523_104128.png)


Choose destination folder - where the files will be moved to - not required.


Select any (or all) option(s) - sort folders; recursive; types:

	* Sort folder - groups the file type folders into categories of audio, video, etc.

	* Recursive - checks inside folders and their subfolders for any files and organises them relative to the source folder.

	* Type - allows a user to select specific file types/format to be organised/sorted.

	* Search - enter the name to search for in the ajdacent box. Only files with this name will be organised/Sorted.

![Choose option(s)](screenshots/Screenshot_20170523_102607.png)

##### Types screen
![Types screen](screenshots/Screenshot_20170505_081054.png)


##### Note

If option 'types' is not checked, by default, all files will be organised/sorted.


##### Click Run


*Resulting Folder*
![Results](screenshots/Screenshot_20170523_101656.png)

*Resulting grouping*
![Resulting organisation](screenshots/Screenshot_20170523_101719.png)


#### Other screenshots 

##### New - Undo 
![Undo specific or all actions](screenshots/Screenshot_20170523_101746.png)


##### New - Update check 
![Update window](screenshots/Screenshot_20170523_101843.png)


##### When "search" is not included

![Resulting groups of folders](screenshots/Screenshot_20170505_081300.png)

![Resulting folders organised by file type](screenshots/Screenshot_20170505_081329.png)


#### Alternatively - clone repo

*Do*

git clone https://github.com/giantas/sorter.git

cd sorter

then 

```
python sorter.py
```

or 

```
python3 sorter.py
```

Then follow the GUI steps listed above.

## Warning
You should have access (read) and *write* permissions on the source and destination folders.
*Be careful* not to use sorter on application folders. ~~Sorter actions are *NOT* reversible (for now).~~
Sorter actions are now reversible.

### Prerequisites 
#### For the installer/binary [packages](releases/latest)
* None

#### For repo clone
* Python 3.x (3.4 recommended)
* [sqlite3](http://www.sqlite.org/download.html)


### Authors

* **[Giantas](https://github.com/giantas)** 


### License

* This project is licensed under the BSD 3-clause "New" or "Revised" License - see the [LICENSE](LICENSE) file for details


### TODO

[![Suggest new Feature](https://img.shields.io/badge/suggest-new-brightgreen.svg)](https://saythanks.io/to/giantas)
