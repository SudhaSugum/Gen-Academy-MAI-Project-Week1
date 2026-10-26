from datetime import date
from html import escape

import streamlit as st
import pandas as pd

from src.charts import trend_chart, weekly_revenue_profit_chart
from src.data_ui import current_currency, get_dashboard_data, target_inputs
from src.metrics import (
    campaign_opportunities,
    compare_with_previous_period,
    format_money,
    grouped_metrics,
    percent_change,
    summarize,
)
from src.table_filters import apply_column_filters, available_column_values


def metric_card(label, value, delta, tone="neutral"):
    safe_label = escape(str(label))
    safe_value = escape(str(value))
    safe_delta = escape(str(delta))
    st.markdown(
        f"""
        <div class="roi-dashboard-kpi">
          <div class="roi-dashboard-kpi-label">{safe_label}</div>
          <div class="roi-dashboard-kpi-value">{safe_value}</div>
          <div class="roi-dashboard-kpi-delta {tone}">{safe_delta}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def styled_table(frame):
    headers = "".join(f"<th>{escape(str(column))}</th>" for column in frame.columns)
    body = "".join(
        "<tr>" + "".join(f"<td>{escape(str(value))}</td>" for value in row) + "</tr>"
        for row in frame.itertuples(index=False, name=None)
    )
    st.markdown(
        f"<table class='roi-dashboard-table'><thead><tr>{headers}</tr></thead><tbody>{body}</tbody></table>",
        unsafe_allow_html=True,
    )


def comparison_delta(key, current, previous):
    current_value, previous_value = current.get(key), previous.get(key)
    if current_value is None or previous_value in (None, 0):
        return "No comparable prior value", "neutral"
    if key == "roi":
        change = current_value - previous_value
        text = f"{change * 100:+.1f} pts vs previous period"
    elif key == "roas":
        change = current_value - previous_value
        text = f"{change:+.2f}x vs previous period"
    else:
        change = percent_change(current_value, previous_value)
        text = f"{change:+.1%} vs previous period"

    favorable = change > 0
    if key in ("spend", "cost_per_order"):
        favorable = change < 0
    if change == 0:
        tone = "neutral"
    else:
        tone = "positive" if favorable else "negative"
    return text, tone


st.markdown(
    """
    <style>
    .roi-dashboard-banner {
      background: #111827; color: #fff; padding: 16px 22px; margin: 0 0 12px;
      font-size: 1.55rem; font-weight: 700; letter-spacing: -.02em;
    }
    .roi-dashboard-meta { color: #687386; margin: 0 0 14px 4px; font-size: .92rem; }
    .roi-dashboard-kpi {
      background: #fff; border: 1px solid #e1e5ea; border-radius: 4px;
      padding: 14px 17px; min-height: 105px; margin: 0 0 12px;
      box-shadow: 0 1px 2px rgba(17,24,39,.04);
    }
    .roi-dashboard-kpi-label { color: #687386; font-size: .86rem; margin-bottom: 6px; }
    .roi-dashboard-kpi-value { color: #111827; font-size: 1.55rem; font-weight: 700; line-height: 1.2; }
    .roi-dashboard-kpi-delta { font-size: .84rem; font-weight: 650; margin-top: 8px; }
    .roi-dashboard-kpi-delta.positive { color: #16803c; }
    .roi-dashboard-kpi-delta.negative { color: #dc2626; }
    .roi-dashboard-kpi-delta.neutral { color: #687386; }
    .roi-dashboard-table { border-collapse: collapse; width: 100%; background: #fff; margin: 0 0 1rem; }
    .roi-dashboard-table th { background: #111827; color: #fff; text-align: left; padding: 9px 10px; }
    .roi-dashboard-table td { border-bottom: 1px solid #e7eaf0; padding: 8px 10px; color: #111827; }
    .roi-dashboard-table tbody tr:nth-child(even) { background: #f8fafc; }
    </style>
    <div class="roi-dashboard-banner">E-commerce ROI Dashboard</div>
    """,
    unsafe_allow_html=True,
)

raw, df = get_dashboard_data()
if df.empty:
    st.info("No rows match the shared filters.")
    st.stop()

currency = current_currency(df)
selections = st.session_state["campaign_filter_selection"]

available_months = sorted(df["date"].dt.to_period("M").unique())
month_labels = {period: period.strftime("%b %Y") for period in available_months}
selected_months = st.multiselect(
    "Metric Month",
    available_months,
    default=available_months,
    format_func=lambda period: month_labels[period],
    key="dashboard_metrics_months",
    label_visibility="visible",
)
if not selected_months:
    st.info("Select at least one month to show dashboard metrics.")
    st.stop()

selected_months = sorted(selected_months)
month_numbers = [period.year * 12 + period.month for period in selected_months]
month_start = max(selected_months[0].start_time.date(), selections["start"])
month_end = min(selected_months[-1].end_time.date(), selections["end"])
month_df = df[df["date"].dt.to_period("M").isin(selected_months)]
month_selections = {**selections, "start": month_start, "end": month_end}
current = summarize(month_df)
if month_numbers[-1] - month_numbers[0] + 1 == len(month_numbers):
    current, previous, previous_dates = compare_with_previous_period(raw, month_df, month_selections)
else:
    previous = {key: None for key in current}
    previous_dates = None
df = month_df
selected_month_labels = ", ".join(month_labels[period] for period in selected_months)
st.caption(f"Dashboard metrics below show: {selected_month_labels}.")
metric_specs = [
    ("Revenue", "revenue", lambda value: format_money(value, currency)),
    ("Ad spend", "spend", lambda value: format_money(value, currency)),
    ("Contribution profit after ads", "contribution_profit_after_ads", lambda value: format_money(value, currency)),
    ("ROI after ad spend", "roi", lambda value: f"{value:.1%}" if value is not None else "Unavailable"),
    ("ROAS", "roas", lambda value: f"{value:.2f}x" if value is not None else "Unavailable"),
    ("Cost per order", "cost_per_order", lambda value: format_money(value, currency)),
]
first_row, second_row = st.columns(3), st.columns(3)
for index, (label, key, formatter) in enumerate(metric_specs):
    row = first_row if index < 3 else second_row
    delta, tone = comparison_delta(key, current, previous)
    with row[index % 3]:
        metric_card(label, formatter(current.get(key)), delta, tone)
if previous_dates:
    st.caption(f"Card changes compare with the previous equal-length period: {previous_dates[0]} to {previous_dates[1]} using the same non-date filters.")
else:
    st.caption("Card changes are unavailable for non-consecutive selected months.")

chart_col, insights_col = st.columns([1, 1], gap="medium")
with chart_col:
    st.subheader("Revenue vs. Profit · Weekly")
    weekly_chart, profit_available = weekly_revenue_profit_chart(df, currency)
    st.plotly_chart(weekly_chart, use_container_width=True, config={"displaylogo": False})
    if profit_available:
        st.caption("Contribution profit is an estimate after refunds, discounts, product cost, shipping cost, and ad spend; taxes are excluded.")
    else:
        st.caption("Product-cost and shipping-cost data is incomplete, so this chart compares revenue with ad spend.")

with insights_col:
    st.subheader("Insights")
    channel_summary = grouped_metrics(df, ["platform"])
    top_revenue = channel_summary.sort_values("revenue", ascending=False).iloc[0]
    st.markdown("**Highest revenue channel**")
    st.write(
        f"{top_revenue['platform']} generated {format_money(top_revenue['revenue'], currency)} "
        f"at {top_revenue['roas']:.2f}x ROAS."
        if pd.notna(top_revenue["roas"])
        else f"{top_revenue['platform']} generated {format_money(top_revenue['revenue'], currency)}."
    )
    campaign_summary = grouped_metrics(df, ["platform", "campaign"])
    campaigns_with_spend = campaign_summary[campaign_summary["roas"].notna()]
    if not campaigns_with_spend.empty:
        top_campaign = campaigns_with_spend.sort_values("roas", ascending=False).iloc[0]
        st.markdown("**Highest ROAS campaign**")
        st.write(f"{top_campaign['campaign']} · {top_campaign['platform']} · {top_campaign['roas']:.2f}x ROAS")
    st.markdown("**Click-to-order rate**")
    overall = summarize(df)
    rate = f"{overall['conversion_rate']:.1%}" if overall["conversion_rate"] is not None else "Unavailable"
    st.write(f"{rate} across the selected rows. This uses ad clicks and attributed orders from the input data.")

st.caption("Additional efficiency metrics")
extra = st.columns(4)
extra[0].metric("Orders", f"{overall['orders']:,.0f}")
extra[1].metric("Average order value", format_money(overall["average_order_value"], currency))
extra[2].metric("Click-to-order rate", rate)
extra[3].metric(
    "Contribution margin after ads",
    f"{overall['contribution_margin_after_ads']:.1%}" if overall["contribution_margin_after_ads"] is not None else "Unavailable",
)

st.subheader("Channel Performance")
channel_table = channel_summary[["platform", "spend", "revenue", "orders", "roas", "roi", "cost_per_order"]].copy()
channel_table["spend"] = channel_table["spend"].map(lambda value: format_money(value, currency))
channel_table["revenue"] = channel_table["revenue"].map(lambda value: format_money(value, currency))
channel_table["orders"] = channel_table["orders"].map(lambda value: f"{value:,.0f}")
channel_table["roas"] = channel_table["roas"].map(lambda value: f"{value:.2f}x" if pd.notna(value) else "Unavailable")
channel_table["roi"] = channel_table["roi"].map(lambda value: f"{value:.1%}" if pd.notna(value) else "Unavailable")
channel_table["cost_per_order"] = channel_table["cost_per_order"].map(lambda value: format_money(value, currency) if pd.notna(value) else "Unavailable")
if channel_summary["contribution_profit_after_ads"].notna().all():
    channel_table["contribution_profit_after_ads"] = channel_summary["contribution_profit_after_ads"].map(lambda value: format_money(value, currency))
channel_table = channel_table.rename(columns={
    "platform": "Channel", "spend": "Ad spend", "revenue": "Revenue", "orders": "Orders",
    "roas": "ROAS", "roi": "ROI", "cost_per_order": "Cost / order",
    "contribution_profit_after_ads": "Contribution profit after ads",
})
styled_table(channel_table)
st.download_button(
    "Download channel summary", channel_table.to_csv(index=False).encode("utf-8"),
    "channel_summary.csv", "text/csv",
)

st.subheader("Purchase Funnel")
funnel = pd.DataFrame([
    {"Stage": "Ad clicks", "Count": f"{overall['clicks']:,.0f}", "Rate": "—"},
    {
        "Stage": "Orders", "Count": f"{overall['orders']:,.0f}",
        "Rate": f"{overall['conversion_rate']:.1%} of ad clicks" if overall["conversion_rate"] is not None else "Unavailable",
    },
])
styled_table(funnel)
st.caption("The source data includes ad clicks and attributed orders; it does not include sessions, add-to-cart, or checkout-start counts.")

targets = target_inputs()
st.subheader("Budget and target pacing")
selected_date_ranges = [
    (
        max(period.start_time.date(), selections["start"]),
        min(period.end_time.date(), selections["end"]),
    )
    for period in selected_months
]
total_days = sum((end - start).days + 1 for start, end in selected_date_ranges)
as_of = min(date.today(), max(end for _, end in selected_date_ranges))
elapsed_days = sum(
    max((min(as_of, end) - start).days + 1, 0)
    for start, end in selected_date_ranges
)
elapsed_fraction = elapsed_days / total_days
to_date = df[df["date"].dt.date <= as_of]
to_date_metrics = summarize(to_date)
st.caption(
    "Spend used = spend to date ÷ budget. Expected spend pace = budget × elapsed selected days ÷ total selected days. "
    "Revenue goal progress = revenue to date ÷ goal."
)
pacing_cols = st.columns(3)
if targets["spend_budget"] > 0:
    spend_progress = to_date_metrics["spend"] / targets["spend_budget"]
    expected_spend = targets["spend_budget"] * elapsed_fraction
    pacing_cols[0].metric("Spend budget used", f"{spend_progress:.1%}", delta=f"{format_money(to_date['spend'].sum() - expected_spend, currency)} vs pace", delta_color="inverse")
    pacing_cols[0].progress(min(max(spend_progress, 0.0), 1.0))
else:
    pacing_cols[0].info("Set a period ad budget in the sidebar to see spend pacing.")
if targets["revenue_goal"] > 0:
    revenue_progress = to_date_metrics["revenue"] / targets["revenue_goal"]
    pacing_cols[1].metric("Revenue goal progress", f"{revenue_progress:.1%}", delta=f"{format_money(to_date_metrics['revenue'], currency)} to date")
    pacing_cols[1].progress(min(max(revenue_progress, 0.0), 1.0))
else:
    pacing_cols[1].info("Set a revenue goal in the sidebar to see progress.")
pacing_cols[2].metric("Target ROAS", f"{targets['roas_goal']:.2f}x", delta=f"{to_date_metrics['roas'] - targets['roas_goal']:+.2f}x to date" if to_date_metrics["roas"] is not None else "Unavailable")

st.subheader("Campaign opportunities")
st.caption(
    f"Campaign ROAS = total campaign revenue ÷ total campaign spend. Review campaigns spend at least "
    f"{format_money(targets['opportunity_min_spend'], currency)} and fall below {targets['roas_goal']:.2f}x ROAS. "
    "Scale candidates spend below the threshold and meet or exceed the ROAS target."
)
opportunities = campaign_opportunities(df, targets["roas_goal"], targets["opportunity_min_spend"])
if opportunities.empty:
    st.info("No campaigns meet the current opportunity rules.")
else:
    st.dataframe(opportunities, use_container_width=True, hide_index=True)
    st.download_button("Download opportunity list", opportunities.to_csv(index=False).encode("utf-8"), "campaign_opportunities.csv", "text/csv")

st.subheader("Daily trend")
st.plotly_chart(trend_chart(df, ["spend", "revenue", "orders", "roas"]), use_container_width=True)
st.subheader("Filtered campaign-day rows")
campaign_rows = df.sort_values("date", ascending=False)
with st.expander("Filter columns", expanded=False):
    filterable_columns = list(campaign_rows.columns)
    selected_filter_columns = st.multiselect(
        "Choose columns",
        filterable_columns,
        key="campaign_table_filter_columns",
        help="Add one or more column filters. All entered filters apply together.",
    )
    table_filters = {}
    for column in selected_filter_columns:
        operator_col, value_col = st.columns([1, 2])
        operator = operator_col.selectbox(
            f"{column} match",
            ["Contains", "Equals"],
            key=f"campaign_table_filter_operator_{column}",
        )
        value_options = available_column_values(campaign_rows[column])
        value_key = f"campaign_table_filter_value_{column}"
        if st.session_state.get(value_key) not in [None, ""] + value_options:
            st.session_state[value_key] = ""
        value = value_col.selectbox(
            f"{column} value",
            [""] + value_options,
            format_func=lambda choice: "Select a value" if choice == "" else choice,
            key=value_key,
            help="Choose a value already present in this table. Leave it blank to skip this column.",
        )
        table_filters[column] = (operator, value)

visible_campaign_rows = apply_column_filters(campaign_rows, table_filters)
st.caption(f"Showing {len(visible_campaign_rows):,} of {len(campaign_rows):,} campaign-day rows.")
st.dataframe(visible_campaign_rows, use_container_width=True, hide_index=True)
st.download_button(
    "Download filtered rows",
    visible_campaign_rows.to_csv(index=False).encode("utf-8"),
    "filtered_campaign_data.csv",
    "text/csv",
)
st.caption("ROI after ad spend = (revenue − ad spend) ÷ ad spend. ROAS = revenue ÷ ad spend.")
