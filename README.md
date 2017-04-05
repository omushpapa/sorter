# sorter

A Python script that checks file types in a folder and sorts them into folders named by type. It (optionally) sorts the folders created in the first sorting into categories as defines by the dictionary in filegroups.py

## Getting Started

sorter.py is already executable
git clone https://github.com/giantas/sorter.git
cd sorter

then 

```
python sorter.py (source folder path)
```

or

```
./sorter.py (source folder path)
```

### Prerequisites

Developed for python3.4 but should work on any version

### WARNING

* Do **NOT** use on folder that has your precious hidden files, the likes of local git repositories. 


### Examples
```
./sorter.py /home/User/Downloads
```
```
python sorter.py D:\User\folder -d E:\newfolder
```
```
./sorter.py /home/User/Downloads --sort-folders
```

### Authors

* **Aswa Paul** 


### License

* This project is licensed under the BSD 3-clause "New" or "Revised" License - see the [LICENSE](LICENSE) file for details


