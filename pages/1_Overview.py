import streamlit as st

from src.charts import trend_chart
from src.data_ui import current_currency, get_dashboard_data
from src.metrics import format_money, summarize

st.title("E-commerce overview")
raw, df = get_dashboard_data()
if df.empty:
    st.info("No rows match the shared filters.")
    st.stop()
m = summarize(df)
currency = current_currency(df)
cards = st.columns(6)
cards[0].metric("Ad spend", format_money(m["spend"], currency))
cards[1].metric("Revenue", format_money(m["revenue"], currency))
cards[2].metric("Orders", f"{m['orders']:,.0f}")
cards[3].metric("ROAS", f"{m['roas']:.2f}x" if m["roas"] is not None else "—")
cards[4].metric("ROI after ad spend", f"{m['roi']:.1%}" if m["roi"] is not None else "—")
cards[5].metric("Contribution profit", format_money(m["contribution_profit_after_ads"], currency))
st.plotly_chart(trend_chart(df, ["spend", "revenue", "orders", "roas", "roi"]), use_container_width=True)
