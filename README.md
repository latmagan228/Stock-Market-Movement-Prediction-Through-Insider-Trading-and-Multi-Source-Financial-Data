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

### 2. Usage

Run the data collector (scraper) to populate your raw dataset:

```bash
python src/data_collection/scraper.py
```

*For detailed instructions on each module, please refer to their respective READMEs linking in the Project Structure section above.*

## ⚙️ Configuration

Global settings (scraping speed, filters, paths) are managed in:
`config/config.yaml`


## 💼 Transaction Types

Available transaction types:
- P - Purchase
- S - Sale
- F - Tax
- D - Disposition
- G - Gift
- X - Exercise
- M - Options Exercise
- C - Conversion
- W - Will/Inheritance
- H - Holdings
- O - Other

## 🔍 Troubleshooting

- If you encounter rate limiting, adjust the `max_workers` setting
- For memory issues, try using Parquet format for large datasets
- Check the log file for detailed error messages
