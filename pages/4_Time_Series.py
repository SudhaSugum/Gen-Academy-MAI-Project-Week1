import streamlit as st

from src.charts import trend_chart
from src.data_ui import get_dashboard_data

st.title("E-commerce trends")
raw, df = get_dashboard_data()
if df.empty:
    st.info("No rows match the shared filters.")
    st.stop()
available_metrics = ["spend", "revenue", "orders", "clicks", "roas", "roi"]
metrics = st.multiselect("Metrics", available_metrics, default=["spend", "revenue", "orders", "roas"], format_func=lambda value: value.replace("_", " ").title(), key="time_series_metrics")
if metrics:
    st.plotly_chart(trend_chart(df, metrics=metrics), use_container_width=True)
else:
    st.info("Select at least one metric to chart.")
