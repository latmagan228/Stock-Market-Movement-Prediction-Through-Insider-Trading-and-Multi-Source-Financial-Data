# ⚙️ Data Processing Module

This module aims to transform raw insider trading data into a structured dataset ready for Machine Learning models.

## 🎯 Objectives
1. **Cleaning**: Remove duplicate transactions and standardize formats.
2. **Feature Engineering**: Create predictive features (e.g., historical returns, insider track record).
3. **Labeling**: define the target variable (e.g., Stock Return > 0 in next 1 month).

## 📄 Dataset Design
Refer to **[dataset_design.md](dataset_design.md)** for the detailed schema specification of the final dataset.

## 🔄 Workflow (Planned)
- **Input**: Raw data from `data/raw/`
- **Output**: Processed dataset in `data/processed/`
