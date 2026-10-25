# E-commerce ROI Dashboard Project Skill

Use this guide when extending or maintaining this Streamlit e-commerce ROI dashboard.

## Project structure

- `app.py` defines Streamlit page navigation.
- `pages/` contains the dashboard, overview, channel comparison, campaign details, and trend views.
- `src/data_loader.py` loads and validates the CSV, normalizes fields, and derives row-level metrics.
- `src/filters.py` provides shared date, platform, and campaign filters.
- `src/metrics.py` calculates dashboard totals and ratios.
- `src/charts.py` contains reusable Plotly chart builders.
- `src/data_ui.py` provides shared CSV upload, data quality, preview, and export controls.
- `tests/` contains automated checks for metric calculations and selected chart behavior.
- `sample_campaign_data.csv` is the illustrative starter dataset. `data/campaign_data.csv` is the optional local working dataset.
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
- Apply the same date, platform, campaign, product, region, device, and single-currency filters to every page.
- Keep chart inputs aligned with the selected metrics, and aggregate time-series values by date before plotting.
- Synchronize all shared filters, including product/region/device and currency; never aggregate monetary amounts across currencies.
- Maintain previous-period comparison, target pacing, campaign-opportunity, CSV quality, preview, and export behavior from `PRODUCT_SPEC.md`.
- Keep the README diagrams and sample-data reference values in sync with the implementation.
- Validate required CSV columns and give a clear message when the data is missing or invalid. Surface duplicate, invalid-date, and numeric coercion diagnostics and provide normalized preview/download.
- Keep README setup instructions, schema notes, and diagrams in sync with meaningful architecture or data contract changes.
- Treat sample values as illustrative; do not describe them as actual store performance.
