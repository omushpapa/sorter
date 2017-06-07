# Sorter

[![Latest Release](https://img.shields.io/github/release/giantas/sorter.svg?maxAge=2592001)](https://github.com/giantas/sorter/releases/latest)
[![Issues](https://img.shields.io/github/issues-raw/giantas/sorter/website.svg)](https://github.com/giantas/sorter/issues)
[![Travis-CI](https://img.shields.io/travis/giantas/sorter.svg?maxAge=2592000)](https://travis-ci.org/giantas/sorter)

Sorter uses a custom search to help you organise files that contain similar names into their own folder. You can put all letters documents into one folder, all images with the name home into another, all music by one artist in yet another folder, etc. 

Sorter organises these files into folders which are grouped by the file types/formats. Sorter is able to recursively look into folders and their subfolders and filter out files that are of the same type (and name). The files are then moved to a different directory and can also be categorised into groups such as audio, video, and so on, as defined in [filegroups](filegroups.py)


## Download
Visit [Sorter](http://giantas.github.io/sorter) for features, download and usage tutorials.

See the full list of supported OSes at [Sorter - Official Releases](https://github.com/giantas/sorter/releases/latest) (**recommended visit**)


## Clone

### Prerequisites 
* Python 3.x (3.4 recommended)
* [sqlite3](http://www.sqlite.org/download.html)
* [TestFixtures](https://testfixtures.readthedocs.io/en/latest/index.html) (for tests)

Open terminal

*Do*

`git clone https://github.com/giantas/sorter.git`

`cd sorter`

then 

```
python sorter.py
```

or 

```
python3 sorter.py
```


### Website
[Sorter](https://giantas.github.io/sorter)


### Authors

* **[Giantas](https://github.com/giantas)** 


### License

* This project is licensed under the BSD 3-clause "New" or "Revised" License - see the [LICENSE](LICENSE) file for details


### TODO

[![Suggest new Feature](https://img.shields.io/badge/suggest-new-brightgreen.svg)](https://saythanks.io/to/giantas)

- [x] Add progress bar

- [ ] Add reverse for operations in history 
