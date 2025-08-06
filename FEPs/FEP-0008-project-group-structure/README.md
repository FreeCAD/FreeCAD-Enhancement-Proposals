# FEP-0008 Project Groups Structure

| FEP-0008   |                                                 |
| ---------- | ----------------------------------------------- |
| Type       | Process                                         |
| Status     | Draft                                           |
| Author(s)  | Kacper Donat @kadet1090 (maintainer, DWG, CQWG) |
| Version    | 0.1                                             |
| Created    | 2025-07-27                                      |
| Updated    | TBD                                             |
| Discussion | TBD                                             |

FreeCAD, as a project, has not historically had a well-defined management or responsibility
structure. Over time, however, some structures have organically emerged in the form of **Working
Groups**. This document formalizes how such groups are created, how they operate, and what their
responsibilities and limitations are.

## Motivation

Many developers and users find the organizational structure of the project confusing. People are
often advised to consult groups like DWG, CWG, or CQWG, but there is little information on what
these groups do, how to contact them, and who their members are.

Historically, all development decisions were made by the Maintainers in dialogue with the community.
This worked when the project and its community were relatively small, and everyone could keep up
with all discussions. Today, however, the size of both the project and its community has outgrown
this model, and it is no longer feasible to rely solely on Maintainers.

Over time, some groups have formed organically. For example, the **Design Working Group** (DWG) grew
out of a few community members active in UX/UI. Since that group was already operating de facto,
Maintainers decided to treat it as an advisory body.

## Rationale

The lack of clear information about these groups has become a barrier to entry and a source of
frustration for both new and existing contributors who are not always aware of the latest
developments. This document aims to formalize the current structure of these groups and answer key
questions:

1. What Working Groups exist?
2. How are groups structured?
3. How can someone become a member of a group?
4. Where can the current membership of a group be found?
5. What are the tasks and non-tasks of these groups?
6. How do these groups operate and communicate?

This document is intended to be a living standard and will always reflect the current state of the Working Groups.

## Maintainers

**Maintainers** are a group of people with permission to merge code into the project's main branch.
They are responsible for following and enforcing the processes defined in
[CONTRIBUTING.md](https://github.com/FreeCAD/FreeCAD/blob/main/CONTRIBUTING.md) and FEPs, reviewing and merging PRs, and more. Maintainers act
in good faith and strive to remain impartial, putting the interests of the project above personal
opinions. Ultimately, Maintainers are responsible for ensuring that the project develops in a
coherent and maintainable way; final decisions rest with them.

However, it is impossible for a single person to have deep expertise in every area of the project.
To ensure that all areas are handled well and that development remains consistent, Maintainers often
seek advice from **Working Groups**. While their recommendations are usually followed, Maintainers
may also consider other factors, such as community impact or maintenance costs, before making a
final decision.

### Current Project Maintainers

In alphabetical order:

- Adrián Insaurralde Avalos (@adrianinsaval)
- Benjamin Nauck (@hyarion)
- **Brad Collette** (@sliptonic)
- **Chris Hennes** (@chennes)
- Kacper Donat (@kadet1090)
- @Roy-043
- @WandererFan
- **Werner Mayer** (@wwmayer)
- **Yorik van Havre** (@yorik)

**Bolded** names indicate Project Administrators.

#### Inactive Maintainers

Some Maintainers who were once active are no longer participating in development. While they do not
lose their Maintainer status, those who are inactive for an extended period will have their write
access temporarily suspended for security reasons. Access is restored if and when they return.

Current list of inactive maintainers:

- ...

### How to Become a Maintainer

New Maintainers are appointed by the current Maintainers through full consensus. Candidates are
selected from active contributors who have been engaged with the community for a significant time,
review PRs and issues, participate in project meetings, and adhere to the Code of Conduct.

### Authority and Accountability

Maintainers hold the **sole authority** to make decisions on behalf of the Project. Maintainers operate on a consensus basis whenever possible, and a rough consensus basis when full consensus cannot be achieved. All decisions from a Maintainer should be interpreted as a decision on behalf of the whole body of Maintainers. However, mistakes can happen, and decisions may need to be revisited. If a member of the FreeCAD community feels that a mistake has been made (for example, a PR merged when it shouldn't have been, or closed when it should have been merged), they should reach out to a member of the Maintainers team to request reconsideration. Maintainers have the responsibility to take these requests into consideration a part of their larger responsibility to the health of the project as a whole.

## Working Groups

A **Working Group** is a team of community members (not necessarily developers) who work together
toward a defined set of goals. Working Groups are typically permanent and cover broad areas of
interest, such as UI/UX, infrastructure, code quality, or CAD industry practices. Groups may focus
on development, infrastructure, policies, or other project-related topics.

The purpose of Working Groups is to provide a more organized venue for discussion and to ensure that such discussions yield useful outcomes. Each Working Group must conduct a genuine, documented discussion process. Working Groups must not be used solely to confer legitimacy on a predetermined decision.

Working Groups have no special decision-making authority unless explicitly delegated by the Maintainers; even in such cases, responsibility rests with the Maintainers, who grant and oversee that authority. Their primary function is to act as an advisory body. Working Groups shall not be held responsible for any decisions.

Working Group statements do not carry any special status over other community views. Maintainers should treat them as such when making decisions. If Maintainers cite a Working Group’s position as a rationale for a decision, the legitimacy of that decision derives from the quality and breadth of the group’s discussion—not from the mere existence of a Working Group statement.

### Structure of a Working Group

Each Working Group must have a designated **Chairperson** responsible for managing the group,
defining its rules, and acting as the primary contact. No individual should chair more than one
Working Group. The Chairperson must appoint at least one (ideally no more than two) **Co-Chairs** to
ensure continuity during absences. Co-Chairs may serve in multiple groups. Collectively, the
Chairperson and Co-Chairs are referred to as “the Chair”. Any decision regarding the Group that
is not covered by the document is up for the Chair to decide.

If a Chair is unable to fulfill their duties, the group members may request that the Maintainers
appoint a replacement.

#### Membership and Internal Structure

The Chair determines the rules for membership, which must be non-discriminatory and allow anyone to
request to join. These rules must be accessible to everyone and the desired communication link for the application must be clearly stated. Specific expertise may be required to become a member. Community members may belong
to multiple Working Groups.

New members of the working group are appointed by the Chair. Community member may request membership by
contacting the Chair or asking over public channel. The Chair can accept or deny such request - in such
case however the Chair should provide rationale for the decision, for example lack of required expertise. Not being a member does not however forbid anyone from taking part in the discussions.

Existing members can be removed from the group by the Chair if they do not longer fulfill the
requirements or the violate Code of Conduct [[2]](#code-of-conduct).

Since official communication takes place on GitHub, all members must have a GitHub account.
Membership is defined by the corresponding GitHub team: `@FreeCAD/<name>-working-group`.

Groups may define additional roles, but the structure should be kept as simple as possible.

### Communication Within a Group

Groups may choose their preferred communication tools, but the chosen platform must allow free
participation without barriers such as payment or special permissions. The method should be as
transparent as possible, ideally allowing read-only access without requiring an account.

Decisions (such as policy proposals, feature opinions, or issue feedback) must involve all group
members and, where appropriate, input from the wider community to avoid echo chambers. The Chair is
responsible for seeking compromise and consensus. If full consensus cannot be reached, the Chair
will summarize the prevailing opinion using the “rough consensus” rule [[1]](#rough-consensus).

Any official group statement must be posted on GitHub (as a comment on a PR/issue, a new issue, or
an FEP). Statements must clearly represent the group's position, not an individual opinion, and
should include a summary of the discussion. In case of group not being able to reach full consensus
over the matter, the summary must contain information about concerns raised within discussion.
Additionally, if possible a link to the full public conversation shall be posted along the summary.

Group statements that are not posted on GitHub shall not be cited as justification for any decision.
Decisions must not be made concurrently with the publication of an official group statement. There
must be a reasonable interval between an official group statement and any related decision, during
which community members who are not part of the group can participate in the discussion.

Only the Chairperson or a Co-Chair may speak on behalf of the Group. If a member makes a statement purporting to represent the Group, confirmation may be requested from the Chairperson or the Co-Chairs. Unless it is expressly stated that the speaker is acting on behalf of the Group, all statements are deemed to be made in a personal capacity.

### Creating a New Working Group

Because Working Groups are permanent, their creation requires extended discussion. A new Working
Group must not overlap or conflict with existing groups and should address an area that is currently
uncovered.

Working Groups are created by submitting a new FEP establishing the group with motivation and rationale. The PR introducing new group should also update this FEP with specification of the new group using template below:

```
### Name of the group (Abbr)

Short description of the group.

#### Tasks of the group
 * Task1
 * Task2
 * ...

#### Non-Tasks of the group
 * Task1
 * Task2
 * ...

### Communication

Description of how to participate in discussions with the group, with links if needed.

#### Members
 * @chairperson (chairperson)
 * @cochair1 (co-chair)
 * @member1
 * @member2

##### Membership Requirements

Description of requirements for membership.
```

## Task Forces

While Working Groups are permanent, sometimes there is a need for smaller, temporary teams dedicated
to a specific, clearly defined objective. A **Task Force** is such a team, often composed of members
from multiple Working Groups, formed to deliver a single, well-scoped result.

Task Forces differ from Working Groups in that they focus on execution rather than consultation.
Once their goal is achieved, Task Forces are typically disbanded.

Examples of Task Forces:

- **TNP Mitigation TF** – focused on improving Topological Naming in FreeCAD
- **Materials TF** – focused on implementing a new materials API

### Structure of a Task Force

Each Task Force must have a designated **Leader**. Leaders may appoint Co-Leaders, but this is
optional given the temporary nature of these teams. Task Forces usually consist of 1–5 members,
often starting with just the Leader.

Membership is managed by the Leader, who may invite others or accept volunteers.

### Communication within Task Force

Just like Working Groups, Task Forces are free to pick communication method that suits them best.
While using open and public communication methods is encouraged, unlike Working Groups there is no strict
requirement for publicity. Results of work of Task Force must however be publicly available and discussed
on GitHub.

### Creating a New Task Force

A Task Force may be created by any community member (typically the person leading an initiative) or
by Maintainers, who can appoint a Leader. To create a Task Force, the Leader (or a Maintainer) must
submit a PR to the Developer Handbook repository in the “Task Forces” section, following the
template:

```
TBD
```

### Differences Between Working Groups and Task Forces

| Aspect                  | Working Group (WG)                                                                                   | Task Force (TF)                                                                                          |
|-------------------------|------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------|
| **Purpose**            | Advisory body focusing on broad, ongoing areas (e.g., UI/UX, infrastructure, code quality).          | Temporary team focused on delivering a single, specific, well-defined result.                             |
| **Duration**           | Permanent                                                                                             | Temporary (disbanded after achieving its goal).                                                           |
| **Scope**              | Broad areas of responsibility.                                                                        | Narrow scope with a clear definition of success.                                                          |
| **Decision Power**     | Advisory only (final decisions are made by Maintainers).                                              | Execution-focused, provides deliverables rather than general advice.                                      |
| **Leadership**         | Led by a Chairperson and Co-Chairs.                                                                    | Led by a Leader (optionally with Co-Leaders).                                                             |
| **Membership**         | Members appointed by the Chair, open to all with relevant expertise.                                   | Membership managed by the Leader, can include volunteers or invitees.                                     |
| **Communication**      | Public, transparent communication; discussions and statements are posted on GitHub.                   | Communication may be private during work, but results must be shared publicly and discussed on GitHub.    |
| **Creation Process**   | Created through FEP process, after broad discussion.                                      | Created by a Maintainer or community member via a PR in the “Task Forces” section of the Developer Handbook. |

## Current Working Groups

This section lists currently active Working Groups.

### Design Working Group (DWG)

The DWG provides advice and feedback on user interface changes and consistency. It works with
developers and Maintainers to propose solutions that improve the coherence and usability of
FreeCAD’s user experience across all platforms.

#### Tasks of the group

- Providing feedback on interface changes and consistency
- Creating guidelines to improve FreeCAD UI/UX
- Ensuring UI/UX consistency within FreeCAD
- Ensuring UI/UX consistency with other applications and CAD suites
- Helping design interfaces for new features
- Maintaining the UX/UI roadmap

#### Non-Tasks of the group

The group consists mainly of UI/UX experts, not developers, so certain tasks are out of scope:

- Implementing suggestions in PRs
- Providing advice on implementation details

### Communication

Discord: https://discord.gg/PzYEBh5aA8

Channels:
- `#design-working-group` – general discussion
- `#ux-topics` – topic-specific discussions

#### Members

- @obelisk79 (chairperson)
- @kadet1090 (co-chair)
- @maxwxyz (co-chair)
- @pierreporte
- @MisterMakerNL
- @tigert

##### Membership Requirements

A member should:

* Participate actively in UI/UX discussions
* Seek consensus, even if it is not aligned with personal opinion
* Provide feedback in line with good UI/UX practices
* Research multiple solutions before providing feedback

The group seeks members with strong UI/UX intuition or experience. Being a
developer is not required but is an advantage.

### CAD Working Group (CWG)

The main goal of CWG is to ensure that FreeCAD is developed in a way that makes it possible to use it
in professional scenarios, aligning it with industry standards and ensuring that most daring issues
are tackled first.

#### Tasks of the group
 * Establishing CAD development roadmap
 * Providing feedback for new features

### Communication

Description of how to participate in discussions with the group, with links if needed.

#### Members
 * @pierreporte (chair)

##### Membership Requirements

_(TBD)_

### Code Quality Working Group (CQWG)

The CQWG provides advice and feedback on code quality, establishes best practices, and helps
contributors write clean and maintainable code.

#### Tasks of the group

- Reviewing PRs for code quality
- Establishing best practices for the FreeCAD codebase
- Creating guidelines for code reviewers
- Providing advice to contributors on code quality

### Communication

Discord: https://discord.gg/hDh4zxhkrw

Channels:
- `#code-quality-working-group` – general discussion
- `#code-quality-topics` – topic-specific discussions

#### Members

- @kadet1090 (chairperson)
- @hyarion (co-chair)
- @bensay
- @tritao
- @pieterhijma

##### How to become a member?

A member should:
* Provide constructive PR reviews
* Participate actively in code quality discussions
* Seek the best possible solutions to problems
* Keep in mind constraint of the existing codebase and costs associated with changes

### Infrastructure Working Group (IWG)

_(TBD)_


## References

- <span name=rough-consensus>[1]</span>: https://en.wikipedia.org/wiki/Rough_consensus
- <span name=code-of-conduct>[2]</span>: https://github.com/FreeCAD/FreeCAD/blob/main/CODE_OF_CONDUCT.md


## License / Copyright

All FEPs are explicitly [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/).
