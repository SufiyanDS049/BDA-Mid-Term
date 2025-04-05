# BDA-Mid-Term.
# Financial Stock Data ETL Pipeline

This project implements an ETL (Extract, Transform, Load) pipeline for collecting, transforming, analyzing, and loading financial stock data from multiple data sources, including MarketStack API, Kaggle datasets, local CSV files, MongoDB, and GitHub.

## Table of Contents

1. [Project Overview](#project-overview)
2. [Technology Stack](#technology-stack)
3. [How It Works](#how-it-works)
4. [Features](#features)
5. [Getting Started](#getting-started)
6. [Usage](#usage)
7. [License](#license)

## Project Overview

The goal of this pipeline is to automate the collection, cleaning, transformation, and aggregation of financial stock data. Data is sourced from:

- **MarketStack API**: Fetches historical stock data based on tickers.
- **Kaggle Dataset**: Loads daily-updating stock price data from Kaggle.
- **Local CSV File**: Uses locally stored stock data for processing.
- **MongoDB**: Retrieves stock data stored in a MongoDB collection.
- **GitHub**: Reads CSV data hosted on GitHub.

After data is collected, it is processed, cleaned, and aggregated by symbol and date. The transformed data is then loaded into a MongoDB database for further analysis.

## Technology Stack

- **Python**: Core language used for implementing the ETL pipeline.
- **Pandas**: Used for data manipulation, cleaning, and transformation.
- **Requests**: Used for making API requests to external services (MarketStack API).
- **MongoDB**: NoSQL database used to store the processed stock data.
- **Kaggle API**: For loading datasets from Kaggle (via KaggleHub).
- **PyMongo**: MongoDB client for interacting with the MongoDB database.
- **Schedule Library (optional)**: For scheduling periodic ETL tasks.
  
## How It Works

The pipeline follows a typical ETL (Extract, Transform, Load) pattern:

1. **Extract**:
   - Data is extracted from various sources such as APIs (MarketStack), Kaggle, local CSV files, MongoDB, and GitHub.
   
2. **Transform**:
   - The data is cleaned and transformed:
     - Timestamps are standardized.
     - Missing values are handled.
     - Invalid data is filtered out.
     - Features such as `capital_gains`, `daily_return`, and `volatility` are engineered.
     - Data is aggregated by ticker symbol and date.
   
3. **Load**:
   - The transformed data is loaded into a MongoDB database.

## Features

- **Multiple Data Connectors**: The pipeline connects to multiple data sources, including APIs, local files, MongoDB, and GitHub.
- **Data Cleaning**: Handles missing values, invalid data, and standardizes timestamps across datasets.
- **Feature Engineering**: Adds meaningful features such as daily returns, capital gains, and volatility.
- **Aggregation**: Aggregates data by symbol and date to calculate financial metrics.
- **Database Integration**: Loads processed data into a MongoDB database for further analysis or reporting.
- **Flexible Configuration**: The pipeline supports flexible date ranges and can be easily adjusted to pull more or fewer tickers.

## Getting Started

To get started, clone the repository and install the necessary dependencies.

### Clone the Repository

```bash
git clone https://github.com/yourusername/etl-stock-data.git
cd etl-stock-data
