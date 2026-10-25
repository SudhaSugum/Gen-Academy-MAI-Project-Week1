# Feature implementation prompt

Use with `system_prompt.md` and `SKILL.md`.

```text
Implement this feature in the E-commerce ROI Dashboard:

[Describe the feature and desired behavior]

Before editing, inspect the relevant page and shared helpers. Follow `PRODUCT_SPEC.md`, the project data contract, and metric definitions. Keep shared logic in src/ and page-specific UI in pages/. Preserve synchronized filters, one-currency aggregation, data-quality feedback, and exports. Update documentation or the sample CSV if the feature changes the schema or user-visible metric definitions.

At the end, summarize the files changed and explain how to use the feature. Run checks only if I ask you to run or verify them.
```
