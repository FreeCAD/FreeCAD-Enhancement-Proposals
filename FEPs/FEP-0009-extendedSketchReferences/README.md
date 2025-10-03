# FEP-0009 — Sketch references (External Geometry & Attachment Supports) across Bodies and Parts

| FEP-0009       |                                                                                     |
| -------------- | ----------------------------------------------------------------------------------- |
| Type           | Core Change                                                                         |
| Status         | Draft                                                                               |
| Author(s)      | @wsteffe                                                                            |
| Version        | 1.0.2                                                                               |
| Created        | 2025-09-05                                                                          |
| Updated        | 2025-10-03                                                                          |
| Discussion     | https://github.com/FreeCAD/FreeCAD-Enhancement-Proposals/pull/26                    |
| Implementation | https://github.com/FreeCAD/FreeCAD/pull/23610                                       |

---

## Motivation
- **Design limitation**: Multibody modeling workflows expect that features in one Body can reference geometry defined in another Body of the same project. Historically, this was restricted, forcing users toward patterns resembling multi-Part assemblies and manual proxy objects. The change proposed here lifts those restrictions for sketches (External Geometry and Attachment Support), thereby enabling more natural design intent propagation across Bodies and, **optionally**, across Parts within the same document.

## Specification

### Scope of references

- **Across Bodies and Parts (same document)**: A sketch may reference External Geometry from, or attach to faces/edges/planes of, features living in other Bodies or other Parts.
- **Across documents**: Out of scope; unchanged from upstream.

### Expected Results

- **No UI regression**: There isn't any new limitation or change in the GUI for any operation allowed in upstream.
- **Backwards compatibility**: Existing files open and behave as before; references created with older versions remain valid.
   Documents created under prior restrictions can now create new cross-Body and cross-Part sketch references.

### Implementation

- **Transparent containers**: Part and Body are set as transparent containers through a call to the new function `GeoFeatureGroupExtension::setActsAsGroupBoundary(bool v)` placed in their constructors.

- **Link-scope adjustment**: The link scoping rules for Sketcher External Geometry and Attachment Support are extended. This enables selecting geometry across Bodies and Parts. Scope definition is handled by the new helper function `App::DocumentObject* getBoundaryGroupOfObject(const App::DocumentObject* obj)`, which depends on `GeoFeatureGroupExtension::actsAsGroupBoundary()`.

- **SketchObject update**: `SketchObject::rebuildExternalGeometry()` is updated to take into account the global position of external geometries.

- **AttachExtension update**: `AttachExtension::positionBySupport()` is updated to take into account the global position of the attached support.

- **Placement propagation**: Changes of Part/Body Placements are propagated to all container children in the updated function `GeoFeatureGroupExtension::extensionOnChanged()`.

## Rationale

This design targets **maximum capability with minimal disruption**:

- **Predictable dependency graphs**: By avoiding implicit SubShapeBinder injection, dependency graphs remain explicit and auditable. Users who prefer proxies can continue to use SubShapeBinders deliberately.
- **Incremental change**: The behavior outside of Sketcher External Geometry and Attachment Support is unchanged, reducing risk.

### Alternative: Automatic/Implicit SubShapeBinders

One alternative discussed in the forum is the automatic creation or injection of SubShapeBinders to bridge geometry across Bodies without forcing the user to manually place them. The idea: when a feature in Body B refers to geometry in Body A, the system would auto-insert a SubShapeBinder behind the scenes.

**Reasons this alternative was considered but ultimately rejected:**

- **Implicit magic is hard to reason about**
  Users may become confused when a SubShapeBinder appears without their action. It obscures the dependency graph, making debugging harder.

- **Performance & dependency complexity**
  Automatically inserting binders on demand can introduce complex dependency chaining and evaluation ordering. Maintaining consistency (particularly in recompute, editing upstream references, or undo/redo) becomes more delicate.

- **Explicitness is preferable in CAD**
  CAD users often prefer to know and control their reference links explicitly (i.e. “this geometry comes from there”). Implicit binders risk introducing hidden dependencies that surprise or confuse users.

## Alternatives
- **Automatic / Implicit SubShapeBinders**: rejected because it introduces hidden dependencies and ambiguous transformations. As discussed in the Rationale, implicit binders obscure the model tree, complicate recompute ordering, and reduce user control.

## Future Work


## References

- PR: [FreeCAD#23610](https://github.com/FreeCAD/FreeCAD/pull/23610)
- Issue: [FreeCAD#22797](https://github.com/FreeCAD/FreeCAD/issues/22797)
- Process: [FEP-0001](https://github.com/FreeCAD/FreeCAD-Enhancement-Proposals/tree/master/FEPs/FEP-0001-process)
- Forum discussion: [FreeCAD Forum Thread](https://forum.freecad.org/viewtopic.php?t=99744)

## Appendix

### Glossary

- **Body**: A container for PartDesign features.
- **Part**: A higher-level container providing a common coordinate system.
- **SubShapeBinder**: A proxy for referencing geometry across Parts.
- **GeoFeatureGroupExtension**: Base providing group behavior and link scoping.
- **resetBodyPlacement**: Function ensuring uniform placements after migration or transform.
