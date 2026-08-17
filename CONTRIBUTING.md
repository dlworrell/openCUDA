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

Issues and pull requests use the repository taxonomy in [`docs/LABEL_TAXONOMY.md`](docs/LABEL_TAXONOMY.md).

- Keep GitHub type/community/state labels such as `bug`, `enhancement`, `documentation`, and `question` orthogonal to the project taxonomy.
- Apply the broad family label whenever a qualified family label is used; for example, pair `architectural` with `architectural:topology`.
- Planned implementation work should normally carry `roadmap` plus one current `roadmap:phase-*` label.
- Use compatibility labels to describe actual execution/support behavior, not merely incomplete work.
- Do not create one-off labels when an existing taxonomy term describes the work.
- Update the taxonomy when architecture, compatibility boundaries, supported hosts, or roadmap phases materially change.

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
