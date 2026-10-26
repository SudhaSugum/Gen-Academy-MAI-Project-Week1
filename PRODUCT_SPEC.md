# E-commerce ROI Dashboard: Product Specification

## Purpose

Help a store operator compare paid advertising cost with ecommerce orders and revenue, then identify which channels and campaigns perform best over a selected period.

The checked-in campaign data is synthetic and is for development and demonstration only. It is not actual store performance.

## Users and primary tasks

The primary user is a marketer or store operator who needs to:

1. See overall spend, revenue, orders, and return metrics for a selected period.
2. Compare results by advertising platform and campaign.
3. Inspect how selected metrics change over time.
4. Filter all views to the same date range, platforms, campaigns, product dimensions, and currency.

## Data contract

One CSV row represents the results for one date, platform, and campaign. Required fields:

| Field | Type / meaning |
| --- | --- |
| `date` | Date parseable by pandas |
| `platform` | Advertising channel name |
| `campaign` | Campaign name |
| `spend` | Numeric advertising cost |
| `impressions` | Numeric impression count |
| `clicks` | Numeric click count |
| `orders` | Numeric ecommerce order count |
| `revenue` | Numeric ecommerce revenue |
| `currency` | ISO currency code for monetary columns (optional; defaults to USD with a warning) |
| `product` | Product or product group (optional) |
| `region` | Sales region (optional) |
| `device` | Device group (optional) |
| `product_cost` | Cost of goods sold for the row (optional; needed for contribution profit) |
| `refunds` | Refunded revenue for the row (optional; assumed zero if omitted) |
| `discounts` | Discount amount for the row (optional; assumed zero if omitted) |
| `shipping_cost` | Fulfillment/shipping cost for the row (optional; needed for contribution profit) |
| `source_dataset` | Data source label; project rows use `Combined campaign data` |
| `cost_data_available` | Boolean indicating product and shipping cost values are populated |
| `data_enrichment_status` | `Provided` or `Estimated`; marks values inferred to replace unavailable dimensions or cost inputs |

The app accepts `conversions` as a legacy alias for `orders`, and normalizes `channel`, `ad_spend_usd`, and `revenue_usd` input aliases to `platform`, `spend`, and `revenue`. It loads an uploaded CSV first, then the canonical `data/campaign_data.csv`. The combined file uses `Combined campaign data` in `source_dataset`. The builder fills missing region/device categories from valid existing choices and estimates missing product and shipping costs using median cost rates from rows with supplied cost data. These rows are marked `Estimated` in `data_enrichment_status`; estimates are synthetic and should not be treated as verified business costs. Missing product values default to `All products`. USD is inferred from `_usd` monetary column names when loading a matching input directly. Revenue and spend must use the same currency and scale.

The product and customer-segment CSVs include `date`, `channel`, and `campaign` keys so date, platform, and campaign filters can slice the Products & customer segments page. Because the original values are aggregate totals, the row-level key allocations are synthetic and proportionally distributed across matching campaign rows; the full keyed tables reconcile to the aggregate totals. Product/region/device filters do not slice these summary tables. Source ROI and acquisition-cost values are retained as supplied when their formulas are not defined.

## Metric definitions

Calculate aggregate metrics from the filtered rows:

- **Spend:** sum of `spend`.
- **Revenue:** sum of `revenue`.
- **Orders:** sum of `orders`.
- **ROI:** `(revenue - spend) / spend`, displayed as a percentage.
- **ROAS:** `revenue / spend`, displayed as a multiplier such as `2.50x`.
- **Average order value:** `revenue / orders`.
- **Cost per order:** `spend / orders`.
- **Click-to-order rate:** `orders / clicks`.
- **Contribution profit after ads:** `revenue - refunds - discounts - product_cost - shipping_cost - spend`; show only when product cost and shipping cost are complete for selected rows.
- **Contribution margin after ads:** contribution profit after ads divided by net revenue (`revenue - refunds - discounts`).

For any ratio, aggregate its numerator and denominator for the selected rows before dividing. Do not average row-level or daily ratios to represent the full selection. If a denominator is zero, show the metric as unavailable. ROI is revenue after ad spend only; it does not account for product costs or other business expenses. Contribution profit is a separate estimate and excludes taxes and operating overhead.

## Shared filters

- Provide an inclusive start and end date, source dataset, platform, campaign, product, region, device, and single-currency selections.
- Default to the full available date range and all available sources, platforms, and campaigns.
- Apply the shared date, platform, and campaign filters to the keyed product and customer-segment tables. Product/region/device filters do not apply to those summaries.
- If filters select no campaign rows, show a clear empty state instead of failing or displaying misleading zero metrics.
- Keep filter selections synchronized across pages and prevent aggregating multiple currencies together.

## Pages and acceptance criteria

### Dashboard

- Use the E-commerce ROI Dashboard brand, a dark title banner, light neutral canvas, and compact six-card KPI layout.
- Provide a visible `Metric Month` multi-select that scopes dashboard metrics to the selected months within the shared date range. Default to all months available under the shared filters. This selector applies to the Dashboard; other pages use the shared sidebar filters.
- Show revenue, ad spend, contribution profit after ads, ROI, ROAS, and cost per order in six KPI cards; include previous-period changes when comparable values exist.
- Place a weekly revenue-versus-contribution-profit chart beside data-derived highlights. If cost inputs are incomplete, compare revenue with ad spend and label the fallback clearly.
- Show channel performance and an ad-click-to-order summary. Do not invent sessions, add-to-cart, or checkout counts when those fields are absent.
- Show spend, revenue, orders, ROAS, ROI, average order value, cost per order, and click-to-order rate.
- Recalculate all KPI values when any shared filter changes.
- Compare with the preceding equal-length date window, using the same non-date filters; show percentage change when a prior value is nonzero.
- Let the user set a period spend budget, revenue goal, target ROAS, and minimum spend threshold for campaign opportunity flags.
- Keep target inputs for the current Streamlit session; they are not saved between sessions.
- Show spend pacing against elapsed calendar days in the selected window and revenue goal progress.
- Flag campaigns above the spend threshold but below target ROAS, and lower-spend campaigns that meet the ROAS target.
- Offer a download of filtered rows and a preview/download of normalized data.
- Show a daily trend chart and a table of filtered campaign-day rows in addition to the weekly overview chart.
- Provide per-column `Contains` and `Equals` filters for the campaign-day table, and make its CSV download match the visible filtered rows.
- Keep the CSV import quality and export controls in the sidebar. The collapsed `Preview cleaned data` section must show every normalized row in a scrollable table and display the row count and earliest/latest valid dates, so later months are accessible even when source rows are date-sorted.

### Overview

- Show spend, revenue, orders, ROAS, ROI after ad spend, and contribution profit when cost data is complete.
- Show a daily trend chart using the shared filters.

### Channel comparison

- Compare spend, revenue, orders, clicks, ROAS, and ROI by platform.
- Include ROI, ROAS, and cost per order in the channel summary.
- Include contribution profit after ads and contribution margin when complete cost inputs are available.
- Changing the comparison metric updates the chart and preserves the shared filters. Ratio metrics are calculated from platform totals.
- Offer a channel summary download.

### Campaign details

- Show results grouped by platform and campaign.
- Include spend, impressions, clicks, orders, revenue, ROI, ROAS, average order value, cost per order, and click-to-order rate.
- Derive ratios from each campaign group's totals.
- Include contribution profit and margin where cost inputs are complete.
- Allow campaign, product, region, and device breakdowns; support sorting and CSV download.

### E-commerce trends

- Aggregate counts and monetary values by date after applying filters.
- Allow the user to select which metrics to chart.
- Display only the selected metrics; ratio series such as ROI and ROAS must be calculated from each day's totals.

### Products & customer segments

- Show product performance from `data/products.csv` and customer-segment performance from `data/customer_segments.csv`.
- Validate required columns and numeric fields, and show actionable messages when a summary file is missing or invalid.
- Apply shared date, platform, and campaign filters to the keyed rows and calculate visible totals from the selected rows.
- Explain that keyed breakdowns are synthetic proportional allocations of aggregate totals, not source-reported per-campaign results.
- Keep source-reported ROI distinct from dashboard-calculated ROI when the source does not define the ROI formula.

### Input handling

- Accept the required CSV fields described above and normalize column names and numeric/date values.
- Show a helpful message for missing required columns, a file with no valid dates, or a filtered result with no rows.
- Show a helpful message when the uploaded CSV is empty or cannot be parsed.
- Never show a misleading ROI/ROAS/rate of zero when its denominator is zero.
- Preview normalized input and offer a cleaned CSV download.
- The cleaned-data preview must represent the complete normalized file rather than only the first rows; include its date coverage for clarity.
- Report exact duplicate rows removed, rows with invalid dates removed, numeric values defaulted to zero, and repeated date/platform/campaign keys found.
- Retain non-identical rows with repeated date/platform/campaign keys and flag them for review rather than silently dropping their values.
- Allow downloads of filtered rows, cleaned rows, channel summaries, business breakdowns, and opportunity lists. Plotly charts provide image export from the chart toolbar.

## Automated checks

Run `python -m unittest discover -s tests` to check the combined dataset baseline values, zero-denominator handling, grouped ratio math, legacy schema support, prior-period windows, shared filtering, required-column validation, and selected time-series metrics.

## Sample data reference values

The default `data/campaign_data.csv` contains 516 synthetic rows across 2026-08-01 through 2026-10-31. Its expected aggregate reference values are:

| Metric | Expected value |
| --- | ---: |
| Spend | 70,893.19 |
| Revenue | 574,506.43 |
| Orders | 19,001 |
| Clicks | 283,316 |
| ROAS | 8.1038x |
| ROI | 710.38% |
| Average order value | 30.2356 |
| Cost per order | 3.7310 |
| Click-to-order rate | 6.7066% |

The project file uses one source label, `Combined campaign data`, in `source_dataset`.

## Business decisions to confirm

The sample is labeled USD, but actual source data units and business definitions still need confirmation before using the dashboard for operational reporting:

- Whether real data uses the correct currency and whether values are in major or minor units.
- Revenue attribution model and attribution window.
- Whether revenue is gross or net of discounts, refunds, taxes, and shipping.
- Reporting timezone and whether dates represent ad platform or store timezone.
- Whether ROI should mean return after ad spend only, or profit after product and operating costs.
- Whether the prototype contribution-profit formula should include other variable costs or a different tax treatment.

Until confirmed, treat displayed ROI as revenue minus advertising spend divided by advertising spend. Contribution profit is an estimate based on available product-cost, refund, discount, and shipping-cost columns; it excludes taxes and operating overhead.
