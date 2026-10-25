# Agent instructions

Before changing this project, read `SKILL.md`, `PRODUCT_SPEC.md`, and the relevant files. Treat the product spec as the intended behavior and the current code as the implementation state; do not assume an acceptance criterion is already implemented.

## Architecture

- Keep Streamlit navigation in `app.py` and page UI in `pages/`.
- Put reusable data loading, validation, filtering, metric calculations, and charts in `src/`.
- Reuse the shared filter behavior on every page. Avoid copy-pasting calculation logic into page scripts.
- Keep README documentation, prompts, sample data, and the product spec aligned when changing the schema or metric behavior.

## Data and metric rules

- Use `orders` as the canonical ecommerce outcome field. Continue accepting legacy `conversions` only as an input alias where applicable.
- Calculate ratios from aggregated totals for the selected rows; do not average row-level ratios.
- ROI = `(revenue - spend) / spend`; ROAS = `revenue / spend`; average order value = `revenue / orders`; cost per order = `spend / orders`; click-to-order rate = `orders / clicks`.
- Contribution profit after ads = `revenue - refunds - discounts - product_cost - shipping_cost - spend`; show only when product-cost and shipping-cost data are complete for the selected rows. Exclude taxes and label the estimate clearly.
- Return an unavailable value for ratios with a zero denominator. Never silently substitute zero for an undefined ratio.
- Filter to one currency before aggregating monetary fields. Do not invent attribution or tax rules; consult `PRODUCT_SPEC.md` and call out unresolved decisions.

## Implementation expectations

- Make focused changes that satisfy the acceptance criteria in `PRODUCT_SPEC.md`.
- Validate CSV structure and show actionable messages for missing columns, invalid dates, and empty filtered results.
- Preserve the data quality report: remove exact duplicates, flag repeated date/platform/campaign keys, report invalid dates and numeric coercions, and keep preview/download data aligned with normalized rows.
- Keep product/region/device breakdowns, currency selection, previous-period comparisons, targets, pacing, and opportunity flags consistent across relevant pages.
- Ensure charts use the metric selection the user made and aggregate time series at the documented date grain.
- Do not claim tests, app runs, or other checks that were not actually performed. Follow the user's request about whether to run checks.
