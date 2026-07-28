import unittest
import pandas as pd
from validation.validator import DataValidator
from core.business_rules import BusinessRules

class TestAnalytics(unittest.TestCase):
    def test_schema_validation(self):
        df = pd.DataFrame({'a': [1], 'b': [2]})
        self.assertTrue(DataValidator.validate_schema(df, ['a', 'b']))
        self.assertFalse(DataValidator.validate_schema(df, ['c']))

    def test_business_rules(self):
        self.assertEqual(BusinessRules.CHURN_THRESHOLD_DAYS, 180)

if __name__ == '__main__':
    unittest.main()
