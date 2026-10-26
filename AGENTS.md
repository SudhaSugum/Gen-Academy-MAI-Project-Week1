# Agent instructions

Before changing this project, read `SKILL.md`, `PRODUCT_SPEC.md`, and the relevant files. Treat the product spec as the intended behavior and the current code as the implementation state; do not assume an acceptance criterion is already implemented.

## Architecture

- Keep Streamlit navigation in `app.py` and page UI in `pages/`.
- Put reusable data loading, validation, filtering, metric calculations, and charts in `src/`.
- Reuse the shared filter behavior on every page. Apply date/platform/campaign filters to keyed product and customer-segment allocations; label their key-level splits as modeled. Avoid copy-pasting calculation logic into page scripts.
- Keep README documentation, prompts, sample data, and the product spec aligned when changing the schema or metric behavior.

## Current dashboard design

- The product is branded **E-commerce ROI Dashboard**. Keep the multipage structure and neutral canvas with a dark Dashboard title banner.
- The Dashboard has a `Metric Month` multi-select that scopes its own metric panels inside the shared date range. Do not apply that selector to the other pages or the full cleaned-data preview.
- Keep CSV quality/export controls and the full cleaned-data preview in the sidebar. The preview must show all normalized rows in a scrollable table and include the row count and date range; a first-rows-only preview can hide later months.
- Preserve the Dashboard sections: six KPI cards with prior-period comparisons, weekly revenue/profit and insights, efficiency metrics, channel performance, purchase funnel, budget and target pacing, campaign opportunities, daily trend, and filterable campaign-day rows.

## Data and metric rules

- Use `orders` as the canonical ecommerce outcome field. Continue accepting legacy `conversions` only as an input alias where applicable.
- Accept prototype daily-ad aliases `channel`, `ad_spend_usd`, and `revenue_usd` as `platform`, `spend`, and `revenue`; infer USD from the explicitly named monetary columns.
- Preserve `source_dataset` in combined rows and keep the source filter synchronized with previous-period comparisons.
- In the synthetic combined dataset, fill missing region/device values from valid existing choices and estimate missing product/shipping costs from observed cost rates; mark imputed rows with `data_enrichment_status=Estimated`.
- Treat the date/channel/campaign splits in `products.csv` and `customer_segments.csv` as synthetic proportional allocations from aggregate totals. Apply matching date/platform/campaign filters and disclose that individual keyed values are modeled.
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
