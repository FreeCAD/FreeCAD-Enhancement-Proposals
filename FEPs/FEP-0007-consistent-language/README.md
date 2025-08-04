# FEP-0007 Consistent Language Across FreeCAD

| FEP-0007       |                                                                                                                                           |
| -------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| Type           | Informational                                                                                                                             |
| Status         | Active                                                                                                                                    |
| Author(s)      | @maxwxyz (DWG), @obelisk79 (DWG), @tigert, @ryankembrey, @kadet1090 (DWG)                                                                 |
| Version        | 1.0.2                                                                                                                                     |
| Created        | 2025-07-08                                                                                                                                |
| Updated        | 2025-08-02                                                                                                                                |
| Discussion     | https://github.com/FreeCAD/FreeCAD-Enhancement-Proposals/discussions/21, https://github.com/FreeCAD/FreeCAD-Enhancement-Proposals/pull/20 |
| Implementation | https://github.com/FreeCAD/FreeCAD/pulls?q=is%3Apr+Update+strings+for+consistency                                                         |

This document defines consistent rules for user-facing text in FreeCAD: menu items, toolbars, dialogs, tooltips, input hints, and other strings.

## Motivation

FreeCAD involves both CAD and programming, it's easy to use overly technical or redundant
language. Names that seem obvious to developers may confuse general users. Additionally, with
limited UI space, concise and clear naming is critical for usability. That FEP establishes guidelines
that developers should follow when naming or labeling functions, features, and addons.

> **Note:** While translations exist, English is the reference standard. This document is about
> English which is the source language. Each translation should have their own guidelines following
> well established practices and existing translation standards.

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

To make these guidelines easier to apply, they are grouped into **General Language Guidelines**, **Tooltip-Specific Guidelines**, **Input Hints Guidelines**, and **UI Text Style**.

### 1. General Text Guidelines

These apply to **all user-facing text**:

- **Always wrap messages in the translate function** for localization.
- In general, uses **sentence case**.
- Use **Title Case** only for command names, buttons, menus, headers, window titles and group titles.
- Don’t address the user directly (“Click this button to…”). Use third-person present tense instead.
- Don't add an extra space at the end of a string.
- Avoid acronyms and only use commonly known like `CAD` or `ISO`.
- Use standard numerals (`0, 1, 2,…`) not words.
- Keep terminology consistent with existing FreeCAD concepts.
- Avoid programmer jargon; use terms users expect.
- For optional plurality use plural language, write naturally and do not account for the singular if it is not possible to dynamically adjust the text for the context: `Creates holes based on the selected profiles` (not “hole(s)”).
- **Do not use periods** on short UI elements like buttons or labels. Use periods only in full-sentence tooltips or longer descriptive text.
- Do not add a colon or space at the end of labels that precede user input or interactive elements: Instead of "X direction: "" write `X direction` without additinal spaces.
- **Ellipsis (…) usage:**
  - In general, limit the use of ellipsis. Use an ellipsis **only** when the action requires further user input, where the ellipsis stands for the missing part and the command or context would benefit from it:
    - Example: `Export As…` → asks for a file type/name.
    - Example: `Save As…` → asks for a file name.
  - Do **not** use ellipses merely because an action opens a dialog:
    - Bad: `Unit Converter…` (no further text to complete the phrase)
  - Always use the single ellipsis character `…` (not three dots `...`) and no spaces before or after it.
  - Do not use an ellipsis as the only text on a command or button.
- Add translator comments in source as needed and to provide context for translators (e.g. "close" can have multiple meanings):
  ```cpp
  //: Sketcher: Command name for new line
  ```
  See [Qt translation documentation](https://doc.qt.io/qt-6/i18n-source-translation.html#add-comments-for-translators).

### 2. Command and Menu Guidelines

These apply to **command names, (context)menu action entries, buttons and headers**:

- Use **Title Case** (see the section below how to write in title case)
- Use short, descriptive terms. Prefer single nouns when possible.
  Example: `Additive Cube`, not “Create new Additive Cube”.
- Favor unique noun-first naming:
  Example: `Horizontal Constraint`, not “Constrain Horizontal”.
  *Clarification:* The **full phrase** should be unique and start with the most important noun or the word that differentiates similar named commands.
  If a noun like “Close” could be ambiguous (homonym), consider alternatives or clarify with context in tooltips.
- Avoid unnecessary verbs unless clarity requires them. Instead of "Create new sketch" write `New Sketch`. Use verbs when it helps clarification, e.g. `Insert Image`.
- Refer to the item always by the same name (e.g. use the command name in the task dialog header). This should also be consistent with translations.
- Other UI elements (e.g. drop down menus) should use sentence case.

### 3. Tooltip and Descriptive Guidelines

Tooltips and explaining decriptive texts have distinct requirements and should be treated separately:

- Use **third-person present tense** and start with an action verb: `Creates`, `Adds`, `Inserts`.
- Prefer complete sentences for long tooltips; short hints (one sentence) can omit the period:
  - Short hint: `Toggles the visibility of the active sketch`
  - Full tooltip: `Constrains new geometry automatically. It is recommended to leave it enabled for most workflows.`
- Tooltips should describe the action and context, not step-by-step instructions:
  - Good: `Inserts a dimension for the selected lines`
  - Avoid: “Select one or more lines and click this button…”
- Avoid stating the obvious:
  Use `Updates view automatically`, not “If checked by the user, the view is updated automatically.”
- Avoid direct references to source-code concepts:
  Use `This feature only works with Part Design bodies`, not “This feature only works with PartDesign bodies.”
- Do not add unnecessary information or list multiple steps like "Select one or more line(s) click this button, add dimension". Better: `Insert dimension for the selected lines`.

### 4. Input Hints Guidelines

**Input Hints** are displayed in the status bar to provide users with hints for available actions. They typically combine key sequences with short action descriptions.

![Input Hints Preview](./assets/input-hints-preview.png)

Hints consist of:
- A message with placeholders (`%1`, `%2`, …) for key sequences.
- Key sequences, which may include single keys, modifiers (e.g. Shift), or combinations.
  Example:
  - Single: `[M] change mode`
  - Multiple: `[U]/[J] increase/decrease number of sides`
  - Combined: `[Shift][M]`

**Guidelines for writing Input Hints:**

- **Start with the input, then a lowercase action**. Input hints are not sentences. Do not add a period at the end.
   Example: `%1 pick radius`.
- **Keep hints as short as possible**. Avoid redundancy when the context is clear.
   Example: `%1 pick arc center` instead of "%1 pick center of an arc".
- **Order inputs consistently**:
   - Modifiers first (Ctrl, Alt, Shift),
   - Then mouse inputs,
   - Then normal keys.
- **Order actions by frequency of use**: common actions first.
- **Be specific**:
   Example: Instead of "change mode", prefer a dynamic hint that shows the next mode name, e.g. `straight segment`.
- **Combine similar actions when possible**:
   Example: `%1/%2 decrease/increase side`, `%1, %2 or %3 constrain axis`.
- **Keep the list short**: ideally no more than 6 hints, focusing on the most common actions.
- **Avoid redundant hints**:
   - Do not show general navigation commands during active tools.
   - Do not show hints for actions that are currently unavailable.
   - Do not show hints for commands which are always possible (e.g. Save Document)
- **Maintain consistency when hints change dynamically**:
    - Keep common hints visible across tool states.
    - If an action disappears, that indicates it is no longer available.

### 5. How to Implement Title Case

In title case, capitalize the following words:

- the first word of the title or heading, even if it is a minor word such as "The" or "A".
- major words, including the second part of hyphenated major words (e.g., "Self-Report", not "Self-report").
- words of four letters or more (e.g., "With", "Between", "From").
- capitalize the last word in the label, regardless of the part of speech.


Lowercase only minor words that are three letters or fewer:

- short conjunctions (e.g., and, as, but, for, if, nor, or, so, yet)
- articles (a, an, the)
- short prepositions (e.g., as, at, by, for, in, of, off, on, per, to, up, via)

More information on APA guidelines for [Title Case](https://apastyle.apa.org/style-grammar-guidelines/capitalization/title-case) and [Sentence case](https://apastyle.apa.org/style-grammar-guidelines/capitalization/sentence-case).


### 6. Examples

- Command: `New File` → Tooltip: `Creates a new file`
- Command: `Save As…` → Tooltip: `Saves the document under a new name or filetype`
- Tooltip: `Constrains new geometry automatically. It is recommended to leave it enabled for most workflows.`
- Descriptive text: `Toggles the visibility of the active sketch`
- Input hint: `%1 cancel`

### Impact

No change to functionality. Translators will need to update strings after these standards are applied.

## Notes

- Guidelines are now **organized into clear sections**: general rules, tooltip rules, input hints, and style rules.
- Additional examples will be added over time to clarify edge cases like homonyms and noun-first naming.

## Changelog
- [1.0] – 2025-07-08 – Initial proposed version
- [1.0.1] – 2025-08-01 – Clarified ellipsis usage
- **1.0.2** – 2025-08-02 – Structured guidelines into general vs. tooltip sections, added input hints guidelines, and retained full ellipsis rule


## References

1. <span name=jakobs-law>Jakob's Law</span>: https://lawsofux.com/jakobs-law/
2. <span name=nielsens-4th>Nielsen's 4th heuristic</span>: https://www.nngroup.com/articles/ten-usability-heuristics/
3. <span name=apple-style-guide>Apple Human Interface Guidelines - Menus</span>: https://developer.apple.com/design/human-interface-guidelines/menus
4. <span name=kde-style-guide>KDE Human Interface Guidelines - Text and labels</span>: https://develop.kde.org/hig/text_and_labels/
5. <span name=microsoft-style-guide>Microsoft Writing Style Guide</span>: https://learn.microsoft.com/en-us/style-guide/text-formatting/using-type/use-sentence-style-capitalization

## License / Copyright

All FEPs are explicitly [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/).

[1.0]: https://github.com/FreeCAD/FreeCAD-Enhancement-Proposals/tree/18cf4fa481a00950c830bae453f76fd5f28d0a97/FEPs/FEP-0007-consistent-language
[1.0.1]: https://github.com/kadet1090/FreeCAD-Enhancement-Proposals/tree/e2b2a01016f2b85a44e245c9abf41ccd44201978/FEPs/FEP-0007-consistent-language
