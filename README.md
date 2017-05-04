# sorter

A Python application that sorts files in a folder into folders which are named by type. It (optionally) sorts the folders created in the first sorting into categories as defined by the dictionary in [filegroups.py](https://github.com/giantas/sorter/blob/master/filegroups.py)

## Getting Started

### New - GUI

Launch GUI with 

```
python sorter.py
```

Or better yet, install program using the latest [package](https://github.com/giantas/sorter/releases)

### ~~Terminal/CMD~~ (since 1.0.5)

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

or 

Use [GUI](https://github.com/giantas/sorter/releases)


### Prerequisites 
#### None (for the installer [packages](https://github.com/giantas/sorter/releases))

#### For repo clone
Python 3.x (3.4 recommended)


#### Note

~~Option --types only supported for terminal/CMD (for now)~~ Working.

### Authors

* **[Giantas](https://github.com/giantas)** 


### License

* This project is licensed under the BSD 3-clause "New" or "Revised" License - see the [LICENSE](LICENSE) file for details


### TODO

1. Add sorting by user provided parameter(s).
2. Add support for reversing actions.
3. Add expose function (to remove files from directories).
