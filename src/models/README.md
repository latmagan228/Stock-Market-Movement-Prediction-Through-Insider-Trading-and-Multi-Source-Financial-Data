# 🤖 Models Module

This directory contains the Machine Learning models for predicting stock alpha based on insider trading activity.

## 🎯 Approach: Classification (Not Regression)

**Why Classification?** Initial regression experiments yielded R² ≈ -17, indicating that predicting exact return values is infeasible due to:
1. **Extreme outliers** distorting the loss function
2. **Low signal-to-noise ratio** in financial data
3. **Random market movements** dominating short-term returns

**Classification Strategy:** Predict whether a trade will generate "High Alpha" (>5%) or should be skipped.

## 📊 Model Architecture

### Target Variable
- **Binary classification**: `alpha_3m > 5%` → Class 1 ("High Alpha")
- **Class distribution**: ~37% positive, ~63% negative

### Features (13 total)
| Category | Features |
|----------|----------|
| Insider | `role_bucket`, `insider_trade_count`, `days_since_last_trade` |
| Transaction | `log_transaction_value`, `delta_owned`, `owned_pct_change` |
| Timing | `reporting_lag` |
| Cluster | `cluster_buy`, `cluster_c_level_pct` |
| Fundamental | `log_market_cap`, `sector` |
| Technical | `price_range_position`, `volatility_30d` |

### Models Implemented
1. **XGBoost Classifier** - Gradient boosting with Optuna hyperparameter tuning
2. **CatBoost Classifier** - Native categorical handling for sector feature
3. **LightGBM Classifier** - Fast training with balanced class weights

### Validation Strategy
- **Temporal split** (NOT random) to prevent look-ahead bias
- **Train**: 2018-2023 (~36,000 samples)
- **Test**: 2024+ (~6,000 samples)
- **Cross-validation**: TimeSeriesSplit (3 folds) during Optuna tuning

## 📥 Input Data

| File | Description |
|------|-------------|
| `data/processed/insider_trades_ml_ready.parquet` | 42,015 records × 23 columns |

## 📤 Output Artifacts

| File | Description |
|------|-------------|
| `saved_models/xgb_classifier.joblib` | Trained XGBoost model |
| `saved_models/catboost_classifier.joblib` | Trained CatBoost model |
| `saved_models/lgb_classifier.joblib` | Trained LightGBM model |
| `saved_models/sector_label_encoder.joblib` | Label encoder for sector |
| `saved_models/feature_config.json` | Feature configuration |

## 📈 Evaluation Metrics

| Metric | Purpose |
|--------|----------|
| **ROC-AUC** | Primary metric - ranking ability |
| **Average Precision** | Precision-recall trade-off |
| **Alpha by Probability Decile** | Does high probability → high alpha? |
| **Backtest Returns** | Simulated trading strategy performance |

