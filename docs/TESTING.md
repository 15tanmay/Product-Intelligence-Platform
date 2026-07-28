# Testing Guide

## Strategy
Tests are isolated in the `tests/` directory and use Python's built-in `unittest` framework to adhere to the "minimal dependencies" constraint.

## Running Tests
```bash
python -m unittest discover -s tests
```

## Coverage Areas
- **Data Validation**: Ensures incoming DataFrames meet schema expectations.
- **Business Rules**: Validates core constants (e.g., Churn Threshold).
- *Future iterations should include mock DB connections to test Analytics Services.*
