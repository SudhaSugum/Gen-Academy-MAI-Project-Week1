# E-commerce ROI Dashboard

## Product overview

The E-commerce ROI Dashboard helps marketers and store operators compare paid advertising spend with attributed ecommerce orders and revenue. Use it to review overall performance, compare channels and campaigns, identify campaigns to investigate, and follow daily trends.

The included CSV contains synthetic example data for demonstration. Replace it with your own validated export before using the dashboard for business decisions.

## Getting started

Start the app from the project directory:

```bash
streamlit run app.py
```

The dashboard loads an uploaded campaign CSV for the current session, otherwise the combined `data/campaign_data.csv`. The builder normalizes and enriches the existing combined file in place. Missing region and device values are assigned valid existing categories. Missing product costs are estimated from the median product-cost-to-revenue rate in rows with supplied costs; shipping costs use the median shipping cost per order. These rows are marked `Estimated` in `data_enrichment_status`. The dashboard's data-quality panel counts these estimates. Review them before using contribution profit as an actual business result.

## Dashboard pages

### Dashboard

The **Metric Month** multi-select scopes Dashboard metrics to one or more months within the shared date range and defaults to all available months after the shared filters. This selector affects the Dashboard only; the other pages use the shared sidebar filters. When non-consecutive months are selected, prior-period comparisons are unavailable. The page uses a dark E-commerce ROI Dashboard title banner on a light neutral background, with six KPI cards for revenue, ad spend, contribution profit after ads, ROI, ROAS, and cost per order. Cards show changes against the previous equal-length window when a comparable value is available. A secondary row shows orders, average order value, click-to-order rate, and contribution margin after ads. It also provides:

- A weekly revenue-versus-contribution-profit chart. If product-cost or shipping-cost inputs are incomplete, the second series switches to ad spend and the chart says so.
- Data-derived highlights for the highest-revenue channel, highest-ROAS campaign, and click-to-order rate.
- A channel performance table and an ad-click-to-order summary. Sessions, add-to-cart, and checkout-start counts are not inferred because those fields are not present in the campaign CSV.
- A comparison with the immediately preceding date window of equal length.
- Spend budget pacing and revenue-goal progress for the selected period.
- A target ROAS indicator and campaign opportunity list.
- A daily trend chart and filtered campaign-day data table.
- Expand **Filter columns** above the campaign-day table to add per-column **Contains** or **Equals** criteria, then choose a value from that column's available values. Multiple active criteria are combined, and the CSV download matches the displayed rows.
- CSV downloads for filtered rows and campaign opportunities.

In the sidebar, **Data quality and export** contains import diagnostics and the cleaned CSV download. **Preview cleaned data** is a separate collapsed section; expand it to browse all normalized rows in a scrollable table. Its caption gives the full row count and earliest-to-latest date range, so months after the first rows are available there too. The preview uses the complete loaded file and is not restricted by the Dashboard's Metric Month selection.

### Overview

Shows the main store performance KPIs and a daily trend chart for the current shared filters.

### Channel comparison

Compare spend, revenue, orders, clicks, ROAS, or ROI by platform. The summary table also includes derived efficiency metrics and contribution profit when available. Download the channel summary as CSV.

### Campaign details

The **Campaign and business breakdowns** page groups results by campaign, product, region, device, or platform and campaign. Choose a metric to sort by, inspect the aggregated results, and download them as CSV.

### E-commerce trends

Choose one or more metrics to chart by day. Available series are spend, revenue, orders, clicks, ROAS, and ROI. Counts and currency values are summed by day; ROAS and ROI are calculated from each day's totals.

### Products & Customer Segments

The **Products & Customer Segments** page reads keyed rows from `data/products.csv` and `data/customer_segments.csv`. Both files include date, channel, and campaign keys, so the page applies the shared date, platform, and campaign filters before calculating the visible totals. Since the original data only contains aggregate values, the key-level splits are synthetic proportional allocations. Summing all keyed rows returns the original aggregate totals; individual date/channel/campaign values are modeled. Product/region/device filters continue to apply only to campaign data. Source-reported ROI is retained because its formula is not documented in the CSV.

The current sample allocations include August 2026 campaign keys as well as September and October keys. August product and segment values are modeled allocations of the same aggregate snapshots, not independently reported monthly totals.

Use the page's **Metric Month** multi-select to choose one or more months from the rows available under the shared filters. It defaults to all available months. The selected months filter both product and customer-segment rows before the page calculates their KPI totals, group summaries, and CSV downloads. Select at least one month to display these metrics.

## Shared filters

The keyed product and customer-segment allocations are generated against the campaign data cohort used for the supplied aggregate totals.

The sidebar filters apply to campaign results across the pages. The project dataset has one **Data sources** option, **Combined campaign data**. On Products & Customer Segments, date, platform, and campaign selections also filter the keyed summary rows. Product, region, and device selections do not apply to those separate tables.

- **Date range:** inclusive start and end dates.
- **Data sources:** identify the campaign dataset being viewed. The checked-in file currently has one combined dataset choice.
- **Platforms and campaigns:** select one or more advertising sources and campaign names.
- **Products, regions, and devices:** optional business breakdown dimensions. If the uploaded data has no product column, rows appear under “All products”; missing region or device values appear as “Unknown.”
- **Currency:** select one currency at a time. The dashboard does not convert currencies.

Filters default to the full available date range and all values. If no campaign rows match, campaign performance views display an empty-state message. The product and customer-segment page displays an empty state when no keyed summary rows match the selected date, platform, and campaign filters.

## Target controls and campaign opportunities

Target values are configured in the Dashboard sidebar and remain available for the current Streamlit session. They are not saved between sessions. The values drive the **Budget and target pacing** and **Campaign opportunities** sections and are scoped to the selected Metric Month months.

- **Period ad budget:** set the budget for the selected Metric Month months. Spend used is spend to date divided by budget. Expected pace is budget multiplied by elapsed selected calendar days divided by total selected calendar days.
- **Period revenue goal:** set the selected-month revenue target. Progress is revenue to date divided by the goal.
- **Target ROAS:** set the benchmark used by the dashboard indicator and campaign opportunity rules. ROAS is total revenue divided by total spend.
- **Opportunity minimum spend:** set the campaign spend threshold used to separate higher-spend reviews from lower-spend scale candidates.

In **Budget and target pacing**, spend used is spend to date divided by the period budget. Expected spend pace is the budget multiplied by elapsed selected calendar days divided by total selected calendar days. The spend delta compares actual spend with that expected pace. Revenue goal progress is revenue to date divided by the goal. Target ROAS shows actual ROAS to date minus the benchmark.

In **Campaign opportunities**, ROAS is each campaign's total revenue divided by its total spend. Campaigns with spend at or above the minimum and ROAS below target are **Review: below target**. Campaigns below the spend threshold and at or above target ROAS are **Scale candidate**. These are review cues, not automatic budget recommendations; consider attribution quality and business context before acting.

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
| `source_dataset` | Data source label; rows in the project dataset use `Combined campaign data`. |
| `cost_data_available` | Whether product and shipping cost values are populated. |
| `data_enrichment_status` | `Provided` or `Estimated`; identifies rows with imputed values. |

Keep monetary amounts in the same currency and scale for each currency code. Dates are treated as calendar dates; the CSV does not provide timezone or attribution-window information.

The loader accepts `channel`, `ad_spend_usd`, and `revenue_usd` aliases and maps them to the standard `platform`, `spend`, and `revenue` fields; USD is inferred from the explicitly named monetary columns. Product and customer-segment allocation rows retain `channel` and campaign keys for their supported filters.

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
