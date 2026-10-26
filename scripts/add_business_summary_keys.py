"""Allocate product and customer summaries to campaign date/channel keys."""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CAMPAIGN_FILE = DATA / "campaign_data.csv"
PRODUCT_FILE = DATA / "products.csv"
SEGMENT_FILE = DATA / "customer_segments.csv"
KEY_COLUMNS = {"date", "channel", "campaign"}
CAMPAIGN_NAMES = {
    "Search - Brand", "Search - Generic", "Shopping", "Prospecting - Lookalike",
    "Retargeting - Warm", "Video Views", "Creator Collab", "Spark Ads",
    # August campaign keys included in the synthetic monthly allocation.
    "Brand Search", "Fall Awareness", "Product Launch", "Product Search",
    "Retargeting", "TikTok Prospecting",
}


def allocate(total, weights, scale=100):
    """Split a total proportionally and preserve its exact rounded sum."""
    weights = [max(float(weight), 0.0) for weight in weights]
    if not weights or sum(weights) == 0:
        raise ValueError("Allocation needs at least one positive weight.")
    target = int(round(float(total) * scale))
    exact = [target * weight / sum(weights) for weight in weights]
    parts = [int(value) for value in exact]
    remainder = target - sum(parts)
    order = sorted(range(len(parts)), key=lambda index: exact[index] - parts[index], reverse=True)
    for index in order[:remainder]:
        parts[index] += 1
    return [int(part) for part in parts] if scale == 1 else [part / scale for part in parts]


def recover_product_totals(frame):
    if not KEY_COLUMNS.issubset(frame.columns):
        return frame
    numeric = ["units_sold", "revenue_usd", "ad_spend_usd", "cogs_usd", "shipping_fees_usd", "profit_usd"]
    totals = frame.groupby("product", as_index=False)[numeric].sum()
    roi = frame.groupby("product", as_index=False)["roi_percent"].first()
    return totals.merge(roi, on="product")


def recover_segment_totals(frame):
    if not KEY_COLUMNS.issubset(frame.columns):
        return frame
    rows = []
    for segment, group in frame.groupby("segment"):
        orders = group["orders"].sum()
        revenue = group["revenue_usd"].sum()
        profit = group["profit_usd"].sum()
        rows.append({
            "segment": segment,
            "orders": orders,
            "revenue_usd": revenue,
            "avg_order_value_usd": (group["avg_order_value_usd"] * group["orders"]).sum() / orders if orders else 0,
            "acquisition_cost_per_order_usd": (group["acquisition_cost_per_order_usd"] * group["orders"]).sum() / orders if orders else 0,
            "profit_usd": profit,
            "profit_per_order_usd": (group["profit_per_order_usd"] * group["orders"]).sum() / orders if orders else 0,
        })
    return pd.DataFrame(rows)


def save_csv(frame, path):
    frame.to_csv(path, index=False, float_format="%.2f", date_format="%Y-%m-%d", lineterminator="\n")


def main():
    campaign = pd.read_csv(CAMPAIGN_FILE, parse_dates=["date"])
    products = recover_product_totals(pd.read_csv(PRODUCT_FILE))
    segments = recover_segment_totals(pd.read_csv(SEGMENT_FILE))

    campaign_rows = campaign[campaign["campaign"].isin(CAMPAIGN_NAMES)].copy()
    campaign_rows = campaign_rows.sort_values(["date", "platform", "campaign"]).reset_index(drop=True)
    product_controls = {
        "units_sold": int(products["units_sold"].sum()),
        "revenue_usd": round(products["revenue_usd"].sum(), 2),
        "ad_spend_usd": round(products["ad_spend_usd"].sum(), 2),
    }
    if campaign_rows.empty or not campaign_rows["date"].dt.month.eq(8).any():
        raise ValueError("Campaign keys must include August rows for the monthly summary allocation.")
    if product_controls != {"units_sold": 2344, "revenue_usd": 128400.00, "ad_spend_usd": 31200.00}:
        raise ValueError(f"Product snapshot totals changed unexpectedly: {product_controls}")
    if int(segments["orders"].sum()) != 2140 or round(segments["revenue_usd"].sum(), 2) != 128400.00:
        raise ValueError("Customer segment totals no longer match the keyed campaign cohort.")

    product_records = []
    order_weights = campaign_rows["orders"].tolist()
    revenue_weights = campaign_rows["revenue"].tolist()
    spend_weights = campaign_rows["spend"].tolist()
    for product in products.to_dict("records"):
        allocations = {
            "units_sold": allocate(product["units_sold"], order_weights, scale=1),
            "revenue_usd": allocate(product["revenue_usd"], revenue_weights),
            "ad_spend_usd": allocate(product["ad_spend_usd"], spend_weights),
            "cogs_usd": allocate(product["cogs_usd"], revenue_weights),
            "shipping_fees_usd": allocate(product["shipping_fees_usd"], order_weights),
            "profit_usd": allocate(product["profit_usd"], revenue_weights),
        }
        for index, campaign_row in campaign_rows.iterrows():
            product_records.append({
                "date": campaign_row["date"],
                "channel": campaign_row["platform"],
                "campaign": campaign_row["campaign"],
                "product": product["product"],
                **{column: values[index] for column, values in allocations.items()},
                "roi_percent": product["roi_percent"],
            })

    segment_records = []
    for segment in segments.to_dict("records"):
        order_allocations = allocate(segment["orders"], order_weights, scale=1)
        revenue_allocations = allocate(segment["revenue_usd"], revenue_weights)
        profit_allocations = allocate(segment["profit_usd"], revenue_weights)
        for index, campaign_row in campaign_rows.iterrows():
            segment_records.append({
                "date": campaign_row["date"],
                "channel": campaign_row["platform"],
                "campaign": campaign_row["campaign"],
                "segment": segment["segment"],
                "orders": order_allocations[index],
                "revenue_usd": revenue_allocations[index],
                "avg_order_value_usd": segment["avg_order_value_usd"],
                "acquisition_cost_per_order_usd": segment["acquisition_cost_per_order_usd"],
                "profit_usd": profit_allocations[index],
                "profit_per_order_usd": segment["profit_per_order_usd"],
            })

    product_output = pd.DataFrame(product_records).sort_values(["date", "channel", "campaign", "product"])
    segment_output = pd.DataFrame(segment_records).sort_values(["date", "channel", "campaign", "segment"])
    save_csv(product_output, PRODUCT_FILE)
    save_csv(segment_output, SEGMENT_FILE)
    print(f"Wrote {len(product_output):,} keyed product rows and {len(segment_output):,} keyed customer-segment rows.")


if __name__ == "__main__":
    main()
