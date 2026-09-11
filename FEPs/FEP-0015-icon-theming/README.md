# FEP-0015 Icon Theming

| FEP-0015       |                                                                                                 |
| -------------- | ----------------------------------------------------------------------------------------------- |
| Type           | Core Change                                                                                     |
| Status         | Draft                                                                                           |
| Author(s)      | Kacper Donat @kadet1090                                                                         |
| Version        | 0.1                                                                                             |
| Created        | 2026-09-09                                                                                      |
| Updated        | 2026-09-09                                                                                      |
| Discussion     | n/a                                                                                             |
| Implementation | n/a                                                                                             |

Defines a new solution for icon themes and recolored pixmaps in FreeCAD.

## Motivation

FreeCAD resolves icons by name today, but nothing about that resolution is configurable.
`BitmapFactoryInst::pixmap()` walks a fixed sequence -- an absolute path, then the `icons:` Qt
search path with a fixed list of extensions, then an optional external theme directory -- and ends
at a hardcoded placeholder. Which file a name reaches is therefore a property of the compiled binary
and of whichever directories happen to be registered, not something a theme can state. While several
hacky solutions like addition of custom Qt Resources to replace some icons and alter search path
exists, none of them is fully supported in core.

The icon support in FreeCAD in general has few important drawbacks:
- **An icon set cannot be easily swapped.** Shipping a second look for FreeCAD means replacing files
  in place or using custom qt resources -- which does not always work reliably.
- **Icons are tightly coupled with filename.** Icon names are based on files and uses are not always
  semantic - a different features can use icon from outside of its domain because it looks good,
  even if semantically it does not make sense.
- **Icon appearance cannot follow the interface theme.** It's not possible to use icons based on
  stroke as it's not possible to recolor the icons for specific use. Theme developers need to
  provide variants of icons for dark and light modes now. Icons cannot also include accent colors.
- **Stroke weight cannot follow icon size.** Same goes for the icon stroke - stroke thickness at
  different sizes is perceived visually in a different way. 2px stroke at 64px feels thin, but 2px
  stroke at 16px is huge.

There are also other defects that follow from the same fixed pipeline. Every SVG is rendered at a
hardcoded 64x64 regardless of the size that will be drawn -- while it's good enough normally because
we don't use larger icons it is still a design flaw.

## Rationale

This FEP proposes making FreeCAD's icon set a themeable declarative resource. A declarative icon
theme file would state how an icon name maps to a file and how that file is processed before it is
drawn, so that an icon set could be replaced, recolored or restroked without recompiling and without
editing the several hundred call sites that ask for icons by name.

Icon lookup is currently compiled in: `BitmapFactoryInst::pixmap()` walks a fixed sequence of
extensions over the `icons:` search path and ends at a hardcoded placeholder. Anything a theme needs
to change about that has to be expressible in a file it ships, since theme authors do not rebuild
FreeCAD. The freedesktop icon theme specification takes the same approach with `index.theme`.

Names are resolved by ordered rewrite rules rather than by a name-to-file table or a list of search
directories. A table is impractical: FreeCAD has several thousand icon names, and enumerating them
would fix in place the accidental sharing described above rather than give a theme a way to undo it.
A directory list is what exists today and cannot rename anything — each directory registered through
`addPath()`, of which Part alone registers four, is searched for every icon name in the application
rather than for the icons it contains. Rewrite rules express a family redirect, a catch-all and a
single remapping with one construct, and decouple the requested name from the answering file.

A rule applies only when its search paths resolve to a file that exists. Icon sets are typically
partial, and on a name match alone a rule matching `PartDesign_(.+)` would blank every PartDesign
icon the theme had not drawn. The existence condition bounds a rule to what it has artwork for and
lets the remainder fall through, which is also what makes a workbench-scoped rule safe to leave
registered permanently. This also allows for graceful degradation - if some new icon is not yet
created in the set we are currently using - it will fallback to the default rule and not apply
potentially wrong processing rules.

The suggested solution also allows theme authors to apply specific overrides to icons and remap them
to something else. For example author can define one file that defines a representation of a box.
With palette change that icon can be used both for Surface workbench (Surface_Box - with yellow
color), Part (Part_Box - with blue color) and as generic object icon (leaving it gray).

Rules arrive from the icon theme, (including the files it inherits) and from any workbench that
registers one, so consultation order cannot be load order - module load order varies with the
installed addons. Modules are expected to provide defaults to serve as fallback for icon resolution
- just like it is now. Explicit priorities, and a tier holding contributed rules below everything
the theme declares, make the winner a function of what was written rather than of when it was read.

### Icon processing

The solution also introduces icon Recoloring at the runtime that removes need for themes to provide
a light and a dark drawing of each icon. Line-art sets are drawn in `currentColor`, an SVG keyword
under which an element takes the color its context supplies, leaving each icon exactly one color to
substitute. Substitution also permits accent-colored icons, which pre-drawn variants cannot express.
Icons with literal colors are unaffected unless a manifest lists substitutions for them.

Stroke weight needs a separate mechanism because the problem is perceptual rather than geometric:
2px reads as thin at 64px and heavy at 16px, so no single drawing scales correctly across sizes.
Weights are declared per size bucket rather than derived from the requested size, which matches both
how a set is authored and the per-size directories of the freedesktop specification.

The proposal does not try to define all possible ways of processing (be it pre- or post-processing)
icons but provides a initial set of possible to apply effects that can be expanded later if needed.
Altering a stroke, changing current color or swapping the palette are only examples of possible
processing steps and more can be introduced if needed.

### Re-rendering icons at runtime

Recoloring one rendering requires recovering the source file from an already drawn pixmap. Qt's
styling entry points hold a `QPixmap` without the `QIcon` behind it - `QStyle::generatedPixmap()`
receives a pixmap and returns a variant of it - because Qt assumes variants are produced by
filtering, a blue tint for selected or desaturation for disabled. Filtering suits bitmaps and not
stroke artwork, where the required result is the same drawing rendered again in another color.

Which color a widget's icon takes is left to the style system. An icon theme cannot know that an
icon sits on a primary button or a hovered row, and answering it here would either duplicate the
token machinery or constrain it. This FEP proposes the mechanism; the policy is expected in a
separate FEP.

The icon theme carries its own preference rather than belonging to the interface theme because the
two vary independently: an icon set is wanted under whichever interface theme runs, and an interface
theme need not ship one, though it may suggest one.

Designs set aside -- icon rules inside the interface theme file, inferring a name from a path by its
shape, and resolving the theme's expressions once at load time — are discussed under [Rejected
Ideas](#rejected-ideas) and [Alternatives](#alternatives).

## Specification

Three things are specified: the manifest that describes an icon set, `Gui::IconManager`, which reads
it and answers requests for icons, and `Gui::ParametrizedIconEngine`, the `QIconEngine` that renders
through the manager so an icon reflects the manifest each time it is drawn rather than at the moment
it was created. The remainder of this section describes them in the present tense, as a
specification of what would hold were the proposal adopted.

### The icon theme file

An icon theme is a YAML file at `qss:icons/{IconTheme}.yaml`, where `IconTheme` comes from the
`BaseApp/Preferences/Bitmaps/Theme/IconTheme` preference. Icon themes can be base on other themes
using the `_inherits` mechanism that merges multiple files together.

```yaml
_inherits: [defaults.yaml]

defaults:
  searchPaths:
    - ":/icons/{}.svg"

  processing:
    svg:
      strokeColorSwap: "@BaseTextColor"
      strokeAdjustment:
        - stroke: 2px
          select: "path, line, circle"

  sizes:
    16px:
      processing:
        svg:
          strokeAdjustment:
            - stroke: 1.5px

rules:
  - match: "PartDesign_(.+)"
    priority: 10
    searchPaths:
      - ":/icons/pd/$1.svg"
    processing:
      svg:
        paletteSwap:
          "#000000": "@AccentColor"

icons:
  PartDesign_Body: ":/icons/pd/body-filled.svg"
  PartDesign_Pad: Part_Extrude
  Std_Refresh:
    searchPaths: [":/icons/tabler/outline/refresh.svg"]
    processing:
      svg:
        strokeColorSwap: "reset()"

missing: "help-browser"
```

A rule states which icon names it applies to, through an regular expression in specified `match`,
and defines `searchPaths` where the icon can possibly be found. As noted earlier, the search paths
are looked through in definition order. The `processing` section defines rules for processing the
icon. The solution allows overrides of the rules for specific `sizes` -- for example a different
processing or even a different search paths can be applied. Each rule also defines a priority -- so
when merging multiple files it is possible to still get proper rule order.

The `searchPaths` holds path templates. `{}` stands for the requested name and `$0` for the whole
match, while `$1`…`$n` are the capture groups of the enclosing rule's `match`; inside `defaults`,
which has no pattern, only `{}` and `$0` are available.

`priority` is an integer defaulting to 0, and rules are considered from the highest downwards. Ties
are broken toward the more derived file, so a file's own rules are considered before those it
inherits, and then by declaration order within a file.  The field exists so that rules gathered from
several files fall into a deliberate order rather than the order they happened to be loaded in.

Processing is keyed by source format. For now only `svg` is defined - but other processing options
can be introduced later if needed without need for separate FEP - so files in other formats resolve
and rasterize untouched. The key exists so that a future raster-processing block does not reshape
the file.

Every value in processing holds a style parameter expression rather than hardcoded value.
Expressions are evaluated at render (pixmap creation - not paint) time rather than at load time, so
an interface theme change recolors icons without the icon theme being reloaded or reparsed.

#### Baseline aka `defaults`

The `defaults` carries the general fallback if no rule is matched, and determines the baseline. If
some processing is defined in the defaults section - it will be applied for every icon, regardless
of the rule matched if not explicitly opted out by the rule.

#### Specific icon overrides

`icons` is the way to remap icons or provide specific overrides form them. It can be used to provide
a concrete mapping between semantic icon name and a file, or provide specific overrides for specific
icon A value written as a plain string is taken as a file if a file is there, and as the name of
another icon if not. `PartDesign_Body` above names a file; `PartDesign_Pad` names `Part_Extrude`,
which is then resolved exactly as though `Part_Extrude` had been asked for in the first place —
through its own override, the rules, and `defaults`. The two readings do not have to be told apart
by how the string looks, because the manifest already answers every question of this kind the same
way: try it, and if it is not there, carry on to the next possibility.

The longer form spells out what a bare string leaves implicit, and is what to use when the override
carries more than a destination:

```yaml
icons:
  Part_Cut:
    alias: Part_Boolean
    processing:
      svg:
        strokeColorSwap: "reset()"
```

An alias is followed from the top for the name it names, so it reaches whatever that name would have
reached, in any manifest. A chain that returns to a name already visited is abandoned with one
warning, and the original name carries on through the rules as though the override had not matched.

#### Others

The `missing:` key names the icon drawn when nothing resolves, replacing the hardcoded
`help-browser`.

### How a rule is chosen

A rule applies to a request when its `match` accepts the name *and* one of its search paths names a
file that exists. Both conditions are required: a rule that claims a family of names but ships no
artwork for the particular one being asked about does not take effect, and the next rule down is
tried instead. A theme may therefore override as much or as little as it has files for. There is no
risk of one rule affecting files from another - it is perfectly valid to have two rules that both
match for `PartDesign_(.+)` and refer to filled or outline icons - with different processing rules.

Within one manifest, the `icons` map is consulted first, then the rules in priority order, then
`defaults`. The first entry that satisfies both conditions is the applied one. It supplies the file,
and it is also the entry whose `processing` is used -- whatever found the icon is what styles it.

An `icons` entry is subject to the same two conditions as a rule. An override whose file is not
there is tried as an alias, and one that is neither a file nor a name anything answers to falls
through to the rules rather than leaving the icon blank. Since such an entry can only be a mistake
in the manifest, that is reported the first time the name is resolved.

When an alias supplies the icon, the entry that won for the aliased name supplies the processing
too, and the aliasing override is consulted ahead of it -- it is the more specific statement about
the icon that was actually asked for. `Part_Cut` above therefore takes `Part_Boolean`'s file and its
processing, less the recoloring it turns off for itself.

A rule that declares no `searchPaths` can never satisfy the second condition. That is a theme
authoring mistake rather than a way to style a family in place, and it is reported once when the
manifest is loaded.

Within the applied rule, its size bucket is consulted ahead of the rule itself, and the bucket may
contribute search paths of its own — which is how a set that ships a separate drawing at 16px offers
it. Size buckets are chosen by taking the nearest declared size at or above the requested one,
floored at the smallest declared bucket, so a layer declares a bucket only where something genuinely
differs. If the size requested is larger than largest bucket - defaults are used.

`processing` then resolves one key at a time, in the manner the style parameter system already
resolves a token: the applied rule's size bucket, then the applied rule, then `defaults`' size
bucket and `defaults`, and the first of those to declare a key supplies it. In the manifest above,
`PartDesign_Body` rendered at 16px takes `paletteSwap` from the rule, `strokeColorSwap` from
`defaults`, and `strokeAdjustment` from `defaults`' `16px` bucket. A rule that wants one
substitution changed says only that, and inherits the rest.

Suppressing an inherited value is the counterpart of declaring one. For a color, `"reset()"` is
already the expression that resolves to nothing, so `strokeColorSwap: "reset()"` leaves the icon
uncolored. For the structural keys the empty declaration does the same: `paletteSwap: {}` swaps
nothing and `strokeAdjustment: []` adjusts nothing, both distinct from omitting the key, which
inherits.

### Workbench fallbacks

A workbench describes where its own icons live by registering a manifest, from wherever it calls
`addIconPath` today:

```python
FreeCADGui.addIconRules(":/PartDesign/icons.yaml")
```

```cpp
IconManager::instance().addRules(":/PartDesign/icons.yaml");
```

The manifest uses the format already described. Only `icons`, `rules` and `defaults` are read from
it; `missing` belongs to the icon theme and is ignored, with a warning, if a contributed manifest
declares one. A workbench naming a handful of its icons exactly is the expected use of `icons`
there.

Everything a contributed manifest declares forms a tier strictly below everything the icon theme
says, its own `defaults` included — a contributed `icons` override outranks that manifest's own
rules, but never anything the theme provides. A workbench can therefore fill gaps but never override
the theme the user chose, whatever priority it writes. Within the tier, rules sort by `priority` and
then by the order their manifests were registered.

Because a rule applies only when it finds a file, a workbench has two ways to describe its icons. It
may name them, matching the family it owns; or it may point a catch-all at its own resource
directory and let existence do the filtering, which is the closest equivalent of the flat
`addIconPath` it replaces, but scoped so that the directory is consulted for its own icons rather
than for every icon in the application:

```yaml
rules:
  - match: "PartDesign_(.+)"
    searchPaths: [":/PartDesign/icons/$1.svg"]

  - match: "(.+)"
    priority: -10
    searchPaths: [":/PartDesign/icons/$1.svg"]
```

When a contributed rule supplies the file, `processing` resolves from that rule, then from its own
manifest's `defaults`, and then from the icon theme's. A workbench icon therefore still takes the
theme's stroke color and stroke weights unless the workbench deliberately says otherwise, which is
what keeps a contributed icon from looking foreign among themed ones.

`addIconPath` and `BitmapFactoryInst::addPath()` keep working and keep their meaning. They remain
the way to make a directory visible to the shipped catch-all templates, and a workbench that is
content with that need do nothing.

### Resolution pipeline

A request is a name, an optional size, a device pixel ratio, a `QIcon::Mode`/`QIcon::State` pair,
and an optional color override. It resolves in five stages.

1. The `icons` override for the name is tried first, then the rules in priority order -- for each
   whose `match` accepts the name, its size bucket's templates and then its own are expanded and
   tested for existence — and `defaults` last. A candidate that is an alias rather than a path
   restarts this stage for the name it gives, keeping a record of the names already tried so a cycle
   ends in a warning rather than a hang. The first file found settles both the icon and the entry
   that supplied it. `QFile::exists` resolves both `:/` resources and the `icons:` Qt search path
   that `BitmapFactoryInst::addPath()` populates, so templates reach module- and addon-registered
   directories without the resolver enumerating them.
2. If nothing is found, the external icon theme directory (`Bitmaps/ExternalTheme`, honoring
   `PreferExternal`) and then the XDG/Qt icon theme (`UseIconTheme`) are consulted, in the order
   those preferences describe. These remain coded stages rather than declarable rules, being
   directory-scanning lookups driven by their own preferences rather than path templates.
3. Failing both, the `missing:` icon is resolved through stage 1 once and non-recursively. A
   `missing:` that does not itself resolve yields a null icon and one warning.
4. The format is taken from the resolved file's extension, and the processing for that format is
   resolved key by key from the applied entry down to `defaults`.
5. Palette swap, stroke color swap and stroke adjustment run in that fixed order, and the result is
   rasterized at `size × devicePixelRatio`. The order is fixed rather than declarable because
   palette swap maps source colors and so must see the original document, while stroke color swap is
   defined over whatever still paints in `currentColor` afterwards.

Stages 1 through 4 depend only on the theme file and the request. They perform no painting and,
apart from the existence tests in stage 1, no I/O.

### Units

`Gui::IconTheme` is the parsed manifest: pure data and a loader, with no I/O and no painting. It
includes no Qt header at all, so it can be built and tested on its own.

```cpp
struct StrokeAdjustment {
    std::string select;
    double stroke;
};

/// What one layer says about processing. An unset member is inherited from the next layer down;
/// an empty one suppresses what would have been inherited.
struct SvgProcessing {
    std::optional<std::map<std::string, std::string>> paletteSwap;  // source color -> expression
    std::optional<std::string> strokeColorSwap;                     // replaces currentColor
    std::optional<std::vector<StrokeAdjustment>> strokeAdjustment;
};

/// What a rule, an override or `defaults` says, before any size refinement.
struct IconLayer {
    std::vector<std::string> searchPaths;   // templates; {} and $0..$n
    std::optional<SvgProcessing> processing;
};

/// A layer together with the buckets that refine it per rendered size. `defaults`, every rule and
/// every override has this shape, and buckets do not nest.
struct IconEntry {
    IconLayer base;
    std::map<int, IconLayer> sizes;
};

struct IconRule {
    std::regex match;
    int priority = 0;
    IconEntry entry;
};

/// An entry of the `icons` map. A plain string in the YAML sets both members, which is what makes
/// such a value a file when there is one and a redirect when there is not.
struct IconOverride {
    std::optional<std::string> alias;   // a name, resolved again from the top
    IconEntry entry;
};

enum class CandidateKind { File, Alias };

/// One thing to try, and the entry that proposed it.
struct IconCandidate {
    std::string value;                  // a path to test, or a name to resolve again
    CandidateKind kind;
    std::size_t source;
};

class GuiExport IconTheme
{
public:
    std::map<std::string, IconOverride> icons;  // exact-name overrides, ahead of every rule
    std::vector<IconRule> rules;                // sorted by priority when loaded
    IconEntry defaults;                         // applies when no rule does

    static IconTheme fromYaml(std::string_view yaml, std::string_view baseDirectory);
    static IconTheme fromFile(std::string_view path);

    /// Every path to try for @p name at @p pixelSize, in the order rules are considered.
    /// Which of them exists is the caller's business.
    std::vector<IconCandidate> candidates(std::string_view name, int pixelSize) const;
    /// The processing for the rule that proposed @p candidate, falling back to `defaults`.
    std::optional<SvgProcessing> svgProcessing(const IconCandidate& candidate, int pixelSize) const;
    std::string missingIcon() const;
};
```

The overrides are held as a map rather than as rules with literal patterns, so an exact name costs a
lookup instead of a walk through every pattern in the manifest.

Splitting the query in two is what keeps the theme free of file system access while still binding
the processing to the entry that supplied the file: `IconManager` walks the candidates, tests each
for existence, and asks for the processing of the one that won.

`Gui::IconManager` is the front door and the only stateful unit.

```cpp
struct IconMeta
{
    std::string iconId;
    std::string svgPath;
    bool themed = true;
};

struct RenderRequest {
    std::optional<QSize> size;     // unset: the file's natural size
    qreal dpr = 1.0;
    std::optional<QColor> color;   // unset: the theme's own color expressions
    QIcon::Mode mode = QIcon::Normal;
    QIcon::State state = QIcon::Off;
};

QIcon   icon(std::string_view name);
QIcon   iconFromFile(std::string_view path);
QPixmap pixmap(std::string_view name, const RenderRequest& request);
QPixmap pixmapFromFile(std::string_view path, const RenderRequest& request);

/// Re-renders an already produced pixmap from its source under @p request.
const IconMeta* metaForPixmap(const QPixmap& pixmap) const;
QPixmap render(const IconMeta& meta, const RenderRequest& request) const;

void reload();  // re-read the theme file, drop every cache
void clear();   // drop rendered pixmaps only
```

Names, paths and expressions are standard library strings throughout, and a Qt type appears only
where the thing being described is itself a Qt one: an icon, a pixmap, and the members of a render
request, every one of which is handed straight to Qt to rasterize with. Nothing in the manifest
layer needs Qt to express it, so nothing there uses it.

A name and a path are distinct arguments to distinct methods rather than one argument whose shape
decides its meaning. An unset `size` means the natural size, which is 64×64 for an SVG and the
file's own dimensions for a raster image; this reproduces what `BitmapFactoryInst::pixmap()` returns
today.

`Gui::ParametrizedIconEngine` is the `QIconEngine` the manager hands out. It holds an icon name or a
verbatim path and nothing resolved, asking the manager on every call, so a theme change alters what
an already-issued `QIcon` paints without anyone re-issuing it. Each pixmap it produces is registered
with the manager against the metadata it came from, which is what makes the recovery described under
[Recoloring](#recoloring) possible. It overrides `pixmap()`, `scaledPixmap()`, `actualSize()`,
`iconName()`, `key()`, `clone()` and `isNull()`.

`Gui::BitmapFactoryInst` gains the processing primitives as stateless members beside its existing
`pixmapFromSvg()`: apply a color map to SVG bytes, swap `currentColor` strokes and fills, scale
stroke widths under a selector, and rasterize at a size and device pixel ratio. The division of
labor is that `BitmapFactory` owns the mechanics and `IconManager` owns the decisions.

### Node selection

`strokeAdjustment.select` takes a small CSS-flavored selector, matched by walking the parsed
document:

```
selector-list := selector ("," selector)*
selector      := compound (" " compound)*        // descendant combinator only
compound      := tag? ("#" id | "." class | "[" name "=" value "]")*
```

Qt 6 provides no XPath engine -- `QXmlQuery` was removed and `QDomDocument` has no selector API — so
any selector language here is code FreeCAD writes and maintains. This subset covers what stroke
adjustment needs. Child, sibling and pseudo-class selectors are not supported, and adding one is a
change to this grammar rather than an escape hatch.

### Recoloring

`paletteSwap` maps colors appearing literally in the source document to expressions, while
`strokeColorSwap` names the color that replaces `currentColor`. Both are resolved for a given icon
by the walk described under [How a rule is chosen](#how-a-rule-is-chosen), so which rule supplies
them depends on which rule found the file.

A render request may carry a color. It takes the place of `strokeColorSwap` for that render only and
leaves `paletteSwap` untouched, so an icon with baked-in colors keeps them while a monochrome glyph
follows the caller.

A caller holding the `QIcon` can request a color directly. A caller holding only a `QPixmap`, which
is what Qt's styling entry points such as `QStyle::generatedPixmap()` are given, recovers the icon's
metadata from the pixmap's cache key through `metaForPixmap()` and re-renders from the source file
rather than filtering the bitmap it was handed. A pixmap the manager did not produce is not found,
and the caller proceeds as it otherwise would.

### Python API

`FreeCADGui` gains three functions. Two of them mirror the C++ surface:

```python
FreeCADGui.icon(name: str,
                color: str | QColor | None = None) -> QIcon

FreeCADGui.pixmap(name: str,
                  size: int | tuple[int, int] | None = None,
                  color: str | QColor | None = None,
                  mode: QIcon.Mode = QIcon.Normal,
                  state: QIcon.State = QIcon.Off) -> QPixmap
```

`icon()` returns a `QIcon` backed by `ParametrizedIconEngine`, wrapped for PySide through the
existing `PythonWrapper::fromQIcon()`. Because the engine resolves through the manager on every
call, such an icon renders at whatever size Qt asks of it and follows a later theme change without
being re-fetched. Size, mode and state are consequently not parameters here: they belong to a
particular rendering, not to the icon, and Qt supplies them at paint time.

`pixmap()` is where those parameters do apply, since asking for pixels settles all of them. An
omitted `size` means the natural size, as it does in C++.

`color` accepts a `QColor` or the string spelling of one, and overrides `currentColor` for that icon
exactly as the C++ request does. It does not accept a style parameter expression; deciding a color
from the theme is the subject of the separate FEP named under [Further Work](#further-work).

A third function registers a workbench's own rules, as described under [Workbench
fallbacks](#workbench-fallbacks):

```python
FreeCADGui.addIconRules(manifest: _Pathish, /) -> None
```

The existing `FreeCADGui.getIcon(name)` is unaffected and keeps its present meaning. It returns a
pixmap-backed `QIcon`, rendered once at the natural size in a fixed color, and remains the right
thing for code that wants a snapshot rather than a live icon. It gains theme resolution, since it
reaches `IconManager` through `BitmapFactory`, but not theme reactivity. `addIcon`, `addIconPath`
and `isIconCached` are likewise unchanged, `addIconPath` included: registering rules is an addition
beside it, not a replacement for it.

### Caching and invalidation

| Cache             | Key                                                           | Dropped by            |
| ----------------- | ------------------------------------------------------------- | --------------------- |
| Resolution        | icon name + pixel size                                        | `reload()`            |
| Source bytes      | file path                                                     | `reload()`            |
| Rendered pixmaps  | name or path, size, dpr, mode, state, color override          | `reload()`, `clear()` |

The resolution cache stores misses as well as hits. Once `BitmapFactory` delegates, every icon
request in the application walks the rule list, and an unresolvable name would otherwise re-run
every pattern and stat the filesystem on each repaint.

There are two invalidation triggers, matching what actually changed. An interface theme change calls
`clear()`, from `Application::reloadTheme()` beside the existing `clearTokenCache()`; only rendered
pixmaps are invalid, since resolution does not depend on color. An icon theme preference change
calls `reload()`, wired through the `ParamHandlers` machinery in
`Application::initStyleParameterManager()`, and also clears `BitmapFactory`'s `xpmCache`, which
would otherwise keep serving the previous theme.

### Shipped defaults

`qss:icons/defaults.yaml` would reproduce present behavior exactly and would be the preference's
default value:

```yaml
defaults:
  searchPaths:
    - "{}"              # absolute path or full resource path, verbatim
    - "icons:{}"        # the name already carries an extension
    - "icons:{}.svg"
    - "icons:{}.png"
    - "icons:{}.xpm"

missing: "help-browser"
```

A FreeCAD with no additional icon theme installed would therefore render as it does today, and the
format would begin doing work only when a second theme file exists.

### Impact on existing features / subsystems

`Gui::IconTheme`, `Gui::IconManager` and `Gui::ParametrizedIconEngine` would be new classes, and
nothing outside them would have to change in order for them to exist.

`BitmapFactoryInst::pixmap(const char*)` would delegate wholly to `IconManager`, so its 287 call
sites would gain theme resolution and processing without being edited, and would keep the pixel
dimensions they receive today.

`BitmapFactoryInst::iconFromTheme()` would keep its own ordering. It consults the XDG icon theme
before FreeCAD's own icons when `UseIconTheme` is set, which is the reverse of stages 1 and 2, so
only its terminal `pixmap()` fallback would delegate. Two orderings would therefore coexist,
deliberately: `icon(name)` answers what the icon theme says, `iconFromTheme(name)` answers what the
desktop says if it says anything. Both are documented as such.

`BitmapFactoryInst` would additionally gain the SVG processing primitives described under
[Units](#units). Its existing members would be unchanged.

`FreeCADGui` would gain the three functions described under [Python API](#python-api), declared in
`ApplicationPy` and typed in `FreeCADGui.module.pyi`. No existing Python function would change
signature or meaning, and no workbench would be required to register anything: the seven modules
that call `addIconPath` today, and the several that call `BitmapFactoryInst::addPath()`, would keep
working untouched.

Installation would add `icons/*.yaml` to the `Stylesheets` CMake data target beside
`parameters/*.yaml`.

### Backwards Compatibility

Documents and addons would be unaffected. No file format or property would change, and the Python
API would be added to rather than altered: `getIcon`, `addIcon`, `addIconPath` and `isIconCached`
would keep their signatures and their meaning, and `icon()`, `pixmap()` and `addIconRules()` would
be new names beside them.

Behavior would be unchanged for a default installation, because the shipped `defaults.yaml` would
express the present lookup. The one visible change would be a fix: an unresolvable icon name would
be reported once rather than on every repaint, because resolution failures would be cached.

Addons that register icon search paths through `BitmapFactoryInst::addPath()` would continue to work
unchanged, because the shipped rules resolve through the `icons:` search path those calls populate.
An addon shipping icons under names a theme's patterns capture would have those icons themed, which
is the intent.

## Open Questions

- The resolution mechanism is quite advanced so it may take time to find icons. It would be good to
  have a cache warmup mechanism that loads all icons and caches the exact matches across program
  runs so it is only slow first time.

## Rejected Ideas

Icon rules could have lived inside the interface theme file, under a reserved `_icons:` key in
`qss:parameters/{Theme}.yaml`. That would keep a theme to a single file, but it couples two things
that vary independently, and it would put structured data inside a file whose every other nested map
is read as dotted token names.

A single `icon()` method could have inferred name from path by the shape of its argument, which
would mean the fewest call-site changes. It was rejected because it leaves a dispatcher deciding
semantics from the form of its input when the caller already knows which of the two it holds.

The 807 `sPixmap` command declarations could have been migrated in the same change. They need not
be: command icons are already resolved by name through `BitmapFactory`, so the delegation themes
them without any of them being touched.

## Alternatives

An XPath subset was considered for node selection, and rejected because Qt 6 provides no XPath
engine. The cost would be writing and testing a parser for a language of which a handful of axes
would ever be used.

The theme's expressions could have been resolved once at load time, with the `IconTheme` rebuilt on
every interface theme reload. That is simpler at render time, but it couples the lifetimes of the
two themes this proposal separates.

`IconTheme` could have been folded into `IconManager` as a private structure, saving a file. The
loader could then only be tested through a singleton and global state.

## Implementation

Nothing here needs a new dependency. yaml-cpp already parses the style parameter files;
`ParameterManager::evaluate()` is public and takes an expression string, which is what makes a color
in the manifest able to be an expression rather than a literal; `PythonWrapper::fromQIcon()` already
exists and is what `getIcon` uses today; and `QFile::exists` already resolves both `:/` resources
and the `icons:` search path that `BitmapFactoryInst::addPath()` populates, so the templates reach
addon-registered directories without the resolver enumerating anything. A prototype of the rendering
half — an SVG recoloring icon engine driven by a manager — has been running in the author's branch,
which is where the sizing and device pixel ratio details below were found.

The manifest layer holds no Qt type and includes no Qt header, so rule ordering, alias resolution,
per-key processing and bucket selection can all be exercised without Qt at all, not merely without a
`QApplication`. That is worth preserving deliberately, because it is what keeps the part of this
feature with the most behavior in it cheap to test. Only the engine's contract and the rendering
itself need Qt.

Alias chains are bounded by remembering the names already visited rather than by a depth limit. A
chain that returns to a name it has seen is abandoned with one warning and the original name carries
on through its remaining candidates, so a mistake in a manifest costs one wrong icon rather than a
hang. A depth limit would additionally turn a legitimate long chain into a mystery.

Reloading has a sharp edge worth stating. Workbenches register their manifests once, as they load,
and are never asked again, so re-reading the icon theme must keep every contributed source. A reload
that rebuilt the rule list from the theme file alone would drop every workbench fallback the moment
a user changed icon theme, and the icons would disappear with no error anywhere.

An unset size in a request means 64×64 for an SVG and the file's own dimensions for a raster image.
That is not a chosen number: it is what `BitmapFactoryInst::loadPixmap()` produces today, and
reproducing it exactly is what lets the 287 existing `pixmap()` call sites be redirected without any
of them being examined.

Finally, the route by which a color override reaches code holding only a `QPixmap` is the pixmap's
cache key. The engine records each pixmap it produces against the file and processing behind it, and
`metaForPixmap()` recovers that. Qt's styling entry points are the reason this is needed rather than
an `iconName()` lookup: `QStyle::generatedPixmap()` is handed a pixmap and asked for a variant of
it, with no `QIcon` anywhere in reach.

The pieces are separable and can land in sequence — the processing primitives, then the manifest
layer, then the manager and engine on top of them, then the delegation that puts existing call sites
onto it — with each step useful and testable before the next. The author intends to carry the work.

## Further Work

This proposal provides the mechanism for recoloring but does not settle what color an icon should
actually take: following the interface theme's tokens, following the text color of the control the
icon sits on, and reacting to interaction state such as disabled or hovered. That is a policy
question touching `FreeCADStyle` and the design token system, and is left to a separate FEP.

A themeable icon set makes several further things possible that are out of scope here: shipping a
filled counterpart to the current outline set, per-workbench icon overrides, and a preferences page
for choosing among installed icon themes. The last is the natural follow-up, since this proposal
adds the preference but no interface for it.

## Changelog

### 0.1 - 2026-09-09

- Initial draft.

## License / Copyright

All FEPs are explicitly [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/).
