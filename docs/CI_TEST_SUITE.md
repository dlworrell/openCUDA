# openCUDA CI, Compliance, and Moderation Test Suite

This document defines the repository verification system. The goal is not only to compile the code: CI must continuously verify the assumptions recorded in the architecture, compatibility, governance, issue/discussion routing, and community-content policies.

## Test layers

openCUDA uses five complementary layers.

| Layer | Workflow/tool | Purpose |
|---|---|---|
| Portable build/test | `portable-ci` | Compile and test the portable C17/C++20/assembly/Python implementation on supported development platforms. |
| Source/repository compliance | `compliance-ci` | Enforce repository hygiene, source-policy, ABI, formatting, static-analysis, sanitizer, GitHub-form, workflow-security, and content-policy checks. |
| Collaboration moderation | `content-moderation` | Scan new/edited Discussions, comments, Issues, PR descriptions, and review comments and route violations for human review. |
| Live repository audit | `repository-audit` | Compare live GitHub settings, labels, categories, and protected-branch state with the repository policy. |
| Legacy hardware validation | `kepler-hardware-ci` | Validate CUDA 11.x / `sm_37` behavior on the self-hosted Kepler reference runner. |

These layers are intentionally separate. A source-code failure must not be hidden by a green repository-settings audit, and a community-content violation is not a compiler failure.

## Portable build/test matrix

`portable-ci` validates:

- Linux x86-64 using the default GNU toolchain;
- Linux x86-64 using Clang;
- Linux AArch64 as a cross-compile, including the AArch64 assembly path;
- macOS arm64 on Apple Silicon;
- macOS x86-64 on the GitHub Intel runner while that runner remains supported;
- Windows x86-64 using MSVC/MASM;
- Python 3.10 through 3.14.

Every native C/C++ build enables `OPENCUDA_WARNINGS_AS_ERRORS=ON`. The legacy CUDA backend remains isolated from portable CI and is tested by the Kepler self-hosted workflow.

## Source and repository compliance

`scripts/ci/repository_policy.py` enforces the versioned policy in `config/repository-policy.json`.

Current blocking checks include:

- UTF-8 text and LF line endings;
- final newline and trailing-whitespace hygiene;
- suspicious Unicode control/format characters;
- repository file-size limit;
- committed compiled/archive/generated artifacts;
- high-signal private-key/token/access-key patterns;
- prohibited high-risk C string APIs;
- reviewed-exception requirement for discouraged bounded legacy string APIs;
- no raw CUDA runtime/Driver API types leaking into the public `include/opencuda/` ABI.

The public ABI check implements the project rule that CUDA implementation pointers/types remain behind openCUDA-owned handles and abstractions.

## Formatting, static analysis, and runtime safety

`compliance-ci` additionally runs:

- `clang-format --dry-run --Werror` over C, C++, headers, and CUDA source;
- ShellCheck over shell tooling;
- strict Clang builds with compiler warnings promoted to errors;
- `clang-tidy` with analyzer, bug-prone, performance, and portability findings promoted to errors;
- AddressSanitizer and UndefinedBehaviorSanitizer native tests;
- Ruff, mypy, pytest, and repository governance/moderation unit tests.

The sanitizer job is Linux-hosted because it is intended to catch memory/undefined behavior independently of the ordinary cross-platform matrix.

## GitHub configuration contract tests

`scripts/ci/validate_github_config.py` treats repository workflow metadata as tested engineering artifacts.

It verifies:

- blank Issues are disabled;
- the Issue chooser has Discussion/security routing links;
- every Issue form has a valid body structure and unique control IDs;
- every Discussion category form matches the slug contract in `config/discussion-categories.json`;
- Polls remain form-less;
- the Issue-routing table is structurally valid and only references documented taxonomy/governance labels;
- all required workflow files exist and parse.

`config/discussion-categories.json` is the machine-readable source of truth for the expected Discussion category inventory. `config/issue-routing.json` is the machine-readable source of truth for form-selection-to-label routing.

## GitHub Actions security policy

`scripts/ci/validate_workflows.py` statically checks every workflow.

The baseline policy requires:

- explicit top-level `permissions`;
- no `permissions: write-all`;
- no `pull_request_target` workflows;
- external Actions only from the repository allowlist and with an explicit version tag or full commit SHA;
- no pipe-to-shell downloads;
- no direct interpolation of untrusted Issue/Discussion/PR text into generated shell commands.

Untrusted collaboration text is read from GitHub's event JSON file by Python rather than injected into shell source.

## Repository content scan

`scripts/ci/content_policy.py` uses `config/content-policy.json` for deterministic text screening.

Repository CI rejects prohibited collaboration language from ordinary source, comments, documentation, workflow text, and project metadata. The policy-data file and its unit test are excluded from the repository scan because the detector must contain its own vocabulary.

The scanner stores/report rule IDs, categories, paths, and line numbers. It does not need to echo the triggering vocabulary in normal CI output.

## Runtime collaboration moderation

`content-moderation` runs when supported GitHub events create or edit:

- a Discussion;
- a Discussion comment;
- an Issue;
- an Issue/PR conversation comment;
- a Pull Request title/body;
- a Pull Request review comment.

The workflow passes the GitHub event JSON path directly to `scripts/ci/moderate_event.py`. User text is never interpolated into shell source.

### Blocking text findings

When a blocking text rule matches, automation:

1. computes a SHA-256 hash of the complete source text;
2. opens or updates one moderation-review Issue for the source object;
3. records the source URL, actor, category, severity, rule IDs, and hash without reproducing the offending content;
4. posts a neutral edit/request notice on the source conversation;
5. leaves deletion/hiding/locking/access action to an authorized human moderator.

If the author edits the same source object and the re-scan is clean, the associated moderation-review Issue is closed automatically.

### Embedded media

The local scanner cannot inspect the pixels/audio of arbitrary images or video. Embedded media therefore produces a `review` finding and a moderator-review task, but not an automatic accusation or deletion. This ensures that explicit media cannot bypass the process while avoiding a blanket ban on legitimate benchmark plots, topology screenshots, or hardware photographs.

A future external media-classification service may replace the manual media-review step only after a separate privacy/security/accuracy review.

## Moderation false-positive policy

The scanner is deterministic and intentionally conservative. A rule match creates a review obligation; it does not establish intent. Good-faith false positives are closed after contextual review or clean edit. The project should tune the policy when repeated false positives occur rather than training contributors to evade the scanner.

## Live repository audit

`repository-audit` is both scheduled and manually invokable.

It checks live GitHub state that cannot be proven from repository files alone:

- Issues enabled;
- Discussions enabled;
- default branch protection enabled;
- required taxonomy/routing labels present;
- expected Discussion category slugs/names present;
- Q&A categories are answerable;
- required governance/CI files exist on the default branch.

Scheduled audits report drift as warnings. A manual run with `strict=true` fails on drift and is the acceptance test used when completing repository-administration work such as Issues #4 and #6.

## Discussion bootstrap and Issue routing integration

`bootstrap-discussions` reads `config/discussion-categories.json`, verifies the live category inventory, verifies Q&A semantics, and creates the documented seed/index discussions idempotently.

`issue-routing` reads `config/issue-routing.json` and applies the project taxonomy after structured Issue forms render their selected values into the Issue body.

Both configurations are unit-tested before they reach `main`.

## Kepler hardware validation

`kepler-hardware-ci` remains manually triggered until the reference DL380p runner is enrolled with the required self-hosted labels. It is the authoritative place for tests that actually require CUDA 11.x, R470, `sm_37`, Tesla K80, CUBIX, NUMA, P2P, ECC, or reference-node measurements.

Portable CI must never claim to validate those properties without the hardware.

## Required status-check target

Once Issue #4 branch/ruleset enforcement is completed, the following should be required on pull requests where available:

- all `portable-ci` native matrix jobs;
- Linux Clang and Linux AArch64 compile coverage;
- the supported Python-version matrix;
- `repository-policy`;
- `formatting-static-analysis`;
- `sanitizers-linux`.

The self-hosted Kepler job should be required only for changes whose taxonomy/path/risk requires actual legacy-hardware validation, otherwise loss of the lab runner would deadlock unrelated portable development.

## Local preflight

Contributors should run at least:

```bash
python -m pip install -e '.[dev]'
python scripts/ci/repository_policy.py --root .
python scripts/ci/validate_github_config.py --root .
python scripts/ci/validate_workflows.py --root .
python scripts/ci/content_policy.py --scan-repository . --fail-on warn
python -m ruff check python scripts
python -m mypy python/opencuda
python -m pytest
cmake --preset dev
cmake --build --preset dev
ctest --preset dev
```

On Linux with Clang available, also run `clang-format`, `clang-tidy`, and the sanitizer configuration before proposing low-level runtime changes.
