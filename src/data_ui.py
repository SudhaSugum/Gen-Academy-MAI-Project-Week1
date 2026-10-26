import streamlit as st
import pandas as pd

from src.data_loader import load_campaign_data
from src.filters import shared_filters


def get_dashboard_data():
    """Render shared upload/quality controls and return raw plus filtered rows."""
    uploaded = st.sidebar.file_uploader("Upload campaign CSV", type="csv", key="campaign_csv_upload")
    try:
        raw, report = load_campaign_data(uploaded, return_report=True)
    except (ValueError, FileNotFoundError, pd.errors.ParserError, pd.errors.EmptyDataError, UnicodeDecodeError) as exc:
        st.error(f"Could not load campaign data: {exc}")
        st.stop()
    st.session_state["campaign_data_source_file"] = report["source_file"]

    with st.sidebar.expander("Data quality and export", expanded=False):
        st.caption(f"Source: {report['source_file']}")
        st.caption(f"{len(raw):,} valid dated rows loaded from {report['rows_received']:,} input rows.")
        if report["duplicate_rows_removed"]:
            st.warning(f"Removed {report['duplicate_rows_removed']} duplicate row(s).")
        if report["duplicate_campaign_day_rows"]:
            st.warning(f"Found {report['duplicate_campaign_day_rows']} additional row(s) sharing the same date, platform, and campaign. Review these before treating the rows as unique.")
        if report["invalid_date_rows_removed"]:
            st.warning(f"Removed {report['invalid_date_rows_removed']} row(s) with invalid dates.")
        numeric_issues = {key: value for key, value in report["numeric_values_defaulted_to_zero"].items() if value}
        if numeric_issues:
            st.warning("Some missing or nonnumeric required values were treated as zero: " + ", ".join(f"{k}: {v}" for k, v in numeric_issues.items()))
        optional_issues = report["optional_numeric_values_invalid"]
        if optional_issues:
            st.warning("Some optional numeric values remain unavailable because they contain nonnumeric text: " + ", ".join(f"{k}: {v}" for k, v in optional_issues.items()))
        if report["currency_inferred_from_usd_columns"]:
            st.info("USD currency was inferred from the `_usd` monetary column names.")
        elif report["currency_assumed_usd"]:
            st.info("Currency is assumed to be USD for missing currency values. Confirm this before using real data.")
        if report["optional_dimensions_defaulted"]:
            st.caption("Defaulted missing breakdown columns: " + ", ".join(report["optional_dimensions_defaulted"]))
        incomplete_cost_rows = int((~raw["cost_data_available"]).sum())
        if incomplete_cost_rows:
            st.info(
                f"Contribution profit is unavailable for {incomplete_cost_rows:,} row(s) with unavailable product or shipping-cost inputs. "
                "Zero placeholders in those cost columns are not treated as actual costs."
            )
        estimated_rows = int(raw["data_enrichment_status"].eq("Estimated").sum()) if "data_enrichment_status" in raw else 0
        if estimated_rows:
            st.info(
                f"{estimated_rows:,} row(s) contain estimated product costs, shipping costs, region, or device values. "
                "Review these estimates before using them as actual business results."
            )
        st.download_button("Download cleaned CSV", raw.to_csv(index=False).encode("utf-8"), "cleaned_campaign_data.csv", "text/csv", key="download_cleaned_csv")
    with st.sidebar.expander("Preview cleaned data", expanded=False):
        if not raw.empty and "date" in raw:
            date_range = pd.to_datetime(raw["date"], errors="coerce").dropna()
            if not date_range.empty:
                st.caption(
                    f"Showing all {len(raw):,} cleaned rows · "
                    f"{date_range.min():%b %-d, %Y} – {date_range.max():%b %-d, %Y}"
                )
        st.dataframe(raw, height=400, use_container_width=True, hide_index=True)
    filtered = shared_filters(raw)
    return raw, filtered


def current_currency(df):
    return str(df["currency"].iloc[0]) if not df.empty else "USD"


def target_inputs():
    st.sidebar.header("Targets")
    return {
        "spend_budget": st.sidebar.number_input(
            "Period ad budget", min_value=0.0, value=0.0, step=100.0,
            key="target_spend_budget",
            help="Budget for the selected Metric Month months. Used to calculate spend used and expected spend pace.",
        ),
        "revenue_goal": st.sidebar.number_input(
            "Period revenue goal", min_value=0.0, value=0.0, step=500.0,
            key="target_revenue_goal",
            help="Revenue target for the selected Metric Month months. Used to calculate revenue goal progress.",
        ),
        "roas_goal": st.sidebar.number_input(
            "Target ROAS", min_value=0.0, value=2.0, step=0.1,
            key="target_roas_goal",
            help="ROAS benchmark used in target pacing and campaign opportunity rules. ROAS is total revenue divided by total ad spend.",
        ),
        "opportunity_min_spend": st.sidebar.number_input(
            "Opportunity minimum spend", min_value=0.0, value=100.0, step=50.0,
            key="opportunity_min_spend",
            help="Spend threshold that separates higher-spend campaigns to review from lower-spend campaigns that may be scale candidates.",
        ),
    }
