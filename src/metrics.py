import pandas as pd
from datetime import timedelta

def summarize(df: pd.DataFrame) -> dict:
    spend, revenue = df["spend"].sum(), df["revenue"].sum()
    clicks = df["clicks"].sum()
    orders = df["orders"].sum()
    net_revenue = revenue - df["refunds"].fillna(0).sum() - df["discounts"].fillna(0).sum()
    profit_available = not df.empty and df["product_cost"].notna().all() and df["shipping_cost"].notna().all()
    contribution_profit = (net_revenue - df["product_cost"].sum() - df["shipping_cost"].sum() - spend) if profit_available else None
    return {"spend": spend, "clicks": clicks, "orders": orders, "revenue": revenue,
            "roi": (revenue - spend) / spend if spend else None,
            "roas": revenue / spend if spend else None,
            "conversion_rate": orders / clicks if clicks else None,
            "cost_per_order": spend / orders if orders else None,
            "average_order_value": revenue / orders if orders else None,
            "net_revenue": net_revenue,
            "contribution_profit_after_ads": contribution_profit,
            "contribution_margin_after_ads": contribution_profit / net_revenue if contribution_profit is not None and net_revenue else None}


def compare_with_previous_period(raw_df: pd.DataFrame, current_df: pd.DataFrame, selections: dict) -> tuple:
    """Compare the selected window with the immediately preceding equal-length window."""
    start, end = selections["start"], selections["end"]
    days = (end - start).days + 1
    previous_start, previous_end = start - timedelta(days=days), start - timedelta(days=1)
    previous = raw_df[raw_df["date"].dt.date.between(previous_start, previous_end)]
    for column in ("platform", "campaign", "product", "region", "device", "currency"):
        previous = previous[previous[column].astype(str).isin(selections[column])]
    return summarize(current_df), summarize(previous), (previous_start, previous_end)


def percent_change(current, previous):
    if previous in (0, None) or current is None:
        return None
    return (current - previous) / abs(previous)


def format_money(value, currency="USD"):
    if value is None:
        return "—"
    symbols = {"USD": "$", "CAD": "CA$", "AUD": "A$", "EUR": "€", "GBP": "£", "JPY": "¥"}
    symbol = symbols.get(str(currency).upper(), str(currency).upper() + " ")
    return f"{symbol}{value:,.2f}"


def campaign_opportunities(df: pd.DataFrame, target_roas: float, min_spend: float) -> pd.DataFrame:
    grouped = df.groupby(["platform", "campaign"], as_index=False).agg(
        spend=("spend", "sum"), revenue=("revenue", "sum"), orders=("orders", "sum")
    )
    grouped["ROAS"] = grouped["revenue"] / grouped["spend"].where(grouped["spend"] != 0)
    grouped["Opportunity"] = "On target"
    grouped.loc[(grouped["spend"] >= min_spend) & (grouped["ROAS"] < target_roas), "Opportunity"] = "Review: below target"
    grouped.loc[(grouped["spend"] < min_spend) & (grouped["ROAS"] >= target_roas), "Opportunity"] = "Scale candidate"
    return grouped[grouped["Opportunity"] != "On target"].sort_values(["Opportunity", "spend"], ascending=[True, False])


def grouped_metrics(df: pd.DataFrame, dimensions) -> pd.DataFrame:
    additive = ["spend", "revenue", "orders", "impressions", "clicks", "refunds", "discounts", "product_cost", "shipping_cost"]
    aggregations = {column: (column, lambda series: series.sum(min_count=1)) for column in additive if column in df.columns}
    grouped = df.groupby(dimensions, as_index=False).agg(**aggregations)
    completeness = df.groupby(dimensions, as_index=False).agg(
        product_cost_complete=("product_cost", lambda series: series.notna().all()),
        shipping_cost_complete=("shipping_cost", lambda series: series.notna().all()),
    )
    grouped = grouped.merge(completeness, on=dimensions, how="left")
    grouped["roi"] = (grouped["revenue"] - grouped["spend"]) / grouped["spend"].where(grouped["spend"] != 0)
    grouped["roas"] = grouped["revenue"] / grouped["spend"].where(grouped["spend"] != 0)
    grouped["average_order_value"] = grouped["revenue"] / grouped["orders"].where(grouped["orders"] != 0)
    grouped["cost_per_order"] = grouped["spend"] / grouped["orders"].where(grouped["orders"] != 0)
    grouped["click_to_order_rate"] = grouped["orders"] / grouped["clicks"].where(grouped["clicks"] != 0)
    has_profit_inputs = grouped["product_cost_complete"] & grouped["shipping_cost_complete"]
    net = grouped["revenue"] - grouped["refunds"].fillna(0) - grouped["discounts"].fillna(0)
    grouped["contribution_profit_after_ads"] = (net - grouped["product_cost"] - grouped["shipping_cost"] - grouped["spend"]).where(has_profit_inputs)
    grouped["contribution_margin_after_ads"] = grouped["contribution_profit_after_ads"] / net.where(net != 0)
    grouped = grouped.drop(columns=["product_cost_complete", "shipping_cost_complete"])
    return grouped
