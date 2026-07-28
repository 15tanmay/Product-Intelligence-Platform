# Installation Guide

## Requirements
- Python 3.9+
- Kaggle Account (for data download)

## Setup
1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/product_intelligence.git
   cd product_intelligence
   ```
2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Download Data:**
   Place the Kaggle Olist Dataset CSV files into `data/raw/`.
5. **Initialize Database:**
   ```bash
   python data_loading/loader.py
   ```
6. **Run Dashboard:**
   ```bash
   streamlit run presentation/app.py
   ```
