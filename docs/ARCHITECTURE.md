# Architecture Documentation

## Overview
The Product Intelligence Platform implements **Clean Architecture** to ensure maintainability, scalability, and strict separation of concerns. The system is designed to process e-commerce transaction data and surface executive insights regarding customer retention.

## Layers
1. **Presentation Layer (`presentation/`)**: Streamlit application, split into pages and components. Responsible only for UI rendering.
2. **Use Case Layer (`use_cases/`)**: Encapsulates all business logic (Customer Analytics, Retention Analytics).
3. **Adapter Layer (`adapters/`)**: Bridges the use cases with external systems (SQLite Database, Plotly Services).
4. **Core Domain (`core/`)**: Business rules and entities (e.g., `business_rules.py`).

## Database
- **SQLite**: chosen for minimal dependency and immediate local deployment.
- Data logic is extracted into pure SQL (`sql/`) for reusability.
