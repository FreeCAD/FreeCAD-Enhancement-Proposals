# FEP-XXXX: Dependency and Platform Policy

| FEP-XXXX       |                                                                 |
| -------------- | --------------------------------------------------------------- |
| Type           | Process                                                         |
| Description    | Defines the baseline platform and dependency policy             |
| Status         | Draft                                                           |
| Author(s)      | Benjamin Nauck (hyarion)                                        |
| Version        | 0.2                                                             |
| Created        | 2025-05-12                                                      |
| Discussion     | \[To be created]                                                |
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

* Any **new required dependency** (previously optional or new entirely) or **change to the minimum required version** of an existing dependency **must be announced four weeks in advance**, regardless of whether it exceeds the baseline LTS version.
* These changes should be communicated at least through a GitHub Pull Request and linked discussion.
* Pull Requests that change required dependencies or affect build configuration **must be labeled `packaging-impact`** to ensure visibility for downstream packagers. Contributors are encouraged to note this need in the PR description or comments if relevant.

  * Tagging active packagers directly in the PR or related discussions is encouraged but optional.
  * For broader visibility, significant changes may also be posted to the FreeCAD development forum or a dedicated packagers channel if one exists.
* Authors must consider the impact on packaging and downstream distributions. Excessive burden on packagers should be avoided or clearly justified.
* Dependency changes must include:
  * Instructions or notes for packagers (e.g., new build options, system packages needed),
  * Compatibility guards (e.g., fallback code or build conditionals), where practical.
* Maintainers may delay or reject changes that create unreasonable challenges for downstream maintainers or violate this policy without clear justification.
* In **exceptional cases** - such as security fixes, urgent regressions, or high-priority build issues - maintainers may approve and merge such changes without prior notification. In those cases, a good-faith effort should be made to notify affected packagers and document the change promptly after merging.

### Transitioning to New Ubuntu LTS Releases

When the current Ubuntu LTS baseline reaches the end of its standard support period, maintainers **must announce a planned transition** to the next supported LTS release. This announcement should occur **at least four weeks in advance**, via:

* A pinned GitHub issue in the FreeCAD repository labeled `packaging-impact`,
* A post on the FreeCAD development forum, and
* Optionally, a notification to a dedicated packagers channel or mailing list (if one exists).

The announcement must include:

* The expected cutoff date,
* The new target LTS version,
* Any anticipated CI or tooling changes.

Contributors should be given time to adjust CI configurations, library usage, or documentation before the new baseline takes effect. Unless the transition involves broader architectural or compatibility changes, no new FEP is required.

#### Timing Considerations:
Maintainers have discretion to choose **when** to transition to the next Ubuntu LTS, as long as the current baseline is no longer under standard support. The transition **should not occur during high-risk phases** of the FreeCAD development cycle, such as just before a major release or during complex refactorings. If practical, transitions should be aligned with minor release cycles or quieter development periods to reduce disruption.

## Alternatives Considered

An alternative approach would have been to explicitly define and independently maintain minimum versions for each dependency across all supported platforms. This was rejected due to the additional maintenance overhead and reduced predictability it would impose on packaging and CI environments. Anchoring to the oldest supported Ubuntu LTS offers a simpler and more consistent policy.

## Future Work

* Define guidelines for dropping support for older Ubuntu LTS versions (e.g., sunset grace period).
* Consider introducing automated tooling or bots to assist maintainers in labeling PRs with `packaging-impact`.
* Consider setting up an RSS feed for PRs labeled `packaging-impact` to improve visibility for downstream maintainers.
Consider formalizing a dedicated channel or mailing list to announce major packaging changes.
* Evaluate whether it would be beneficial to shift the baseline from the **oldest** supported Ubuntu LTS to the **newest** available LTS, and clarify the implications for developers and packagers.

## Changelog

* *0.1* – Initial draft
* *0.2* – Clarified support window definition, added platform-wide dependency consistency policy, formalized LTS transition notice requirements

## References

* [Ubuntu Release Cycle](https://ubuntu.com/about/release-cycle)

## License

[CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/)
