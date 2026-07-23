# FEP-0012: Gating All FreeCAD Network Access

| FEP-0012       |                                                                       |
| -------------- | --------------------------------------------------------------------- |
| Type           | Core Change                                                           |
| Description    | Route all outbound network access through a single user-controllable gate with a default-deny policy. |
| Status         | Draft                                                                 |
| Author(s)      | Chris Hennes (@chennes)                                               |
| Version        | 0.1                                                                   |
| Created        | 2026-07-22                                                            |
| Updated        | 2026-07-22                                                            |
| Discussion     | TBD                                                                   |
| Implementation | TBD                                                                   |

FreeCAD and its bundled components make outbound network connections for a variety of reasons: fetching the addon catalog and downloading addons, retrieving online documentation, loading the in-application BIM tutorial and object libraries, and more. There is no single, authoritative place where these connections are declared, controlled, or can be observed by the user. This FEP proposes a central network-access gate through which **all** outbound connections originating from FreeCAD core, workbenches, and (where technically possible) addons must pass. The gate enforces a user-configurable policy, defaults to denying access until the user has made an explicit choice, and gives the user a clear, auditable record of what FreeCAD is connecting to and why.

## Motivation

FreeCAD is used in environments with a wide range of network expectations: air-gapped industrial and defense settings, privacy-sensitive individual users, corporate networks with egress policies, and ordinary desktop users who simply want to know what their CAD program is doing on the internet. Today, that user has no coherent answer to a simple question: *"What does FreeCAD connect to, why is it connection, and how can I stop it?"*

The current situation has several problems:

1. **No single source of truth.** Network calls are scattered across the C++ core, Python workbenches, and third-party addons. There is no inventory of endpoints and no consistent way to disable them.
2. **Inconsistent and incomplete controls.** Some features (e.g. the Addon Manager, Help, BIM Tutorial) have their own *ad hoc* preferences, but these are per-feature, worded differently, and easy to miss. Disabling one does not imply anything about the others.
3. **No default-safe posture.** A fresh install may connect to the network before the user has had any opportunity to consent. This is unacceptable in regulated, air-gapped, or privacy-sensitive deployments, and inadvisable in any setting.
4. **No auditability.** A user cannot see a log of what network resource was contacted, when, and by which subsystem, which makes it impossible to verify claims about FreeCAD's network behavior or to debug egress-policy problems.
5. **Addons are unconstrained.** Addons can make arbitrary network calls with no visibility to the user and no relationship to any FreeCAD-level policy.

This affects the whole community: it is a recurring source of forum questions and mistrust, a blocker for adoption in secure environments, and a growing liability as more features become network-aware.

## Rationale

The central design decision of this enhancement proposal is to funnel **all** outbound access through one gate rather than adding more per-feature toggles. A single choke point is the only way to make guarantees ("nothing leaves this machine unless you allow it") that are actually verifiable. Per-feature preferences, by construction, can never make a whole-application guarantee, because a feature added tomorrow will not be covered by today's toggles.

FreeCAD will adopt a **default-deny** posture for a first-run installation because the cost of a wrongly-allowed connection (a privacy or policy violation that has already happened) is not reversible, whereas the cost of a wrongly-denied connection (a feature does not work until the user opts in) is visible, recoverable, and clearly attributable to the policy. A first-run prompt lets ordinary users opt into the convenient default with one click, while secure deployments can pin the policy closed.

This policy is expressed in terms of **named capabilities** (e.g. "addon catalog", "online documentation", "BIM tutorial") rather than raw hosts or URLs, because users reason about *what a connection is for*, not about hostnames, and because the set of hosts backing a capability may change over time without any change in user intent.

Enforcement is placed in the **core network layer** rather than relying on each caller to check a flag, because voluntary compliance cannot provide a guarantee and cannot cover code the FEP authors do not control. Callers ask the gate; the gate is the only sanctioned way to open a connection, and within first-party code it is the only transport provided, so a bypass is a reviewable policy violation, not a supported code path. As discussed under *Enforcement point* below, this is a strong guarantee for code FreeCAD controls, but it is not a runtime trap that can catch arbitrary in-process code.

## Specification

### Overview

A new core component, the **Network Access Gate**, mediates every outbound network request made by FreeCAD. In this framework, no FreeCAD-originated code opens a network connection directly; instead it requests access from the gate, identifying itself and the **capability** it is exercising. The gate consults the active **policy**, optionally prompts the user, records the decision and the request in an **audit log**, and either permits the connection or refuses it.

### Capabilities

Every network-using feature declares one or more capabilities. A capability has:

- a stable machine identifier (e.g. `addon.catalog`, `addon.install`, `help.documentation`, `bim.tutorial`, `bim.library`),
- a human-readable name and description shown in the user interface,
- the owning subsystem (core, a named workbench, or a named addon),
- the set of endpoints (hosts / URL patterns) it is expected to contact.

Capabilities are registered at startup (for example in a module's `Init.py` file) so that the policy UI can enumerate them even before any connection is attempted. A later request that names an unregistered capability is logged and denied.

### Policy

The policy maps each capability (and a global default) to one of:

- **Allow**: permit without prompting.
- **Deny**: refuse without prompting.
- **Ask**: prompt the user on first use in a session (or per configured scope), remembering the answer according to the user's choice.

The policy is layered, from lowest to highest precedence:

1. **Built-in default:** global default is **Ask** on a normal desktop install; the shipped configuration MUST NOT set any capability to **Allow** without a prior user decision.
2. **Administrative policy:** a deployment (e.g. an air-gapped or corporate install) can supply a locked policy file that pins capabilities and forbids the user from loosening them. This supports "network fully disabled" as an enforced deployment mode.
3. **User policy:** the user's own choices, stored in preferences.

Where layers conflict, the more restrictive administrative layer wins over the user layer.

### First-run behavior

On first run (no user policy present), FreeCAD MUST NOT make any outbound connection before the user has been presented with a network-access choice. The first-run experience offers at minimum: "Allow FreeCAD's standard online features", "Ask me each time", and "Keep FreeCAD offline". This choice seeds the user policy and can be revisited at any time in preferences.

### Enforcement point

The gate is enforced in the core network layer used by FreeCAD (the C++ networking utilities and the Python HTTP helpers exposed to workbenches). Direct use of lower-level networking that bypasses the gate is prohibited within FreeCAD core and bundled/first-party workbenches and should be caught in review and, where feasible, by automated checks.

It is important to be precise about what "enforcement" means here, because it is not a runtime trap. For code FreeCAD controls, enforcement rests on three legs: the gate is the only sanctioned API, it is the only network transport the core provides to that code, and a CI/static check flags direct use of raw networking (`QNetworkAccessManager`, `urllib`, `requests`, `socket`, `curl`, and similar) outside the gate. That combination is strong precisely because we control the code and its review process. It is **not**, however, a mechanism that can intercept an arbitrary in-process connection attempt: native libraries, compiled extensions, spawned subprocesses, and determined or hostile code can open sockets the gate never sees. Best-effort *observation* of some traffic is possible (see the addon-ecosystem discussion under Open Issues), but a hard guarantee against uncooperative in-process code requires an OS-level boundary, which is out of scope for this component and is covered under Alternatives and Further Work.

### Audit log

Every access decision is recorded: timestamp, capability, requesting subsystem, target endpoint, decision (allow/deny), and the policy layer responsible. The log is viewable in the UI and exportable. The audit log itself performs no network access. Sensitive payloads are not logged; only connection metadata is recorded.

### API sketch

The gate exposes a small, stable API in both C++ and Python, for example (illustrative, not final):

```python
from FreeCAD import NetworkGate

# Register at startup
NetworkGate.registerCapability(
    id="addon.catalog",
    name="Addon catalog",
    description="Downloads the list of available addons.",
    owner="AddonManager",
    endpoints=["https://addons.freecad.org/*"],
)

# At point of use (simplest case, e.g. a blocking get)
try:
    with NetworkGate.session("addon.catalog") as net:
        reply = net.get("https://addons.freecad.org/addon_catalog_cache.zip")
        data = reply.content
except NetworkGate.AccessDenied:
    ...  # offline / user declined --- degrade gracefully
```

The equivalent in C++:
```c++
Base::NetworkSession net("addon.catalog", Base::NetworkSession::NoThrow);
if (!net.granted()) {
    return;   // denied/offline --- nothing opened
}
Base::NetworkReply reply = net.get(QUrl("https://addons.freecad.org/addon_catalog_cache.zip"));
```

Non-blocking gets, etc. will take a slightly different form, but the basic idea remains to attempt to grab a network access session for a specific capability. Proceed normally if it's approved (either because the user responded to a dialog, or because their allow preference has been previously stored), and if the request is denied gracefully degrade (in most cases simply logging the attempt and then ignoring the failure).

### Impact on existing features / subsystems

A survey of the current codebase finds the following outbound network consumers, all of which must be migrated to declare a capability and route through the gate:

- **Addon Manager** (`Mod/AddonManager`): the largest consumer. It downloads the addon and macro catalog caches and runs connectivity/status checks against `addons.freecad.org`, fetches addon popularity stats, installs and updates addons via the `git` CLI (clone/fetch) or ZIP download from GitHub/GitLab repos, and installs Python dependencies via `pip`. It already funnels most network access through its own `NetworkManager` wrapper, which is a natural first adapter to the gate.
- **Help** (`Mod/Help`): fetches documentation from `wiki.freecad.org` and `raw.githubusercontent.com`. Notably, it also *POSTs* page content to `api.github.com/markdown` for server-side rendering. That is an outbound data flow, not just a download, and the audit log and consent model should make it visible.
- **BIM** (`Mod/BIM`): several independent fetchers: the in-application tutorial (`freecad.org/wiki`), online object libraries (FreeCAD-library repo and third-party vendor sites), the IfcOpenShell installer (which scrapes a GitHub comment thread for a download URL), a generic Arch downloader, and a runtime download of the `pyshp` module source during shapefile import (remote code fetched and executed on demand).
- **Core GUI download manager** (`Gui/DownloadManager`): used by `MainWindow::loadUrls()` to download remote URLs that are opened in or dropped onto FreeCAD.
- **Material** (`Mod/Material`): provides a framework for *external* (potentially online) material libraries via `ExternalManager`. No network endpoint ships in core today; the transport is delegated to a user-provided external manager. The capability should exist so that, if such a manager is installed, its access is gated like any other.

Migration can be incremental: the gate can ship first with a permissive compatibility mode that logs (but allows) un-migrated callers, so that the audit log immediately reveals every remaining un-migrated caller that still routes through FreeCAD's own networking helpers. Note that this reveals only callers that use those helpers; a caller that reaches the network through raw sockets, a native library, or a subprocess will not appear this way, which is why the CI/static check described under *Enforcement point* is needed to find them. The default-deny guarantee is only asserted once all core/bundled callers are migrated and the compatibility mode is removed.

### Backwards Compatibility (only for Core Changes)

- **User-facing:** existing per-feature network preferences should be mapped onto the new policy so that users who previously disabled a feature stay disabled. Where an old preference has no clean mapping, err toward the more restrictive interpretation and ensure the change is added to the release notes.
- **Files:** no document file format changes are required. Policy is stored in user/system preferences, not in documents.
- **Addons/API:** addons that make direct network calls will continue to function while compatibility mode exists, but will be visible in the audit log as ungated. A future addon-guidelines update should require addons to declare capabilities; enforced sandboxing of addon network access is called out under Further Work as it is substantially harder.

## Open Issues

- Exact granularity and scope of "remember my answer" for the **Ask** policy (per session, per capability, per endpoint, persistent).
- The format and locking mechanism for administrative/deployment policy files.
- Interaction with system-level proxies and corporate TLS-inspection setups.

### The addon ecosystem

The addon ecosystem is the hardest open question for this proposal, because FreeCAD does not directly control addon code, addons run arbitrary Python in-process, and their network behavior is difficult to audit, especially when an addon is *actively trying to conceal* its network access (e.g. via dynamic imports, subprocesses, native extensions, or obfuscated endpoints). The following must be resolved before this FEP can advance:

- **Requirement vs. observation.** Will FreeCAD *require* addons to use the network-access API, or will it only be able to *observe and report* their traffic? Given that addons execute arbitrary code in-process, the gate can guarantee behavior for callers that cooperate, but a determined addon can bypass any in-process check. We must be honest about the limits of enforcement versus mere visibility, and decide how strong a claim we are willing to make.
- **Grandfathering existing addons.** There is a large body of existing addons that predate this API. We need a migration policy: a compatibility/observation-only period, deprecation timelines, and clear guidance so that older addons continue to function (visible in the audit log as ungated) while authors adapt, rather than breaking the ecosystem on a flag day.
- **Compliance and delisting.** Should the official addon catalog *require* declared network capabilities as a condition of listing? If so, what are the consequences of non-compliance? Warnings, reduced trust indicators, or delisting? Who adjudicates, and what is the appeal path? Delisting is a governance action with community impact and should not be decided unilaterally within this FEP.
- **Concealed / evasive access.** For addons that deliberately hide network access, what detection, disclosure, and response mechanisms are realistic? Options range from static/dynamic analysis at submission time, to community reporting, to relying on OS-level egress controls as a backstop. We should document what we can and cannot detect so users are not given a false sense of security.
- **Trust and labeling.** How is an addon's declared-and-audited network posture presented to users at install time (e.g. "this addon declares these capabilities" / "this addon's network access is unverified"), so that the consent model extends sensibly to addons without overstating the guarantee?
- **Native and out-of-process code.** How are addons that reach the network through compiled extensions, bundled binaries, or spawned subprocesses handled, since these can escape the in-process gate entirely?

These questions require coordination with the Addon Manager maintainers and the broader community, and may warrant a follow-up FEP focused specifically on addon network governance. Enforced (as opposed to observed) addon sandboxing is tracked under Further Work.

## Rejected Ideas

- **More per-feature toggles.** Rejected because they cannot provide an application-wide guarantee and do not cover future features. (See Rationale.)
- **A build-time "offline build" flag only.** Useful for some deployments but insufficient: it does not help ordinary binary users, is not auditable at runtime, and fragments the ecosystem into offline/online builds.
- **Host/URL-based policy as the primary user model.** Rejected as the primary interface because users reason about purpose, not hostnames; endpoints may still be shown as detail under each capability.

## Alternatives

- **OS-level firewalling** (per-application egress rules). This is a legitimate complementary control and secure deployments may still use it, but it cannot distinguish FreeCAD's capabilities from one another, is per-platform, and provides no in-application audit or consent experience.
- **Proxy-only routing** through a user-run local proxy. Powerful for advanced users but far too complex as the default consent mechanism for the general user base.

## Implementation

A feasible path:

1. Introduce the gate component and its C++/Python API with a permissive, logging-only compatibility mode.
2. Migrate core and bundled-workbench network callers to declare capabilities and route through the gate.
3. Add the policy UI, first-run experience, and audit-log viewer.
4. Add administrative/locked-policy support for deployments.
5. Flip the default to Ask/Deny and remove compatibility mode once all bundled callers are migrated.

The incremental compatibility mode makes this tractable without a flag-day migration, and the audit log provides a concrete completion criterion (no ungated callers remain among bundled code).

## Further Work

- Enforced (not merely observed) network sandboxing for addons.
- Fine-grained rate/volume reporting per capability.
- A signed manifest of expected endpoints per release, so egress can be validated against a known-good set.
- Integration with FreeCAD's addon store to publish each addon's declared capabilities.

## References

- FEP-0001: FEP Process: [./FEPs/FEP-0001-process/README.md](../FEP-0001-process/README.md)

## License / Copyright

All FEPs are explicitly [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/).
