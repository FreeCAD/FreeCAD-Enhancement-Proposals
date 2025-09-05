# FEP-00XX — PartDesign Multibody: direct cross-Body references in a unified Part coordinate system

**Status:** Draft  
**Type:** User Experience / Core Data Model  
**Created:** 2025-09-05  
**Author(s):** Walter Steffe (@wsteffe)  
**Champion(s):** (tbd)  
**Related PR(s):** FreeCAD PR #23610 (PartDesign: all entities in the same coordinate system; disable Body/Compound Placement)  
**Discussion:** PR thread (and forum topic, tbd)  
**Process reference:** FEP-0001 (FEP process)

---

## Summary (what users get)

Bring **multibody part modeling** in FreeCAD’s PartDesign closer to mainstream CAD expectations:

- Inside a **Part**, every **Body** shares the **same coordinate system** (single frame).  
- In Sketcher and PartDesign, you can **directly reference geometry from other Bodies in the same Part** (edges, faces, datums)—**no mandatory SubShapeBinder** hops.  
- **Body.Placement** is **hidden in the UI** (retained only for backward-compatibility and migration); **Compound** placement is **deactivated** for modeling. To reposition, users **move features** (e.g., a “Transform Tip” workflow) or **move the Part**.  
- Existing projects **open unchanged visually**: a one-time migration preserves world geometry and clears container placements.

---

## Motivation (why users care)

**Multibody modeling** is a well-established workflow in modern CAD (CATIA, SolidWorks, Inventor, etc.). Designers expect to:

- put a master sketch or datum in one Body and **drive features in another**,  
- **reference faces/edges across Bodies** directly in Sketcher/PartDesign,  
- keep everything **parametric** without proliferating proxy objects.

In current upstream FreeCAD, per-Body/Compound `Placement` produces **multiple local frames**, so Sketcher/PartDesign often **blocks or complicates** cross-Body references. Workarounds (binders) add indirection, maintenance, and confusion; if cross-Body referencing is precluded or cumbersome, **the multibody environment loses its main advantage** over assembling separate, single-Body parts.

This FEP proposes the most user-intuitive fix: **one coordinate system per Part** + **direct cross-Body references** inside that Part. SubShapeBinders remain available when you **cross Parts**.

---

## Goals & non-goals

**Goals**
- Enable **direct** cross-Body references within the **same Part** (Sketcher external geometry, feature references).  
- Remove the mental tax of “which frame am I in?” by eliminating per-Body transforms.  
- Keep old files visually identical via automatic migration.

**Non-goals**
- Replace Assemblies or inter-Part linking. Cross-**Part** references still use SubShapeBinder/Link.  
- Change feature-level placements beyond what’s needed for a clean “Transform Tip” story.  
- Affect non-PartDesign workbenches except where they relied on Body/Compound placement semantics.

---

## User stories (before → after)

1) **Aligning holes across Bodies**  
   - *Before:* create binder(s) or copy geometry; fragile when containers move.  
   - *After:* in a Sketch for Body A, **external-reference** an edge/face in Body B directly and constrain.

2) **Master sketch drives multiple Bodies**  
   - *Before:* share via binders or duplicated datums; transforms fall out of sync.  
   - *After:* place the master sketch in the Part; Bodies read from it directly.

3) **Move a Body’s final result**  
   - *Before:* tweak `Body.Placement` (risk breaking references).  
   - *After:* use **feature-level transforms** (e.g., a Transform-Tip) or **move the Part** if the intention is assembly-like.

---

## Specification (what changes)

### 1) Coordinate system policy
- Inside **App::Part**, all **PartDesign::Body** children **share the Part’s coordinate system**.  
- The Body “Origin” concept is removed (or retained as a non-transform UI placeholder if needed for compatibility).

### 2) Container placements
- **Body.Placement** is **hidden in the UI**. It remains programmatically accessible **only for migration and legacy scripts**; **writes have no modeling effect** after migration (optionally warn).  
- **Part::Compound** placement is **deactivated** for modeling to avoid conflicting frames.  
- **App::Part** placement remains available to move the **whole Part**.

### 3) Cross-Body references
- Sketcher and PartDesign treat Bodies inside the same Part as the **same frame**, so **direct references** are allowed and robust.  
- Cross-**Part** references are unchanged (use SubShapeBinder/Link).

### 4) Migration (one-time, on file open)
For any Body with legacy non-identity `Placement`:

1. **Bake Body transform into the result**  
   - Wrap the Body Tip with a **SubShapeBinder** whose `Placement` equals the legacy Body placement.  
   - Set binder `Relative=False` (when present).  
   - Make the binder the **new Tip**.

2. **Fix inter-Body binders**  
   - For a binder that lived in old `B₁` and referenced geometry in old `B₂` with placements `T₁` and `T₂`, update the binder placement by  
     **`T₁₂ = T₂ · T₁⁻¹`**,  
     then it still lands in the same world place after Bodies become identity.

3. **Clear container placements**  
   - Set all Body placements to identity and recompute.  
   - World geometry remains unchanged.

*(A reference implementation exists in PR #23610 and has been locally validated by an automated test: world bounding boxes preserved; Body placements become identity; Tip becomes a SubShapeBinder with `Relative=False` when present.)*

---

## UX changes (how it feels)

- **Body/Compound placement in UI**  
  - **Body.Placement** is **hidden**. It’s still readable via Python for migration/legacy, but a **write** is a no-op post-migration (optionally warns).  
  - **Compound** placement is **disabled** for modeling.  
  - **Part** placement remains for moving everything.

- Provide/extend a **Transform-Tip** action so users who previously “nudged a Body” can nudge the **final result** explicitly, without re-enabling Body.Placement.

- In Sketcher, selecting external geometry from another Body in the same Part is **first-class** (no auto-injected binders).

- Documentation: “Multibody modeling in PartDesign—best practices” (master sketch, datums, direct references, Transform-Tip).

---

## Backward compatibility

- Automatic migration keeps shapes visually identical.  
- SubShapeBinder workflows continue to work; they’re just **not required** within one Part.  
- Python API: `Body.Placement` remains readable for migration/legacy scripts; **setting it** post-migration is a **no-op** (optionally logs a deprecation message guiding users to Transform-Tip/feature transforms or moving the Part).

---

## Software design rationale (separation of concerns)

- **Single source of truth:** “Inside a Part, all Bodies share one coordinate system.”  
- **Layering:** the **data model** enforces the frame; **solvers/features** don’t compose container transforms.  
- **Explicit intent beats implicit magic:** if you want a result moved, use Transform-Tip (explicit) or move the Part (explicit).  
- **Maintainability:** fewer moving parts across modules; easier to reason about references and debug user models.  
- **Extensibility:** new features and external WBs don’t need bespoke placement plumbing—direct references “just work”.

---

## Alternatives considered

### A) Auto-create binders for every cross-Body reference
- **Pros:** reduces manual steps.  
- **Cons:** preserves multiple frames; hides indirection; increases graph complexity and maintenance.  
- **Status:** Rejected—paper-over, not fix.

### B) Keep Body placement and “improve” reference resolution
**Idea:** Preserve per-Body `Placement`, and teach Sketcher/PartDesign to auto-translate every cross-Body reference by composing container and Body transforms at use-time.

**Why reject:**
- **Hidden complexity & fragility:** every reference/constraint depends on a live chain of transforms; harder to debug.  
- **Solver/perf impact:** solvers must maintain/propagate transforms for each reference.  
- **UI mismatch:** a movable Body (`Placement`) conflicts with the “one frame per Part” mental model; users remain confused.  
- **Modularity violation:** leaks placement mechanics into higher layers—Sketcher/features must know container transforms, creating **tight coupling** and **leaky abstractions**. Cross-WB consumers must replicate the same logic.  
- **Net effect:** a half-step toward auto-binders; doesn’t deliver the simplicity users expect.

### C) Go “all-Link everywhere”
- **Pros:** powerful generalization.  
- **Cons:** heavier than needed for this specific PartDesign workflow issue.  
- **Status:** Out of scope for this FEP.

---

## Risks & mitigations

- **Users who relied on Body placement** to “move” solids inside a Part  
  - *Mitigation:* Transform-Tip and documentation; migration preserves results.  
- **Other workbenches** that read Body/Compound placement  
  - *Mitigation:* scope change to PartDesign modeling and Part contexts; coordinate early with maintainers if any downstream relies on Body placement values.

---

## Performance considerations

- Migration is O(N) over bodies and inter-Body binders.  
- After migration, the model graph removes nested container transforms, which can simplify recomputes and reduce failure cases from mis-framed references.

---

## Acceptance criteria (how we’ll know it’s good)

1) In a Part with Bodies A and B, a Sketch in A can **reference** an edge/face/datums in B directly (no binders); constraints solve.  
2) Opening legacy files **preserves** world-space bounding boxes and clears Body placements to identity.  
3) A **Transform-Tip** (or equivalent) lets users reposition a Body’s final result without re-enabling Body placement.  
4) Documentation covers the new multibody best practices.

---

## Rollout plan

- Land PR with migration + disabled UI + tests (bounding-box invariance; cross-Body reference cases).  
- Update wiki/docs and add a “What changed in multibody modeling” guide.  
- Encourage addon authors to avoid depending on Body placement; provide a small API note.

---

## Open questions

- Exact UI affordance for **Transform-Tip** (new command vs. extending Transform).  
- Whether to keep a read-only `Placement` field visible on Body for UI continuity (always identity post-migration) vs. fully hidden (current state: hidden).  
- Any Draft/BIM nuances when a Part contains PartDesign Bodies (confirm unchanged).

---

## Appendix — Migration intuition & math

Let legacy placements be `T₁` for Body `B₁` and `T₂` for Body `B₂`.

- **Bake transforms:** Wrap each Body Tip with a SubShapeBinder carrying its `Tᵢ`; set `Relative=False`; set as Tip.  
- **Fix inter-Body binders:** For a binder living in `B₁` and referencing `B₂`, set binder placement to  
  **`T₁₂ = T₂ · T₁⁻¹`**  
  so it maps to the same world location once Bodies are identity.  
- **Clear placements:** Set Body placements to identity and recompute.  
- **Outcome:** world geometry unchanged; Bodies share one frame.

---

