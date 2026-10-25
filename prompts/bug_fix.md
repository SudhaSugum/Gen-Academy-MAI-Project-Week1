# Bug fix prompt

Use with `system_prompt.md` and `SKILL.md`.

```text
Investigate and fix this dashboard issue:

[Describe the observed behavior, expected behavior, and steps to reproduce]

Trace the behavior through the relevant page and shared src/ helpers before editing. Make the smallest complete fix, preserve the CSV contract and synchronized filters, and check related views for the same issue. If the fix affects metrics or transformations, update or add a unittest in tests/. Explain the cause, files changed, and any verification performed. Do not claim checks were run unless you ran them.
```
