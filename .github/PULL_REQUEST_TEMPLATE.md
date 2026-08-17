## Summary

Describe the problem, approach, and observable result.

## Classification

Apply the repository taxonomy from `docs/LABEL_TAXONOMY.md`.

- [ ] Type label applied (`bug`, `enhancement`, `documentation`, etc.)
- [ ] Relevant family + qualified labels applied
- [ ] Roadmap phase applied when this is planned implementation work
- [ ] Required role/approval labels applied

## Change domains

Check all that apply.

- [ ] Portable C ABI/runtime
- [ ] C++ layer
- [ ] Python/front end
- [ ] Assembly/ISA-specific code
- [ ] Legacy CUDA/Kepler backend
- [ ] Build/CI/tooling
- [ ] Architecture
- [ ] Compatibility policy
- [ ] Documentation
- [ ] Security
- [ ] Release/governance
- [ ] Reference hardware/benchmarks

## Required approval routing

Consult `GOVERNANCE.md` and `.github/CODEOWNERS`.

- [ ] Code Reviewer requested where implementation changed
- [ ] Architecture Approver requested where ABI/component boundaries changed
- [ ] Compatibility Approver requested where support/lowering/fallback behavior changed
- [ ] Documentation Approver requested for proposed documentation
- [ ] Security Reviewer requested for security-sensitive changes
- [ ] Hardware Validation Maintainer requested for reference-platform claims/measurements
- [ ] Release Manager requested for release/version changes
- [ ] Project Owner requested for governance/access/role changes
- [ ] Author is not being counted as the sole binding approver

## Validation

- [ ] `cmake --preset dev`
- [ ] `cmake --build --preset dev`
- [ ] `ctest --preset dev`
- [ ] `python -m pytest`
- [ ] `python -m ruff check python scripts`
- [ ] `python -m mypy python/opencuda`
- [ ] Hardware-in-the-loop validation performed when required, or explicitly documented as unavailable/not applicable

## Documentation and compatibility

- [ ] Relevant engineering documentation is updated in the same PR
- [ ] New behavior is classified as native/lowerable/substitution/fallback/unsupported where applicable
- [ ] No unsupported hardware capability is presented as native
- [ ] New reference-platform claims include reproducible evidence or source attribution

## Risk / rollback

Describe security, compatibility, ABI, performance, or operational risk and how the change can be reverted.

## Approval exceptions

If required independent review is unavailable during bootstrap, record the exception and rationale here. Do not use this section to bypass required security/governance review without the authority defined in `GOVERNANCE.md`.
