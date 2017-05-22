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

For specific OS versions, go to [Sorter - Official Releases](https://github.com/giantas/sorter/releases/latest)


## Usage

Launch [Sorter GUI](releases/latest)

![main screen](screenshots/Screenshot_20170505_081019.png)


Choose source folder - folder in which files should be organised

![Choose source folder](screenshots/Screenshot_20170505_081200.png)


Choose destination folder - where the files will be moved to - not required.


Select any (or all) option(s) - sort folders; recursive; types:

	* Sort folder - groups the file type folders into categories of audio, video, etc.

	* Recursive - checks inside folders and their subfolders for any files and organises them relative to the source folder.

	* Type - allows a user to select specific file types/format to be organised/sorted.

![Choose option(s)](screenshots/Screenshot_20170505_081200.png)

![Types screen](screenshots/Screenshot_20170505_081054.png)

##### Note
If option 'types' is not checked, by default, all files will be organised/sorted.

##### Click Run

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
*Be careful* not to use sorter on application folders. Sorter actions are *NOT* reversible (for now).

### Prerequisites 
#### For the installer/binary [packages](releases/latest)
* None

#### For repo clone
* Python 3.x (3.4 recommended)


### Authors

* **[Giantas](https://github.com/giantas)** 


### License

* This project is licensed under the BSD 3-clause "New" or "Revised" License - see the [LICENSE](LICENSE) file for details


### TODO

1. Add sorting by user provided parameter(s).
2. Add support for reversing actions.
3. Add expose function (to remove files from directories).
