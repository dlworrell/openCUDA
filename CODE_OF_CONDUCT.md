# openCUDA Code of Conduct

openCUDA is a technical research and engineering project. Collaboration surfaces must remain usable for engineering review, debugging, research, documentation, and project governance.

## Expected conduct

Participants should:

- keep technical disagreement focused on claims, evidence, code, measurements, and design tradeoffs;
- use professional language suitable for a mixed workplace/academic engineering environment;
- provide reproducible evidence when making hardware, performance, compatibility, or security claims;
- respect review, moderation, security, and governance decisions while using the documented escalation process when disagreement remains;
- avoid posting private credentials, personal data, proprietary SDK material, or content that contributors are not authorized to redistribute.

## Prohibited collaboration content

The following is not permitted in Issues, Pull Requests, review comments, Discussions, Discussion comments, or repository source/documentation except inside the maintained moderation-policy data needed to implement and test the filter itself:

- profanity or deliberately abusive language;
- pornographic, sexually explicit, or otherwise X-rated text, links, images, video, or other media;
- targeted harassment, threats, intimidation, or degrading personal attacks;
- hateful or discriminatory slurs directed at protected classes or individuals;
- spam, malicious links, credential harvesting, or deliberately deceptive content;
- unauthorized disclosure of secrets, credentials, personal information, or restricted/proprietary material.

Necessary technical discussion of the moderation system should refer to policy rule IDs and categories rather than reproducing prohibited vocabulary.

## Automated moderation

openCUDA uses deterministic repository and collaboration-surface checks as an initial moderation layer. The automation may:

1. scan text when a Discussion, Discussion comment, Issue, Issue comment, Pull Request, or review comment is created or edited;
2. flag prohibited-language or explicit-adult-content matches;
3. route embedded images/video for human review because the local scanner does not inspect media pixels;
4. create a moderation-review Issue containing the source URL, actor, rule IDs, severity, and a content hash without copying the offending text;
5. post a neutral notice on content that triggered a blocking text rule.

Automated findings are moderation signals, not an irreversible judgment. The workflow does not automatically delete user content. A Community Moderator, Repository Administrator, or Project Owner reviews context and applies the appropriate GitHub moderation action.

## Enforcement

Depending on severity, repetition, and context, maintainers may request an edit, hide or delete content, lock a conversation, close an Issue/Discussion, restrict participation, revoke project roles/access, or escalate to GitHub/platform reporting. Security incidents follow `SECURITY.md` in addition to this policy.

Good-faith false positives should be corrected without penalty. Attempts to evade the moderation filters deliberately may be treated as a stronger policy violation.

## Appeals and escalation

Moderation decisions should first be reviewed by the assigned Community Moderator. Unresolved disputes escalate to a Maintainer or Repository Administrator and ultimately to the Project Owner under `GOVERNANCE.md`.

## Scope

This policy governs openCUDA project spaces. It does not attempt to regulate unrelated conduct outside the project except where off-platform activity creates a direct security, harassment, or participation risk for the repository.
