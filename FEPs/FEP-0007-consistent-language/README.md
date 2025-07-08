# FEP-0007 Consistent language across FreeCAD

| FEP-0007       |                                                                                                                                           |
| -------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| Type           | Informational                                                                                                                             |
| Status         | Draft                                                                                                                                     |
| Author(s)      | @maxwxyz (DWG), @obelisk79 (DWG), @tigert, @ryankembrey, @kadet1090 (DWG)                                                                 |
| Version        | 0.1                                                                                                                                       |
| Created        | 2025-07-08                                                                                                                                |
| Updated        | 2025-07-08                                                                                                                                |
| Discussion     | https://github.com/FreeCAD/FreeCAD-Enhancement-Proposals/discussions/21, https://github.com/FreeCAD/FreeCAD-Enhancement-Proposals/pull/20 |
| Implementation | https://github.com/FreeCAD/FreeCAD/pulls?q=is%3Apr+Update+strings+for+consistency                                                         |

FreeCAD involves both CAD and programming, it's easy to use overly technical or redundant
language. Names that seem obvious to developers may confuse general users. Additionally, with
limited UI space, concise and clear naming is critical for usability. That FEP establishes guidelines
that developers should follow when naming or labeling functions, features, and addons.

> **Note:** While translations exist, English is the reference standard. This document is about
> English which is the source language. Each translation should have their own guidelines following
> well established practices and existing translation standards.

## Motivation

FreeCAD has a lot of different user facing texts: menu entries, toolbar items, tooltips, and tool
hints - to name a few. Historically these texts were added by many developers, often non-native
english speakers which creates inconsistencies in terms of writing style used.

Certain workbenches use Title Case for menu items, other use Sentence case. Some field labels have
additional colon (:) at the end, some do not. Tooltips for features are sometime written as third
person (`Creates ...`) and sometimes as imperatives (`Create ...`). While workbenches are usually
consistent within themselves (with exceptions, like `Create sketch` but `Edit Sketch`) there is no
defined standard for the whole application.

In order to achieve consistency, such standard must be defined and implemented across whole
application - in all workbenches and for all core features. Clearly defining the standard will allow
more people to check if PRs are adhering to rules and thus keep the consistency. It will also
prevent changing the style to something else without extended discussion.

## Rationale

User Experience is often defined as sum of small details that are often easy to miss. While there is
no one single correct way to approach mentioned problem, we can utilize certain tools to find a good
set of guidelines that will survive the test of time.

One of most (if not the most) important factors affecting User Experience is consistency not only
within the application, but also with other applications. This is known as Jakob's Law [[1]](#jakobs-law) or 4th
Nielsen's heuristic [[2]](#nielsens-4th-heuristic):

> Users should not have to wonder whether different words, situations, or actions mean the same
> thing. Follow platform and industry conventions.

FreeCAD is multi platform application, which does not allow us to simply use guidelines from any
given platform. Different platforms often recommend different solutions to the same problem. For
example, Apple [[3]](#apple-style-guide) and KDE [[4]](#kde-style-guide) using Title Case for menu
entries and Microsoft recommends [[5]](#micrsoft-style-guide) using Sentence case in the same
scenario. While in theory it would be possible to create different sets of texts per platform, it
would be impossible to maintain in the long run.

As mentioned by Jakob's Law users tend to prefer things, that they already know and are used to. To
find proper set of guidelines it is important to check how other applications are solving the same
problems and use similar approach if applicable for researched use case. Going through various
desktop applications (including, but not limited to: Firefox, Chromium, Visual Studio Code,
IntelliJ, Fusion360, AutoCAD, Catia v5 and more) one can find that these applications:

- predominantly use Title Case for menu entries;
- for short tooltips, do not put dot at the end;
- for longer tooltips place the dot the end if needed (clearly a sentence or multiple sentences);
- prefer short texts are over long ones.

## Specification

Avoid verbose or inconsistent language in the UI, as it may cause layout issues across workbenches
and dialogs. Always review naming before merging UI-related pull requests.

### Language

- Use short, descriptive terms. Prefer single nouns when possible: `Additive Cube`, not "Create new
  Additive Cube".
- Favor unique noun-first naming: `Horizontal Constraint`, not "Constrain Horizontal".
- Avoid unnecessary verbs in command names (`New File`, not "Create new file"). Use verbs only if
  clarity requires them (e.g. `Insert Image`).
- For items with optional plurality use plural language: e.g. `Creates holes based on the selected
profiles` not "Creates hole(s) based on the selected profile(s)".
- Do not add additional information which is obvious or list multiple steps like "Select one or more
  line(s) click this button, add dimension". Better: `Insert dimension for the selected lines`.
- Acronyms like `CAD` or `ISO` are allowed but should be reviewed for clarity.
- Use standard numerals (`0, 1, 2,…`) not spelled out ("one, two,…")
- Keep terminology consistent with existing FreeCAD concepts.
- Avoid programmer jargon in favor of simpler terminology.
- For user-facing strings add comments as needed to help provide context for translators `//:
Sketcher: Command name for new line`. [More info in Qt
  docs](https://doc.qt.io/qt-6/i18n-source-translation.html#add-comments-for-translators).
- Use **third-person present tense** in tooltips: `Creates`, `Adds`, `Inserts`. Write complete
  sentences where appropriate.
- Tooltips should describe the action and required context. E.g., `Adds a new sketch to the active
body`, not just "Add sketch".
- Avoid step-by-step instructions in tooltips. Focus on outcome: `Inserts a dimension for the
selected lines`, not "Select one or more lines…".
- Avoid stating the obvious: "If checked by the user, the view is updated automatically", use
  `Updates view automatically`.
- Don't address the user directly: say what the command does, not "Click this button…".
- Avoid direct source-code references in the UI, instead of "This feature only works with PartDesign
  bodies" use `This feature only works with Part Design bodies`

### UI Text Style

Use **Title Case** only for command names, buttons, menu items, and group titles. All other text
should use normal **sentence case**.

**Do not use periods** on short UI elements like buttons or labels. Use them only in full-sentence
tooltips or descriptive text.

**Use ellipsis (…)** at the end of menu items or commands that require user input. Do not use three
periods "..." instead of the ellipsis character `…` for consistency.

Do not put a colon or space at the end of labels that are followed by required user input (e.g.
QLabel for input box, button, dropdown, or checkbox) or headers. Instead of "X direction: " write `X
direction`

### How to Implement Title Case

In title case, capitalize the following words:

- the first word of the title or heading, even if it is a minor word such as "The" or "A"
- major words, including the second part of hyphenated major words (e.g., "Self-Report", not
  "Self-report")
- words of four letters or more (e.g., "With", "Between", "From")
- capitalize the last word in the label, regardless of the part of speech.

Lowercase only minor words that are three letters or fewer:

- short conjunctions (e.g., and, as, but, for, if, nor, or, so, yet)
- articles (a, an, the)
- short prepositions (e.g., as, at, by, for, in, of, off, on, per, to, up, via)

More information on APA guidelines for [Title
Case](https://apastyle.apa.org/style-grammar-guidelines/capitalization/title-case) and [Sentence
case](https://apastyle.apa.org/style-grammar-guidelines/capitalization/sentence-case).

### Examples

- Tooltip: `Constrains new geometry automatically. It is recommended to leave it enabled for most
workflows.` - Complete sentences end with a period.
- Hint: `Toggles the visibility of the active sketch` - No period at the end
- Command: `New File` - This is just a short label. A tooltip for that command button would be
  "Creates a new file".
- Command: `Save As…` - The function requires user input to function.
- Command: `Addon Manager` - This is not a simple action, so no ellipsis.

The technical details of the proposed change.

### Impact on existing features / subsystems

No impact on core functionality. Translations will be rendered out of date and new strings need to
be submitted on Crowdin. Similar (previous) translations are suggested on the new strings on Crowdin
but we advice to wait with the translations, until all strings in main are changed. @sifabiancic is
planning to create similar guidelines for different languages with the translator community, a
discussion on Crowdin was already started, to make the translations consistent as well.

### Backwards Compatibility

Not applicable, only user-facing text is updated.

## Open Issues

None known.

## Rejected Ideas

Sentence case for all strings was analyzed and rejected. This decision was made to have a unified UI
experience across the different OS and with other CAD or FOSS applications (English as base
language).

## Further Work

As further work it is possible to create linter rules that would perform automatic checks over
codebase to help with keeping consistency.

## References (optional)

1. <span name=jakobs-law>Jakob's Law</span>: https://lawsofux.com/jakobs-law/
2. <span name=nielsens-4th>Nielsen's 4th heuristic</span>: https://www.nngroup.com/articles/ten-usability-heuristics/
3. <span name=apple-style-guide>Apple Human Interface Guidelines - Menus</span>: https://developer.apple.com/design/human-interface-guidelines/menus
4. <span name=kde-style-guide>KDE Human Interface Guidelines - Text and labels</span>: https://develop.kde.org/hig/text_and_labels/
5. <span name=microsoft-style-guide>Microsoft Writing Style Guide</span>: https://learn.microsoft.com/en-us/style-guide/text-formatting/using-type/use-sentence-style-capitalization

## License / Copyright

All FEPs are explicitly [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/).
