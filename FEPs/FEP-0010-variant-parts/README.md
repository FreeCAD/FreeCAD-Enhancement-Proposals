# FEP-0010 Variant Parts

| FEP-0010       |                           |
|----------------|---------------------------|
| Type           | Core Change               |
| Status         | Draft                     |
| Author(s)      | Pieter Hijma @pieterhijma |
| Version        | 0.1                       |
| Created        | 2025-09-23                |
| Updated        | 2025-09-23                |
| Discussion     | TBD                       |
| Implementation | n/a                       |

This proposal introduces variant parts to FreeCAD.  Variant parts are parts
with with a clear interface that communicate to users what the designer of the
part intended the user to vary in terms of parameters.  This allows users to
introduce different variants of the same part without affecting the original
design.

## Motivation

FreeCAD has no good solution for Variant Parts.  A **Variant Part** is a
parametric part with the following properties:

1. a user can create more than one instances,
2. those instances can vary for specific properties that are designated for
   creating variants, and
3. changes in properties that are not designated for creating variants,
   propagate to all other instances.

In FreeCAD, it is virtually impossible to create parts with these properties.
As a result, in FreeCAD, parametric design is limited, it is not possible to
reuse or exchange parts independently and as such, parametric parts are not
modular.  This modularity in parametric designs is important because as FreeCAD
is an open source application, seamless sharing and exchange of parts should be
central to FreeCAD's mission.

Another reason why this functionality is important is because parametric design
is at the heart of FreeCAD (it uses the subtitle "Your own 3D parametric
modeler" prominently on the website), yet, the kind of parametric design
introduced by this proposal is currently a weakness of FreeCAD.

FreeCAD has functionality that comes close to true variant parts with various
techniques.  However, all these options have their issues.  A first option is
creating **copies of parts**.  However, with this technique, it is not clear
which parameters are designated for variants and a change to all instances of
the variant is not possible.

A second option is **copy-on-change links**.  However, this technique is not
user friendly and it makes use of hidden references.  Propagating a change to
all instances is only possible by making it regular links first, which cancels
all previously introduced parameterization.  Moreover, a hidden copy of the
part is maintained and finally, the technique requires a complex
administration.

An improvement is the technique of **tracked copy-on-change links**.  However,
this has the same issues of copy-on-change links with an even more complex
administration for variants, but with the benefit that it is possible to
propagate changes to all instances.  However, these updates to the original
part cause newly created document objects for each small change with new names
and labels, potentially breaking geometry that was built on the tracked
copy-on-change link.

Finally, **subshape binders** use a different way of storing the copy, namely
in a hidden temporary document.  This has the benefit, that the copy is not
stored inside the document and is generated each time, but the document is not
fully hidden and sometimes, the user is confronted with a document that appears
out of nowhere.  Additionally, this techniques is not user friendly and relies
on hidden references, it has a complex administration for parts as well, and
other than tracked copy-on-change links, subshape binders can only reference
shapes.  This means that the document object subtree is not available to users
to make use of, something that is possible with regular links.

## Rationale

Why particular decisions were made in the proposal.

## Specification

The technical details of the proposed change.

### Impact on existing features / subsystems

Any remarks about how the proposal will impact existing features or subsystem within the FreeCAD.

### Backwards Compatibility (only for Core Changes)

Any remarks about how the proposed change will affect the backwards compatibility for files, addons and workflows.

## Open Issues (optional)

Issues that are not yet answered in terms of specification. Proposal cannot proceed into Proposed state unless all
questions are answered.

## Rejected Ideas (optional)

List of ideas that were rejected at discussion stage with rationale on why they were rejected.

## Alternatives (optional)

Discussion about alternative approaches considered during the design or the discussion.

## Implementation (only for Core Changes)

Further discussion about implementation details, with link to implementation (if available) or any other way
proving that implementation is feasible and someone is willing to carry the implementation effort.

## FAQ (optional)

Frequently Asked Questions ans answers to them, based on author

## Further Work (optional)

Discussion on further work related to the FEP that can be done.

## Changelog (once more versions are released)

Any substantial changes to the FEP should be recorded in this section - latest changes should be on top:

### 0.x - 2025-02-15

- First Change
- Second Change
- ...

## References (optional)

Any references used in the design of the FEP, forum discussions etc.

## License / Copyright

All FEPs are explicitly [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/).
