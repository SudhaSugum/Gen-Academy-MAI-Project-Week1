from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CSV = ROOT / "data" / "campaign_data.csv"
REQUIRED_COLUMNS = {"date", "platform", "campaign", "spend", "impressions", "clicks", "orders", "revenue"}
OPTIONAL_NUMERIC_COLUMNS = ("product_cost", "refunds", "discounts", "shipping_cost")
OPTIONAL_DIMENSIONS = ("product", "region", "device")

def load_campaign_data(uploaded_file=None, return_report=False):
    """Read and normalize campaign data from an upload or the default CSV."""
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        source_file = getattr(uploaded_file, "name", "uploaded CSV")
    else:
        path = DEFAULT_CSV
        if not path.exists():
            raise FileNotFoundError("No campaign CSV found. Add data/campaign_data.csv or upload a file.")
        df = pd.read_csv(path)
        source_file = path.name
    df.columns = [str(column).strip().lower() for column in df.columns]
    source_columns = set(df.columns)
    original_rows = len(df)
    duplicate_rows = int(df.duplicated().sum())
    df = df.drop_duplicates().copy()
    numeric_issues = {}
    # Normalize the supplied prototype performance export to the shared campaign schema.
    aliases = {"channel": "platform", "ad_spend_usd": "spend", "revenue_usd": "revenue"}
    rename = {source: target for source, target in aliases.items() if target not in df.columns and source in df.columns}
    if rename:
        df = df.rename(columns=rename)
    if "source_dataset" not in df.columns:
        df["source_dataset"] = source_file
    else:
        df["source_dataset"] = df["source_dataset"].fillna(source_file).astype(str).str.strip()
        df.loc[df["source_dataset"] == "", "source_dataset"] = source_file
    # Accept the original marketing sample schema while standardizing on ecommerce orders.
    if "orders" not in df.columns and "conversions" in df.columns:
        df = df.rename(columns={"conversions": "orders"})
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"CSV is missing required columns: {', '.join(sorted(missing))}")
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    invalid_dates = int(df["date"].isna().sum())
    for column in ("spend", "impressions", "clicks", "orders", "revenue"):
        numeric = pd.to_numeric(df[column], errors="coerce")
        numeric_issues[column] = int(numeric.isna().sum())
        df[column] = numeric.fillna(0)
    optional_numeric_issues = {}
    for column in OPTIONAL_NUMERIC_COLUMNS:
        if column in df.columns:
            numeric = pd.to_numeric(df[column], errors="coerce")
            has_input = df[column].notna() & df[column].astype(str).str.strip().ne("")
            optional_invalid = int((has_input & numeric.isna()).sum())
            if optional_invalid:
                optional_numeric_issues[column] = optional_invalid
            df[column] = numeric
        else:
            df[column] = float("nan")
    for column in ("platform", "campaign"):
        df[column] = df[column].fillna("Unknown").astype(str).str.strip()
    for column in OPTIONAL_DIMENSIONS:
        if column not in df.columns:
            df[column] = "All products" if column == "product" else "Unknown"
        else:
            df[column] = df[column].fillna("Unknown").astype(str).str.strip()
    if "cost_data_available" in df.columns:
        flags = df["cost_data_available"].astype(str).str.strip().str.lower().map({
            "true": True, "1": True, "yes": True,
            "false": False, "0": False, "no": False,
        })
        inferred = df[["product_cost", "shipping_cost"]].notna().all(axis=1)
        df["cost_data_available"] = flags.where(flags.notna(), inferred).fillna(False).astype(bool)
    else:
        df["cost_data_available"] = df[["product_cost", "shipping_cost"]].notna().all(axis=1)
    if "data_enrichment_status" not in df.columns:
        df["data_enrichment_status"] = "Provided"
    else:
        df["data_enrichment_status"] = df["data_enrichment_status"].fillna("Provided").astype(str).str.strip()
        df.loc[df["data_enrichment_status"] == "", "data_enrichment_status"] = "Provided"
    currency_inferred_from_usd_columns = "currency" not in df.columns and {"ad_spend_usd", "revenue_usd"}.issubset(source_columns)
    currency_missing = "currency" not in df.columns and not currency_inferred_from_usd_columns
    missing_currency_values = 0
    if currency_missing:
        df["currency"] = "USD"
    elif currency_inferred_from_usd_columns:
        df["currency"] = "USD"
    else:
        missing_currency_values = int(df["currency"].isna().sum() + (df["currency"].astype(str).str.strip() == "").sum())
        df["currency"] = df["currency"].fillna("USD").astype(str).str.strip().str.upper()
        df.loc[df["currency"] == "", "currency"] = "USD"
    df = df.dropna(subset=["date"]).copy()
    if df.empty:
        raise ValueError("The CSV contains no rows with valid dates.")
    duplicate_campaign_days = int(df.duplicated(subset=["date", "platform", "campaign"]).sum())
    df["roi"] = (df["revenue"] - df["spend"]) / df["spend"].where(df["spend"] != 0)
    df["conversion_rate"] = df["orders"] / df["clicks"].where(df["clicks"] != 0)
    df["roas"] = df["revenue"] / df["spend"].where(df["spend"] != 0)
    df["cost_per_order"] = df["spend"] / df["orders"].where(df["orders"] != 0)
    df["average_order_value"] = df["revenue"] / df["orders"].where(df["orders"] != 0)
    net_revenue = df["revenue"] - df["refunds"].fillna(0) - df["discounts"].fillna(0)
    has_profit_inputs = df[["product_cost", "shipping_cost"]].notna().all(axis=1) & df["cost_data_available"]
    df["contribution_profit_after_ads"] = (net_revenue - df["product_cost"] - df["shipping_cost"] - df["spend"]).where(has_profit_inputs)
    df["contribution_margin_after_ads"] = df["contribution_profit_after_ads"] / net_revenue.where(net_revenue != 0)
    report = {
        "rows_received": original_rows,
        "duplicate_rows_removed": duplicate_rows,
        "duplicate_campaign_day_rows": duplicate_campaign_days,
        "invalid_date_rows_removed": invalid_dates,
        "numeric_values_defaulted_to_zero": numeric_issues,
        "optional_numeric_values_invalid": optional_numeric_issues,
        "currency_assumed_usd": currency_missing or missing_currency_values > 0,
        "currency_inferred_from_usd_columns": currency_inferred_from_usd_columns,
        "missing_currency_values": missing_currency_values,
        "optional_dimensions_defaulted": [name for name in OPTIONAL_DIMENSIONS if name not in source_columns],
        "source_file": source_file,
    }
    return (df, report) if return_report else df
