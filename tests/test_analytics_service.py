import unittest
from unittest.mock import patch
import pandas as pd
from adapters.analytics_service import AnalyticsService, DatabaseError

class TestAnalyticsService(unittest.TestCase):
    @patch('adapters.analytics_service.get_connection')
    @patch('adapters.analytics_service.pd.read_sql_query')
    def test_execute_query_success(self, mock_read_sql, mock_get_conn):
        mock_df = pd.DataFrame({'a': [1]})
        mock_read_sql.return_value = mock_df
        
        result = AnalyticsService.execute_query("SELECT * FROM test")
        
        self.assertTrue(result.equals(mock_df))
        mock_read_sql.assert_called_once()
        mock_get_conn.assert_called_once()

    @patch('adapters.analytics_service.get_connection')
    def test_execute_query_failure(self, mock_get_conn):
        mock_get_conn.side_effect = Exception("DB Connection Failed")
        
        with self.assertRaises(DatabaseError):
            AnalyticsService.execute_query("SELECT * FROM test")
