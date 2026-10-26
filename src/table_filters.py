"""Apply per-column contains and equals filters to dashboard tables."""

import pandas as pd
from pandas.api.types import is_bool_dtype, is_datetime64_any_dtype, is_numeric_dtype


def available_column_values(series: pd.Series) -> list[str]:
    """Return sorted, display-ready, distinct options for a column filter."""
    values = series.dropna().unique().tolist()
    if is_datetime64_any_dtype(series):
        return sorted(pd.Timestamp(value).strftime("%Y-%m-%d") for value in values)
    if is_bool_dtype(series):
        return sorted((str(value) for value in values), key=str.casefold)
    if is_numeric_dtype(series):
        return [format(float(value), ".15g") for value in sorted(values)]
    return sorted((str(value).strip() for value in values), key=str.casefold)


def apply_column_filters(frame: pd.DataFrame, filters: dict[str, tuple[str, str]]) -> pd.DataFrame:
    """Return rows matching every non-empty (operator, value) column filter."""
    result = frame
    for column, (operator, value) in filters.items():
        if column not in result.columns or not str(value).strip():
            continue

        series = result[column]
        query = str(value).strip()
        if operator == "Contains":
            if is_datetime64_any_dtype(series):
                searchable = series.dt.strftime("%Y-%m-%d")
            else:
                searchable = series.astype("string")
            result = result[searchable.str.contains(query, case=False, regex=False, na=False)]
        elif is_bool_dtype(series):
            result = result[series.astype(str).str.casefold() == query.casefold()]
        elif is_numeric_dtype(series):
            try:
                result = result[pd.to_numeric(series, errors="coerce") == float(query)]
            except ValueError:
                return result.iloc[0:0]
        elif is_datetime64_any_dtype(series):
            try:
                target = pd.to_datetime(query, errors="raise").date()
            except (TypeError, ValueError):
                return result.iloc[0:0]
            result = result[series.dt.date == target]
        else:
            result = result[series.astype("string").str.strip().str.casefold() == query.casefold()]
    return result
