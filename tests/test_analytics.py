"""Core unit tests for DataValidator and BusinessRules."""
import unittest
import pandas as pd
from validation.validator import DataValidator
from core.business_rules import BusinessRules


class TestDataValidator(unittest.TestCase):

    def test_validate_schema_success(self) -> None:
        df = pd.DataFrame({"a": [1], "b": [2]})
        self.assertTrue(DataValidator.validate_schema(df, ["a", "b"]))

    def test_validate_schema_failure(self) -> None:
        df = pd.DataFrame({"a": [1], "b": [2]})
        self.assertFalse(DataValidator.validate_schema(df, ["c"]))

    def test_check_nulls_below_threshold(self) -> None:
        df = pd.DataFrame({"price": [1.0, 2.0, None]})
        # 33 % nulls — exceeds 0.0 threshold for 'price' in NULL_THRESHOLDS
        self.assertFalse(DataValidator.check_nulls(df, "price"))

    def test_check_nulls_review_comment_allowed(self) -> None:
        # review_comment_message has threshold 1.0 (all nulls allowed)
        df = pd.DataFrame({"review_comment_message": [None, None, None]})
        self.assertTrue(DataValidator.check_nulls(df, "review_comment_message"))

    def test_check_primary_key_uniqueness_clean(self) -> None:
        df = pd.DataFrame({"order_id": ["o1", "o2"], "item": [1, 1]})
        self.assertTrue(DataValidator.check_primary_key_uniqueness(df, ["order_id"]))

    def test_check_primary_key_uniqueness_duplicate(self) -> None:
        df = pd.DataFrame({"order_id": ["o1", "o1"], "item": [1, 1]})
        self.assertFalse(DataValidator.check_primary_key_uniqueness(df, ["order_id"]))

    def test_validate_table_customers(self) -> None:
        df = pd.DataFrame({
            "customer_id": ["c1"],
            "customer_unique_id": ["u1"],
            "customer_zip_code_prefix": ["01000"],
            "customer_city": ["São Paulo"],
            "customer_state": ["SP"],
        })
        self.assertTrue(DataValidator.validate_table(df, "customers"))

    def test_validate_table_missing_columns(self) -> None:
        df = pd.DataFrame({"customer_id": ["c1"]})  # missing required cols
        self.assertFalse(DataValidator.validate_table(df, "customers"))


class TestBusinessRules(unittest.TestCase):

    def test_churn_threshold(self) -> None:
        self.assertEqual(BusinessRules.CHURN_THRESHOLD_DAYS, 180)


if __name__ == "__main__":
    unittest.main()
