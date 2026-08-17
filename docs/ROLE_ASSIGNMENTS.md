# openCUDA Role Assignments

This registry is the authoritative record of project governance roles defined in [`GOVERNANCE.md`](../GOVERNANCE.md). GitHub repository permission alone does not create project approval authority.

## Bootstrap assignments

Until additional maintainers are explicitly delegated, the repository owner is the bootstrap authority and fallback CODEOWNER.

| Principal | Administration level | Functional roles | Domain/scope | Status |
|---|---:|---|---|---|
| `@dlworrell` | **L7 — Project Owner** | Project Owner; Repository Administrator; Maintainer / Merge Steward; Task Manager / Triage Coordinator; Community Moderator; Code Reviewer; Architecture Approver; Compatibility Approver; Documentation Approver; Security Reviewer; Release Manager; CI/Build Maintainer; Hardware Validation Maintainer | Repository-wide bootstrap authority | Active / bootstrap |

This concentration of roles is a bootstrap condition, not the desired long-term separation of duties. As qualified maintainers are added, responsibilities should be delegated and independent-review requirements strengthened.

## Assignment rules

Each future assignment must record:

- GitHub user or organization team;
- administration level (`L0`–`L7`);
- one or more functional roles;
- domain/path scope where the role is limited;
- effective date;
- assigning authority;
- optional expiry/review date;
- active, suspended, expired, or revoked status.

A user may hold a functional role only when their GitHub access is sufficient to perform the associated action. For example, a binding pull-request approver must have the repository permission GitHub requires for approval under protected-branch rules.

## Delegation targets

These are the first roles that should be separated as the contributor base grows.

| Priority | Role | Minimum governance level | Recommended GitHub organization role | Reason to separate |
|---:|---|---:|---|---|
| 1 | Code Reviewer | L3 | Write | Independent implementation review. |
| 2 | Documentation Approver | L3 | Write | Independent technical-document review. |
| 3 | Community Moderator | L2 | Triage | Allows Discussion/content moderation without merge or repository-admin authority. |
| 4 | Task Manager / Triage Coordinator | L2 | Triage | Allows issue assignment/classification without code-write authority. |
| 5 | Hardware Validation Maintainer | L4 | Maintain or Write with scoped policy | Independent validation of DL380p/CUBIX/K80 measurements. |
| 6 | CI/Build Maintainer | L4 | Maintain | Maintains build/CI without full admin authority. |
| 7 | Architecture Approver | L5 | Maintain or Write plus explicit domain delegation | Protects ABI and component boundaries. |
| 8 | Compatibility Approver | L5 | Maintain or Write plus explicit domain delegation | Protects support/lowering/fallback truthfulness. |
| 9 | Security Reviewer | L5 | Maintain; security-management permissions as needed | Separates security approval from ordinary development. |
| 10 | Release Manager | L5 | Maintain | Separates release authority from general code contribution. |
| 11 | Repository Administrator | L6 | Admin | Limit destructive/sensitive controls to very few users. |

## Future organization-team mapping

If openCUDA is transferred to a GitHub organization, prefer teams such as:

- `@<org>/opencuda-maintainers`
- `@<org>/opencuda-code-reviewers`
- `@<org>/opencuda-architecture-approvers`
- `@<org>/opencuda-compatibility-approvers`
- `@<org>/opencuda-docs-approvers`
- `@<org>/opencuda-community-moderators`
- `@<org>/opencuda-security-reviewers`
- `@<org>/opencuda-release-managers`
- `@<org>/opencuda-ci-maintainers`
- `@<org>/opencuda-hardware-validators`
- `@<org>/opencuda-triage`

Those team names are design targets only until an organization and teams actually exist. Do not place nonexistent teams in CODEOWNERS.

## Change control

Role assignments must be committed through a pull request so the repository history records who changed authority and why. L5+ authority changes require Project Owner approval. L6/L7 changes require explicit Project Owner approval.
