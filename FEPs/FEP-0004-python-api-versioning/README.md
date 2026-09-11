# FEP-0004 Python API Versioning

| FEP-0004       |                                                                                                 |
| -------------- | ----------------------------------------------------------------------------------------------- |
| Type           | Core Change                                                                                     |
| Status         | Draft                                                                                           |
| Author(s)      | @oursland                                                                                       |
| Version        | 0.1                                                                                             |
| Created        | 2025-06-24                                                                                      |
| Updated        | 2025-06-24                                                                                      |
| Discussion     |                                                                                                 |
| Implementation |                                                                                                 |

This FEP proposes a means by which the Python API may be versioned and information about changes, deprecation, and obsolescence may be conveyed to developers.

## Motivation

The Python API is the mechanism by which third parties develop workbenches and macros for FreeCAD.  Consequently, there has been a reluctance to alter the Python API as there is no effective contract or means of communication for support to users of the Python APIs.  This limitation is a significant barrier to improvement, and has led to unnecessary duplication of functionality in code.

A mechanism for versioning of the API and declaring used API versions permits:
* changelog introducing functionality or altering behavior between versions
* a mechanism by which APIs may be declared deprecated or obsoleted
* a standard by which workbenches or macros can be compared to ensure compatibility with a given releases' APIs

## Rationale

(TBD) Decisions on specification will be noted here.

## Specification

(TBD) The binding IDLs will need to be augmented and updated with versioning information, the binding generators will need the same treatment.  Somewhere, the APIs and their documentation should be automatically generated with their support status and versioning information, so that developers may use this as a reference.

### Impact on existing features / subsystems

Python binding generators will need to be updated to incorporate the versioning information.

### Backwards Compatibility (only for Core Changes)

The FEP does not break backwards compatibility, but does introduce a mechanism for conveying future breaking Python API changes to developers.

## License / Copyright

All FEPs are explicitly [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/).
