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
│   ├── processed/         # Feature-engineered training data
│   └── tiingo_cache/      # Cached market data from Tiingo API
├── src/
│   ├── data_collection/    # Scraper source code
│   ├── data_processing/    # ETL, Feature Engineering & Visualizations
│   │   └── visualizations/ # Paper visualizations and backtest analysis
│   └── models/             # Machine Learning models and saved artifacts
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
2. **02_tiingo_integration.ipynb**: Fetch market data, calculate returns, and diagnose ticker quality
3. **03_feature_engineering.ipynb**: Complete feature engineering 
   - Basic features: insider track record, cluster quality, trading frequency
   - Alpha targets: Market-corrected alpha (SPY/IWM/IWV benchmarks via Tiingo)
   - Fundamental data: market_cap, sector via yfinance
   - Technical features: price_range_position, volatility_30d
   - Outlier capping: Returns -100%/+300%, Alpha -150%/+300%

**Expected Output:**
- **42,015 transactions** with **23 features** (optimized, no redundancy)
- **Benchmark distribution**: IWM 67%, IWV 21.3%, SPY 11.6%
- **ML-ready dataset**: `insider_trades_ml_ready.parquet` (3.95 MB)
- **Tiingo cache**: 5,063 tickers, 530 MB

#### Step 3: Train Machine Learning Models
Open `src/models/model_training.ipynb` to:
1. **Split data**: Train on 2018-2023 (~35K samples), test on 2024+ (7,773 trades)
2. **Train three models**: LightGBM, XGBoost, and CatBoost with Optuna hyperparameter optimization
3. **Evaluate performance**: ROC-AUC, precision-recall curves, calibration analysis
4. **Save artifacts**: Best model, feature configuration, and probability predictions

**Model Configuration:**
- **Target**: Binary classification (alpha_3m > 5%)
- **Optimization**: 50 Optuna trials maximizing ROC-AUC
- **Features**: 13 numerical + 1 categorical (sector)
- **Output**: Trained models in `src/models/saved_models/`

#### Step 4: Generate Paper Visualizations
Open `src/data_processing/visualizations/paper_visualizations.ipynb` for thesis-ready outputs:


*For detailed instructions on each module, please refer to their respective READMEs linked in the Project Structure section above.*

## ⚙️ Configuration

Global settings (scraping speed, filters, paths) are managed in:
`config/config.yaml`

## 🔍 Troubleshooting

- If you encounter rate limiting, adjust the `max_workers` setting
- For memory issues, try using Parquet format for large datasets
- Check the log file for detailed error messages
