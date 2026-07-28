# Technical Documentation

## Design Patterns Used
- **Repository/Adapter Pattern**: `AnalyticsService` abstracts SQL execution.
- **Controller Pattern**: `DashboardBackend` acts as a facade connecting Streamlit to multiple Use Cases.
- **Factory Pattern**: `PlotlyService` centralizes chart generation.

## Performance Optimization
- Heavily relies on `@st.cache_data` to cache DataFrame results from SQLite.
- SQL aggregates (CTEs) are used instead of Pandas transformations to minimize memory overhead.

## Data Quality
- `DataPreprocessor` and `DataValidator` modules handle null values and enforce schemas before analysis.
