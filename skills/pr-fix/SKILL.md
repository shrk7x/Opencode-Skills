---
name: pr-fix
description: Shortcut skill. Fix actionable PR comments, verify locally, then publish changes with git-ship.
---

# PR Fix

This is a shortcut wrapper for `pr-review-autopilot` in semi-auto mode followed by `git-ship`.

## Default behavior

- Mode: `semi-auto`
- Implements valid review comments
- Runs local verification
- After fixes and verification pass, continue with `git-ship`
- Do not ask a separate commit/push confirmation unless there is unusual risk or ambiguity

## How to use

Just say:

```text
Use pr-fix on this PR
```

Optional PR target:

```text
Use pr-fix on PR #38
```

If PR number is omitted, infer from current branch.

## Internal mapping

Equivalent to:

```text
Use pr-review-autopilot with MODE=semi-auto PR=<auto>, then use git-ship after local verification passes.
```
