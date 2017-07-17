# Sorter

[![Latest Release](https://img.shields.io/github/release/giantas/sorter.svg?maxAge=2591001)](https://github.com/giantas/sorter/releases/latest)
[![Issues](https://img.shields.io/github/issues-raw/giantas/sorter/website.svg)](https://github.com/giantas/sorter/issues)
[![Travis-CI](https://img.shields.io/travis/giantas/sorter.svg?maxAge=2592000)](https://travis-ci.org/giantas/sorter)
[![Codacy Badge](https://api.codacy.com/project/badge/Coverage/cc39b46d83564cd687bb1278f7a942b4)](https://www.codacy.com/app/giantas/sorter?utm_source=github.com&utm_medium=referral&utm_content=giantas/sorter&utm_campaign=Badge_Coverage)

Sorter makes file organisation easier. It simply helps you organise several files that contain similar characteristics into a single folder. You can put all letters documents into one folder, all images with the word home into another, all music by one artist in yet another folder, etc. 

Sorter organises these files into folders which are grouped according to one or more of the following patterns:

* A common name in multiple files' names. For example, multiple files may have a common word(s) `season one`. Every file bearing these word(s) will be moved to (by default) a folder named `season one`.
* A custom name (of your choosing). For example, after searching using the above criteria, you might choose the destination folder to be named `My Series`.
* By file type/format. For instance, pdf files will be put in a folder named PDF, docx files in a DOCX folder, jpeg files in a JPEG folder, etc.
* By categories of the file formats. For instance, pdf, docx and txt files are all documents, hence will be put in a folder named `document`. These categories are defined in [filegroups](filegroups.py)

Sorter majorly focuses on file management but most of these operations should generally apply to folders too.

> **Note:** If you want a folder and its contents to be left as is (i.e. not to be sorted or affected in any way), just add a file named `.signore` (no extension) into the folder.


## Download
Visit [Sorter](http://giantas.github.io/sorter) for features, download and usage tutorials.

**Recommended:** See the full list of supported OSes at [Sorter - Official Releases](https://github.com/giantas/sorter/releases/latest)


## Clone

### Prerequisites 
* Python 3.4
* [sqlite3](http://www.sqlite.org/download.html)
* [TestFixtures](https://testfixtures.readthedocs.io/en/latest/index.html) (for tests)

**NB**: View [requirements.txt](requirements.txt) for detailed requirements

Open terminal

*Do*

```
git clone https://github.com/giantas/sorter.git`

cd sorter

python sorter.py
```

### Compile executable DIY

#### Install Prerequisites
* Python 3.4
* [Pyinstaller](http://www.pyinstaller.org/) (tested with v3.2.1)
* [sqlite3](http://www.sqlite.org/download.html)
* [Django](https://www.djangoproject.com/download/) v1.8.x

#### How to compile
* Create and activate a [Virtual Environment](http://python-guide-pt-br.readthedocs.io/en/latest/dev/virtualenvs/) (optional but recommended)
* Ensure prerequisites are available
* Clone this repository
* In terminal/cmd, run the command in [pybuild.sh](pybuild.sh)
* Check into the `dist/` and copy the `sorter` folder to any location for use.


### Website
* **[Sorter](https://giantas.github.io/sorter)**


### Contributing

Thank you for your interest in contributing to the [Sorter](https://github.com/giantas/sorter) project. To get you started, have a look at the contribution [guidelines](CONTRIBUTING.md)


### Authors

* **[Giantas](https://github.com/giantas)** 


### License

* This project is licensed under the BSD 3-clause "New" or "Revised" License - see the [LICENSE](LICENSE) file for details


### TODO

[![Suggest new Feature](https://img.shields.io/badge/suggest-new-brightgreen.svg)](https://github.com/giantas/sorter/issues/new)

- Add search for files in history

### Warning

The coverage results exclude the GUI code. I will not write test for the GUI classes as most of the operations are separate.
