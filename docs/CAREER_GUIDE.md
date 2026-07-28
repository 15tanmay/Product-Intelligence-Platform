# Career & Portfolio Guide

## Resume Bullets
- **Architected a Product Intelligence Platform** using Python and Clean Architecture, processing over 100k e-commerce transactions to identify drivers of customer churn.
- **Engineered an automated analytics pipeline** with SQLite, abstracting complex SQL cohorts and RFM segmentation models behind a scalable Facade layer.
- **Developed an interactive executive dashboard** utilizing Streamlit and Plotly, caching aggregated queries to achieve sub-second load times for business KPIs.

## Interview Questions & Answers
**Q: Why did you choose SQLite over PostgreSQL?**
*A: For an internal decision-support MVP, SQLite provides zero-configuration deployment. By using the Adapter pattern (`AnalyticsService`), migrating to Postgres later requires zero changes to the core business logic.*

**Q: How did you optimize the dashboard performance?**
*A: I pushed heavy aggregations (like Cohort Analysis) down to the SQL engine rather than doing it in Pandas, and implemented Streamlit's `@st.cache_data` to memoize the resulting datasets.*

## GitHub Optimization
- Ensure `README.md` has a GIF of the Streamlit dashboard running.
- Add architecture diagrams.
- Tag repository with: `product-analytics`, `clean-architecture`, `streamlit`, `rfm-segmentation`.

## Portfolio & Recruiter Review
- **Strengths**: Highly structured, production-ready code. Shows deep understanding of software engineering applied to data, rather than just "notebook data science."
- **Feedback**: Outstanding encapsulation. Ready for technical review by Staff-level engineers.
