# openCUDA Governance

openCUDA uses a least-privilege governance model that separates **GitHub access**, **project authority**, and **domain approval responsibility**. A person's repository permission level does not by itself grant every project role, and a project role is not effective until it is recorded in [`docs/ROLE_ASSIGNMENTS.md`](docs/ROLE_ASSIGNMENTS.md).

## Current GitHub ownership constraint

The repository is currently owned by a personal GitHub account. GitHub personal-account repositories have an owner and collaborators rather than the full organization repository-role ladder. That means the policy below can be documented and partially enforced with pull requests, CODEOWNERS, reviews, labels, and rulesets/branch protection, but the most granular built-in access controls require an organization-owned repository.

If openCUDA moves to an organization, the project should map these governance levels to GitHub's Read, Triage, Write, Maintain, and Admin roles. GitHub Enterprise Cloud organizations may additionally define custom repository roles.

## Administration levels

Administration levels define the maximum authority a person may exercise. Functional roles below may require a minimum level, but do not automatically grant a higher level.

| Level | Name | Intended GitHub access | Authority |
|---|---|---|---|
| **L0** | Observer | Read | View code, issues, discussions, CI results, and published documentation. No project-management authority. |
| **L1** | Contributor | Write when direct collaboration is required; otherwise fork/PR | Create branches/PRs, propose code/docs, run tests, respond to review. Cannot approve their own work for governance purposes. |
| **L2** | Triage Coordinator | Triage | Classify issues/PRs, apply taxonomy, request information, assign ordinary tasks, manage milestones and queues. No merge authority. |
| **L3** | Reviewer | Write | Submit binding PR approvals/requests for changes within assigned review domains. No independent policy or release authority. |
| **L4** | Maintainer | Maintain | Manage repository workflow, merge approved PRs, manage branches/releases/CI operations within policy, and delegate ordinary tasks. |
| **L5** | Domain Approver | Maintain or Write plus explicit project delegation | Final domain authority for architecture, compatibility, documentation, security, release, or hardware-validation decisions. |
| **L6** | Repository Administrator | Admin | Manage repository settings, rulesets/branch protection, access, secrets, webhooks, security configuration, and emergency administrative actions. |
| **L7** | Project Owner | Owner/Admin | Final project-policy authority, role delegation/removal, governance amendments, ownership transfer, and resolution of unresolved cross-domain disputes. |

### Least privilege

Assign the lowest GitHub permission and lowest administration level that allow the required work. Domain approval authority should be delegated independently of general administrative power whenever possible.

## Functional roles

| Role | Minimum level | Primary authority |
|---|---:|---|
| **Project Owner** | L7 | Final governance and project-direction authority. |
| **Repository Administrator** | L6 | Repository settings, access control, rulesets, secrets, destructive/recovery operations. |
| **Maintainer / Merge Steward** | L4 | Merge PRs after required approvals/checks, maintain branches, coordinate normal repository operation. |
| **Task Manager / Triage Coordinator** | L2 | Classify, prioritize, assign, reassign, and close ordinary work items according to roadmap/taxonomy. |
| **Code Reviewer** | L3 | Approve/request changes on implementation PRs within assigned language/component scope. |
| **Architecture Approver** | L5 | Approve changes to ABI boundaries, component structure, scheduler/topology/memory/transport models, and `ARCHITECTURE.md`. |
| **Compatibility Approver** | L5 | Approve support-policy, lowering/fallback/unsupported behavior, CUDA-generation boundaries, and `COMPATIBILITY.md`. |
| **Documentation Approver** | L3 | Approve proposed documentation for clarity, accuracy, links, terminology, and consistency. Architecture/compatibility/security docs additionally require the appropriate domain approver. |
| **Security Reviewer** | L5 | Approve security-sensitive code, legacy-driver containment, secrets/CI security, and `SECURITY.md` changes. |
| **Release Manager** | L5 | Approve versioning, release candidates, release notes, release artifacts, and release publication. |
| **CI/Build Maintainer** | L4 | Maintain build presets, Actions workflows, self-hosted runner policy, compiler/toolchain gates, and reproducibility. |
| **Hardware Validation Maintainer** | L4 | Approve reference-hardware evidence, K80/CUBIX/DL380p topology captures, ECC/P2P/bandwidth baselines, and hardware-in-the-loop test results. |

One person may hold multiple roles. High-impact work should still receive independent review when another qualified person is available.

## Role assignment and revocation

1. Every active role assignment must be recorded in [`docs/ROLE_ASSIGNMENTS.md`](docs/ROLE_ASSIGNMENTS.md).
2. The assignment must name the GitHub user or organization team, administration level, functional role(s), domains, effective date, and assigning authority.
3. A role is not binding merely because a user has a high GitHub permission level.
4. The Project Owner or a delegated Repository Administrator may grant/revoke access; only the Project Owner or a governance-approved delegation may grant L5+ project authority.
5. Expired, inactive, or revoked assignments must remain in history through normal Git commits rather than being silently erased.
6. When organization teams become available, prefer teams for durable responsibilities (`@org/architecture-approvers`, `@org/docs-approvers`, etc.) rather than hard-coding individuals across the repository.

## Pull-request approval policy

Authors may not supply the sole binding approval for their own PR.

| Change class | Minimum approval |
|---|---|
| Ordinary implementation/tests/tooling | 1 Code Reviewer; Maintainer merges after checks pass. |
| Documentation-only, non-policy | 1 Documentation Approver. |
| Stable C ABI/public API | 1 Code Reviewer **and** 1 Architecture Approver. |
| Architecture or `docs/ARCHITECTURE.md` | 1 Architecture Approver; 2 total approvals when implementation changes accompany it. |
| Compatibility policy or `docs/COMPATIBILITY.md` | 1 Compatibility Approver; 2 total approvals when runtime behavior changes. |
| Security-sensitive code, workflows, secrets policy, or `SECURITY.md` | 1 Security Reviewer plus 1 Maintainer/Administrator approval. |
| Governance, CODEOWNERS, role assignments, access policy | Project Owner approval; changes affecting owner/admin authority require explicit L7 approval. |
| Release/versioning/public artifacts | 1 Release Manager plus 1 Maintainer; all required CI/hardware gates for the release target must pass. |
| Reference-hardware claims/baselines | 1 Hardware Validation Maintainer; benchmark methodology changes also require an appropriate Code/Architecture Reviewer. |

If one person currently holds all required bootstrap roles, that person may merge bootstrap work, but the PR must record that independent review was unavailable. This exception should disappear as maintainers are added.

## Documentation approval

Documentation is treated as an engineering artifact, not an informal side channel.

- Proposed documentation changes use pull requests.
- General documentation requires Documentation Approver review.
- `ARCHITECTURE.md` requires Architecture Approver review.
- `COMPATIBILITY.md` requires Compatibility Approver review.
- `SECURITY.md` requires Security Reviewer review.
- `ROADMAP.md` requires Maintainer approval and Project Owner approval for phase addition/removal or material scope changes.
- `GOVERNANCE.md`, `ROLE_ASSIGNMENTS.md`, `.github/CODEOWNERS`, and the governance taxonomy require Project Owner approval.
- Documentation that asserts measured hardware behavior must link or attach reproducible evidence and receive Hardware Validation review where applicable.

## Task assignment

- L2+ Task Managers may assign and reassign normal issues and roadmap work.
- L4+ Maintainers may override normal assignment to resolve blocking dependencies, abandoned work, or release-critical sequencing.
- Security-sensitive issues are assigned only by a Security Reviewer, Repository Administrator, or Project Owner.
- Governance/access-control work is assigned only by L6/L7 authority.
- Contributors may volunteer for work, but assignment is not final until accepted by an authorized Task Manager/Maintainer for critical or cross-cutting items.
- Assignment does not confer approval authority over the resulting PR.

## CODEOWNERS and repository rules

`.github/CODEOWNERS` is the machine-readable ownership layer. CODEOWNERS identifies who must be requested for review; this document defines what those reviews mean.

The target protection policy for `main` is:

- changes land through pull requests;
- required status checks must pass;
- required conversations must be resolved;
- CODEOWNER review is required for owned paths;
- stale approvals are dismissed after material changes;
- the most recent reviewable push must be approved by someone other than the pusher when practical;
- force-push and branch deletion are disabled;
- administrators should not routinely bypass protections.

Because different change classes need different domain approvals, CODEOWNERS/rulesets are a baseline enforcement mechanism; the governance approval matrix remains authoritative where GitHub cannot express the complete rule directly.

## Merge authority

A Maintainer may merge only after all required approvals and checks are satisfied. A domain approver who authored the PR does not satisfy the independent-review requirement where an independent reviewer is required.

Emergency bypasses require L6 or L7 authority and must be followed by a documented post-merge review issue explaining the reason, scope, risk, and remediation.

## Security and destructive actions

Only L6/L7 authority may change repository visibility, transfer/delete the repository, manage collaborator access, alter security settings/secrets, disable required protection controls, or perform equivalent destructive/sensitive actions.

## Conflict and escalation

Technical disagreements should first be resolved by the responsible domain approver. Cross-domain conflicts escalate to a Maintainer, then Repository Administrator for operational conflicts, and ultimately Project Owner for governance/project-direction decisions.

## Governance changes

Changes to this policy must be proposed by PR, labeled for governance/role review, and approved by the Project Owner. Material reductions in review, security, or access-control requirements must include explicit rationale in the PR.
