# FEP-0009 — PartDesign Multibody: direct cross-Body references in a unified Part coordinate system

| FEP-0007       |                                                                                                                                           |
| -------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| Type           | Informational                                                                                                                             |
| Status         | Active                                                                                                                                    |
| Author(s)      | @wsteffe
   |
| Version        | 1.0.2                                                                                                                                     |
| Created        | 2025-09-05                                                                                                                                |
| Updated        | 2025-09-05                                                                                                                                |
| Discussion     | https://github.com/FreeCAD/FreeCAD-Enhancement-Proposals/pull/26
   |
| Implementation | https://github.com/FreeCAD/FreeCAD/pull/23610


---

## Motivation
- **Design limitation**: multibody modeling expects that bodies can freely reference geometry within a part; the current model hampers this.

The main reason for using a multibody model instead of building an assembly of separate parts (the old way) is precisely the possibility of referencing geometries of other bodies. In thecurrent FreeCAD implementation this is precluded: direct cross-Body links are blocked.  
The proposed PR overcomes this limitation by enabling cross-linking between different Bodies inside the same Part (or between top-level Bodies).

## Specification

### Expected Results
- Users can perform all operations that were allowed before this PR, with only one exception:  
  they will no longer be able to specify or read `Body.Placement` from the GUI.  
- In exchange for this small limitation, users gain the ability to directly reference geometries of other Bodies within the same Part (or among top-level Bodies).  
- The Transform tool continues to work as before for repositioning Bodies.  
- Opening legacy documents remains seamless; their behavior is preserved after automatic migration.

### Implementation
- The `Placement` property of `Body` is disabled in the GUI, but still exists internally and may be used programmatically.  
- Migration routine `migrateLegacyBodyPlacements()` converts legacy Body placements into equivalent transformations on contained features.  
- `resetBodyPlacement()` ensures all Bodies in a document end up with identical placements after migration or transform operations.  
- Bodies are treated as transparent containers (`m_actsAsGroupBoundary = false`), removing the Body boundary from link scoping.  
- Cross-Body links inside a Part (e.g. external geometry in Sketcher, or attaching a sketch to a face of another Body) are allowed.  
- Cross-Part links remain disallowed unless mediated through a `SubShapeBinder`.  


## Rationale  

The chosen approach was selected because it strikes a balance between **minimal disruption** to existing workflows and **significant new capabilities** (cross-Body referencing). Below is the reasoning, trade-offs, and how it compares to alternatives:

### Why this approach  

1. **Preserve document structure**  
   By *disabling* `Body.Placement` in the GUI rather than removing it completely, the document hierarchy and relationships remain intact. Scripts, macros, or internal code that still access `Body.Placement` will not break (though they will no longer be visible or modifiable in the UI). This minimizes compatibility risks.  

2. **Migration and Transform reuse via reset**  
   The use of `resetBodyPlacement` in both migration and transform operations ensures that after moving or migrating, all Bodies end up with a consistent placement. Internally, `Body.Placement` is still meaningful and remains synchronized. This avoids drift, double transformations, or inconsistencies.

3. **Widened linking scope vs constrained boundaries**  
   The primary limitation of the legacy model is that Bodies act as rigid boundaries: you cannot reliably reference geometry across Bodies. With a unified reference frame (no per-Body offset in the UI) and adjusted linking logic, cross-Body links are possible—for example, *External Geometry* in sketches, or selecting a face on another Body as the support for a new sketch. This unlocks much more flexible multibody workflows.

4. **Retention of SubShapeBinder / cross-Part isolation**  
   We do not change the mechanism for cross-Part referencing: `SubShapeBinder` remains the sanctioned and controlled mechanism to cross the Part boundary. This avoids a “wild west” of arbitrary cross-document linking and preserves modularity.

### Alternative: Automatic/Implicit SubShapeBinders  

One alternative discussed in the forum is the automatic creation or injection of SubShapeBinders to bridge geometry across Bodies without forcing the user to manually place them. The idea: when a feature in Body B refers to geometry in Body A, the system would auto-insert a SubShapeBinder behind the scenes.

**Reasons this alternative was considered but ultimately rejected / deemphasized:**

- **Implicit magic is hard to reason about**  
  Users may become confused when a SubShapeBinder appears without their action. It obscures the dependency graph, making debugging harder.

- **Performance & dependency complexity**  
  Automatically inserting binders on demand can introduce complex dependency chaining and evaluation ordering. Maintaining consistency (particularly in recompute, editing upstream references, or undo/redo) becomes more delicate.

- **Explicitness is preferable in CAD**  
  CAD users often prefer to know and control their reference links explicitly (i.e. “this geometry comes from there”). Implicit binders risk introducing hidden dependencies that surprise or confuse users.

### Trade-offs and caveats  

- Users lose direct GUI placement control of `Body`.  
- In the vast majority of cases, Body geometry is built from an initial sketch attached to a plane of the Body’s `Origin`. In these cases, the Body as a whole can still be repositioned using the `Origin.Placement` property, which effectively takes over the role that `Body.Placement` had before.  
- Some legacy workflows that assumed visual Body placement may require users to adjust their modeling strategy.  


## Alternatives
- **Automatic / Implicit SubShapeBinders**: rejected because it introduces hidden dependencies and ambiguous transformations. As discussed in the Rationale, implicit binders obscure the model tree, complicate recompute ordering, and reduce user control.  
- **Replace Body with a new container type**: rejected because it would break backward compatibility and require major restructuring of both code and user workflows, with no clear advantage over simply disabling `Body.Placement`.  



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



