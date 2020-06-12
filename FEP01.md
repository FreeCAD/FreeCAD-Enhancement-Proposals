
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

A clear requirement for the handling of the versions is the basis for an efficient optimization of FreeCAD and libraries that use FreeCAD. Each of the three digits of the version string represents a different degree of change. This must be formulated precisely in order to  on the one hand and on the other hand to give the user a clear message of what type of change he is dealing with.

Furthermore, a suggestion for the versioning of extensions for FreeCAD should be given. Basically, the same scheme should be used as for FreeCAD itself. This enables package managers and the internal add-on manager to find a compatible version of an extension.


## Definitions of different forms of compatibility

__Interface compatibility__ is important for developers who use FreeCAD as a dependency in other projects. FreeCAd offers interfaces at various levels (c ++, Python, comman-line). All of these interfaces can be handled in the same way using the version number.
The __file compatibility__ is the compatibility of different versions for opening FreeCAD files (.FCstd).
__Forward compatible__ is the term used to describe changes which guarantee the compatibility of files or interfaces for the new version with an older version.
A version is __backward compatible__ with another version if interfaces/files created for the old version are also working with the new version.

## The version numbers

The version is given by three digits (major.minor.patch)

### The major version

The first number of the version number indicates the degree of development of the project. The 0 (zero) version is a special case and is called (development version). The minor version is handled differently for this. Changing the major version in non-zero versions is equivalent to changing the minor version in the null version.

### The minor version

#### 0 versions

In the 0 versions, a change in the minor version represents a change that neither guarantees backward compatibility nor forward compatibility. This corresponds to a change in the major version for 1+ versions.

#### 1+ versions

In the 1+ versions, a change in the minor version represents a change that guarantees backward compatibility. There is no compatibility in the other direction (forward compatibility)


### The patch version

A change in the patch version number represents a change that does not represent a loss of compatibility (forward + backward). Such changes can be, for example:

- Adaptations to dependencies, which were made available in a newer version
- Bugfixes

## Change from 0 version to 1+ version

This topic was heavily discussed in the FreeCAD-Forum. (TODO @vocx, @triplus what is the conclusion)

## Copyright

All FEPs are explicitly [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/).
