This is a map analyzer for [Space Station 14](github.com/space-wizards/space-station-14) maps. I wrote it mostly to satisfy my own curiousity about some things, so it is very rough.

## Usage

Settings that are in the python file that should probably be elsewhere:
* Filenames to ignore
* Proto ID prefixes to group entities by
* Entities and groups to calculate density per 1000 tiles for

To run it, specify a map file or directory with map files as the first command line argument. If you specify a directory, the analyzer will read all the non-ignored files in the directory but it will not recurse into subdirectories.

The output is CSV on stdout; you should generally redirect it to a file.

Example:
```python3 ss14_map_analyzer space-station-14/Resources/Maps > data.csv
```

The output contains rows for the following, with a column for each map analyzed:
* Station ID
* Tile count
* Counts and densities for the entities and groups that densities were calculated for
* Counts for other groups
* Counts for other entities, sorted by how many of the analyzed stations the entity appears on

## Known issues

* I really should have written this in C# and used SS14's existing map handling code
* Even in python, it could be much faster if I bothered to set up libyaml
* As mentioned above, the configuration setup is kind of a mess
* Honestly the output could be clearer too

