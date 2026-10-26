from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PRODUCTS_CSV = ROOT / "data" / "products.csv"
CUSTOMER_SEGMENTS_CSV = ROOT / "data" / "customer_segments.csv"

PRODUCT_COLUMNS = {
    "date", "channel", "campaign",
    "product", "units_sold", "revenue_usd", "ad_spend_usd", "cogs_usd",
    "shipping_fees_usd", "profit_usd", "roi_percent",
}
SEGMENT_COLUMNS = {
    "date", "channel", "campaign",
    "segment", "orders", "revenue_usd", "avg_order_value_usd",
    "acquisition_cost_per_order_usd", "profit_usd", "profit_per_order_usd",
}


def _load_summary(path: Path, required_columns: set[str], numeric_columns: tuple[str, ...]) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Summary data file not found: {path.name}")
    try:
        frame = pd.read_csv(path)
    except (pd.errors.ParserError, pd.errors.EmptyDataError, UnicodeDecodeError) as exc:
        raise ValueError(f"Could not parse {path.name}: {exc}") from exc
    frame.columns = [str(column).strip().lower() for column in frame.columns]
    if frame.empty:
        raise ValueError(f"{path.name} contains no data rows.")
    missing = required_columns - set(frame.columns)
    if missing:
        raise ValueError(f"{path.name} is missing required columns: {', '.join(sorted(missing))}")
    if "date" in frame.columns:
        frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
        invalid_dates = int(frame["date"].isna().sum())
        if invalid_dates:
            raise ValueError(f"{path.name} has {invalid_dates} missing or invalid campaign date(s).")
    for column in ("channel", "campaign"):
        if column in frame.columns:
            frame[column] = frame[column].fillna("").astype(str).str.strip()
            if frame[column].eq("").any():
                raise ValueError(f"{path.name} has blank values in the required {column} key.")
    invalid = {}
    for column in numeric_columns:
        parsed = pd.to_numeric(frame[column], errors="coerce")
        bad_count = int(parsed.isna().sum())
        if bad_count:
            invalid[column] = bad_count
        frame[column] = parsed
    if invalid:
        details = ", ".join(f"{column}: {count}" for column, count in invalid.items())
        raise ValueError(f"{path.name} has missing or nonnumeric values in numeric columns ({details}).")
    return frame


def load_product_summary() -> pd.DataFrame:
    numeric = tuple(PRODUCT_COLUMNS - {"product", "date", "channel", "campaign"})
    return _load_summary(PRODUCTS_CSV, PRODUCT_COLUMNS, numeric)


def load_customer_segment_summary() -> pd.DataFrame:
    numeric = tuple(SEGMENT_COLUMNS - {"segment", "date", "channel", "campaign"})
    return _load_summary(CUSTOMER_SEGMENTS_CSV, SEGMENT_COLUMNS, numeric)
