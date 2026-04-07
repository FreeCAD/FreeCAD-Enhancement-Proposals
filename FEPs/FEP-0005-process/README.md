# FEP-0005: Dependency and Platform Policy

| FEP-0005       |                                                                 |
| -------------- | --------------------------------------------------------------- |
| Type           | Process                                                         |
| Description    | Defines the baseline platform and dependency policy             |
| Status         | Draft                                                           |
| Author(s)      | Benjamin Nauck (hyarion)                                        |
| Version        | 0.3                                                             |
| Created        | 2025-05-12                                                      |
| Discussion     | https://github.com/FreeCAD/FreeCAD-Enhancement-Proposals/discussions/ |
| Implementation | Process enforced through maintainer policy and CI configuration |

This FEP provides a long-term policy for baseline dependency expectations in FreeCAD development. It defines which operating systems and dependency versions FreeCAD targets for compatibility, based on the oldest currently supported Ubuntu LTS under standard support. This ensures broad accessibility, simplifies packaging, and clarifies expectations for developers and contributors.

## Motivation

FreeCAD is developed and used across multiple platforms, with a strong presence in the Linux ecosystem. While there is an informal practice of maintaining compatibility with older Ubuntu LTS releases and notifying packagers of significant dependency changes, this has not been formally documented.

To reduce ambiguity, ensure packaging compatibility, and provide a clear reference for contributors and packagers, this FEP formalizes that policy. It clarifies the expected baseline environment, establishes a shared understanding of compatibility goals, and makes it easier to anticipate, discuss, and manage changes in a coordinated way.

## Rationale

Ubuntu LTS releases are widely used, well-supported, and provide a consistent foundation across both developer and user systems. Aligning with the oldest currently supported LTS (within its standard support period):

* Provides long-term stability while still allowing regular updates,
* Matches the expectations of many contributors and packagers,
* Avoids surprises from bleeding-edge library versions or features.

While some platforms or users may have access to newer libraries or compilers, this policy helps guarantee a stable and consistent baseline.

## Specification

This policy defines the **baseline development environment** that FreeCAD must remain compatible with. It is distinct from the environment used to build official releases, which may use newer dependencies.

* FreeCAD **must be buildable and runnable by contributors** on the **oldest Ubuntu LTS release still under standard support**.
* The baseline platform determines the **minimum supported versions** of compilers, interpreters, build tools, and libraries.
* Features that depend on newer libraries or APIs **must be conditionally compiled or included**, preserving compatibility with the baseline environment.
* CI must include at least one build targeting the baseline Ubuntu LTS environment.
* Core FreeCAD code must compile cleanly with **GCC**, **Clang**, and **MSVC**. This ensures cross-platform compatibility and prevents compiler-specific behavior. CI infrastructure should regularly test builds using all three compilers.
* While development targets the baseline LTS environment, **official FreeCAD releases and pre-releases may be built using newer dependencies** to provide the best experience for end users. This does not change the requirement that core code must remain compatible with the baseline. Any features requiring newer APIs must remain guarded or compatible.

### Platform Scope

Although this policy anchors compatibility to Ubuntu LTS, it **applies across all platforms** FreeCAD supports (Linux, Windows, macOS). The **Ubuntu LTS baseline defines the minimum dependency versions** - for example, the minimum Clang or Qt version required on macOS should match what is available on the baseline Ubuntu LTS. This ensures consistency and simplifies development and CI expectations across platforms.

### Dependency Changes

* Any **new required dependency** or **change to the minimum required version** of an existing dependency should be communicated via a GitHub Pull Request labeled `Packaging/building`. The team `@FreeCAD/packaging-team` should be tagged to ensure visibility for downstream packagers.
* PRs should include relevant context for packagers (e.g., new build options, system packages needed, fallback code or build conditionals) and avoid placing unnecessary burden on downstream distributions.
* In **exceptional cases**, such as security fixes, urgent regressions, high-priority build issues, or **loss of CI runner availability** (e.g., GitHub beginning a brownout for a supported OS), maintainers may approve changes without prior notice. A good-faith effort should be made to notify affected packagers and document the change promptly after merging.

### Transitioning to New Ubuntu LTS Releases

When the current Ubuntu LTS baseline reaches the end of its standard support period, maintainers **should announce a planned transition** to the next supported LTS release. This announcement should occur **at least four weeks in advance**, via:

* A pinned GitHub issue in the FreeCAD repository labeled `Packaging/building` tagging `@FreeCAD/packaging-team`, and
* A post on the FreeCAD development forum

The announcement should include:

* The expected cutoff date,
* The new target LTS version,
* Any anticipated CI or tooling changes.

Contributors should be given time to adjust CI configurations, library usage, or documentation before the new baseline takes effect. Unless the transition involves broader architectural or compatibility changes, no new FEP is required.

#### Timing Considerations:
Maintainers have discretion to choose **when** to transition to the next Ubuntu LTS, as long as the current baseline is no longer under standard support. The transition **should not occur during high-risk phases** of the FreeCAD development cycle, such as just before a major release or during complex refactorings. If practical, transitions should be aligned with minor release cycles or quieter development periods to reduce disruption.

If a GitHub runner brownout forces an earlier transition, the normal notice period may be shortened, but maintainers should communicate the change promptly.

## Alternatives Considered

An alternative approach would have been to explicitly define and independently maintain minimum versions for each dependency across all supported platforms. This was rejected due to the additional maintenance overhead and reduced predictability it would impose on packaging and CI environments. Anchoring to the oldest supported Ubuntu LTS offers a simpler and more consistent policy.

An alternative to using a dedicated GitHub team (`@FreeCAD/packaging-team`) for notification would be to rely on individual outreach to known packagers, posting to external channels (forums, mailing lists) or an RSS feed. The team-based approach was preferred because it is low-friction and stays within the existing GitHub workflow.

## Future Work

* Consider introducing automated tooling or bots to assist maintainers in labeling PRs and pinging the packaging-team.
* Evaluate whether it would be beneficial to shift the baseline from the **oldest** supported Ubuntu LTS to the **newest** available LTS, and clarify the implications for developers and packagers.

## Changelog

* *0.1* – Initial draft
* *0.2* – Clarified support window definition, added platform-wide dependency consistency policy, formalized LTS transition notice requirements
* *0.3* - Simplified dependency change process, added GitHub team notification, added CI runner brownout as exceptional case

## References

* [Ubuntu Release Cycle](https://ubuntu.com/about/release-cycle)

## License

[CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/)
