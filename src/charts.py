import plotly.express as px
import plotly.graph_objects as go
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


def weekly_revenue_profit_chart(df, currency="USD"):
    """Compare weekly revenue with estimated contribution profit, when complete."""
    frame = df.copy()
    frame["week_start"] = frame["date"].dt.to_period("W-SUN").dt.start_time
    frame["weekly_profit"] = frame["contribution_profit_after_ads"]
    weekly = frame.groupby("week_start", as_index=False).agg(
        revenue=("revenue", "sum"),
        contribution_profit=("weekly_profit", lambda values: values.sum(min_count=1)),
        period_start=("date", "min"),
    ).sort_values("week_start")

    has_profit = frame["contribution_profit_after_ads"].notna().all()
    second_metric = "contribution_profit" if has_profit else None
    second_label = "Contribution profit after ads" if has_profit else "Ad spend"
    if not has_profit:
        spend = frame.groupby("week_start", as_index=False)["spend"].sum()
        weekly = weekly.merge(spend, on="week_start", how="left")
        second_metric = "spend"

    symbols = {"USD": "$", "CAD": "CA$", "AUD": "A$", "EUR": "€", "GBP": "£", "JPY": "¥"}
    prefix = symbols.get(str(currency).upper(), f"{currency} ")
    labels = weekly["period_start"].dt.strftime("%b %-d")
    chart = go.Figure()
    chart.add_bar(x=labels, y=weekly["revenue"], name="Revenue", marker_color="#111827")
    chart.add_bar(x=labels, y=weekly[second_metric], name=second_label, marker_color="#16803c")
    chart.update_layout(
        barmode="group", height=320, margin=dict(l=12, r=12, t=28, b=12),
        paper_bgcolor="white", plot_bgcolor="white", font=dict(color="#111827"),
        legend=dict(orientation="h", y=1.12, x=0),
        xaxis=dict(title=None, showgrid=False, tickfont=dict(color="#687386")),
        yaxis=dict(title=None, tickprefix=prefix, tickformat="~s", gridcolor="#e9edf2", zeroline=False),
    )
    return chart, has_profit
