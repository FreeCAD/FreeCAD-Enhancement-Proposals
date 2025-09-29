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
techniques.  However, all these options have their issues [[1](#ref1)].  A
first option is creating **copies of parts**.  However, with this technique, it
is not clear which parameters are designated for variants and a change to all
instances of the variant is not possible.

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

Various design directions have been investigated and considered.  We first list
the various directions and explain below why the current direction is chosen.

### Keep current functionality

Keeping the current functionality in essence not doing anything and use
subshapebinders if only shapes need to be references, and tracking
copy-on-change links for link behavior.  However, this is not considered
because these techniques have various limitations: Designs that use these
techniques are brittle because of the complex administration and two separate
ways of doing dependency checks (the regular mechanism and the special
mechanism for hidden references).  Additionally, these techniques are not user
friendly.

### Granularity dependency checking

Improved dependency checking can remove the need for using hidden references by
introducing **exposed properties** that define for users what properties can be
used to vary parts.  Two directions are considered: **Fine-grained dependency
checking** is a re-implementation of FreeCAD's dependency checking that defines
relations between objects based on the properties.  **Current dependency check
with special cases** adds exceptions for properties that are exposed but keeps
the overall logic.

#### Fine-grained dependency checking

This is a reimplementation of dependency checking where dependencies are not
recorded between document objects, but between the properties of document
objects.  This allows us to avoid circular dependencies for exposed properties
and it allows improved recomputation where a property change only causes the
document objects that depend on that property and not all document objects that
depend on any property.

#### Current dependency check with special cases

This enhances the current dependency check and creates exceptions for exposed
properties to prevent cyclic dependencies.  A drawback of this direction is
that the dependency code becomes even more complex and it does not help with
the improved recomputation efficiency that fine-grained dependency checks
offer.

### Shape-based vs. subtree-based variants

Variants that are **shape-based**, do not expose the subtree of document
objects to the user, whereas **subtree-based** variants do.

#### Shape-based variants

Creating a variant of a part results in a flat part without subtree with only
a shape.  A benefit of this approach is that the implementation is relatively
simple.  However, this implementation cannot handle, more complex parts such as
assemblies and it is necessary to introduce the new concept of a variant part.
For example, creating a variant of an assembly cannot show its origin or local
coordinate systems because the subtree of the assembly is not incorporated.

#### Subtree-based variants

Creating a variant of a part provides the complete subtree of the part to the
user.  This allows us to make use of the logic of links, it provides users with
the familiar interface of links, and this solution can handle complex parts.  A
drawback is that the implementation needs to be integrated with FreeCAD's links
system.

### Copy-based vs. intercept-based variants

To create a variant, it is always necessary to duplicate some properties.
**Copy-based** variants maintain a full copy of the variant part whereas
**intercept-based** variants keep the duplication to a minimum and intercept
property access.

#### Copy-based variants

Copy-based variants maintain a full copy of the variant part and maintain an
administration to give the user the illusion that there is no copy.  To ensure
that the correct dependencies are captured, an extensive administration is
required may go out of sync and causes problems as a result.  Another risk is
that document objects are user defined (for example, in an addon) and it may be
the case that the administration is not capable of fully capturing what is
required to copy.

#### Intercept-based variants

This direction aims to minimize what is copied.  Instead, it intercepts
property accesses and redirects these to temporary data structures.  A benefit
of this system is that it gives FreeCAD support for variants at a very low
level and only one mechanism is needed.  Additionally, this system has the
potential to be used for concurrency because reads and writes can be captured
temporarily.  A drawback of this approach is that each property type with each
property access needs to be touched.

### Chosen directions

Keeping the current functionality is not a viable option in my opinion because
virtually no users seem to make use of the current mechanisms.  The mechanisms
are not user friendly and often provide results in designs that are hard to
analyze and understand.

The chosen direction is fine-grained dependency checking with subtree-based and
intercept-based variants.  Fine-grained dependency checking is chosen because
dependency checking will improve in general with:

1. a means to refer to properties of parent document objects without triggering
   cyclic dependencies,
2. one mechanism for dependency checking (as opposed to two in the current
   implementation), and
3. remove unnecessary recomputes.

Subtree-based variants are chosen, because users are already familiar with the
link interface, it can handle complex parts, and the already complex link
logic will go through a new code-review cycle.

The direction of intercept-based variants is chosen because this mechanism
allows us to bring FreeCAD variants as core functionality that acts at a low
level instead of logic that is built on top of existing logic and has to
circumvent limitations of the current system.  An additional benefit is that
only one mechanism is needed and complex administration problems for
maintaining copies are avoided.

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

1. <span name=ref1>Forum post with videos of the 4 alternatives</span>: <https://forum.freecad.org/viewtopic.php?p=786692&sid=3e7a311d0f05b2f10697de4128d9b33f#p786692>

## License / Copyright

All FEPs are explicitly [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/).
