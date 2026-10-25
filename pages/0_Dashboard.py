from datetime import date

import streamlit as st

from src.data_ui import current_currency, get_dashboard_data, target_inputs
from src.metrics import campaign_opportunities, compare_with_previous_period, format_money, percent_change, summarize
from src.charts import trend_chart

st.title("E-commerce ROI Dashboard")
st.caption("Track ad spend, store revenue, orders, return on ad spend, and contribution profit.")
raw, df = get_dashboard_data()
if df.empty:
    st.info("No rows match the shared filters.")
    st.stop()

currency = current_currency(df)
m = summarize(df)
cols = st.columns(5)
cols[0].metric("Ad spend", format_money(m["spend"], currency))
cols[1].metric("Revenue", format_money(m["revenue"], currency))
cols[2].metric("Orders", f"{m['orders']:,.0f}")
cols[3].metric("ROAS", f"{m['roas']:.2f}x" if m["roas"] is not None else "—")
cols[4].metric("ROI after ad spend", f"{m['roi']:.1%}" if m["roi"] is not None else "—")
extra = st.columns(5)
extra[0].metric("Average order value", format_money(m["average_order_value"], currency))
extra[1].metric("Cost per order", format_money(m["cost_per_order"], currency))
extra[2].metric("Click-to-order rate", f"{m['conversion_rate']:.1%}" if m["conversion_rate"] is not None else "—")
extra[3].metric("Contribution profit after ads", format_money(m["contribution_profit_after_ads"], currency))
extra[4].metric("Contribution margin after ads", f"{m['contribution_margin_after_ads']:.1%}" if m["contribution_margin_after_ads"] is not None else "—")
if m["contribution_profit_after_ads"] is not None:
    st.caption("Contribution profit = revenue − refunds − discounts − product cost − shipping cost − ad spend. Taxes are excluded; see PRODUCT_SPEC.md.")

selections = st.session_state["campaign_filter_selection"]
current, previous, previous_dates = compare_with_previous_period(raw, df, selections)
st.subheader("Compared with the previous period")
st.caption(f"Previous equal-length window: {previous_dates[0]} to {previous_dates[1]} (same non-date filters).")
comparison_cols = st.columns(5)
compare_specs = [("Ad spend", "spend", True), ("Revenue", "revenue", False), ("Orders", "orders", False), ("ROAS", "roas", False), ("ROI after ad spend", "roi", False)]
for col, (label, key, inverse) in zip(comparison_cols, compare_specs):
    change = percent_change(current[key], previous[key])
    delta = f"{change:+.1%} vs previous" if change is not None else "No comparable prior value"
    if key in ("spend", "revenue"):
        value = format_money(current[key], currency)
    elif key == "roas":
        value = f"{current[key]:.2f}x" if current[key] is not None else "—"
    elif key == "roi":
        value = f"{current[key]:.1%}" if current[key] is not None else "—"
    else:
        value = f"{current[key]:,.0f}"
    col.metric(label, value, delta=delta, delta_color="inverse" if inverse else "normal")

targets = target_inputs()
st.subheader("Budget and target pacing")
period_start, period_end = selections["start"], selections["end"]
total_days = max((period_end - period_start).days + 1, 1)
as_of = min(date.today(), period_end)
elapsed_days = max(min((as_of - period_start).days + 1, total_days), 0)
elapsed_fraction = elapsed_days / total_days
to_date = df[df["date"].dt.date <= as_of]
to_date_metrics = summarize(to_date)
pacing_cols = st.columns(3)
if targets["spend_budget"] > 0:
    spend_progress = min(to_date_metrics["spend"] / targets["spend_budget"], 1.0)
    expected_spend = targets["spend_budget"] * elapsed_fraction
    pacing_cols[0].metric("Spend budget used", f"{spend_progress:.1%}", delta=f"{format_money(to_date['spend'].sum() - expected_spend, currency)} vs pace", delta_color="inverse")
    pacing_cols[0].progress(spend_progress)
else:
    pacing_cols[0].info("Set a period ad budget in the sidebar to see spend pacing.")
if targets["revenue_goal"] > 0:
    revenue_progress = min(to_date_metrics["revenue"] / targets["revenue_goal"], 1.0)
    pacing_cols[1].metric("Revenue goal progress", f"{revenue_progress:.1%}", delta=f"{format_money(to_date_metrics['revenue'], currency)} to date")
    pacing_cols[1].progress(revenue_progress)
else:
    pacing_cols[1].info("Set a revenue goal in the sidebar to see progress.")
pacing_cols[2].metric("Target ROAS", f"{targets['roas_goal']:.2f}x", delta=f"{to_date_metrics['roas'] - targets['roas_goal']:+.2f}x to date" if to_date_metrics["roas"] is not None else "Unavailable")

st.plotly_chart(trend_chart(df, ["spend", "revenue", "orders", "roas"]), use_container_width=True)
st.subheader("Campaign opportunities")
opportunities = campaign_opportunities(df, targets["roas_goal"], targets["opportunity_min_spend"])
if opportunities.empty:
    st.info("No campaigns meet the current opportunity rules.")
else:
    st.dataframe(opportunities, use_container_width=True, hide_index=True)
    st.download_button("Download opportunity list", opportunities.to_csv(index=False).encode("utf-8"), "campaign_opportunities.csv", "text/csv")

st.subheader("Filtered campaign performance")
st.dataframe(df.sort_values("date", ascending=False), use_container_width=True, hide_index=True)
st.download_button("Download filtered rows", df.to_csv(index=False).encode("utf-8"), "filtered_campaign_data.csv", "text/csv")
st.caption("ROI after ad spend = (revenue − ad spend) ÷ ad spend. ROAS = revenue ÷ ad spend.")
