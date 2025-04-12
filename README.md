# ETL Pipeline for Financial Stock Data Integration

## 1. Introduction

This project implements a complete ETL (Extract, Transform, Load) pipeline for integrating financial stock data from various sources including APIs, cloud storage, and databases. The goal is to unify diverse data formats, enrich them with derived metrics, and load the cleaned data into MongoDB for further analysis or visualization.

---

## 2. Objectives

- To design and implement a robust ETL pipeline.
- To extract stock data from multiple heterogeneous sources.
- To clean, transform, and enrich the datasets.
- To standardize and merge the data into a unified structure.
- To load the final dataset into a MongoDB collection.

---

## 3. Data Sources

| Source          | Type         | Description                                                                 |
|-----------------|--------------|-----------------------------------------------------------------------------|
| MarketStack API | API (mocked) | Fetches historical stock prices via public API or mock JSON endpoint.      |
| Kaggle Dataset  | CSV via API  | Daily-updating world stock prices loaded using KaggleHub.                  |
| Local CSV File  | CSV (local)  | Historical stock data from 2001 stored locally.                            |
| MongoDB         | NoSQL DB     | Preloaded stock data in `BDA_Data.Stock` collection.                       |
| GitHub CSV      | CSV (remote) | 2005 stock data hosted on GitHub repository (`main` branch).              |

---

## 4. Tools and Technologies

- **Python 3.x**
- **Pandas** for data manipulation
- **Requests** for API handling
- **KaggleHub** for fetching Kaggle datasets
- **PyMongo** for MongoDB integration
- **Matplotlib / Seaborn** for optional visualizations
- **GitHub Actions** for CI/CD pipeline automation

---

## 5. ETL Pipeline Design

### 5.1 Extraction

- Connects to each data source using its appropriate method.
- For APIs, uses HTTP requests to retrieve JSON data.
- For CSVs, uses `pandas.read_csv` directly or through KaggleHub.
- For MongoDB, connects using `pymongo` and retrieves documents.

### 5.2 Transformation

- **Standardizes timestamps** and filters by relevant years.
- **Normalizes column names** to lowercase and snake_case.
- **Validates** data by removing negative financial entries.
- **Handles missing values** and computes new features:
  - `daily_return = (close - open) / open`
  - `volatility = high - low`
  - `capital_gains = close - open`
- **Aggregates** data by symbol and date:
  - Computes average open/close, max high, min low, total volume.

### 5.3 Loading

- Transformed data is loaded into a new MongoDB collection:  
  **`BDA_Data.Stock_New`**
- Timestamps are converted to BSON-compatible format before insertion.

---

## 6. CI/CD Pipeline (GitHub Actions)

- Automatically triggers on every push to the `main` branch.
- Steps:
  1. Checkout repository.
  2. Install Python dependencies.
  3. Run ETL transformation and loading script.

---

## 7. Results

- Final dataset contains clean, enriched, and unified stock data.
- All records are timestamped and grouped by stock ticker.
- Duplicate entries are removed using `(symbol, date_only)` pair.
- Data ready for analytics or visual dashboards.

---

## 8. Conclusion

This ETL pipeline successfully demonstrates multi-source data integration, preprocessing, and cloud-based loading using Python. It serves as a scalable and extendable framework for financial data engineering tasks.

---

## 9. Author

**Name:** Sufiyan  
**MongoDB Cluster:** `BDA_Data`  
**Branch:** `main`

---
