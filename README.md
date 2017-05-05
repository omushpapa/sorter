# sorter

An application that organises/sorts files in a folder into folders which are named by type. It (optionally) groups the folders created in the first sorting into categories as defined by the dictionary in [filegroups](filegroups.py)

## Usage

Launch [Sorter GUI](releases/latest)

![main screen](screenshots/Screenshot_20170505_081019.png)


Choose source folder - folder in which files should be organised

![Choose source folder](screenshots/Screenshot_20170505_081200.png)


Choose destination folder - where the files will be moved to - not required.


Select any option - sort folders or recursive or types

![Choose source folder](screenshots/Screenshot_20170505_081200.png)

![Types screen](screenshots/Screenshot_20170505_081054.png)

##### Note
If option 'types' is not checked, by default, all files will be organised/sorted.

Click Run

![Resulting groups of folders](screenshots/Screenshot_20170505_081300.png)

![Resulting folders organised by file type](screenshots/Screenshot_20170505_081329.png)

#### Alternatively

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

### Prerequisites 
#### For the installer/binary [packages](releases/latest)
None

#### For repo clone
Python 3.x (3.4 recommended)


### Authors

* **[Giantas](https://github.com/giantas)** 


### License

* This project is licensed under the BSD 3-clause "New" or "Revised" License - see the [LICENSE](LICENSE) file for details


### TODO

1. Add sorting by user provided parameter(s).
2. Add support for reversing actions.
3. Add expose function (to remove files from directories).
