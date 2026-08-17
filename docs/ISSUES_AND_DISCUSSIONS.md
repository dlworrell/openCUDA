# Issues and Discussions Workflow

openCUDA separates conversation/design discovery from committed implementation work.

- Discussions are for questions, research, RFCs, proposals, roadmap planning, benchmark interpretation, hardware observations, and governance deliberation.
- Issues are the work queue for reproducible defects, approved/scoped implementation, validation tasks, documentation changes, operational work, moderation review, and administrative actions.
- Pull requests implement tracked work and follow `GOVERNANCE.md`.

GitHub can create an issue directly from a discussion; the discussion body is copied and its labels are retained. openCUDA uses that native transition as the preferred promotion path.

## Discussion category inventory

The category slug must match the corresponding file in `.github/DISCUSSION_TEMPLATE/`. The machine-readable contract is `config/discussion-categories.json`.

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

The chooser includes: Bug; Implementation Request; Discussion Promotion; Compatibility; Hardware Validation; Build/CI; Performance/Benchmark; Documentation; Governance/Administration; Security Hardening; and Moderation Report.

Blank issues are disabled for normal contributors. Contact links route exploratory architecture, compatibility, ideas, help, and general questions into Discussions. Sensitive security reporting is routed to `SECURITY.md`.

The Moderation Report form must be used without quoting, pasting, screenshotting, or re-uploading prohibited content. Reporters link to the source and classify the concern so the review task does not duplicate harmful material.

## Automation

`issue-routing.yml` reads `config/issue-routing.json` and adds granular labels derived from structured form fields, including roadmap phase, compatibility class/target, and documentation domain.

`bootstrap-discussions.yml` reads `config/discussion-categories.json`. After Discussions and the category inventory exist, it verifies category slugs/names/Q&A semantics and creates initial index/welcome discussions without duplicating existing seed posts.

`content-moderation.yml` scans newly created/edited Discussions, Discussion comments, Issues, Issue/PR conversation comments, Pull Request descriptions, and review comments. Blocking text findings are routed to a Community Moderator without copying the matched content into the moderation Issue. Embedded media receives a manual-review signal because local CI cannot inspect image/video pixels.

`repository-audit.yml` verifies live settings that source CI cannot prove, including Issues/Discussions enablement, branch protection, labels, and the live Discussion category inventory.

The full verification model is documented in `docs/CI_TEST_SUITE.md` and moderation operations in `docs/CONTENT_MODERATION.md`.

## Moderation and authority

- `CODE_OF_CONDUCT.md` applies to Issues, Pull Requests/reviews, Discussions, comments, and committed project content.
- L2+ Community Moderators may disposition ordinary content-review tasks without code-merge or repository-admin authority.
- Q&A authors and users with sufficient triage authority may mark answers.
- Architecture, compatibility, security, release, hardware-validation, and governance decisions require the authorities defined in `GOVERNANCE.md`.
- Security-sensitive moderation (credential exposure, malicious links, threats, or related incidents) also requires Security Reviewer/Administrator escalation.
- Creating an issue from a discussion does not itself approve or assign work.
- Labels route responsibility; labels do not grant authority.
- Automated moderation does not auto-delete content; human review remains authoritative for destructive/moderation actions.

## Bootstrap checklist

A Repository Administrator must:
1. Enable Settings -> Features -> Discussions.
2. Create the sections/categories above using the exact slugs/formats.
3. Merge the PR containing `.github/DISCUSSION_TEMPLATE/` and the CI/moderation workflows.
4. Run Actions -> bootstrap-discussions -> Run workflow.
5. Run Actions -> repository-audit with `strict=true`.
6. Run Actions -> content-moderation manually to execute the policy self-test.
7. Verify issue chooser contact links, discussion forms, automatic labels, Q&A answer behavior, Discussion -> Issue label retention, and moderation-task routing.
8. Configure the required pull-request status checks from `docs/CI_TEST_SUITE.md` when branch protection/rulesets are established.

References:
- https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/enabling-or-disabling-github-discussions-for-a-repository
- https://docs.github.com/en/discussions/managing-discussions-for-your-community/managing-categories-for-discussions
- https://docs.github.com/en/discussions/managing-discussions-for-your-community/creating-discussion-category-forms
- https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/creating-an-issue
