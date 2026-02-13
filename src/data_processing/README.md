# ⚙️ Data Processing Module

This module aims to transform raw insider trading data into a structured dataset ready for Machine Learning models.

## 🎯 Objectives
1. **Cleaning**: Remove duplicate transactions and standardize formats.
2. **Feature Engineering**: Create predictive features (e.g., historical returns, insider track record).
3. **Labeling**: define the target variable (e.g., Stock Return > 0 in next 1 month).

## 📄 Dataset Design
Refer to **[dataset_design.md](dataset_design.md)** for the detailed schema specification of the final dataset.

## 🔄 Workflow
1. **[01_data_cleaning.ipynb](01_data_cleaning.ipynb)**: Data cleaning and basic feature engineering.
   - **Input**: Raw data from `data/raw/`
   - **Output**: `data/processed/insider_trades_processed.parquet`
   - **Features**: `insider_role`, `delta_owned`, `reporting_lag`, `is_c_level`, `cluster_buy`

2. **[02_tiingo_integration.ipynb](02_tiingo_integration.ipynb)**: Fetch and cache market data + diagnostics.
   - **Input**: Processed insider trades
   - **Data Source**: Tiingo API (historical prices)
   - **Output**: 
     - Cached price data in `data/tiingo_cache/{TICKER}.parquet`
     - `data/processed/insider_trades_with_targets.parquet` (with returns)
   - **Diagnostics**:
     - Active tickers: 3,855 (76.2%)
     - Stale tickers: 119 (2.4%)
     - Delisted tickers: 1,086 (21.5%) - **kept** to avoid survivorship bias
     - No data tickers: 456 - **removed** (3,211 transactions, 7.1%)
   - **⚡ Cache**: 530 MB, 5,063 tickers cached
   - **Final**: 42,015 transactions

3. **[03_feature_engineering.ipynb](03_feature_engineering.ipynb)**: Complete feature engineering
   - **Input**: `data/processed/insider_trades_with_targets.parquet`
   - **Output**: `data/processed/insider_trades_ml_ready.parquet` (ML-ready)
   - **Part 1 - Basic Features**:
     - `insider_id`: Unique identifier (ticker + role)
     - `insider_trade_count`: Insider's track record
     - `days_since_last_trade`: Trading frequency
     - `cluster_c_level_pct`: Cluster quality (% C-levels)
   - **Part 2 - Advanced Features**:
     - **Alpha Targets**: `alpha_1w`, `alpha_1m`, `alpha_3m`, `benchmark_used`
     - **Fundamentals**: `sector` (78.5% coverage), `log_market_cap`
     - **Technicals**: `price_range_position` (97.1%), `volatility_30d` (94.1%)
     - **Refined**: `role_bucket`, `log_transaction_value`
   - **Outlier Capping**: Returns -100%/+300%, Alpha -150%/+300%
   - **Benchmark Distribution**: IWM 67%, IWV 21.3%, SPY 11.6%
   - **⚡ Fast**: < 2 minutes (local calculations + yfinance)
   - **Final dataset**: 42,015 records × **23 columns** (optimized)

4. **[visualizations/paper_visualizations.ipynb](visualizations/paper_visualizations.ipynb)**: Academic paper visualizations and backtest analysis
   - **Input**: `data/processed/insider_trades_ml_ready.parquet` + saved models
   - **Paper Figures & Tables**:
     - **Figure 2**: Correlation heatmap (features vs targets)
     - **Figure 3**: Price range position vs alpha scatter plot with trend line
     - **Figure 4**: Role bucket distribution (insider hierarchy)
     - **Figure 5**: Return vs Alpha distribution comparison (2×3 histogram grid)
     - **Figure 6**: Sector distribution bar chart
     - **Table 1**: Complete feature list with coverage percentages
     - **Table 2**: Return vs Alpha statistics by horizon
     - **Table 3**: Model performance comparison (LightGBM, XGBoost, CatBoost)
   - **Backtest Analysis** (Calendar-Time Portfolio methodology):
     - **Figure 7**: CTP cumulative net return curves by threshold
     - **Figure 8**: Drawdown underwater plot
     - Trade-level signal quality analysis
     - Position sizing comparison (equal-weight, prob-weighted, vol-scaled)
     - Walk-forward quarterly evaluation with dual bar charts
     - Sensitivity analysis heatmaps (threshold × max positions)
     - Diagnostic analysis (Figure 5 vs backtest discrepancy explanation)
   - **Key Results**:
     - Baseline (all trades): -2.1% cumulative return
     - Model @ 0.5 threshold: +12.3% cumulative, Sharpe 1.98
     - Model @ 0.6 threshold: +47.4% cumulative, Sharpe 5.14
     - Realistic transaction costs: 10 bps round-trip + 5 bps slippage
     - 13-week holding period matching prediction target

## 📦 Tiingo Integration

The module uses `tiingo_client.py` for intelligent data fetching:
- **Persistent cache**: Data stored in `data/tiingo_cache/` (Parquet format)
- **Incremental updates**: Only fetches missing date ranges
- **Rate limiting**: Respects API limits (configurable)
- **Retry logic**: Automatic retries with exponential backoff
- **Delisted detection**: Skips API calls for likely delisted stocks (gap > 30 days)