# Governance, Role, and Access Taxonomy

This document extends [`LABEL_TAXONOMY.md`](LABEL_TAXONOMY.md) with responsibility-routing and administration-level labels. These labels classify **what authority a work item requires**. They do not grant authority to a user; human assignments are recorded in [`ROLE_ASSIGNMENTS.md`](ROLE_ASSIGNMENTS.md) and governed by [`../GOVERNANCE.md`](../GOVERNANCE.md).

## Role family

Apply `role` plus the qualified role label when an issue/PR must be handled, reviewed, or approved by that functional role.

| Label | Required responsibility |
|---|---|
| `role:project-owner` | Project-policy, ownership, governance, or L5+ delegation decision requiring Project Owner authority. |
| `role:repository-admin` | Repository settings, access, rulesets, secrets, destructive/recovery, or other L6 administrative action. |
| `role:maintainer` | Merge stewardship, branch/repository workflow, ordinary project management, or maintain-level action. |
| `role:task-manager` | Issue triage, taxonomy, priority, assignment/reassignment, milestone, and queue management. |
| `role:community-moderator` | Code-of-Conduct/content review, Discussion moderation, moderation-task disposition, and community-safety escalation. |
| `role:code-reviewer` | Binding implementation review within an assigned code/component domain. |
| `role:architecture-approver` | ABI/component/process/topology/scheduler/memory/transport architecture approval. |
| `role:compatibility-approver` | CUDA-generation support, native/lowering/substitution/fallback/unsupported policy approval. |
| `role:documentation-approver` | Technical-document review for accuracy, consistency, terminology, and evidence. |
| `role:security-reviewer` | Security-sensitive code/configuration, legacy-driver containment, CI/secrets policy, or `SECURITY.md`. |
| `role:release-manager` | Versioning, release candidates, notes, artifacts, and publication. |
| `role:ci-build-maintainer` | CMake/toolchain/build reproducibility, GitHub Actions, self-hosted runners, and quality gates. |
| `role:hardware-validator` | DL380p/CUBIX/K80 topology, ECC/P2P/bandwidth evidence, hardware-in-the-loop validation, and reference baselines. |

A work item may need multiple role labels. For example, a stable ABI change should normally carry `role:code-reviewer` and `role:architecture-approver`.

## Access family

Apply `access` plus a qualified level when the issue/PR concerns granting, revoking, reviewing, or requiring a governance administration level. Do **not** use these labels as a substitute for `ROLE_ASSIGNMENTS.md`.

| Label | Governance level | Meaning |
|---|---|---|
| `access:l0-observer` | L0 | Read/view/discuss only; no project-management authority. |
| `access:l1-contributor` | L1 | Propose code/docs and submit PRs; no binding self-approval authority. |
| `access:l2-triage` | L2 | Classify and assign ordinary work; manage issue/PR queues without merge authority. |
| `access:l3-reviewer` | L3 | Binding review authority in explicitly assigned domains. |
| `access:l4-maintainer` | L4 | Merge approved work and manage normal repository workflow. |
| `access:l5-domain-approver` | L5 | Final delegated approval authority for a defined engineering/governance domain. |
| `access:l6-repository-admin` | L6 | Sensitive repository administration, access, rules, secrets, security settings, and recovery. |
| `access:l7-project-owner` | L7 | Final project-policy/ownership authority and high-level role delegation. |

## Label application rules

1. **Role labels route responsibility.** They tell contributors which authority must participate in the work item.
2. **Access labels classify privilege requirements.** They are used primarily for access-control/governance changes, not ordinary implementation work.
3. **Labels do not grant permissions.** A username gains project authority only through an active entry in `ROLE_ASSIGNMENTS.md` plus sufficient GitHub repository access.
4. **Use least privilege.** Do not mark an item L6/L7 when L2–L5 authority is sufficient.
5. **Approval roles are independent of implementation ownership.** Assignment to an issue does not make the assignee the required approver.
6. **Self-approval is not sufficient where governance requires independent review.**
7. **Keep role routing orthogonal to technical taxonomy.** A compatibility PR can simultaneously be `compatibility:kepler`, `roadmap:phase-5-compiler-lowering`, and `role:compatibility-approver`.

## Examples

A documentation-only update to `docs/DEVELOPMENT.md`:

`documentation`, `developmental`, `developmental:documentation`, `role`, `role:documentation-approver`.

A change to the public C ABI:

`architectural`, `architectural:stable-abi`, `developmental`, `developmental:c17`, `role`, `role:code-reviewer`, `role:architecture-approver`.

A change to `.github/workflows/` that modifies secrets/permissions:

`operational`, `operational:ci`, `operational:security`, `role`, `role:ci-build-maintainer`, `role:security-reviewer`; add `role:repository-admin` and `access:l6-repository-admin` only if repository-admin settings or secrets must actually be changed.

A moderation report or content-policy change:

`operational`, `discussion`, `role`, `role:community-moderator`; add `role:security-reviewer` when malicious links, credential exposure, or another security concern is involved.

A role grant for a new architecture approver:

`documentation`, `role`, `role:project-owner`, `role:architecture-approver`, `access`, `access:l5-domain-approver`.
