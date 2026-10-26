import streamlit as st
import pandas as pd

def filter_rows(df, selections):
    filtered = df[df["date"].dt.date.between(selections["start"], selections["end"])]
    for column in ("platform", "campaign", "product", "region", "device", "source_dataset"):
        if column in selections:
            filtered = filtered[filtered[column].astype(str).isin(selections[column])]
    if "currency" in selections:
        filtered = filtered[filtered["currency"].astype(str).isin(selections["currency"])]
    return filtered


def filter_by_campaign_keys(df, selections):
    """Apply shared date, platform/channel, and campaign filters to keyed summaries."""
    filtered = df.copy()
    if "date" in filtered.columns:
        filtered["date"] = filtered["date"] if pd.api.types.is_datetime64_any_dtype(filtered["date"]) else pd.to_datetime(filtered["date"], errors="coerce")
        filtered = filtered[filtered["date"].dt.date.between(selections["start"], selections["end"])]
    platform_column = "platform" if "platform" in filtered.columns else "channel" if "channel" in filtered.columns else None
    if platform_column and "platform" in selections:
        filtered = filtered[filtered[platform_column].astype(str).isin(selections["platform"])]
    if "campaign" in filtered.columns and "campaign" in selections:
        filtered = filtered[filtered["campaign"].astype(str).isin(selections["campaign"])]
    return filtered


def shared_filters(df):
    st.sidebar.header("Filters")
    min_date, max_date = df["date"].min().date(), df["date"].max().date()
    date_range = st.sidebar.date_input("Date range", value=(min_date, max_date), min_value=min_date, max_value=max_date, key="campaign_date_range")
    start, end = date_range if isinstance(date_range, (tuple, list)) and len(date_range) == 2 else (date_range, date_range)
    selections = {"start": start, "end": end}
    selectors = [
        ("source_dataset", "Data sources"),
        ("platform", "Platforms"),
        ("campaign", "Campaigns"),
        ("product", "Products"),
        ("region", "Regions"),
        ("device", "Devices"),
    ]
    for column, label in selectors:
        values = sorted(df[column].dropna().astype(str).unique())
        key = "campaign_filter_" + column
        selected = st.sidebar.multiselect(label, values, default=values, key=key)
        selections[column] = selected
    currencies = sorted(df["currency"].dropna().astype(str).unique())
    currency = st.sidebar.selectbox("Currency", currencies, key="campaign_filter_currency")
    selections["currency"] = [currency]
    st.session_state["campaign_filter_selection"] = selections
    return filter_rows(df, selections)
