import unittest
from io import StringIO

import pandas as pd

from src.charts import trend_chart
from src.data_loader import load_campaign_data
from src.filters import filter_rows
from src.metrics import compare_with_previous_period, grouped_metrics, summarize


class DashboardMetricTests(unittest.TestCase):
    @staticmethod
    def campaign_rows():
        return load_campaign_data()

    def test_combined_dataset_matches_documented_baseline(self):
        metrics = summarize(self.campaign_rows())
        self.assertAlmostEqual(metrics["spend"], 70893.19, places=2)
        self.assertAlmostEqual(metrics["revenue"], 574506.43, places=2)
        self.assertEqual(metrics["orders"], 19001)
        self.assertAlmostEqual(metrics["roas"], 8.1038, places=4)
        self.assertAlmostEqual(metrics["roi"], 7.1038, places=4)

    def test_zero_denominators_produce_unavailable_ratios(self):
        rows = pd.DataFrame({
            "spend": [0.0], "revenue": [100.0], "clicks": [0], "orders": [0],
            "refunds": [0.0], "discounts": [0.0], "product_cost": [20.0], "shipping_cost": [5.0],
        })
        metrics = summarize(rows)
        self.assertIsNone(metrics["roas"])
        self.assertIsNone(metrics["roi"])
        self.assertIsNone(metrics["conversion_rate"])
        self.assertIsNone(metrics["average_order_value"])

    def test_grouped_ratios_are_based_on_group_totals(self):
        rows = pd.DataFrame({
            "platform": ["A", "A"], "spend": [10.0, 90.0], "revenue": [20.0, 90.0],
            "orders": [1, 9], "clicks": [10, 90], "impressions": [100, 900],
            "refunds": [0.0, 0.0], "discounts": [0.0, 0.0],
            "product_cost": [5.0, 45.0], "shipping_cost": [2.0, 18.0],
        })
        result = grouped_metrics(rows, ["platform"]).iloc[0]
        self.assertAlmostEqual(result["roas"], 1.1)
        self.assertAlmostEqual(result["click_to_order_rate"], 0.1)

    def test_time_series_chart_respects_selected_metrics(self):
        frame = self.campaign_rows()
        chart = trend_chart(frame, metrics=["orders"])
        self.assertEqual(len(chart.data), 1)
        self.assertEqual(chart.data[0].name, "Orders")

    def test_legacy_conversions_column_is_accepted_as_orders(self):
        csv = StringIO("date,platform,campaign,spend,impressions,clicks,conversions,revenue\n2026-01-01,A,B,10,100,5,2,25\n")
        frame = load_campaign_data(csv)
        self.assertEqual(frame.loc[0, "orders"], 2)

    def test_prior_period_uses_equal_days_and_shared_dimensions(self):
        frame = self.campaign_rows()
        start, end = pd.Timestamp("2026-08-04").date(), pd.Timestamp("2026-08-05").date()
        selections = {
            "start": start, "end": end,
            "platform": sorted(frame["platform"].unique()), "campaign": sorted(frame["campaign"].unique()),
            "product": sorted(frame["product"].unique()), "region": sorted(frame["region"].unique()),
            "device": sorted(frame["device"].unique()), "currency": ["USD"],
        }
        current, previous, previous_range = compare_with_previous_period(
            frame, frame[frame["date"].dt.date.between(start, end)], selections
        )
        self.assertEqual(previous_range, (pd.Timestamp("2026-08-02").date(), pd.Timestamp("2026-08-03").date()))
        self.assertGreater(current["spend"], 0)
        self.assertGreater(previous["spend"], 0)

    def test_shared_filter_function_applies_dimensions_and_currency(self):
        frame = self.campaign_rows()
        selected = {
            "start": pd.Timestamp("2026-08-01").date(), "end": pd.Timestamp("2026-08-03").date(),
            "platform": ["Google Ads"], "campaign": sorted(frame["campaign"].unique()),
            "product": sorted(frame["product"].unique()), "region": sorted(frame["region"].unique()),
            "device": sorted(frame["device"].unique()), "currency": ["USD"],
        }
        result = filter_rows(frame, selected)
        self.assertTrue((result["platform"] == "Google Ads").all())
        self.assertTrue(result["date"].dt.date.between(selected["start"], selected["end"]).all())

    def test_missing_required_csv_columns_are_reported(self):
        csv = StringIO("date,platform,campaign\n2026-01-01,A,B\n")
        with self.assertRaisesRegex(ValueError, "missing required columns"):
            load_campaign_data(csv)


if __name__ == "__main__":
    unittest.main()
