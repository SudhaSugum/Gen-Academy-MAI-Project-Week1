import streamlit as st

from src.charts import platform_chart
from src.data_ui import get_dashboard_data
from src.metrics import grouped_metrics

st.title("Channel comparison")
raw, df = get_dashboard_data()
if df.empty:
    st.info("No rows match the shared filters.")
    st.stop()
metric = st.selectbox("Compare metric", ["spend", "revenue", "orders", "clicks", "roas", "roi"], format_func=lambda value: value.replace("_", " ").title(), key="channel_metric")
st.plotly_chart(platform_chart(df, metric), use_container_width=True)
summary = grouped_metrics(df, ["platform"])
st.dataframe(summary.sort_values(metric, ascending=False), use_container_width=True, hide_index=True)
st.download_button("Download channel summary", summary.to_csv(index=False).encode("utf-8"), "channel_summary.csv", "text/csv")
