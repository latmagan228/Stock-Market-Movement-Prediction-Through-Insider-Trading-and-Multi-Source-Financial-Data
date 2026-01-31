# 🕷️ Data Collection Module

This module is responsible for scraping and collecting insider trading data from OpenInsider.

## 🎯 Data Quality Strategy

**Current Configuration** (see `config/config.yaml`):
- **Time Range**: 2018-2025 (8 years of data)
- **Transaction Type**: Purchases only (P)  
- **Quality Filter**: $50,000 minimum transaction value

**Why $50k threshold?**
- Eliminates ~51% of noise (automatic/small transactions)
- Keeps ~41,000 high-quality insider signals over 8 years
- Focuses on intentional, significant purchases by insiders
- Full analysis: [DATA_QUALITY_DECISION.md](../../DATA_QUALITY_DECISION.md)

## 📋 Components
- **`scraper.py`**: Main script that handles the scraping logic, multi-threading, and caching.

## 🚀 Usage
From the project root directory:

```bash
# Run the scraper
./venv/bin/python src/data_collection/scraper.py
```

## ⚙️ Configuration
The scraper behavior is controlled by `config/config.yaml`:

## 📂 Output
The collected data includes raw transaction records saved in CSV or Parquet format in the `data/raw/` directory.
