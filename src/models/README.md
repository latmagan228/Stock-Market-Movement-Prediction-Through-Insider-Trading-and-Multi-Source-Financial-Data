# 🤖 Models Module

This directory contains the Machine Learning models for predicting stock alpha based on insider trading activity.

## 🎯 Approach: Classification (Not Regression)

**Why Classification?** Initial regression experiments yielded R² ≈ -17, indicating that predicting exact return values is infeasible due to:
1. **Extreme outliers** distorting the loss function
2. **Low signal-to-noise ratio** in financial data
3. **Random market movements** dominating short-term returns

**Classification Strategy:** Predict whether a trade will generate alpha above a given threshold, or should be skipped.

## 📊 Multi-Horizon Results

Best hyperparameters were found via Optuna (50 trials, 3-fold TimeSeriesSplit CV) and are hardcoded in `model_training.ipynb` for reproducibility.

| Horizon | Target | Threshold | Best Model | Test ROC-AUC |
|---------|--------|-----------|------------|--------------|
| 1 week  | `alpha_1w` | 2% | CatBoost | **0.6110** |
| 1 month | `alpha_1m` | 3% | CatBoost | **0.5695** |
| 3 months| `alpha_3m` | 5% | LightGBM | **0.5640** |

Switch horizons by changing `ACTIVE_HORIZON` in the notebook's config cell.

### Features (13 total)
| Category | Features |
|----------|----------|
| Insider | `role_bucket`, `insider_trade_count`, `days_since_last_trade` |
| Transaction | `log_transaction_value`, `delta_owned`, `owned_pct_change` |
| Timing | `reporting_lag` |
| Cluster | `cluster_buy`, `cluster_c_level_pct` |
| Fundamental | `log_market_cap`, `sector` |
| Technical | `price_range_position`, `volatility_30d` |

### Models Trained
1. **XGBoost Classifier** — Gradient boosting
2. **CatBoost Classifier** — Native categorical handling for sector
3. **LightGBM Classifier** — Fast training with balanced class weights

### Validation Strategy
- **Temporal split** (NOT random) to prevent look-ahead bias
- **Train**: 2018-2023 (~31,600 samples)
- **Test**: 2024+ (~7,700 samples)

## 📥 Input Data

| File | Description |
|------|-------------|
| `data/processed/insider_trades_ml_ready.parquet` | 42,015 records × 23 columns |

## 📤 Output Artifacts

| File | Description |
|------|-------------|
| `saved_models/xgb_classifier.joblib` | Trained XGBoost model |
| `saved_models/catboost_classifier.joblib` | Trained CatBoost model |
| `saved_models/lgb_classifier.joblib` | Trained LightGBM model (production best) |
| `saved_models/sector_label_encoder.joblib` | Label encoder for sector |
| `saved_models/feature_config.json` | Feature schema, horizon & threshold metadata |

## 📈 Evaluation Metrics

| Metric | Purpose |
|--------|----------|
| **ROC-AUC** | Primary metric — ranking ability |
| **Average Precision** | Precision-recall trade-off |
| **Alpha by Probability Decile** | Does high probability → high alpha? |
| **Backtest Returns** | Simulated trading strategy performance |

## 🏭 Production Model

**Horizon**: alpha_3m (3-month market-corrected alpha > 5%)  
**Best model**: LightGBM (ROC-AUC 0.5633)  
**Use case**: Real-time monitoring system to identify promising insider trading opportunities

## 📁 Directory Structure

```
src/models/
├── model_training.ipynb          # Train all 3 models with best hyperparameters
├── README.md                     # This file
└── saved_models/
    ├── xgb_classifier.joblib     # Trained XGBoost (alpha_3m)
    ├── lgb_classifier.joblib     # Trained LightGBM (alpha_3m) ← production
    ├── catboost_classifier.joblib# Trained CatBoost (alpha_3m)
    ├── sector_label_encoder.joblib
    └── feature_config.json       # Feature schema + target config
```

