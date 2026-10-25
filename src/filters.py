import streamlit as st

def filter_rows(df, selections):
    filtered = df[df["date"].dt.date.between(selections["start"], selections["end"])]
    for column in ("platform", "campaign", "product", "region", "device"):
        filtered = filtered[filtered[column].astype(str).isin(selections[column])]
    return filtered[filtered["currency"].astype(str).isin(selections["currency"])]

def shared_filters(df):
    st.sidebar.header("Filters")
    min_date, max_date = df["date"].min().date(), df["date"].max().date()
    date_range = st.sidebar.date_input("Date range", value=(min_date, max_date), min_value=min_date, max_value=max_date, key="campaign_date_range")
    start, end = date_range if isinstance(date_range, (tuple, list)) and len(date_range) == 2 else (date_range, date_range)
    selections = {"start": start, "end": end}
    selectors = [("platform", "Platforms"), ("campaign", "Campaigns"), ("product", "Products"), ("region", "Regions"), ("device", "Devices")]
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
