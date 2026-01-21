# FEP-0009 — Sketch references (External Geometry & Attachment Supports) across Bodies and Parts

# FEP-0009 — Sketch references (External Geometry & Attachment Supports) across Bodies and Parts

| FEP-0009       |                                                                                     |
| -------------- | ----------------------------------------------------------------------------------- |
| Type           | Core Change                                                                         |
| Status         | Draft                                                                               |
| Author(s)      | @wsteffe                                                                            |
| Version        | 1.0.3                                                                               |
| Created        | 2025-09-05                                                                          |
| Updated        | 2026-01-21                                                                          |
| Discussion     | https://github.com/FreeCAD/FreeCAD-Enhancement-Proposals/pull/26                    |
| Implementation | https://github.com/FreeCAD/FreeCAD/pull/23610                                       |

---

## Motivation

### The Problem: Geometrical Silos
Current multibody modeling in FreeCAD is characterized by "geometrical silos". While the software allows multiple Bodies and Parts within a single document, it enforces a strict isolation of their coordinate systems to avoid the complexity of cross-container spatial calculations.

This isolation manifests as a significant design limitation:
* **Workflow Fragmentation**: Users cannot directly reference geometry (External Geometry) or attach features (Attachment Support) across Body or Part boundaries.
* **Dependency Bloat**: To overcome these boundaries, users are forced to manually create proxy objects (e.g., SubShapeBinders), adding unnecessary clutter to the Tree View and obscuring the original design intent.
* **Cognitive Load**: Users must manage the technical "plumbing" of the model instead of focusing on geometry, ensuring that references are correctly updated when containers are moved.

### The Objective: Transparent Design Intent
The goal of this proposal is to evolve FreeCAD’s core architecture to support **Transparent Containers**. By generalizing how relative positions are calculated, we aim to:
1. **Eliminate Artificial Barriers**: Allow Sketcher and Attachment tools to "see" and "link" to geometry anywhere in the document.
2. **Simplify the Model Tree**: Remove the mandatory need for intermediate proxy objects for common cross-body tasks.
3. **Ensure Geometric Integrity**: Replace the current policy of "prohibition" with a robust mathematical framework that resolves coordinate transformations dynamically and automatically.

## Rationale

The "SimplerBody" design provides a native and transparent mechanism for cross-container references, replacing the current "manual workaround" paradigm with a robust architectural solution.

### Why it is done like that?
The implementation within `GeoFeatureGroupExtension` and `AttachExtension` allows FreeCAD to resolve spatial relationships directly at the core level.
* **Native Coordinate Resolution**: Instead of requiring an intermediate object (Binder) to translate coordinates, the system calculates the relative transformation matrix dynamically.
* **Transaction-Based Updates**: By utilizing `onCommitTransaction`, the proposal ensures that updates are performant and occur only when the document is in a stable state.

### Why it is the best solution?
1. **Alignment with Industry Standards**: In professional CAD tools (Solidworks, Inventor, Creo), cross-container references are a native capability. SimplerBody brings FreeCAD in line with these standards.
2. **Geometry-level vs. Container-level links**: While fine-grained links can be created manually with Binders, it severely clutters the tree. SimplerBody provides the same safety of a fine-grained link with zero visual overhead.
3. **Predictable DAG Management**: By making references direct and selective, "heavy" dependencies (such as importing the entire Body Tip) are avoided, which often lead to cycles in automated Binder-based systems.

## Specification

### Universal Container Transparency
The `GeoFeatureGroupExtension` class, base for containers such as `Body`, `Part`, and `Boolean`, is now transparent by default.
* **Class-Level Control**: Transparency is managed by the `setActsAsGroupBoundary(bool)` flag allowing links through their hierarchy.
* **Flexible Architecture**: While the default is `false`, this mechanism serves as a safety valve to isolate container types that might require restrictions in the future.

### Generalized Coordinate Mapping
The system replaces static coordinate assumptions with a dynamic resolution engine:
* **Dynamic Relative Placement**: The system calculates the transformation matrix between source and target by traversing the parent hierarchy up to the nearest non-transparent boundary.
* **Matrix Calculation**: Matrix inversion and multiplication are used to resolve final placement relative to external supports: $T_{rel} = T_{target}^{-1} \cdot T_{refGroup} \cdot T_{ref}$.

### Automated Recompute Propagation
* **Deferred Notification**: Placement changes trigger a "deferred touch" on child objects, processed at the end of the transaction via `onCommitTransaction`.
* **Sketcher Synchronization**: Specifically forces an update of the `ExternalGeometry` property, ensuring 2D constraints re-solve against the updated 3D spatial data of external references.

### Impact on existing features / subsystems

The proposed change is a **transparent generalization** of the existing coordinate resolution and linking logic. 

* **No Negative Impact on Existing Workflows**: Since the modification expands the allowed link scope rather than restricting it, all current modeling techniques remain fully functional. Users can continue to use manual SubShapeBinders or work within single-body constraints exactly as they did before.
* **Workbench and Addon Compatibility**: 
    - **PartDesign**: This workbench is the primary beneficiary, achieving native multibody support without workarounds.
    - **Other Workbenches**: Any workbench utilizing the Sketcher or Attachment engine (e.g.,Part, BIM, SheetMetal) will automatically benefit from the expanded link scope without requiring code changes within the workbenches themselves.
* **Safety through Generalization**: By resolving transformations at the core level (`GeoFeatureGroupExtension`), we ensure uniform behavior across the application without patching individual features.

### Backwards Compatibility (only for Core Changes)

* **File Compatibility**: Existing files are not negatively affected. The generalized mapping logic is backward compatible with documents created in previous versions of FreeCAD.
* **Workflow Continuity**: The change does not break existing Python scripts or macros. The resolution happens at the C++ core level, maintaining consistent behavior for high-level API calls.
* **Migration**: No explicit migration of old data is required, as the new logic interprets the existing hierarchy more flexibly without changing the underlying data structure of old objects.

## Implementation

### 1. Core Extensions
- **GeoFeatureGroupExtension**: Introduces `globalGroupPlacementInBoundary()`, calculating the cumulative matrix up to the boundary.
- **AttachExtension**: Added the `RefPlacement` transient property to store the reference coordinate system. The `positionBySupport()` logic now resolves final positioning regardless of nested containers.

### 2. Feature Updates
- **PartDesign ProfileBased / Extrude**: Classes like `FeatureSketchBased` and `FeatureExtrude` have been updated to handle references in external coordinate systems. Operations like "Up to face" now dynamically transform target geometry into the local space of the active feature.


### 3. Stability Mechanisms
- **Recursion Guard**: Uses `MAX_RECOMPUTE_DEPTH` to prevent infinite loops during hierarchical updates.
- **Local Link Management**: The `getInvalidLinkObjects` function has been updated to ensure local links do not cross the defined movable group boundaries.

## Alternatives

### Automatic / Implicit SubShapeBinders

One alternative discussed in the forum is the automatic creation or injection of SubShapeBinders to bridge geometry across Bodies without forcing the user to manually place them. The idea: when a feature in Body B refers to geometry in Body A, the system would auto-insert a SubShapeBinder behind the scenes.

**Reasons this alternative was considered but ultimately rejected:**

- **Implicit magic is hard to reason about**: Users may become confused when a SubShapeBinder appears without their action. It obscures the dependency graph, making debugging harder.
- **Performance & dependency complexity**: Automatically inserting binders on demand can introduce complex dependency chaining and evaluation ordering. Maintaining consistency (particularly in recompute, editing upstream references, or undo/redo) becomes more delicate.
- **Explicitness is preferable in CAD**: CAD users often prefer to know and control their reference links explicitly. Implicit binders risk introducing hidden dependencies that surprise or confuse users.

## Future Work

## References

- PR: [FreeCAD#23610](https://github.com/FreeCAD/FreeCAD/pull/23610)
- Forum discussion: [FreeCAD Forum Thread](https://forum.freecad.org/viewtopic.php?t=99744)

## Appendix

### Glossary

- **Body**: A container for PartDesign features.
- **Part**: A higher-level container providing a common coordinate system.
- **SubShapeBinder**: A proxy for referencing geometry across Parts.
- **GeoFeatureGroupExtension**: Base providing group behavior and link scoping.
