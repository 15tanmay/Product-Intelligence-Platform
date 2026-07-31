"""Tests for AnalyticsService adapter.

These tests use mocking to verify that AnalyticsService correctly delegates
to get_connection() and pd.read_sql_query, and that DatabaseError is raised
on connection failure.
"""
import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from adapters.analytics_service import AnalyticsService, DatabaseError


class TestAnalyticsService(unittest.TestCase):

    def setUp(self) -> None:
        self.service = AnalyticsService()

    @patch("adapters.analytics_service.pd.read_sql_query")
    @patch("adapters.analytics_service.get_connection")
    def test_execute_query_success(
        self, mock_get_conn: MagicMock, mock_read_sql: MagicMock
    ) -> None:
        """execute_query returns the DataFrame produced by read_sql_query."""
        expected = pd.DataFrame({"a": [1]})
        mock_read_sql.return_value = expected
        mock_get_conn.return_value.__enter__ = lambda s: s
        mock_get_conn.return_value.__exit__ = MagicMock(return_value=False)

        result = self.service.execute_query("SELECT * FROM test")

        self.assertTrue(result.equals(expected))
        mock_read_sql.assert_called_once()
        mock_get_conn.assert_called_once()

    @patch("adapters.analytics_service.get_connection")
    def test_execute_query_failure(self, mock_get_conn: MagicMock) -> None:
        """execute_query raises DatabaseError when connection fails."""
        mock_get_conn.side_effect = Exception("DB Connection Failed")

        with self.assertRaises(DatabaseError):
            self.service.execute_query("SELECT * FROM test")

    @patch("adapters.analytics_service.pd.read_sql_query")
    @patch("adapters.analytics_service.get_connection")
    def test_execute_query_with_params(
        self, mock_get_conn: MagicMock, mock_read_sql: MagicMock
    ) -> None:
        """execute_query passes params through to read_sql_query."""
        mock_read_sql.return_value = pd.DataFrame({"x": [42]})
        mock_get_conn.return_value.__enter__ = lambda s: s
        mock_get_conn.return_value.__exit__ = MagicMock(return_value=False)

        self.service.execute_query("SELECT * FROM t WHERE id = ?", ("abc",))

        _, call_kwargs = mock_read_sql.call_args
        self.assertEqual(call_kwargs.get("params"), ("abc",))


if __name__ == "__main__":
    unittest.main()
