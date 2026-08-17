# Content Moderation Operations

This document describes how openCUDA enforces `CODE_OF_CONDUCT.md` across GitHub collaboration surfaces.

## Scope

Automated moderation covers text in Discussions, Discussion comments, Issues, Issue/PR conversation comments, Pull Request titles/bodies, and Pull Request review comments. Repository CI separately scans ordinary committed text.

The scanner is deterministic and repository-owned. Its policy data is versioned in `config/content-policy.json`, so changes to moderation behavior are reviewed like source-code changes.

## Moderation roles

The preferred operational role is **Community Moderator** at L2 or higher. Repository Administrators and the Project Owner retain escalation authority. A moderator does not need source-code merge authority merely to review content, classify a report, request an edit, or coordinate a discussion.

Security-sensitive content, credential disclosure, or malicious links must additionally involve a Security Reviewer or Repository Administrator.

## Finding classes

- **block** — prohibited text/link content. Automation opens/updates a moderation task and posts a neutral source notice requesting an edit.
- **warn** — policy-sensitive content that should be corrected/reviewed but may not justify immediate restriction. Current policy can add warn rules without changing workflow design.
- **review** — human inspection required. Embedded images/video are currently routed this way because the local scanner does not inspect media pixels/audio.

The scanner records rule IDs and categories rather than repeating matched vocabulary.

## Review procedure

1. Open the moderation-review Issue created by automation or a submitted Moderation report.
2. Follow the source URL; do not reproduce prohibited content into the moderation Issue.
3. Determine whether the finding is a true violation, a good-faith false positive, or a security/platform incident.
4. For a correctable text issue, request that the author edit the source.
5. After a clean edit, the automated re-scan should close its tracking Issue. Manually close a human-filed report with a short disposition note.
6. For explicit media, harassment, threats, spam/malicious links, repeated evasion, or other high-severity conduct, use appropriate GitHub moderation controls and escalate under `GOVERNANCE.md`.
7. If the scanner produced a recurring false positive, propose a policy change through PR rather than relying on undocumented exceptions.

## Automation behavior

`content-moderation.yml` deliberately does not auto-delete posts. Automatic deletion would make false positives destructive and would remove the evidence needed for review. Instead it creates an auditable moderation task and, for blocking text findings, asks the author to edit.

The tracking Issue contains:

- source URL;
- actor;
- source object type;
- policy category and severity;
- rule IDs;
- SHA-256 hash of the scanned text.

The offending text itself is not copied.

## Embedded media limitation

Local CI can identify that Markdown/HTML embeds media but cannot determine what the pixels or audio contain. All embedded media therefore receives a non-accusatory manual-review signal.

A future media-classification integration must address privacy, retention, false-positive rate, service availability, security, and cost before becoming an automated enforcement dependency.

## Moderation policy changes

Changes to `config/content-policy.json`, `CODE_OF_CONDUCT.md`, this document, or `content-moderation.yml` require Community Moderator review and Documentation Approver review; changes that alter security handling or workflow token permissions also require Security Reviewer participation.

## Testing

The moderation system is tested without duplicating the policy vocabulary into test fixtures. Unit tests load the policy data and verify that every configured blocking term/rule produces the expected finding. Additional tests verify clean technical text, explicit-link rules, and embedded-media review behavior.

A manual `content-moderation` workflow dispatch runs the deterministic moderation self-test without requiring anyone to post prohibited content to a live Discussion.
