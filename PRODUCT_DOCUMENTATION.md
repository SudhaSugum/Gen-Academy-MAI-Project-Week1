# E-commerce ROI Dashboard

## Product overview

The E-commerce ROI Dashboard helps marketers and store operators compare paid advertising spend with attributed ecommerce orders and revenue. Use it to review overall performance, compare channels and campaigns, identify campaigns to investigate, and follow daily trends.

The included CSV contains synthetic example data for demonstration. Replace it with your own validated export before using the dashboard for business decisions.

## Getting started

Start the app from the project directory:

```bash
streamlit run app.py
```

The dashboard loads `data/campaign_data.csv` when that file exists. Otherwise, it loads `sample_campaign_data.csv`. You can upload a different CSV using the sidebar. Uploaded data applies for the current Streamlit session.

## Dashboard pages

### Dashboard

The main page summarizes spend, revenue, orders, ROAS, ROI after ad spend, average order value, cost per order, click-to-order rate, and contribution profit when cost data is complete. It also provides:

- A comparison with the immediately preceding date window of equal length.
- Spend budget pacing and revenue-goal progress for the selected period.
- A target ROAS indicator and campaign opportunity list.
- A daily trend chart and filtered campaign-day data table.
- CSV downloads for filtered rows and campaign opportunities.

### Overview

Shows the main store performance KPIs and a daily trend chart for the current shared filters.

### Channel comparison

Compare spend, revenue, orders, clicks, ROAS, or ROI by platform. The summary table also includes derived efficiency metrics and contribution profit when available. Download the channel summary as CSV.

### Campaign and business breakdowns

Group results by campaign, product, region, device, or platform and campaign. Choose a metric to sort by, inspect the aggregated results, and download them as CSV.

### E-commerce trends

Choose one or more metrics to chart by day. Available series are spend, revenue, orders, clicks, ROAS, and ROI. Counts and currency values are summed by day; ROAS and ROI are calculated from each day's totals.

## Shared filters

The sidebar filters apply across the pages:

- **Date range:** inclusive start and end dates.
- **Platforms and campaigns:** select one or more advertising sources and campaign names.
- **Products, regions, and devices:** optional business breakdown dimensions. If the uploaded data has no product column, rows appear under “All products”; missing region or device values appear as “Unknown.”
- **Currency:** select one currency at a time. The dashboard does not convert currencies.

Filters default to the full available date range and all values. If there are no matching rows, the page displays an empty-state message.

## Target controls and campaign opportunities

Target values are configured in the Dashboard sidebar and remain available for the current Streamlit session. They are not saved between sessions.

- **Period ad budget:** compare spend to budget and expected spend pace based on elapsed calendar days in the selected date range.
- **Period revenue goal:** see revenue-to-date progress toward the goal.
- **Target ROAS:** set the benchmark used by the dashboard indicator and campaign opportunity logic.
- **Opportunity minimum spend:** set the spend threshold that separates campaigns to review from scale candidates.

The opportunity list flags campaigns with spend at or above the threshold and ROAS below target as **Review: below target**. Campaigns below the spend threshold and at or above target ROAS are labeled **Scale candidate**. These are review cues, not automatic budget recommendations; consider attribution quality and business context before acting.

## Metrics

| Metric | Definition |
| --- | --- |
| Spend | Sum of advertising spend in the selected rows. |
| Revenue | Sum of attributed ecommerce revenue in the selected rows. |
| Orders | Sum of ecommerce orders. The legacy input column `conversions` is accepted as an alias. |
| ROAS | `revenue / spend`, displayed as a multiple (for example, `2.50x`). |
| ROI after ad spend | `(revenue - spend) / spend`, displayed as a percentage. This is revenue after advertising spend only; it is not accounting profit. |
| Average order value | `revenue / orders`. |
| Cost per order | `spend / orders`. |
| Click-to-order rate | `orders / clicks`. |
| Contribution profit after ads | `revenue - refunds - discounts - product_cost - shipping_cost - spend`. Shown only when product-cost and shipping-cost inputs are complete for all selected rows. |
| Contribution margin after ads | Contribution profit after ads divided by `revenue - refunds - discounts`. |

Ratios are calculated from aggregate totals, not from averages of row-level ratios. A zero denominator produces an unavailable value. Contribution profit excludes taxes and operating overhead; confirm the formula suits your business before relying on it.

## CSV format

One row should represent one date, platform, and campaign. Required columns:

| Column | Description |
| --- | --- |
| `date` | Reporting date, parseable by pandas. |
| `platform` | Advertising channel, such as Google Ads or Meta Ads. |
| `campaign` | Campaign name. |
| `spend` | Numeric ad spend. |
| `impressions` | Numeric impression count. |
| `clicks` | Numeric click count. |
| `orders` | Numeric ecommerce order count. |
| `revenue` | Numeric attributed ecommerce revenue. |

Optional columns:

| Column | Description |
| --- | --- |
| `currency` | ISO currency code for spend and revenue. Missing values default to USD and are called out. |
| `product` | Product or product group. |
| `region` | Store or customer region. |
| `device` | Device group. |
| `product_cost` | Product cost / cost of goods sold for the row. |
| `refunds` | Refunded revenue for the row; omitted values are treated as zero for contribution calculations. |
| `discounts` | Discount amount for the row; omitted values are treated as zero for contribution calculations. |
| `shipping_cost` | Shipping or fulfillment cost for the row. |

Keep monetary amounts in the same currency and scale for each currency code. Dates are treated as calendar dates; the CSV does not provide timezone or attribution-window information.

## Data quality and downloads

Expand **Data quality and export** in the sidebar to view import feedback and download normalized data. The dashboard:

- Removes exact duplicate rows and reports how many were removed.
- Drops rows with invalid dates and reports the count.
- Converts missing or nonnumeric required numeric values to zero and reports affected fields.
- Flags repeated date/platform/campaign keys that have different row values. Those rows are retained to avoid silently discarding data; review them before treating rows as unique.
- Defaults missing optional breakdown fields and missing currency values as described above.

The cleaned CSV contains normalized columns and derived row metrics. Other pages provide filtered-row, channel-summary, business-breakdown, and opportunity-list downloads. Plotly charts include an image export control in the chart toolbar.

## Limitations and reporting assumptions

- ROI and ROAS use the revenue attributed in the input file. The dashboard does not choose or verify an attribution model or window.
- No currency conversion is performed. Use the currency filter to keep each monetary summary to one currency.
- The app assumes `revenue` and `spend` share the same currency and scale.
- The contribution estimate subtracts refunds, discounts, product cost, shipping cost, and ad spend; taxes, payment fees, and other overhead are excluded.
- Missing `currency` values default to USD. Confirm this before loading real data.
- The dashboard is an analytics aid, not an accounting system or an automated campaign optimizer.

## Troubleshooting

- **Missing columns:** check the required CSV column names. `conversions` can replace `orders` for legacy files.
- **No valid dates:** ensure dates are valid and consistently formatted.
- **No results:** broaden the date range or select more platforms, campaigns, products, regions, or devices.
- **Contribution profit unavailable:** include complete `product_cost` and `shipping_cost` values for the selected rows.
- **Unexpected totals:** inspect the normalized data preview, quality warnings, currency selection, duplicate-key warnings, and revenue attribution in the source export.
