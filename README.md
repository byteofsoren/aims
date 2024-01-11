# AppImage Management System(AIMS)
This program aim's to be used to manage AppImages available on GitHub releases pages.
The thoughts behind AIM is to be able to install those AppImages on the local computer with as little effort as possible.

# How to use AIM
First begin with listing the inbuilt help function

```
$ python aims.py -h

usage: aims.py [-h] [-n NAME] [-N NAME] action

AppImage Manager for Linux (aim)

Positional arguments:
  action            Action to preform: search, install, update, show, debug

options:
  -h, --help        show this help message and exit
  -n, --name NAME   Name of the AppImage in the official repo
  -N, --Name NAME   Name of the AppImage in the personal repo
```

Then to install a package it goes something like this.
First we search the repo for what we want.

```
$ python aims.py -n FreeCAD search

FreeCADlink:
  FreeCAD link stage 3 branch

FreeCADondsel
  FreeCAD Ondsel-Development brancg

```

Then After we have decided we install that branch with the following command:

```
$ python aims.py -n FreeCADlink install

```

Then FreeCAD link stage 3 is installed in side `$HOME/bin/freecad` directory and a symlink is placed inside `$HOME/bin` with the name `freecadlink` that can be executed with the command:

``` bash
$ ./freecadlink
```
That would then launch FreeCAD link stage 3.

> Note: In the -h --help i also show that -N can be used to use personal repos.
> That functionality is not completed. That would be a future work.

Then you can use the `show` argument that shows what repos are installed and tracked by aim.

```
$ python aims.py show
```

# Adding AppImages to the repo.yaml file.
Adding AppImages to the `repo.yaml` file can be a bit laborious becouse the program uses regular expressions to search for the file name and url of the AppImage on the GitHub releases page.
To help with that situation I have added a debug feature that saves the response from GitHub on a file that can be used to search for the correct regular expressions.

To begin adding a AppImage first open the `repos.yaml` file and add the repo as follow:

``` yaml
repoName:
  link: GitHubOwner/repoName
  platform: GitHub
  installation:
    path: repoName
    symlink: 1
  description: "This is my repo"
  regex:
    filename: 'This_my_progra_[v,V]\d\.\d*\.\d.AppImage'
    version: '[v,V]\d\.\d*\.\d'
```

Notice that the filename contains regular expressions.
Those expressions are used to what the files are called.
But that is often enough as the string containing the whole url also has an extra version inside the string.
To fix that the extra version regular expressions is needed.

But to find the exact regex for the AppImage file name and url the extra debug command can be used as follow.

```
$ python aims.py -n repoName debug
```

This will save a file named `responce.html` that contains the response from GitHub.
To help searching for the correct regular expressions we can use the Linux command `grep` as follow.

``` bash
cat responce.html | grep -P "https://github.com/{user}/{repo}/releases/download/{version}/{filename}"
```

Where you replace the:
* `{user}` With the who created the GitHub repo.
* `{repo}` Is the name of the GitHub repo at that user.
* `{version}` is the version regular expressions inside the yaml file.
* `{filename}` is the filename inside the yaml file.
The `-P` option on the `grep` command is to tell `grep` to use the pearl version of grep.
Witch is almost the same as Pythons re module uses.

After trimming your regular expressions a bit to detect the correct AppImage.
Then you can update the `repo.yaml` file again and test with the debug command.

```
$ python aims.py -n repoName debug
```
If you get a OK sign, then you can install that AppImage by using `$ aims.py -n name install`.







