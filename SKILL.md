# E-commerce ROI Dashboard Project Skill

Use this guide when extending or maintaining this Streamlit e-commerce ROI dashboard.

## Project structure

- `app.py` defines Streamlit page navigation.
- `pages/` contains the branded Dashboard, E-commerce overview, Channel comparison, Campaign and business breakdowns, E-commerce trends, and Products & customer segments.
- `src/data_loader.py` loads and validates campaign CSVs, normalizes accepted input aliases, and derives row-level metrics.
- `src/business_data.py` validates the keyed product and customer-segment allocation files.
- `src/filters.py` provides shared date, source, platform, campaign, and business-dimension filters.
- `src/metrics.py` calculates dashboard totals and ratios.
- `src/charts.py` contains reusable Plotly chart builders, including daily trends, platform comparisons, and the dashboard's weekly revenue/profit view.
- `src/data_ui.py` provides shared CSV upload, data quality, full cleaned-data preview, and export controls.
- `tests/` contains automated checks for metric calculations and selected chart behavior.
- `data/campaign_data.csv` is the canonical campaign source. `scripts/build_campaign_data.py` fills and normalizes this file in place. `data/products.csv` and `data/customer_segments.csv` contain aggregate totals allocated across date/channel/campaign keys.
- `prompts/` contains the project system prompt and reusable feature, bug-fix, and review request templates.

## Data contract

Campaign data is intended to use one row per date, platform, and campaign. Non-identical repeated keys are retained and flagged for review; exact duplicate rows are removed. Expected columns:

| Column | Meaning |
| --- | --- |
| `date` | Reporting date parseable by pandas |
| `platform` | Advertising channel, such as Google Ads or Meta Ads |
| `campaign` | Campaign name |
| `spend` | Ad spend in the reporting currency |
| `impressions` | Ad impressions |
| `clicks` | Ad clicks |
| `orders` | Ecommerce orders attributed to the campaign |
| `revenue` | Ecommerce revenue attributed to the campaign, in the same currency as spend |
| `currency` | Optional ISO currency code; defaults to USD with a warning |
| `product`, `region`, `device` | Optional breakdown dimensions |
| `product_cost`, `refunds`, `discounts`, `shipping_cost` | Optional components for estimating contribution profit after ads |
| `cost_data_available` | Boolean metadata indicating product and shipping cost values are populated |
| `data_enrichment_status` | `Provided` or `Estimated`; identifies imputed values |

The loader supports legacy CSVs using `conversions` in place of `orders`; normalize that field to `orders` before calculations.

## Metric definitions

- **ROI:** `(revenue - spend) / spend`, formatted as a percentage.
- **ROAS:** `revenue / spend`, formatted as a multiple (for example, `2.5x`).
- **Average order value:** `revenue / orders`.
- **Cost per order:** `spend / orders`.
- **Click-to-order rate:** `orders / clicks`.
- **Contribution profit after ads:** `revenue - refunds - discounts - product_cost - shipping_cost - spend`; show only when product and shipping costs are complete.
- **Contribution margin after ads:** contribution profit after ads divided by `revenue - refunds - discounts`.

Calculate ratios from aggregated numerators and denominators for the selected rows. Do not average row-level ROI, ROAS, or rates. Show a ratio as unavailable when its denominator is zero. Use the single-currency filter before aggregating money. Contribution margin uses net revenue (`revenue - refunds - discounts`) as its denominator.

## Change guidance

- Put reusable data, filter, metric, and chart logic in `src/`; keep page files focused on layout and user interaction.
- Apply the same date, source, platform, campaign, product, region, device, and single-currency filters to campaign-grain results on every page. Apply date/platform/campaign filters to keyed product and customer-segment allocations; disclose that the key-level splits are modeled allocations.
- Keep chart inputs aligned with the selected metrics, and aggregate time-series values by date before plotting.
- Synchronize all shared filters, including product/region/device and currency; never aggregate monetary amounts across currencies.
- Maintain previous-period comparison, target pacing, campaign-opportunity, CSV quality, preview, and export behavior from `PRODUCT_SPEC.md`.
- Keep the README diagrams and sample-data reference values in sync with the implementation.
- Validate required CSV columns and give a clear message when the data is missing or invalid. Surface duplicate, invalid-date, and numeric coercion diagnostics and provide normalized preview/download.
- Keep README setup instructions, schema notes, and diagrams in sync with meaningful architecture or data contract changes.
- Keep dashboard highlights and funnel summaries grounded in available fields; do not infer sessions, cart, or checkout counts when they are absent.
- Keep the Dashboard's `Metric Month` multi-select scoped to dashboard calculations; shared sidebar date and dimension filters remain available across all pages.
- The `Preview cleaned data` control belongs in the sidebar, shows the complete normalized dataset in a scrollable table, and states the cleaned row count and date range. Do not limit it to the first rows, which can hide later months in date-sorted data.
- Keep the Dashboard layout aligned with the current design: dark title banner, light neutral background, six KPI cards with prior-period deltas, weekly revenue/profit chart with insight panel, efficiency metrics, channel performance, purchase funnel, budget pacing, campaign opportunities, daily trend, and filterable campaign-day table.
- Keep product and customer-segment allocation keys in their files and use the shared date/platform/campaign filters on those keyed rows. Preserve the synthetic-allocation disclosure.
- Use `Combined campaign data` as the source label in the canonical combined file. Preserve `data_enrichment_status` when regenerating it.
- Estimate unavailable cost and dimension values only in this synthetic demonstration dataset, and label those rows `Estimated`.
- Treat sample values as illustrative; do not describe them as actual store performance.
