# 📈 OpenInsider Intelligent Prediction Project

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)

An end-to-end Machine Learning project designed to predict stock market movements based on insider trading data collected from [OpenInsider](http://openinsider.com).

## 🏗️ Project Structure

This project is organized into three main stages:

1.  **[Data Collection](src/data_collection/README.md)**: robust web scraper to harvest historical insider data.
2.  **[Data Processing](src/data_processing/README.md)**: pipelines to clean, structure, and engineer features from the raw data.
3.  **[Models](src/models/README.md)**: development and training of predictive value models.

```text
openinsiderData/
├── config/                 # Global configuration files
├── data/
│   ├── raw/               # Scraped data storage
│   └── processed/         # Feature-engineered training data
├── src/
│   ├── data_collection/    # Scraper source code
│   ├── data_processing/    # ETL and Feature Engineering pipeline
│   └── models/             # Machine Learning models
└── venv/                   # Python Virtual Environment
```

## 🚀 Getting Started

### 1. Installation

1.  Clone the repository:
    ```bash
    git clone git@github.com:sd3v/openinsiderData.git
    cd openinsiderData
    ```

2.  Create and activate the virtual environment:
    ```bash
    python3.11 -m venv venv
    source venv/bin/activate
    ```

3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4.  Configure Tiingo API:
    # Edit .env and add your Tiingo API key

    Get your free API key at [tiingo.com](https://www.tiingo.com)
    
    Tiingo is used for historical stock prices only.

### 2. Usage

#### Step 1: Collect Insider Trading Data

**Data Collection Parameters:**
- **Time Range**: 2018-2025 (8 years of historical data)
- **Transaction Type**: Purchases only (insider buying signals)
- **Quality Filter**: Minimum $50,000 transaction value
  - Eliminates ~51% noise (small/automatic transactions)
  - Keeps ~41,000 high-quality transactions

Run the data collector:

```bash
python src/data_collection/scraper.py
```

#### Step 2: Process and Enrich Data
Open the Jupyter notebooks in `src/data_processing/` (execute in order):
1. **01_data_cleaning.ipynb**: Clean and engineer base features from insider data
2. **02_tiingo_integration.ipynb**: Fetch market data and calculate target returns (1w, 1m, 3m)
3. **03_feature_engineering.ipynb**: Add advanced features (insider track record, cluster quality, etc.)
4. **04_advanced_features.ipynb**:  Market-corrected alpha & optimization
   - Corrects market bias using hybrid benchmarks (SPY/IWM/IWV via Tiingo)
   - Adds fundamental data (market_cap, sector) via yfinance

**Expected Output:**
- **45,242 transactions** with **25 features** (optimized, no redundancy)
- **ML-ready dataset**: `insider_trades_ml_ready.parquet`

*For detailed instructions on each module, please refer to their respective READMEs linking in the Project Structure section above.*

## ⚙️ Configuration

Global settings (scraping speed, filters, paths) are managed in:
`config/config.yaml`

## 🔍 Troubleshooting

- If you encounter rate limiting, adjust the `max_workers` setting
- For memory issues, try using Parquet format for large datasets
- Check the log file for detailed error messages
