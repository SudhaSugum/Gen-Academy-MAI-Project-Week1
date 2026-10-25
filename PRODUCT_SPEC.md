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

The app accepts `conversions` as a legacy alias for `orders`. It loads `data/campaign_data.csv` when present, otherwise `sample_campaign_data.csv`, unless the user uploads a CSV. Missing product values default to `All products`; missing region/device values default to `Unknown`. Revenue and spend must use the same currency and scale.

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

- Provide an inclusive start and end date, platform, campaign, product, region, device, and single-currency selections.
- Default to the full available date range and all available platforms and campaigns.
- Apply the same selected values to every page and every result on that page.
- If filters select no rows, show a clear empty state instead of failing or displaying misleading zero metrics.
- Keep filter selections synchronized across pages and prevent aggregating multiple currencies together.

## Pages and acceptance criteria

### Dashboard

- Show spend, revenue, orders, ROAS, ROI, average order value, cost per order, and click-to-order rate.
- Recalculate all KPI values when any shared filter changes.
- Compare with the preceding equal-length date window, using the same non-date filters; show percentage change when a prior value is nonzero.
- Let the user set a period spend budget, revenue goal, target ROAS, and minimum spend threshold for campaign opportunity flags.
- Keep target inputs for the current Streamlit session; they are not saved between sessions.
- Show spend pacing against elapsed calendar days in the selected window and revenue goal progress.
- Flag campaigns above the spend threshold but below target ROAS, and lower-spend campaigns that meet the ROAS target.
- Offer a download of filtered rows and a preview/download of normalized data.
- Show a daily trend chart and a table of filtered campaign-day rows.

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

### Input handling

- Accept the required CSV fields described above and normalize column names and numeric/date values.
- Show a helpful message for missing required columns, a file with no valid dates, or a filtered result with no rows.
- Show a helpful message when the uploaded CSV is empty or cannot be parsed.
- Never show a misleading ROI/ROAS/rate of zero when its denominator is zero.
- Preview normalized input and offer a cleaned CSV download.
- Report exact duplicate rows removed, rows with invalid dates removed, numeric values defaulted to zero, and repeated date/platform/campaign keys found.
- Retain non-identical rows with repeated date/platform/campaign keys and flag them for review rather than silently dropping their values.
- Allow downloads of filtered rows, cleaned rows, channel summaries, business breakdowns, and opportunity lists. Plotly charts provide image export from the chart toolbar.

## Automated checks

Run `python -m unittest discover -s tests` to check the sample baseline values, zero-denominator handling, grouped ratio math, legacy schema support, prior-period windows, shared filtering, required-column validation, and selected time-series metrics.

## Sample data reference values

The current `sample_campaign_data.csv` contains 21 rows from 2026-09-01 through 2026-09-07. With no filters applied, the expected aggregate values are:

| Metric | Expected value |
| --- | ---: |
| Spend | 3,047.80 |
| Revenue | 32,319.00 |
| Orders | 1,226 |
| Clicks | 16,542 |
| ROAS | 10.6040x |
| ROI | 960.40% |
| Average order value | 26.3613 |
| Cost per order | 2.4860 |
| Click-to-order rate | 7.4114% |

These are arithmetic references for the synthetic CSV. Its currency metadata is USD.

## Business decisions to confirm

The sample is labeled USD, but actual source data units and business definitions still need confirmation before using the dashboard for operational reporting:

- Whether real data uses the correct currency and whether values are in major or minor units.
- Revenue attribution model and attribution window.
- Whether revenue is gross or net of discounts, refunds, taxes, and shipping.
- Reporting timezone and whether dates represent ad platform or store timezone.
- Whether ROI should mean return after ad spend only, or profit after product and operating costs.
- Whether the prototype contribution-profit formula should include other variable costs or a different tax treatment.

Until confirmed, treat displayed ROI as revenue minus advertising spend divided by advertising spend. Contribution profit is an estimate based on available product-cost, refund, discount, and shipping-cost columns; it excludes taxes and operating overhead.
