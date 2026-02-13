# 📊 Academic Paper Visualizations

This module generates all figures, tables, and backtest analysis for the academic paper **"Stock Market Movement Prediction Through Insider Trading and Multi-Source Financial Data: A Machine Learning Approach"**.

## 📓 Notebook: `paper_visualizations.ipynb`

A comprehensive notebook that produces publication-ready visualizations and rigorous backtest analysis using the Calendar-Time Portfolio (CTP) methodology.

### 📈 Figures

| Figure | Description | Purpose |
|--------|-------------|---------|
| **Figure 2** | Correlation Heatmap | Shows relationships between engineered features and target variables (returns/alpha) |
| **Figure 3** | Price Range vs Alpha Scatter | Examines whether insiders purchasing near 52-week lows achieve superior alpha (includes trend line) |
| **Figure 4** | Role Bucket Distribution | Distribution of transactions by insider hierarchy (C-level, Senior Management, Directors, Other) |
| **Figure 5** | Return vs Alpha Distribution (2×3 grid) | Demonstrates the effect of market correction on return distributions across 1w/1m/3m horizons |
| **Figure 6** | Sector Distribution | Bar chart showing transaction distribution across economic sectors (ensures dataset diversity) |
| **Figure 7** | CTP Cumulative Return Curves | Shows portfolio equity curves over time by probability threshold |
| **Figure 8** | Drawdown Underwater Plot | Visualizes portfolio drawdowns per threshold to assess risk |

### 📋 Tables

| Table | Description | Key Insights |
|-------|-------------|--------------|
| **Table 1** | Complete Feature List | 23 features with coverage percentages, data types, and descriptions across 7 categories |
| **Table 2** | Return vs Alpha Statistics | Mean return/alpha by horizon (1w/1m/3m) showing the effect of benchmark correction |
| **Table 3** | Model Performance Comparison | ROC-AUC, Precision, Recall, F1 for LightGBM (0.5640), XGBoost (0.5613), CatBoost (0.5601) |

### 🔬 Backtest Analysis (Calendar-Time Portfolio)

The notebook implements the academic-standard **Calendar-Time Portfolio (CTP)** methodology to evaluate the trading strategy:

#### Methodology
- **Holding Period**: 13 weeks (≈3 months), matching the model's prediction target
- **Alpha Decomposition**: Each trade's `alpha_3m` is spread geometrically over 13 weeks: `weekly_alpha = (1 + alpha_3m)^(1/13) - 1`
- **Transaction Costs**: 10 bps round-trip + 5 bps slippage (realistic)
- **Capacity Constraint**: Max 30 new positions per week
- **Ticker Deduplication**: One position per stock per week
- **No Look-Ahead Bias**: Strict temporal split (train ≤ 2023, test ≥ 2024)

#### Key Results

| Strategy | Cumulative Return | Sharpe Ratio | Max Drawdown | Trades |
|----------|-------------------|--------------|--------------|--------|
| **Baseline** (no model) | **-2.1%** | -0.66 | -4.1% | 2,770 |
| **Model ≥ 0.50** | **+12.3%** | **1.98** | -2.7% | 2,413 |
| **Model ≥ 0.60** | **+47.4%** | **5.14** | -7.7% | 351 |

**Critical Finding**: Blindly following insider trades **loses money** (baseline -2.1%). The ML model's value is in filtering for profitable trades.

#### Additional Analyses

1. **Trade-Level Signal Quality**: Mean/median alpha by threshold, hit rates
2. **Position Sizing Comparison**: Equal-weight, probability-proportional, volatility-scaled (all identical due to ~306 active positions)
3. **Walk-Forward Quarterly Evaluation**: Tests strategy stability across different market regimes (positive alpha every quarter)
4. **Sensitivity Analysis**: Grid search over thresholds (0.3-0.6) × max positions (10, 20, 30, 50)
5. **Figure 5 Diagnostic**: Explains why Figure 5 shows positive mean alpha while backtest shows negative median (fat right tail analysis)

### 🎯 Why CTP? 

The CTP approach is superior to naive alpha compounding because:

1. **Overlapping Positions**: Insider trades naturally overlap in time (one purchase may span weeks 1-13 while another spans weeks 3-16)
2. **Realistic Holding Periods**: 13 weeks matches the model's actual prediction horizon
3. **Avoids Alpha Inconsistency**: Raw `alpha_1w` captures a post-filing spike that reverses, making weekly compounding unreliable
4. **Academic Standard**: CTP is the accepted methodology in finance research for event-driven strategies

### 📊 Diagnostic Insights

The notebook includes a diagnostic cell that explains a key discrepancy:
- **Figure 5** shows mean alpha_3m = +2.09% (positive)
- **Backtest** shows median alpha_3m = -2.53% (negative)

**Explanation**: The distribution is right-skewed. 8.3% of trades have |alpha| > 50%, creating a fat right tail that pulls the mean positive while the majority of trades lose money. Figure 5 only shows the mean (red line) and clips at ±50%, concealing this asymmetry.

## 🚀 Usage

1. **Prerequisites**: 
   - Run all three data processing notebooks first (01, 02, 03)
   - Train ML models using `src/models/model_training.ipynb`
   - Ensure saved models exist in `src/models/saved_models/`

2. **Run the Notebook**:
   ```bash
   jupyter notebook src/data_processing/visualizations/paper_visualizations.ipynb
   ```

3. **Execute All Cells**: The notebook is designed to run top-to-bottom. Expected runtime: ~2-3 minutes on a standard laptop.

## 📤 Outputs

All visualizations are displayed inline in the notebook. For the academic paper, capture figures using:
- Jupyter's "Save Figure As" (right-click on plot)
- Or use `plt.savefig()` to export to PDF/PNG

Tables are formatted for direct inclusion in LaTeX/Markdown documents (bordered console output).

