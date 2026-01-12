# 🕷️ Data Collection Module

This module is responsible for scraping and collecting insider trading data from OpenInsider.

## 📋 Components
- **`scraper.py`**: Main script that handles the scraping logic, multi-threading, and caching.

## 🚀 Usage
From the project root directory:

```bash
# Run the scraper
./venv/bin/python src/data_collection/scraper.py
```

## ⚙️ Configuration
The scraper behavior is controlled by `config/config.yaml`. 
- **Output**: By default, data is saved to `data/raw/`.
- **Filters**: You can adjust transaction types, minimum values, and date ranges in the config file.

## 📂 Output
The collected data includes raw transaction records saved in CSV or Parquet format in the `data/raw/` directory.
