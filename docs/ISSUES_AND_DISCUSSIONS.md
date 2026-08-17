# Issues and Discussions Workflow

openCUDA separates conversation/design discovery from committed implementation work.

- Discussions are for questions, research, RFCs, proposals, roadmap planning, benchmark interpretation, hardware observations, and governance deliberation.
- Issues are the work queue for reproducible defects, approved/scoped implementation, validation tasks, documentation changes, operational work, and administrative actions.
- Pull requests implement tracked work and follow `GOVERNANCE.md`.

GitHub can create an issue directly from a discussion; the discussion body is copied and its labels are retained. openCUDA uses that native transition as the preferred promotion path.

## Discussion category inventory

The category slug must match the corresponding file in `.github/DISCUSSION_TEMPLATE/`.

| Section | Category | Slug | Format | Default routing |
|---|---|---|---|---|
| Project | Announcements | `announcements` | Announcement | Maintainer project news/releases |
| Project | General | `general` | Open-ended | `discussion` |
| Project | Roadmap & Planning | `roadmap-planning` | Open-ended | `discussion`, `roadmap` |
| Design & Compatibility | RFC & Architecture | `rfc-architecture` | Open-ended | `discussion:rfc`, `architectural` |
| Design & Compatibility | Compatibility Research | `compatibility-research` | Open-ended | `discussion:research`, `compatibility` |
| Design & Compatibility | Ideas & Proposals | `ideas-proposals` | Open-ended | `discussion:proposal` |
| Engineering | Hardware & Reference Platforms | `hardware-reference-platforms` | Open-ended | `discussion:research`, `reference` |
| Engineering | Benchmarks & Performance | `benchmarks-performance` | Open-ended | `discussion:benchmark-analysis`, `operational:benchmarking` |
| Engineering | Development Help | `development-help` | Question & Answer | `discussion:question`, `developmental` |
| Community | Questions | `questions` | Question & Answer | `discussion:question` |
| Community | Show & Tell | `show-and-tell` | Open-ended | `discussion` |
| Community | Polls | `polls` | Poll | No form; GitHub does not support category forms for polls |
| Governance | Governance & Administration | `governance` | Open-ended | `discussion`, `role`, `access` |

## Discussion to Issue promotion

Promote when the outcome is scoped, required domain decisions are made or explicitly deferred, acceptance criteria can be stated, and an assignee can start without reopening the fundamental design question.

Preferred path:
1. Open the discussion.
2. Use **Create issue from discussion**.
3. Preserve inherited labels.
4. Add the appropriate roadmap phase, domain, role-routing, and operational labels.
5. Assign through a Task Manager/Maintainer under `GOVERNANCE.md`.
6. Link the issue back to the discussion and close the discussion when the decision record is complete.

If extra scoping is required, use the **Promote a discussion to implementation** issue form.

## Issue forms

The chooser includes: Bug; Implementation Request; Discussion Promotion; Compatibility; Hardware Validation; Build/CI; Performance/Benchmark; Documentation; Governance/Administration; and Security Hardening.

Blank issues are disabled for normal contributors. Contact links route exploratory architecture, compatibility, ideas, help, and general questions into Discussions. Sensitive security reporting is routed to `SECURITY.md`.

## Automation

`issue-routing.yml` adds granular labels derived from structured form fields, including roadmap phase, compatibility class/target, and documentation domain.

`bootstrap-discussions.yml` is a manual idempotent bootstrap workflow. After Discussions and the category inventory exist, it verifies category slugs and creates initial index/welcome discussions without duplicating existing seed posts.

## Moderation and authority

- L2+/Triage authority may classify and moderate ordinary discussions.
- Q&A authors and users with sufficient triage authority may mark answers.
- Architecture, compatibility, security, release, hardware-validation, and governance decisions require the authorities defined in `GOVERNANCE.md`.
- Creating an issue from a discussion does not itself approve or assign work.
- Labels route responsibility; labels do not grant authority.

## Bootstrap checklist

A Repository Administrator must:
1. Enable Settings -> Features -> Discussions.
2. Create the sections/categories above using the exact slugs/formats.
3. Merge the PR containing `.github/DISCUSSION_TEMPLATE/`.
4. Run Actions -> bootstrap-discussions -> Run workflow.
5. Verify issue chooser contact links, discussion forms, automatic labels, Q&A answer behavior, and Discussion -> Issue label retention.

References:
- https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/enabling-or-disabling-github-discussions-for-a-repository
- https://docs.github.com/en/discussions/managing-discussions-for-your-community/managing-categories-for-discussions
- https://docs.github.com/en/discussions/managing-discussions-for-your-community/creating-discussion-category-forms
- https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/creating-an-issue
