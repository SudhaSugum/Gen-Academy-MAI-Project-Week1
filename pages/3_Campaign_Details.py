import streamlit as st

from src.data_ui import get_dashboard_data
from src.metrics import grouped_metrics

st.title("Campaign and business breakdowns")
raw, df = get_dashboard_data()
if df.empty:
    st.info("No rows match the shared filters.")
    st.stop()
breakdown = st.selectbox("Break down by", ["campaign", "product", "region", "device", "platform and campaign"], key="business_breakdown")
dimensions = ["platform", "campaign"] if breakdown == "platform and campaign" else [breakdown]
summary = grouped_metrics(df, dimensions)
sort_by = st.selectbox("Sort by", ["spend", "revenue", "orders", "roas", "roi", "contribution_profit_after_ads", "contribution_margin_after_ads"], format_func=lambda value: value.replace("_", " ").title(), key="breakdown_sort")
st.dataframe(summary.sort_values(sort_by, ascending=False, na_position="last"), use_container_width=True, hide_index=True)
st.download_button("Download breakdown", summary.to_csv(index=False).encode("utf-8"), "business_breakdown.csv", "text/csv")
