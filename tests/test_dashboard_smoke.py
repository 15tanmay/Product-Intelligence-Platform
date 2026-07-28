"""Dashboard smoke tests using Streamlit's AppTest framework.

Note: Requires streamlit >= 1.28.0 with a compatible starlette version.
If the import fails (e.g. starlette version mismatch), tests are skipped
with a clear message rather than raising an ImportError at collection time.
"""
import os
import unittest

try:
    from streamlit.testing.v1 import AppTest
    _STREAMLIT_AVAILABLE = True
except (ImportError, Exception) as _st_exc:
    _STREAMLIT_AVAILABLE = False
    _STREAMLIT_ERROR = str(_st_exc)


@unittest.skipUnless(
    _STREAMLIT_AVAILABLE,
    f"streamlit.testing.v1 unavailable: {'' if _STREAMLIT_AVAILABLE else _STREAMLIT_ERROR}",  # type: ignore[name-defined]
)
class TestDashboardSmoke(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"

    def test_app_loads(self) -> None:
        at = AppTest.from_file("t:/product/presentation/app.py").run()
        self.assertFalse(at.exception)

    def test_home_page_loads(self) -> None:
        at = AppTest.from_file("t:/product/presentation/pages/1_Home.py").run()
        self.assertFalse(at.exception)

    def test_executive_summary_loads(self) -> None:
        at = AppTest.from_file(
            "t:/product/presentation/pages/2_Executive_Summary.py"
        ).run()
        self.assertFalse(at.exception)


if __name__ == "__main__":
    unittest.main()
