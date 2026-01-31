# ⚙️ Data Processing Module

This module aims to transform raw insider trading data into a structured dataset ready for Machine Learning models.

## 🎯 Objectives
1. **Cleaning**: Remove duplicate transactions and standardize formats.
2. **Feature Engineering**: Create predictive features (e.g., historical returns, insider track record).
3. **Labeling**: define the target variable (e.g., Stock Return > 0 in next 1 month).

## 📄 Dataset Design
Refer to **[dataset_design.md](dataset_design.md)** for the detailed schema specification of the final dataset.

## 🔄 Workflow
1. **[01_data_cleaning.ipynb](01_data_cleaning.ipynb)**: Interactive data cleaning and basic feature engineering.
   - **Input**: Raw data from `data/raw/`
   - **Output**: `data/processed/insider_trades_processed.parquet`
   - **Features**: `insider_role`, `delta_owned`, `reporting_lag`, `is_c_level`, `cluster_buy`

2. **[02_tiingo_integration.ipynb](02_tiingo_integration.ipynb)**: Fetch and cache market data.
   - **Input**: Processed insider trades
   - **Data Source**: Tiingo API (historical prices only)
   - **Output**: 
     - Cached price data in `data/tiingo_cache/{TICKER}.parquet`
     - `data/processed/insider_trades_with_targets.parquet` (with returns)
   - **⚡ Cache**: Segunda ejecución es instantánea

3. **[03_feature_engineering.ipynb](03_feature_engineering.ipynb)**: Advanced feature engineering.
   - **Input**: `data/processed/insider_trades_with_targets.parquet`
   - **Output**: `data/processed/insider_trades_final.parquet`
   - **Features added** (high-importance only):
     - `insider_id`: Unique identifier (ticker + role)
     - `insider_trade_count`: Insider's track record (# previous trades)
     - `days_since_last_trade`: Trading frequency indicator
     - `trade_day_of_week`: Trade timing (0=Monday, 4=Friday)
     - `cluster_c_level_pct`: Cluster quality (% of C-levels)
   - **⚡ Fast**: < 1 minute (local calculations only)
   - **Final dataset**: 45,242 records × 19 columns

4. **Calculate Targets**: Use notebook 02 to calculate returns for all data after enrichment.

## 📦 Tiingo Integration

The module uses `tiingo_client.py` for intelligent data fetching:
- **Persistent cache**: Data stored in `data/tiingo_cache/` (Parquet format)
- **Incremental updates**: Only fetches missing date ranges
- **Rate limiting**: Respects API limits (configurable)
- **Retry logic**: Automatic retries with exponential backoff
