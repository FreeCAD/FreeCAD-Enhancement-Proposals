
| FEP01             |                                                                               |
|-------------------|-------------------------------------------------------------------------------|
| Title             | version handling                                                              |
| Status            | Draft                                                                         |
| Author(s)         | looooo                                                                        |
| Created           | Jun 12, 2020                                                                  |
| Updated           | Jun 12, 2020                                                                  |
| Discussion        | https://forum.freecadweb.org/viewtopic.php?f=8&t=43525                        |
| Implementation    | -                                                                             |


## Abstract

A proposal for the future handling of versions in FreeCAD. 

## Motivation

A clear requirement for the handling of the versions is the basis for an efficient optimization of FreeCAD and libraries that use FreeCAD. Each of the three numbers of the version string represents a different degree of change. The meaning of each digit-change must be formulated precisely to make decisions on how the version of a release must be selected and on the other hand give a clear sign for developers using freecad as library if the version is API-compatible or not and for users to see if files from older versions are compatible.

Furthermore, a suggestion for the versioning of extensions for FreeCAD should be given.


## Specification
### Definitions of different forms of compatibility

__Interface compatibility__ is important for developers who use FreeCAD as a library. FreeCAD offers interfaces at various levels (c ++, Python, comman-line). All of these interfaces can be handled in the same way using the version number.
The __file compatibility__ is the compatibility of different versions for opening FreeCAD files (.FCstd).
__Forward compatible__ is the term used to describe changes which guarantee the compatibility of files or interfaces for the new version with an older version.
A version is __backward compatible__ with another version if interfaces/files created for the old version are also working with the new version.

### The version numbers

The version is given by three numbers (**major**.**minor**.**patch**)

The first digit of the version-string is the **major-version**. It indicates the degree of development of the project. The major-version is changed whenever a bigger change (This can be for example refactoring or a change of the functionality). The change from 0 to 1 stands for a change from development-phase to a more stable-phase. This means that the 1-version should not get any big changes in terms of functionality and trying to keep the versions compatible will be taken more seriously.

The second number is the **minor-version**. A change in the minor version-number represents a change that neither guarantees backward compatibility nor forward compatibility.

The third number is the **patch-version**. If this version-number increases only backward-compatible chnanges are added.

Once a higher priority digit changes all lower priority numbers are reset to 0. This means if the minor-version is increased from 18 to 19 the patch version is set to 0. If the major version is increased from 0 to 1 both the minor-version and the patch-version are set to 0.


This scheme possible change in the future but holds for major-versions 0 and 1.

### Decision when to change from 0 to 1

It was decided on topological naming beeing the critical feature which marks the point where we should change the major version from 0 to 1.

### Suggestion for choosing a version-scheme for 3rd-party modules

Extension should use the same scheme as FreeCAD but at least should define theire version handling so that maintainers can provide packages which have no incompatibilities between freecad and the extension itself.

## Copyright

All FEPs are explicitly [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/).
