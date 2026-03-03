# FEP-0011 Generic Collaboration Framework

| FEP-0011       |                                                                                                                                    |
|----------------|------------------------------------------------------------------------------------------------------------------------------------|
| Type           | Core Change                                                                                                                        |
| Status         | Draft                                                                                                                              |
| Author(s)      | Pieter Hijma @pieterhijma                                                                                                          |
| Version        | 0.1                                                                                                                                |
| Created        | 2026-01-25                                                                                                                         |
| Updated        | 2026-03-03                                                                                                                         |
| Discussion     | [💬 Discussion FEP-0011: Generic Collaboration Framework](https://github.com/FreeCAD/FreeCAD-Enhancement-Proposals/discussions/40) |
| Implementation |                                                                                                                                    |

This document proposes to add a generic collaboration framework to FreeCAD.
The generic collaboration framework would become a new module inside FreeCAD
that can be extended by external addons for specific use-cases.

## Motivation

<!-- Why the proposed change is needed. Links to affected issues / PRs are also welcome. -->

Now that there are various initiatives (see below) that support or could
benefit from collaboration features, it would be good to have a shared set of
building blocks for collaboration.  These building blocks can then be reused by
various different initiatives to ensure that not every project reinvents the
wheel.  Additionally, another benefit is that FreeCAD will obtain a
standardized set of features for collaboration.

Current known initiatives that could benefit from a generic collaboration framework are:
- [BCF plugin for FreeCAD](https://github.com/podestplatz/BCF-Plugin-FreeCAD),
- [CADBaseLibrary](https://cadbase.rs/en/) and its [Addon](https://github.com/mnnxp/cadbaselibrary-freecad),
- [FreePDM](https://github.com/grd/FreePDM),
- [nanoPLM](https://github.com/alekssadowski95/nanoPLM),
- [Taack FreeCAD PLM](https://taack.org/en/app/Plm) and its [Addon](https://github.com/Taack/taack-plm-freecad), and
- [Ondsel Server](https://github.com/FreeCAD/Ondsel-Server) and its [Addon](https://github.com/FreeCAD/Ondsel-Lens-Addon/).

The following issues are relevant:

- [Core: Collaboration features](https://github.com/FreeCAD/FreeCAD/issues/25681)
  - [Core: Improve annotations as a collaboration feature](https://github.com/FreeCAD/FreeCAD/issues/25682)
  - [Core: Add conversations to annotations](https://github.com/FreeCAD/FreeCAD/issues/25685)

Issue [Core: Improve annotations as a collaboration feature](https://github.com/FreeCAD/FreeCAD/issues/25682) has already a PR associated with it:
- [#26306: Collaboration: Add a generic collaboration framework](https://github.com/FreeCAD/FreeCAD/pull/26306).

The BCF plugin of itself is already a collaboration framework that follows the
BCF standard.  However, if any of the other projects would like to also acquire
collaboration features, the code cannot easily be reused, for example because
of licensing issues or because the code of the BCF plugin is tailored to
BCF-specific features.  So, the main motivation for this generic collaboration
framework is reuse of building blocks and a standardized set of collaboration
features within FreeCAD.

## Rationale

<!-- Why particular decisions were made in the proposal. -->

An important design choice is to make a generic collaboration framework that is
useable as is.  However, as explained in the Motivation section, the main idea
is that the collaboration framework is extended by means of external addons
that target specific use-cases.  As a collaborator of the Ondsel Server and its
Addon, I would like to build on and add functionality to the collaboration
framework for Lens-specific features.  As an example, Lens supports versions,
so I would like to be able to extend the collaboration framework to allow users
to refer to specific versions of a model.

The collaboration framework will be written mostly in Python because this
allows external addons to understand how the collaboration framework works and
how to extend it.  Small parts need to be written in C++ because the framework
makes use of `App::AnnotationLabel` for annotations.  Because
`App::AnnotationLabel` only supports absolute positioning, it is extended to to
associate annotation labels with the geometry, for example with faces or edges.
This allows to reposition the geometry with the annotation labels to reposition
itself as well.

Since the main idea is that the collaboration framework is used by external
addons, the provided API is versioned to make sure that external addons can
target a specific API version.  This allows the collaboration framework to
evolve and introduce a new API version without breaking functionality of the
external addons that use older API versions.

[BuildingSMART](https://www.buildingsmart.org/) is an organization for open
standards in the BIM field.  Besides their [IFC
Standard](https://www.buildingsmart.org/standards/bsi-standards/industry-foundation-classes/),
they also have the [BIM Collaboration Format
(BCF)](https://www.buildingsmart.org/standards/bsi-standards/bim-collaboration-format/).
FreeCAD has an (unmaintained) [external addon for
BCF](https://github.com/podestplatz/BCF-Plugin-FreeCAD) and since this is an
important standard, we made sure that this generic collaboration framework is
aligned with the BCF standard and supports all that the BCF standard requires.
With this generic collaboration framework, we could revise the old external
addon to build on top of this work.

A distinct design decision of the BCF standard is that the comments are stored
in `.bcf` files separate from the `.icf` files.  As opposed to that design
decision, this generic collaboration framework stores the collaboration
information in the FreeCAD document.

However, storing collaboration information in the FreeCAD document has
drawbacks.  For example, a new comment to a model would change the file, which
could mean that the version of the file needs to be updated, for example in a
PLM/PDM setting.  This means that there is a valid reason to store discussions
on models separate from the model as the BCF standard prescribes.  This is
perfectly possible with FreeCAD making use of `App::Link`: If the original file
needs to stay unmodified, users can create a second FreeCAD document that
contains a link to the model from the original file and make comments in that
document.

## Specification

We first provide an overview of the generic collaboration framework and then
give details on how to customize the framework, an inherent goal of the
framework.

### Overview

The generic collaboration framework is a new module called "Collaboration" that
is part of the FreeCAD source code.  The collaboration framework provides
several constructs to foster collaboration among users.  The main construct is
a Topic.  A **Topic** is document object that is created by a user.  Optionally
a topic has an **Annotation** in the 3D view with the topic title that can be
globally positioned to mark geometry or can be attached to geometry.  The topic
is a collection of **Comments** created by **Users**.  A sequence of comments
is the main contents of a topic and forms a **History**.  A **Comment** is a
string of text associated with a **Date**, **Time**, and **User**.  A **User**
is someone who can be uniquely identified and distinguished from other users
and is capable of making comments.  How users are represented can be customized
(more on this later) but as a minimal implementation, users are identified by
email addresses.  The history of comments inside topics allow users to discuss
models.

As collaboration feature, users can make **Snapshots** of a model.  A
**Snapshot** is a screenshot of the model in its current state.  Another
collaboration feature is a **Viewpoint**, a camera position that can direct the
user to view a model in a particular way.

The text of a comment can contain **Links** that can reference various things.
**Links** have a standardized set of things they can refer to, but it is also
possible to have **Custom Links** which will be discussed in the next section.
The standardized set of things that a link can refer to is:
- other topics,
- other comments,
- snapshots,
- viewpoints, and
- users.

Comments are entered by users in a text field that supports a subset of
[Markdown](https://www.markdownguide.org/).  This allows users to easily create
links or minor markup features such as making text bold.

Links are created using the Markdown syntax.  The following URL schemes are used for the items above:
- topics: `topic:identifier`,
- comments: `comment:identifier`,
- snapshots: `snapshot:identifier`,
- viewpoints: `viewpoint:identifier`,
- users: `user:email address`, and see below.

### Customization

Although the proposed collaboration framework can be used as is, the main idea
is that the generic collaboration framework is used by external addons to adapt
the collaboration framework for specific use-cases.  We call these addons
**Adaptors** that adapt the generic collaboration framework through an API.

Since the API is specifically meant to be used by addons, the API is versioned
to allow the API to evolve while ensuring that old versions of the API remain
working for addons that make use of it.

The main customization points are **Users** and **Links**.  For **Users** to
make use of the collaboration framework, a user must register itself.
Registrations can happen by means of the default mechanism, or the default
mechanism can be overridden by adaptors.  The default mechanism allows users to
provide their name and email address while adaptors can disable this and
provide their own means of providing the user's identity.

- `register_user(adaptor_id: str, name: str, username: str) -> None`: This
  function registers the name and username for a specific adaptor and disables
  the default way to authenticate a user.
- `unregister_user(adaptor_id: str, username: str) -> None`: This function
  unregisters the user and enables the default way to authenticate users.
- `register_user_handler(adaptor_id: str, user_handler: Callable[[link: str,
  context: str], None] -> None)`: This function registers a handler that is going to
  be called if a user for the adaptor is clicked in a certain context.  The URL
  schema for the user becomes `user:adaptor_id:username`.  The context is a
  string that specifies the context for an action and can be one of the
  following: `create-reply`, `view-user`.
- `unregister_user_handler(adaptor_id: str)`: This function unregisters a
  user handler.

Another point for customization is **Links**.  Adaptors can introduce their own
URL scheme and install handlers for that:

- `register_url_scheme(adaptor_id: str, scheme: str, handler: Callable[[link:
  str, context: str], None])`: Clicking a link of that type, will call the
  handler with the provided link and the context.  This allows the adaptor to
  handle the link according to the use-case of the adaptor.  The context gives
  the adaptor an idea of where the link is used.  Valid values are `comment`
  and `topic-title`.

To improve the user experience, the `@` key will enable autocompletion for the
various types of links.  The auto-completer will give suggestions based on user
input.  Adaptors can register their own completer with the following function:

- `register_completer(adaptor_id: str, completer: Callable[[prefix: str],
  List[tuple[str, str]]])`: This function registers a completer for a specific
  adaptor.  Given a prefix string (typed immediately after `@`), the completer
  will return a list of matches.  A match is a tuple of two strings with the
  first string being the representation for the user, for example a username,
  and the second the link to be inserted.
- `unregister_completer(adaptor_id: str) -> None`: This function unregisters
  the completer for an adaptor.

For example, if a user types `@use` or `@Pie` given the registered urls, an
adaptor could provide the following list:
``` python
[('Pieter Hijma', 'user:my-adaptor:pieterhijma')]
```

Since it cannot be assumed that an adaptor is installed when a document is
opened with custom url schemes, an adaptor has to register itself and its url
schemas inside a document.  The API to register itself is:

- `register_adaptor(adaptor_id: str, adaptor_name: str, url: str)`: This
  function registers an adaptor with a specific identifier, a name, and a URL
  where the adaptor can be found, ideally a link to the addon manager.

When URL schemas are registered, the URL schemes are stored in the document
where the topics occur.  Below are the properties and contents that are used
for an adaptor with id `myadaptor` with name `My Adaptor` and url
`https://myadaptor.org`, and a url schema `myadaptormodel`:

```
Adaptors: [('myadaptor', 'My Adaptor', 'https://myadaptor.org')]
Schemas: [('myadaptor', ['myadaptormodel'])]
```

When a document is opened in FreeCAD that does not have "My adaptor" installed,
clicking a link with scheme `myadaptormodel` will give the user a message
indicating that to view this link, "My adaptor" will have to be installed.

The collaboration framework supports all features that are required for the
[BIM Collaboration Framework
v3.0](https://github.com/buildingSMART/BCF-XML/tree/release_3_0/Documentation).

### Impact on existing features / subsystems

<!-- Any remarks about how the proposal will impact existing features or subsystem within the FreeCAD. -->

Since the generic collaboration framework will be contained in its own module,
there is almost no impact to existing features or the subsystem.  Since the
generic framework builds on `App::AnnotationLabel`, this document object and
its viewprovider may be changed minimally.

### Backwards Compatibility (only for Core Changes)

This core change will not have any impact on backwards compatibility.

## Implementation (only for Core Changes)

<!-- Further discussion about implementation details, with link to implementation (if available) or any other way -->
<!-- proving that implementation is feasible and someone is willing to carry the implementation effort. -->

There is an initial PR available to study: [#26306: Collaboration: Add a
generic collaboration
framework](https://github.com/FreeCAD/FreeCAD/pull/26306).  This PR mainly
introduces the new Collaboration module and its central document object
`Collaboration::Topic`.  This is a subclass of the already existing
`App::AnnotationLabel`.  Topics have a title and an optional label in the 3D
view with the title.  Clicking on the label in the 3D view or on the document
object in the object tree opens up a task panel for the topic.  There is no
support for comments yet and this is planned for subsequent PRs.


## Changelog (once more versions are released)

<!-- Any substantial changes to the FEP should be recorded in this section - latest changes should be on top: -->

### 0.1 - 2026-03-03

- Initial version

## License / Copyright

All FEPs are explicitly [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/).
