# Contributing to openCUDA

openCUDA is pre-alpha compatibility research. Changes should prioritize correctness, reproducibility, and explicit capability boundaries over making unsupported operations appear to work.

## Pull requests

- Keep changes focused.
- Add or update tests for observable behavior.
- Update architecture/compatibility documentation when an ABI, backend, or support-policy decision changes.
- Do not commit proprietary NVIDIA libraries, drivers, SDK archives, firmware, or other redistributability-restricted artifacts.
- Do not introduce raw CUDA runtime pointers into the public ABI.
- Prefer deterministic CPU reference implementations for numerical correctness tests.

## Labels

Issues and pull requests use the repository taxonomy in [`docs/LABEL_TAXONOMY.md`](docs/LABEL_TAXONOMY.md) and the governance routing taxonomy in [`docs/GOVERNANCE_TAXONOMY.md`](docs/GOVERNANCE_TAXONOMY.md).

- Keep GitHub type/community/state labels such as `bug`, `enhancement`, `documentation`, and `question` orthogonal to the project taxonomy.
- Apply the broad family label whenever a qualified family label is used; for example, pair `architectural` with `architectural:topology`.
- Planned implementation work should normally carry `roadmap` plus one current `roadmap:phase-*` label.
- Use compatibility labels to describe actual execution/support behavior, not merely incomplete work.
- Use `role:*` labels to route required review/approval responsibility; labels do not themselves grant authority to a user.
- Use `access:*` labels only when a work item concerns governance privilege or an administration-level requirement.
- Do not create one-off labels when an existing taxonomy term describes the work.
- Update the taxonomy when architecture, compatibility boundaries, supported hosts, governance roles, or roadmap phases materially change.

## Governance and review

Project authority is defined by [`GOVERNANCE.md`](GOVERNANCE.md) and active assignments are recorded in [`docs/ROLE_ASSIGNMENTS.md`](docs/ROLE_ASSIGNMENTS.md).

- Assignment to an issue does not grant approval authority for the resulting pull request.
- Authors may not count their own review as the sole binding approval where independent review is required.
- Ordinary implementation changes require Code Reviewer approval before a Maintainer merges them.
- Stable ABI or architectural changes require Architecture Approver participation.
- Compatibility-policy or support-boundary changes require Compatibility Approver participation.
- Proposed technical documentation requires Documentation Approver review; architecture, compatibility, security, roadmap, and governance documents also require their domain-specific approver.
- Security-sensitive changes require Security Reviewer participation.
- Reference-platform measurements/claims require Hardware Validation review where applicable.
- Governance/access/role changes require Project Owner authority.
- Follow `.github/CODEOWNERS` review routing in addition to the governance approval matrix.

Task assignment is controlled by the governance level/role model: L2+ Task Managers may assign ordinary work; L4+ Maintainers may override ordinary assignment for project sequencing; security and governance/access work require the higher authorities defined in `GOVERNANCE.md`.

## Languages

- C17: stable ABI/runtime.
- C++20: convenience layer and internal abstractions.
- Python 3.10+: tooling/front ends.
- Assembly: narrowly scoped low-level primitives with portable fallbacks.
- CUDA C++: contained in legacy backend directories and built only through the legacy-toolchain option.

## Before submitting

```bash
cmake --preset dev
cmake --build --preset dev
ctest --preset dev
python -m pytest
python -m ruff check python scripts
python -m mypy python/opencuda
```
