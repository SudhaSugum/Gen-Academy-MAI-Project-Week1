# Feature implementation prompt

Use with `system_prompt.md` and `SKILL.md`.

```text
Implement this feature in the E-commerce ROI Dashboard:

[Describe the feature and desired behavior]

Before editing, inspect the relevant page and shared helpers. Follow `PRODUCT_SPEC.md`, the project data contract, and metric definitions. Keep shared logic in src/ and page-specific UI in pages/. Preserve synchronized date/source/dimension filters, one-currency aggregation, data-quality feedback, and exports. Keep `source_dataset` provenance intact; regenerate combined campaign data with `scripts/build_campaign_data.py` if a source changes. Update documentation or source data if the feature changes the schema or user-visible metric definitions.

Preserve the current Dashboard visual hierarchy and page behavior: `Metric Month` scopes only Dashboard metrics, and the sidebar cleaned-data preview shows all normalized rows with date coverage.

At the end, summarize the files changed and explain how to use the feature. Run checks only if I ask you to run or verify them.
```
