"""Fill missing values and normalize the canonical campaign data file."""

import csv
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_FILE = ROOT / "data" / "campaign_data.csv"

OUTPUT_COLUMNS = [
    "date", "platform", "campaign", "spend", "impressions", "clicks", "orders", "revenue",
    "product", "region", "device", "currency", "product_cost", "refunds", "discounts",
    "shipping_cost", "source_dataset", "cost_data_available", "data_enrichment_status",
]
NUMERIC_COLUMNS = (
    "spend", "impressions", "clicks", "orders", "revenue",
    "product_cost", "refunds", "discounts", "shipping_cost",
)


def read_csv(path: Path) -> tuple[list[dict[str, str]], set[str]]:
    if not path.exists():
        raise FileNotFoundError(f"Campaign data file not found: {path}")
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError(f"Source file has no header: {path.name}")
        return list(reader), set(reader.fieldnames)


def clean_combined_rows(rows: list[dict[str, str]], columns: set[str]) -> list[dict[str, str]]:
    required = set(OUTPUT_COLUMNS[:16])
    if not required.issubset(columns):
        missing = ", ".join(sorted(required - columns))
        raise ValueError(f"{OUTPUT_FILE.name} is missing columns: {missing}")
    cleaned = []
    for row in rows:
        combined = {column: row.get(column, "") or "" for column in OUTPUT_COLUMNS[:16]}
        supplied_flag = row.get("cost_data_available", "").strip().lower()
        if supplied_flag in {"true", "1", "yes"}:
            cost_available = True
        elif supplied_flag in {"false", "0", "no"}:
            cost_available = False
        else:
            cost_available = all(
                str(row.get(column, "")).strip() != ""
                for column in ("product_cost", "shipping_cost")
            )
        combined["product"] = combined["product"] or "All products"
        combined["region"] = combined["region"] or "Unknown"
        combined["device"] = combined["device"] or "Unknown"
        combined["currency"] = combined["currency"] or "USD"
        for column in ("spend", "impressions", "clicks", "orders", "revenue", "product_cost", "refunds", "discounts", "shipping_cost"):
            combined[column] = combined[column] or "0"
        combined["source_dataset"] = row.get("source_dataset") or OUTPUT_FILE.name
        combined["cost_data_available"] = str(cost_available)
        combined["data_enrichment_status"] = row.get("data_enrichment_status") or "Provided"
        cleaned.append(combined)
    return cleaned


def enrich_missing_values(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    """Replace unavailable dimensions and cost inputs with labeled estimates."""
    complete_rows = [row for row in rows if row["cost_data_available"].lower() == "true"]
    if not complete_rows:
        raise ValueError("Cannot estimate missing costs without any complete cost rows.")

    product_cost_rates = [
        float(row["product_cost"]) / float(row["revenue"])
        for row in complete_rows
        if float(row["revenue"]) > 0
    ]
    shipping_per_order = [
        float(row["shipping_cost"]) / float(row["orders"])
        for row in complete_rows
        if float(row["orders"]) > 0
    ]
    product_cost_rate = statistics.median(product_cost_rates)
    shipping_cost_per_order = statistics.median(shipping_per_order)

    valid_regions = sorted({row["region"] for row in complete_rows if row["region"] and row["region"] != "Unknown"})
    valid_devices = sorted({row["device"] for row in complete_rows if row["device"] and row["device"] != "Unknown"})
    if not valid_regions or not valid_devices:
        raise ValueError("Cannot assign missing dimensions without valid region and device choices.")
    device_by_platform = {}
    for platform in {row["platform"] for row in complete_rows}:
        counts = {}
        for row in complete_rows:
            if row["platform"] == platform and row["device"] and row["device"] != "Unknown":
                counts[row["device"]] = counts.get(row["device"], 0) + 1
        if counts:
            device_by_platform[platform] = max(counts, key=counts.get)

    campaign_regions = {}
    for platform in sorted({row["platform"] for row in rows}):
        campaigns = sorted({row["campaign"] for row in rows if row["platform"] == platform})
        for index, campaign in enumerate(campaigns):
            if valid_regions:
                campaign_regions[(platform, campaign)] = valid_regions[index % len(valid_regions)]

    enriched = []
    for row in rows:
        item = dict(row)
        needs_estimation = item["cost_data_available"].lower() != "true"
        if item["product"] in {"", "Unknown", "Unknown product"}:
            item["product"] = "All products"
            needs_estimation = True
        if item["region"] in {"", "Unknown", "Unknown region"}:
            item["region"] = campaign_regions.get((item["platform"], item["campaign"]), valid_regions[0])
            needs_estimation = True
        if item["device"] in {"", "Unknown", "Unknown device"}:
            item["device"] = device_by_platform.get(item["platform"], valid_devices[0])
            needs_estimation = True

        if item["cost_data_available"].lower() != "true":
            revenue = float(item["revenue"])
            orders = float(item["orders"])
            item["product_cost"] = f"{revenue * product_cost_rate:.2f}"
            # The product contract treats omitted refunds and discounts as zero.
            item["refunds"] = item["refunds"] or "0"
            item["discounts"] = item["discounts"] or "0"
            item["cost_data_available"] = "True"
        if needs_estimation:
            item["data_enrichment_status"] = "Estimated"

        item["source_dataset"] = "Combined campaign data"
        for column in NUMERIC_COLUMNS:
            value = float(item[column])
            if column in {"impressions", "clicks", "orders"}:
                item[column] = str(int(value))
            elif column in {"spend", "revenue", "product_cost", "refunds", "discounts", "shipping_cost"}:
                item[column] = f"{value:.2f}"
        enriched.append(item)
    return enriched


def build_rows() -> list[dict[str, str]]:
    rows, columns = read_csv(OUTPUT_FILE)
    return enrich_missing_values(clean_combined_rows(rows, columns))


def main() -> None:
    rows = build_rows()
    with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows):,} rows to {OUTPUT_FILE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
