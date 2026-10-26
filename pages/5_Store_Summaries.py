import streamlit as st

from src.data_ui import get_dashboard_data
from src.metrics import format_money
from src.business_data import load_customer_segment_summary, load_product_summary
from src.filters import filter_by_campaign_keys

st.title("Products & customer segments")
_, filtered_ad_rows = get_dashboard_data()
selection = st.session_state["campaign_filter_selection"]
st.caption(
    f"Shared ad-performance filter: {selection['start']} to {selection['end']} "
    f"({len(filtered_ad_rows):,} matching campaign rows)."
)
st.info(
    "Product and customer-segment totals are allocated across dated channel and campaign rows so the shared date, platform, and campaign filters can slice them. "
    "The keyed splits are modeled allocations because the source summaries only contain aggregate totals; summing all keyed rows preserves those totals. "
    "Product, region, and device filters apply to campaign data, not these separate summaries."
)

try:
    products = filter_by_campaign_keys(load_product_summary(), selection)
except (FileNotFoundError, ValueError) as exc:
    products = None
    st.error(f"Could not load product summary: {exc}")

if products is not None:
    st.subheader("Product performance")
    if products.empty:
        st.info("No product rows match the selected date, platform, and campaign filters.")
    else:
        product_summary = products.groupby("product", as_index=False).agg(
            units_sold=("units_sold", "sum"),
            revenue_usd=("revenue_usd", "sum"),
            ad_spend_usd=("ad_spend_usd", "sum"),
            cogs_usd=("cogs_usd", "sum"),
            shipping_fees_usd=("shipping_fees_usd", "sum"),
            profit_usd=("profit_usd", "sum"),
            roi_percent=("roi_percent", "first"),
        )
        product_metrics = st.columns(4)
        product_metrics[0].metric("Units sold", f"{products['units_sold'].sum():,.0f}")
        product_metrics[1].metric("Revenue", format_money(products["revenue_usd"].sum(), "USD"))
        product_metrics[2].metric("Ad spend", format_money(products["ad_spend_usd"].sum(), "USD"))
        product_metrics[3].metric("Reported profit", format_money(products["profit_usd"].sum(), "USD"))

        product_table = product_summary.rename(columns={
            "product": "Product", "units_sold": "Units sold", "revenue_usd": "Revenue",
            "ad_spend_usd": "Ad spend", "cogs_usd": "COGS", "shipping_fees_usd": "Shipping fees",
            "profit_usd": "Reported profit", "roi_percent": "Reported ROI (%)",
        }).copy()
        for column in ("Revenue", "Ad spend", "COGS", "Shipping fees", "Reported profit"):
            product_table[column] = product_table[column].map(lambda value: format_money(value, "USD"))
        product_table["Units sold"] = product_table["Units sold"].map(lambda value: f"{value:,.0f}")
        product_table["Reported ROI (%)"] = product_table["Reported ROI (%)"].map(lambda value: f"{value:.1f}%")
        st.dataframe(product_table, use_container_width=True, hide_index=True)
        st.download_button(
            "Download filtered product rows", products.to_csv(index=False).encode("utf-8"),
            "products.csv", "text/csv", key="download_product_summary",
        )
        st.caption("Reported ROI is shown as supplied and does not vary by date, channel, or campaign allocation.")

try:
    segments = filter_by_campaign_keys(load_customer_segment_summary(), selection)
except (FileNotFoundError, ValueError) as exc:
    segments = None
    st.error(f"Could not load customer-segment summary: {exc}")

if segments is not None:
    st.subheader("Customer segment performance")
    if segments.empty:
        st.info("No customer-segment rows match the selected date, platform, and campaign filters.")
        st.stop()

    segments = segments.assign(
        _weighted_acquisition_cost=segments["acquisition_cost_per_order_usd"] * segments["orders"]
    )
    segment_summary = segments.groupby("segment", as_index=False).agg(
        orders=("orders", "sum"),
        revenue_usd=("revenue_usd", "sum"),
        profit_usd=("profit_usd", "sum"),
        _weighted_acquisition_cost=("_weighted_acquisition_cost", "sum"),
    )
    total_orders = segment_summary["orders"].sum()
    total_revenue = segment_summary["revenue_usd"].sum()
    total_profit = segment_summary["profit_usd"].sum()
    weighted_aov = total_revenue / total_orders if total_orders else None
    weighted_acquisition_cost = segment_summary["_weighted_acquisition_cost"].sum() / total_orders if total_orders else None
    segment_summary["avg_order_value_usd"] = segment_summary["revenue_usd"] / segment_summary["orders"].where(segment_summary["orders"] != 0)
    segment_summary["acquisition_cost_per_order_usd"] = segment_summary["_weighted_acquisition_cost"] / segment_summary["orders"].where(segment_summary["orders"] != 0)
    segment_summary["profit_per_order_usd"] = segment_summary["profit_usd"] / segment_summary["orders"].where(segment_summary["orders"] != 0)
    segment_metrics = st.columns(5)
    segment_metrics[0].metric("Orders", f"{total_orders:,.0f}")
    segment_metrics[1].metric("Revenue", format_money(total_revenue, "USD"))
    segment_metrics[2].metric("Average order value", format_money(weighted_aov, "USD"))
    segment_metrics[3].metric("Reported profit", format_money(total_profit, "USD"))
    segment_metrics[4].metric("Acquisition cost / order", format_money(weighted_acquisition_cost, "USD"))

    segment_table = segment_summary.drop(columns="_weighted_acquisition_cost").rename(columns={
        "segment": "Segment", "orders": "Orders", "revenue_usd": "Revenue",
        "avg_order_value_usd": "Average order value",
        "acquisition_cost_per_order_usd": "Acquisition cost / order",
        "profit_usd": "Reported profit", "profit_per_order_usd": "Profit / order",
    }).copy()
    for column in ("Revenue", "Average order value", "Acquisition cost / order", "Reported profit", "Profit / order"):
        segment_table[column] = segment_table[column].map(lambda value: format_money(value, "USD"))
    segment_table["Orders"] = segment_table["Orders"].map(lambda value: f"{value:,.0f}")
    st.dataframe(segment_table, use_container_width=True, hide_index=True)
    st.download_button(
        "Download filtered customer-segment rows", segments.drop(columns="_weighted_acquisition_cost").to_csv(index=False).encode("utf-8"),
        "customer_segments.csv", "text/csv", key="download_customer_segment_summary",
    )
