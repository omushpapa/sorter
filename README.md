# sorter

A Python program that sorts files in a folder into folders which are named by type. It (optionally) sorts the folders created in the first sorting into categories as defined by the dictionary in [filegroups.py](https://github.com/giantas/sorter/blob/master/filegroups.py)

## Getting Started

### New - GUI

Launch GUI with 

```
python sorter.py
```

### Terminal/CMD

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

Alternatively, do
```
./sorter.py -h 
```
for more usage info.


### Prerequisites

Python 3.x (3.4 recommended)


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
```
python sorter.py D:\User\folder --types pdf docx
```

#### Note

Option --types only supported for terminal/CMD (for now).

### Authors

* **[Giantas](https://github.com/giantas)** 


### License

* This project is licensed under the BSD 3-clause "New" or "Revised" License - see the [LICENSE](LICENSE) file for details


### TODO

1. Add sorting by user provided parameter(s).
2. Add support for reversing actions.
3. Add expose function (to remove files from directories).
