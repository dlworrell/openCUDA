# Contributing to openCUDA

openCUDA is pre-alpha compatibility research. Changes should prioritize correctness, reproducibility, and explicit capability boundaries over making unsupported operations appear to work.

## Pull requests

- Keep changes focused.
- Add or update tests for observable behavior.
- Update architecture/compatibility documentation when an ABI, backend, or support-policy decision changes.
- Do not commit proprietary NVIDIA libraries, drivers, SDK archives, firmware, or other redistributability-restricted artifacts.
- Do not introduce raw CUDA runtime pointers into the public ABI.
- Prefer deterministic CPU reference implementations for numerical correctness tests.
- Treat GitHub forms, workflows, moderation policy, routing tables, and governance files as tested engineering artifacts rather than informal configuration.

## Collaboration conduct and content

All repository collaboration is governed by [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) and the operational process in [`docs/CONTENT_MODERATION.md`](docs/CONTENT_MODERATION.md).

- Use professional language in Issues, Pull Requests, reviews, Discussions, comments, code comments, and documentation.
- Do not post pornographic/sexually explicit material, abusive language, harassment, threats, malicious links, credentials, or restricted/private material.
- Do not reproduce prohibited content inside a moderation report; link to the source and use the policy category/rule ID.
- Embedded media may be routed for manual moderation review because local CI does not inspect image/video pixels.
- Good-faith false positives are reviewable; do not attempt to evade or obfuscate the moderation filters.

## Issues and Discussions

Use [`docs/ISSUES_AND_DISCUSSIONS.md`](docs/ISSUES_AND_DISCUSSIONS.md) to choose the correct intake path.

- Start exploratory architecture, compatibility, research, proposal, roadmap, benchmark-analysis, hardware, help, question, and governance work in the matching Discussion category.
- Open an Issue when a defect is reproducible or work is scoped enough to have acceptance criteria and an assignee.
- Prefer GitHub's **Create issue from discussion** path when a Discussion becomes implementation-ready so its body and labels are retained.
- The issue chooser disables blank issues for normal contributors and provides specialized engineering forms plus links back to Discussions.
- Use the Moderation Report form for conduct/content concerns without copying the reported content.
- Creating or assigning an issue does not approve the work; the review and approval requirements below still apply.

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
- Community-content/moderation-policy changes require Community Moderator participation.
- CI/workflow policy changes require CI/Build Maintainer review and Security Reviewer participation when token permissions or trust boundaries change.
- Reference-platform measurements/claims require Hardware Validation review where applicable.
- Governance/access/role changes require Project Owner authority.
- Follow `.github/CODEOWNERS` review routing in addition to the governance approval matrix.

Task assignment is controlled by the governance level/role model: L2+ Task Managers may assign ordinary work; L2+ Community Moderators may own moderation-review work; L4+ Maintainers may override ordinary assignment for project sequencing; security and governance/access work require the higher authorities defined in `GOVERNANCE.md`.

## Languages

- C17: stable ABI/runtime.
- C++20: convenience layer and internal abstractions.
- Python 3.10+: tooling/front ends.
- Assembly: narrowly scoped low-level primitives with portable fallbacks.
- CUDA C++: contained in legacy backend directories and built only through the legacy-toolchain option.

## Before submitting

Install the development dependencies, then run the repository contract and portable tests described in [`docs/CI_TEST_SUITE.md`](docs/CI_TEST_SUITE.md):

```bash
python -m pip install -e '.[dev]'
python scripts/ci/repository_policy.py --root .
python scripts/ci/validate_github_config.py --root .
python scripts/ci/validate_workflows.py --root .
python scripts/ci/content_policy.py --scan-repository . --fail-on warn
python -m pytest
python -m ruff check python scripts
python -m mypy python/opencuda
cmake --preset dev
cmake --build --preset dev
ctest --preset dev
```

Low-level runtime changes should also be exercised with Clang static analysis and sanitizer jobs when available. Legacy CUDA/K80 behavior must be validated on the self-hosted Kepler workflow rather than inferred from portable CI.
