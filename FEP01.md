
| FEP01             |                                                                               |
|-------------------|-------------------------------------------------------------------------------|
| Title             | Namespace-packages and python imports                                         |
| Status            | Draft                                                                         |
| Author(s)         | user name                                                                     |
| Created           | Dec 28, 2019                                                                  |
| Updated           | Dec 28, 2019                                                                  |
| Issue             | -                                                                             |
| Discussion        | https://forum.freecadweb.org/viewtopic.php?f=22&t=13238                       |
| Implementation    | -                                                                             |


## Abstract

This FEP adresses the so called new-style-modules and the python import structure of FreeCAD in general. It proposes a solution for different problems arising by the traditional way of initializing workbenches and packages. Further it defines the python import interface for the future.

## Specification

### Traditional structure of workbenches and their problems

The traditional structure of workbenches is a set of files stored in a directory. There are two files which are called at initialization of freecad and freecadcmd (`InitGui.py` and `Init.py`) During the initialization every Workbench/Module which contains one of these two files will be added to `sys.path` and afterwards executed (`exec`) inside the initilization process. 

By using `exec` these files behave different to modules which are imported by the `import` statement. So objects which normally live in another namespace can be used directly (eg. the class `Workbench` can be used without importing it). Computiing the path of the file which is `exec`'ed is not possible by using the `__file__`-variable. Another drawback of the traditional way to initilaize workbenches is the chance of clashing module-names. This is due to the way how initialization works for the traditional workbenches (adding workbench-directory to `sys.path`)

### Namespace packages as a solution

Namesppace packages were implemented in (https://github.com/FreeCAD/FreeCAD/commit/2ff47374f2b27b8ab8c3cbee70a8d24214ca69aa#diff-f376214989010d8eefb6b08fbe2a733b). The most important difference between namespace-packages and traditional packages is the initialization. Namespace-packages are NOT `exec`'ed they are imported. So the initialization files (`init_gui.py` and `init.py`) behave like normal python-modules (eg. using `__file__` works like expected). Also due to the design of the namespace-packages name-clashes cannot occure anymore.
Namespace-packages extend the freecad-namespace. This is done by placing the workbench inside a directory named `freecad`. So any namespace-package for freecad is extending the `freecad` namespace. For further details about namespace-packages please have a look at https://github.com/FreeCAD/Workbench-Starterkit.

### Developing the future module interface for FreeCAD by using namespace-packages

There is another problem somehow related to the traditional workbench structure. It's not possible to use freecad in any 3rd party python application without modifying sys.path. As this modification is dependent on the plattform (win, linux, mac) writing application depending on FreeCAD but not running inside a freecad-appliaction (freecad, freecadcmd) is very difficult. (TODO: example, can't remember it's name). So there is a need to define the python import structure for FreeCAD to make it possible for other projects to rely on the freecad-python-interface. Again the solution provided by namespace-packages is used to acchieve this goal but a proposal needs to be defined to keep the backwards compatibility while slowly moving towards the new structure.


## Rationals:

1. The freecad namespace is proposed to be the entry-point for all freecad-related python imports and it's the same for internally importing a module via freecad or freecadcmd or external via a python interpreter. (`from freecad import <package>`)
2. Due to 1. Namespace-packages are the preferred way to write 3rd party modules.
3. A slow transition from traditional workbenches to namespace-packages is proposed. This means that there is no pressure to update any workbench, but we agree on deprecating the traditional workbenches at one point.


## Open points:

- How to deal with internal c++-workbenches?
It shouldn't be too difficult to use extension modules inside of namespace packages. But there is currently no example available.
- How to use translation within namespace packages? Are there any difficulties?


## Copyright

All FEPs are explicitly [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/).
