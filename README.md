# sorter

A Python script that sorts files in a folder into folders which are named by type. It (optionally) sorts the folders created in the first sorting into categories as defined by the dictionary in [filegroups.py](https://github.com/giantas/sorter/blob/master/filegroups.py)

## Getting Started

sorter.py is already executable (if not, make it executable :P )

*Do*

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

* **[Giantas](https://github.com/giantas)** 


### License

* This project is licensed under the BSD 3-clause "New" or "Revised" License - see the [LICENSE](LICENSE) file for details


### TODO

1. Add GUI
2. Add sorting by user provided parameter(s)