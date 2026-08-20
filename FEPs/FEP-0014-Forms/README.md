# FEP-0014 Subdivision-Surface Forms Workbench

| FEP-0014      |                                                                                               |
| -------------- | -------------------------------------------------------------------------------------------- |
| Type           | Core Change                                                                                  |
| Status         | Draft                                                                                        |
| Author(s)      | paddlestroke                                                                                 |
| Version        | 0.1                                                                                          |
| Created        | 2026-08-20                                                                                   |
| Updated        | 2026-08-20                                                                                   |
| Discussion     | Discord                                                                                      |
| Implementation | https://github.com/FreeCAD/FreeCAD/pull/32073                                                |

This FEP proposes adding the Forms workbench to FreeCAD.

Forms provides interactive subdivision-surface modeling based on a low-resolution polygonal control cage. The editable cage is stored parametrically in the FreeCAD document and converted during recompute into an Open CASCADE Technology (OCCT) BRep surface or solid.

The workbench is intended for free-form product modeling, concept modeling, ergonomic shapes, transitions, and other geometry that is cumbersome to construct as a sequence of conventional sketches and analytic features. Its output remains normal FreeCAD BRep geometry and can therefore participate in Part Design and other downstream workflows.

## Motivation

FreeCAD provides strong parametric solid, sketch, surface, and mesh modeling tools, but it does not currently provide an integrated subdivision-surface workflow comparable to the Form or Sculpt environments found in other CAD applications.

Organic or continuously changing product shapes are possible with existing FreeCAD tools, but often require manually constructing and maintaining many curves, surface patches, constraints, and continuity relationships. This is powerful for precision surfacing, but it is not an efficient replacement for direct control-cage modeling.

A subdivision workflow complements these tools by allowing a user to:

- begin with a simple primitive or open surface;
- manipulate a small number of control vertices, edges, and faces;
- refine only the regions that need additional detail;
- introduce sharp or semi-sharp features;
- create openings, bridges, extrusions, and thickness;
- convert the result into a standard BRep for use elsewhere in FreeCAD.

The proposal is not intended to replace Part Design, the Surface workbench, curve-based modeling, or Class-A surfacing. It fills a separate modeling role between conceptual polygon modeling and precise BRep-based CAD.

Keeping this capability in FreeCAD also avoids workflows in which users must create free-form geometry in an external application, export it through a mesh or neutral file format, and lose its editable construction data.

## Rationale

### Why Forms is a separate workbench

Control-cage modeling has a substantially different interaction model from conventional FreeCAD feature editing.

A Forms editing session requires:

- persistent vertex, edge, face, loop, and whole-form selection modes;
- direct manipulation with move, rotate, and scale handles;
- topology tools that operate on the cage rather than on the generated BRep;
- local refinement and semi-sharp subdivision data;
- interactive previews that do not recompute an expensive BRep on every pointer movement;
- specialized task panels, selection gates, keyboard modifiers, and viewer overlays.

Adding all of these controls directly to Part Design or Surface would mix distinct modeling concepts and considerably enlarge their interfaces. A dedicated workbench gives subdivision modeling a coherent workflow while keeping its generated geometry interoperable with the rest of FreeCAD.

The separation is therefore primarily a user-interface and data-model boundary, not an interoperability boundary. Forms objects are normal document objects, and their generated shapes are standard `Part::TopoShape` values.

### Editable cage and generated BRep are separate representations

The control cage is the authoritative editable representation. The generated BRep is an evaluated result.

This distinction is important because BRep topology is not a suitable persistence format for subdivision control data. Rebuilding a surface can change the number or ordering of BRep faces, edges, and vertices, while the logical cage can remain unchanged.

Forms consequently persists:

- control points;
- control faces;
- vertex and edge sharpness;
- symmetry settings;
- local control points;
- hierarchical refinement topology;
- associative matching information;
- BRep conversion tolerance and status.

The generated `Shape` can be consumed by other workbenches without making the editable cage dependent on transient OCCT subelement numbering.

### Python-first implementation

The initial implementation uses `FeaturePython` objects, Python command classes, Python view providers, Qt Designer task panels, and existing FreeCAD geometry and viewer APIs.

This has several benefits:

- the implementation remains localized to the workbench;
- document behavior can be reviewed without introducing a new native object hierarchy;
- topology algorithms and persistence formats can mature before becoming a compiled API;
- the implementation uses existing FreeCAD transaction, recompute, selection, and serialization mechanisms;
- native code can be introduced later for a measured performance requirement rather than pre-emptively.

A native component should only be introduced if profiling demonstrates that the numerical evaluator cannot meet interactive or recompute requirements in Python. In that case, only the evaluator should need to move to a native Forms module; the document model and user interface can remain unchanged.

## Specification

### Scope

The initial Forms workbench provides standalone Forms features and Part Design-integrated additive and subtractive Forms.

Supported starting forms include:

- Box;
- Cylinder;
- Quadball;
- Sphere;
- path-driven Pipe;
- Face, optionally initialized from a face or closed profile;
- Torus;
- hollow Tube.

A primitive initially remains parameter-driven. Once it is converted to editable mode, its control cage becomes authoritative and its primitive dimensions are locked to prevent conflicting sources of geometry.

The editor provides control-point, edge, face, and whole-form selection, together with translation, rotation, and scaling. Transform orientation can be based on global, view, or selection coordinates. A temporary pivot can be placed using FreeCAD snapping, and persistent symmetry can be enabled on a local principal plane.

Topology and shape-editing operations include:

- face and boundary-edge extrusion;
- local and loop edge insertion;
- point insertion;
- face subdivision;
- face deletion;
- edge dissolution;
- hole filling;
- boundary bridging;
- erase and fill;
- weld and unweld;
- crease and uncrease, including semi-sharp weights;
- straighten;
- flatten;
- boundary matching;
- thickening of open Forms.

Each completed modeling action creates an independent FreeCAD transaction and undo step. Cancelling an edit session restores the state from before the session began.

### Document model

Standalone Forms use `Part::FeaturePython` document objects.

Their proxies share a common lifecycle for property creation, recompute, restoration, migration, parameter locking, and BRep generation. Primitive-specific proxies provide only their parameters and initial topology.

The base control cage is stored using standard FreeCAD properties such as `App::PropertyVectorList` and `App::PropertyStringList`.

Locally refined topology is stored as a versioned hierarchical T-mesh. Logical faces use stable identifiers, explicit parametric sides, dyadic parameter intervals, and independently stored local control points. Topology edits construct and validate a replacement mesh before assigning it to the document object, so a failed operation does not expose a partially modified mesh.

Property and topology version fields provide a migration boundary for future document-format changes.

### Subdivision and BRep conversion

Forms evaluates Catmull-Clark subdivision surfaces, including extraordinary vertices and semi-sharp control elements.

Local refinement is represented by a hierarchical T-mesh. The current evaluation strategy uses nested uniform Catmull-Clark levels and retains one fitted root surface for each original control face. Logical refined leaves are represented as parameter-space trims of that root surface.

The converter:

1. validates that the cage is suitable for an open surface or closed solid;
2. evaluates Catmull-Clark limit samples;
3. fits cubic B-spline patches;
4. validates the fitted surfaces against a denser set of subdivision samples;
5. trims locally refined patches where necessary;
6. sews the patches using OCCT;
7. validates the resulting shell or solid.

The document records the requested tolerance, achieved maximum deviation, refinement level, and conversion status. Invalid or non-manifold input is reported rather than silently producing an invalid result.

Interactive cage movement and topology previews operate on viewer geometry. Full BRep conversion is deferred until an operation is committed or a recompute is otherwise required.

### Interaction with Part Design

Forms can be used in two ways:

- as a standalone form that generates a BRep surface or solid;
- as an additive or subtractive feature inside a Part Design Body.

Part Design exposes Additive Form and Subtractive Form command groups for the supported primitives.

A Part Design Form stores:

- the preceding Body feature;
- the independent Form tool shape;
- its additive or subtractive operation;
- its placement relative to the Body;
- the final combined result and a human-readable combination status.

While the Form is being edited, the preceding feature and the independent Form tool are displayed separately. When editing finishes, a closed intersecting Form is fused with or cut from the preceding feature.

If the Form is open, disjoint, or would produce an invalid multi-solid result, the geometry is retained and a diagnostic status is reported. The editable cage is not discarded merely because the Boolean operation is not yet valid.

Standalone Forms can also be moved into a Body and converted into additive features while preserving their editable control data and global placement.

### Associative matching

The Match tool associates one complete Form boundary with an external face or closed wire.

The association is stored as a standard `App::PropertyLinkSub`, together with ordered boundary controls and normalized support parameters. On recompute, the boundary is evaluated against the linked support.

Connected continuity is supported for general compatible boundaries. Tangent continuity is supported where the selected face, adjacent faces, or planar wire provide the required tangent information.

This permits an editable Form to remain a separate feature while following changes to conventional FreeCAD geometry.

### Topological naming

Forms does not use generated BRep vertex, edge, or face numbers as the authoritative identity of its control cage.

Control-cage topology is persisted independently. Locally refined T-mesh faces and vertices use stable logical identifiers, allowing unaffected cage regions to retain their identity when another region is refined.

For the generated BRep, Forms preserves the element history produced by OCCT and FreeCAD operations. It does not replace an existing element map with Python-generated names. A basic element map is initialized only when a producer returns a completely unmapped shape.

Associative references use FreeCAD link-subproperties and therefore participate in FreeCAD’s normal topological naming mechanisms. The editor accepts both simple and mapped subelement names and resolves their current terminal `Vertex`, `Edge`, or `Face` token when mapping a BRep selection back to cage controls.

This design has three consequences:

- cage editing does not depend on incidental BRep element ordering;
- downstream features receive a normal mapped `TopoShape`;
- Forms does not introduce a competing custom topological naming system.

As with other topology-changing CAD operations, an edit that logically deletes or replaces a referenced region can invalidate a downstream reference. The proposal aims to preserve references to unchanged regions, not to claim that arbitrary topology replacement can preserve every reference.

### Dependencies

Forms introduces no new external runtime dependency.

The application-side implementation uses:

- FreeCAD App and document APIs;
- the Part module and OCCT for BRep creation, fitting, sewing, validation, and Boolean operations;
- standard Python modules;
- FreeCADGui and PySide/Qt for commands and task panels;
- pivy/Coin3D for interactive control-cage rendering, previews, sensors, and transform draggers;
- Part Design APIs for additive and subtractive Body integration.

All of these are existing FreeCAD dependencies. The subdivision and T-mesh algorithms are implemented within the Forms module and do not depend on OpenSubdiv, a separate mesh library, NumPy, or another third-party geometry kernel.

A headless build can load and test the document and geometry portions without loading the GUI-specific command and interaction modules.

### Implementation requirements

The following implementation boundaries are intentional:

- Cage topology must remain independent of generated BRep topology.
- Persisted topology formats must be versioned.
- Topology operations must validate their complete result before changing document properties.
- Interactive previews must avoid unnecessary BRep reconstruction.
- Commands must use FreeCAD transactions and produce predictable undo/redo behavior.
- Edit-session cleanup must be safe and idempotent.
- Selection observers, document observers, Coin sensors, dragger callbacks, timers, event filters, selection gates, and temporary scene nodes must be removed when editing finishes or fails.
- Existing OCCT and FreeCAD element history must be preserved.
- Common primitive persistence and recompute behavior must remain in shared proxy infrastructure.
- Native code should be localized to numerical evaluation if it becomes necessary.

### Impact on existing features / subsystems

The proposal adds a new workbench and its document objects without changing the modeling behavior of existing Part, Surface, Mesh, or Part Design features.

Part Design receives command and view integration for additive and subtractive Forms. The resulting objects use standard Part Design additive and subtractive Python feature types and participate in the Body feature history.

Generated Forms shapes can be used by downstream systems that accept normal BRep geometry. Open Forms can be consumed as faces or shells; closed Forms can produce solids.

The workbench registers its own commands, resources, task panels, and unit tests. GUI-specific files are loaded only when FreeCAD is built with GUI support.

### Backwards Compatibility

This proposal is additive. Existing documents, commands, workbenches, and modeling workflows are not modified by the presence of Forms.

Forms documents use standard FreeCAD document properties and `FeaturePython` serialization. The generated `Shape` is stored as a normal `Part::TopoShape`.

The Forms Python proxy must be available to recompute or edit a Forms feature. If it is unavailable, the last saved BRep remains ordinary stored document geometry, subject to FreeCAD’s normal behavior for unavailable Python proxies.

Persisted control-cage and T-mesh representations contain explicit version information. Restoration code adds missing properties and migrates older supported representations where required.

Once released, incompatible changes to persisted cage or T-mesh data will require an explicit migration path. Existing property meanings must not be silently reinterpreted.

## Rejected Ideas

### Implement Forms directly inside Part Design

Part Design integration is important, but the Forms editing model is not limited to additive or subtractive solid features. Forms also supports standalone objects and open surfaces.

Placing the complete editor inside Part Design would couple cage operations to Body semantics and would expose specialized subdivision tools in a workbench intended primarily for feature-based solid modeling.

The adopted design keeps the editor independent while providing native additive and subtractive entry points in Part Design.

### Treat a polygon mesh as the final result

A mesh-only result would be easier to generate, but it would reduce interoperability with the rest of FreeCAD. Most downstream CAD features expect BRep faces, shells, or solids.

Forms therefore stores a polygonal control structure but evaluates it into OCCT BRep geometry.

### Store only the generated BRep

Recovering an editable subdivision cage from an arbitrary BRep is not reliable. BRep regeneration can also change subelement organization without changing the intended cage.

The cage must remain explicit and authoritative in the document.

### Introduce custom Python topological names

Replacing OCCT and FreeCAD element history with Python-authored names would create a second naming system and could discard operation history already attached to a `TopoShape`.

Forms instead preserves native element maps and maintains separate stable identities only for its internal cage topology.

### Require an external subdivision library

An external library would add packaging, licensing, platform, and maintenance concerns. The current implementation is feasible using FreeCAD’s existing Python and OCCT stack.

A future optimized evaluator can be introduced as a localized native component without changing the public document model.

### Implement the complete system in C++ initially

The principal risks in the initial work are interaction design, topology semantics, persistence, and BRep conversion—not Python call overhead.

A Python-first implementation makes those decisions easier to review and evolve. Native optimization remains possible after profiling identifies an actual bottleneck.

## Implementation

A working implementation accompanies this proposal.

It includes:

- the Forms Python workbench;
- standalone primitives and shared feature-proxy infrastructure;
- the interactive cage editor;
- topology and modification commands;
- Catmull-Clark and hierarchical T-mesh evaluation;
- OCCT BRep conversion and validation;
- Part Design additive and subtractive integration;
- associative boundary matching;
- document restoration and migration handling;
- automated geometry, topology, persistence, command, and edit-lifecycle tests.

The implementation deliberately separates the major responsibilities:

- feature proxies own persistence and recompute behavior;
- the canonical cage and T-mesh modules own topology validation;
- the BRep module owns subdivision evaluation and OCCT conversion;
- the edit session owns selection, draggers, transactions, and cleanup;
- individual edit tools own their task panels, previews, and commits;
- Part Design integration is confined to additive/subtractive feature and command boundaries.

This separation is intended to keep future topology tools from duplicating viewer, transaction, persistence, or conversion infrastructure.


## FAQ

### Is Forms intended to replace the Surface workbench?

No. The Surface workbench constructs and modifies explicit CAD surfaces. Forms provides direct subdivision control-cage modeling. The two workflows are complementary, and Forms produces BRep surfaces that can be used by downstream surface tools.

### Is Forms intended for Class-A surfacing?

Not in its initial scope. Class-A patch layout, curvature constraints, and advanced surface analysis require a related but distinct workflow. Forms may later share reference and analysis tools with such a workflow.

### Does Forms produce meshes?

The editable cage is polygonal, but the primary evaluated output is an OCCT BRep surface, shell, or solid. A mesh is not used as the document’s final CAD result.

### Can Forms be used with Part Design?

Yes. Forms can create additive and subtractive features inside a Body. Standalone Forms can also be converted into additive Body features.

### Does it add another geometry dependency?

No. It uses dependencies already required by FreeCAD: OCCT through Part, Qt/PySide, and Coin3D through pivy.

### Why not convert every drag event into a BRep?

BRep fitting and sewing are substantially more expensive than updating control-cage viewer geometry. Deferring conversion preserves interactive manipulation while still producing a validated BRep when an operation is committed.

### Are Forms objects parametric?

Yes. Initial primitives are parameter-driven, and Forms features recompute inside the FreeCAD document graph. After conversion to editable mode, the persisted control cage becomes the parameterization of the object.

## Further Work

Potential follow-up work includes:

- soft selection with geometric and topological falloff;
- grow, shrink, ring, loop, and shortest-path selection;
- numerical transform entry and additional snapping;
- smooth, relax, slide, bevel, pull, and project operations;
- more flexible merge and weld operations;
- bridge operations for unequal boundaries and guided transitions;
- additional primitive and sketch-driven creation tools;
- richer internal, circular, and duplicate symmetry;
- conversion from suitable meshes or NURBS geometry;
- documented control-cage import and export;
- non-manifold, self-intersection, and extraordinary-vertex diagnostics;
- zebra, curvature, reflection-line, and draft analysis;
- performance profiling and, if justified, a localized native evaluator.

These are extensions rather than requirements for the initial architectural proposal.

## Changelog

### 0.1 - 2026-08-20

- Initial draft.
- Defined the Forms scope and its separation from Part Design and Surface.
- Documented the control-cage and BRep architecture.
- Documented Part Design integration, topological naming, dependencies, persistence, and implementation requirements.

## References

- Catmull, E. and Clark, J., “Recursively generated B-spline surfaces on arbitrary topological meshes,” *Computer-Aided Design*, 1978.
- Kovács, D., Bisceglio, J., and Zorin, D., “Dyadic T-mesh subdivision,” *ACM Transactions on Graphics*, 2015. DOI: 10.1145/2766972.

## License / Copyright

All FEPs are explicitly [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/).
