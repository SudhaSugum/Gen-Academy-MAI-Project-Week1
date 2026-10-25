import plotly.express as px
from src.metrics import grouped_metrics

METRIC_LABELS = {"spend": "Ad spend", "clicks": "Clicks", "orders": "Orders", "revenue": "Revenue", "roas": "ROAS (x)", "roi": "ROI (%)"}

def trend_chart(df, metrics=("spend", "revenue", "orders")):
    daily = df.groupby("date", as_index=False)[["spend", "revenue", "orders", "clicks"]].sum().sort_values("date")
    daily["roas"] = daily["revenue"] / daily["spend"].where(daily["spend"] != 0)
    daily["roi"] = (daily["revenue"] - daily["spend"]) / daily["spend"].where(daily["spend"] != 0)
    valid_metrics = [metric for metric in metrics if metric in daily.columns]
    if not valid_metrics:
        return px.line(title="Select at least one available metric")
    melted = daily.melt("date", value_vars=valid_metrics, var_name="metric", value_name="value")
    melted["metric"] = melted["metric"].map(METRIC_LABELS)
    currency = str(df["currency"].iloc[0]) if "currency" in df.columns and not df.empty else ""
    chart = px.line(melted, x="date", y="value", color="metric", facet_row="metric", markers=True, title=f"Daily e-commerce performance ({currency})" if currency else "Daily e-commerce performance")
    chart.for_each_yaxis(lambda axis: axis.update(matches=None, tickformat=".0%" if "ROI" in str(axis.title.text) else None))
    return chart

def platform_chart(df, metric="spend"):
    grouped = grouped_metrics(df, ["platform"])
    grouped = grouped.sort_values(metric, ascending=False, na_position="last")
    currency = str(df["currency"].iloc[0]) if metric in ("spend", "revenue") and "currency" in df.columns and not df.empty else ""
    suffix = f" ({currency})" if currency else ""
    return px.bar(grouped, x="platform", y=metric, color="platform", title=f"{METRIC_LABELS.get(metric, metric.title())}{suffix} by platform")
