import requests
import pandas as pd
import kagglehub
from kagglehub import KaggleDatasetAdapter
from pymongo import MongoClient
import schedule
import time


class ETLPipeline:
    """
    A class for collecting, transforming, analyzing, and loading financial stock data
    from MarketStack API and Kaggle datasets.
    """

    # API and configuration constants
    ticker_url = 'https://gist.githubusercontent.com/SufiyanDS049/38188ac53b3d4b265efc4e4efaf99b1f/raw/58975d091bdc26ff0b7af218ec6bea62ab8fa0d2/tickers.json'
    marketstack_baseapiurl = 'https://api.marketstack.com/v2/eod?access_key=580c67effd676378137d18d392f35603'
    marketstack_apiurlgist = 'https://gist.githubusercontent.com/SufiyanDS049/78a23e2a5be5f9113ed44dcc71172098/raw/9a152deca2c51a4a5c460e7bb1d0c4896a44ce43/marketstack_stockdata.json'
    datefrom = '2025-03-01'
    dateto = '2025-04-01'
    IS_MOCK = True

    def __init__(self, datefrom=None, dateto=None):
        """Initialize DataCollection with optional custom date range."""
        if datefrom and dateto:
            self.datefrom = datefrom
            self.dateto = dateto

    def api_request(self, requesturl):
        """Generic method to make API requests."""
        data = requests.get(requesturl)
        return data.json()

    def get_tickers(self):
        """Fetch the list of tickers from the provided ticker URL."""
        tickers_json = self.api_request(self.ticker_url)
        data = tickers_json['data'][:25]
        tickers_list = [x['ticker'] for x in data]
        return tickers_list

    def get_stock_data_from_marketstack(self):
        """
        Connector # 1
        Fetch historical stock data either from MarketStack API or a mock source.
        """
        tickers_list = self.get_tickers()
        tickers_str = ','.join(tickers_list)
        if self.IS_MOCK:
            marketstack_url = self.marketstack_apiurlgist
        else:
            marketstack_url = f'{self.marketstack_baseapiurl}&symbols={tickers_str}&date_from={self.datefrom}&date_to={self.dateto}'
        stock_data = self.api_request(marketstack_url)['data']
        df = pd.DataFrame(stock_data)
        return df

    def get_data_from_kaggle_df(self):
        """
        Connector # 2
        Load stock data from Kaggle dataset using KaggleHub.
        """
        file_path = "World-Stock-Prices-Dataset.csv"
        df = kagglehub.load_dataset(
            KaggleDatasetAdapter.PANDAS,
            "nelgiriyewithana/world-stock-prices-daily-updating",
            file_path
        )
        return df

    def get_data_from_local_csv(self):
      """
      Connector #3
      Load stock data from local CSV dataset.
      """
      df = pd.read_csv("2001_stock_data.csv")
      return df

    def get_data_from_mongodb(self):
      """
      Connector #4
      Load stock data from mongodb dataset.
      """
      mongoclient = MongoClient('mongodb+srv://sufiyan96:bscs2016@cluster0.nnspm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
      db = mongoclient['BDA_Data']
      collection = db['Stock']

      # Fetch all documents
      data = list(collection.find({}))

      # Convert to DataFrame
      df = pd.DataFrame(data)

      # Optionally drop the MongoDB "_id" field
      if '_id' in df.columns:
          df.drop('_id', axis=1, inplace=True)

      return df

    def get_data_from_github(self):
      """
      Connector #5
      Load stock data from github dataset.
      """
      df = pd.read_csv('https://raw.githubusercontent.com/SufiyanDS049/BDA-Mid-Term/refs/heads/main/2005_stock_data.csv')
      return df

    def check_for_null_values(self):
        """Check and return columns with null values in both datasets."""
        marketstack_df = self.get_stock_data_from_marketstack()
        kaggle_df = self.get_data_from_kaggle_df()
        local_csv = self.get_data_from_local_csv()
        mongo_db = self.get_data_from_mongodb()
        github = self.get_data_from_github()

        marketstack_nulls = marketstack_df.isnull().sum()
        kaggle_nulls = kaggle_df.isnull().sum()
        local_nulls = local_csv.isnull().sum()
        mongo_nulls = mongo_db.isnull().sum()
        github_nulls = github.isnull().sum()

        marketstack_null_cols = {col: count for col, count in marketstack_nulls.items() if count > 0}
        kaggle_null_cols = {col: count for col, count in kaggle_nulls.items() if count > 0}
        local_null_cols = {col: count for col, count in local_nulls.items() if count > 0}
        mongo_null_cols = {col: count for col, count in mongo_nulls.items() if count > 0}
        github_null_cols = {col: count for col, count in github_nulls.items() if count > 0}

        print("Null values in MarketStack DataFrame:", marketstack_null_cols)
        print("Null values in Kaggle DataFrame:", kaggle_null_cols)
        print("Null values in Local csv DataFrame:", local_null_cols)
        print("Null values in MongoDb DataFrame:", mongo_null_cols)
        print("Null values in Github DataFrame:", github_null_cols)

        return {
            "marketstack_nulls": marketstack_null_cols,
            "kaggle_nulls": kaggle_null_cols,
            "local_nulls": local_null_cols,
            "mongo_nulls": mongo_null_cols,
            "github_nulls": github_null_cols
        }

    def handle_missing_values(self, kaggle_df):
        """Add capital gains feature (close - open) to Kaggle data."""
        kaggle_df['capital_gains'] = kaggle_df['close'] - kaggle_df['open']
        return kaggle_df

    def normalize_column_names(self, df):
        """Normalize column names to lowercase and underscores."""
        df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
        return df

    def validate_data(self, df):
        """Drop rows with invalid (negative) financial values."""
        numeric_cols = ['open', 'close', 'high', 'low', 'volume']
        for col in numeric_cols:
            if col in df.columns:
                df = df[df[col] >= 0]
        return df

    def add_features(self, df):
        """Calculate daily return and volatility as new features."""
        if {'close', 'open', 'high', 'low'}.issubset(df.columns):
            df['daily_return'] = (df['close'] - df['open']) / df['open']
            df['volatility'] = df['high'] - df['low']
        return df

    def aggregate_data(self, df, date_col='date', groupby_col='symbol', company='name'):
        """Aggregate financial metrics by ticker and date."""
        df[date_col] = pd.to_datetime(df[date_col])
        df['date_only'] = df[date_col].dt.date
        grouped = df.groupby([groupby_col, 'date_only']).agg({
            'open': 'mean',
            'close': 'mean',
            'high': 'max',
            'low': 'min',
            'volume': 'sum',
            'daily_return': 'mean',
            'volatility': 'mean'
        }).reset_index()
        return grouped

    def standardize_timestamps(self, df, year, date_column='date'):
      """Convert date columns to datetime and filter data for year 2025."""
      df[date_column] = pd.to_datetime(df[date_column], utc=True)
      df = df[df[date_column].dt.year == year]
      return df

    def merge_datasets(self, market_agg, kaggle_agg, local_agg, mongo_agg, github_agg):
        """Merge MarketStack and Kaggle data, dropping duplicates on symbol + date."""
        print(mongo_agg)
        combined_df = pd.concat([market_agg, kaggle_agg, local_agg, mongo_agg, github_agg], ignore_index=True)
        combined_df = combined_df.drop_duplicates(subset=['symbol', 'date_only'], keep='first')
        return combined_df

    def run_transformation(self):
      """
      Runs the full ETL transformation pipeline:
      1. Load data (including local and MongoDB data)
      2. Normalize and validate
      3. Feature engineering
      4. Aggregation and merging
      """
      # Step 1: Load
      market_df = self.get_stock_data_from_marketstack() # Load MarketStack api
      kaggle_df = self.get_data_from_kaggle_df() # Load Kaggle
      local_df = self.get_data_from_local_csv()  # Load local CSV data
      mongo_df = self.get_data_from_mongodb()    # Load MongoDB data
      github_df = self.get_data_from_github() # Load Github csv

      # Step 2: Standardize timestamps for each dataset (handling 'date' and 'Date' separately)
      market_df = self.standardize_timestamps(market_df,2025, date_column='date')
      kaggle_df = self.standardize_timestamps(kaggle_df,2025, date_column='Date')
      local_df = self.standardize_timestamps(local_df,2024, date_column='Date')  # assuming local_df also uses 'date'
      mongo_df = self.standardize_timestamps(mongo_df,2023, date_column='Date')  # assuming mongo_df also uses 'date'
      github_df = self.standardize_timestamps(github_df,2022, date_column='Date')  # assuming mongo_df also uses 'date'

      print('===========================')
      print(mongo_df)
      print('===========================')
      print(local_df)

      # Fix case issues in brand names for Kaggle data
      kaggle_df['Brand_Name'] = kaggle_df['Brand_Name'].str.title()
      local_df['Brand_Name'] = kaggle_df['Brand_Name'].str.title()
      mongo_df['Brand_Name'] = kaggle_df['Brand_Name'].str.title()
      github_df['Brand_Name'] = github_df['Brand_Name'].str.title()

      # Step 3: Normalize column names for all datasets
      market_df = self.normalize_column_names(market_df)
      kaggle_df = self.normalize_column_names(kaggle_df)
      local_df = self.normalize_column_names(local_df)
      mongo_df = self.normalize_column_names(mongo_df)
      github_df = self.normalize_column_names(github_df)

      # Step 4: Handle missing data (you already have missing value handling for Kaggle)
      kaggle_df = self.handle_missing_values(kaggle_df)
      # You can apply similar missing value handling to other datasets (local_df, mongo_df)
      # For simplicity, let's assume they all require the same missing values handling
      local_df = self.handle_missing_values(local_df)

      mongo_df = self.handle_missing_values(mongo_df)
      github_df = self.handle_missing_values(github_df)

      # Step 5: Validate data
      market_df = self.validate_data(market_df)
      kaggle_df = self.validate_data(kaggle_df)
      local_df = self.validate_data(local_df)
      mongo_df = self.validate_data(mongo_df)
      github_df = self.validate_data(github_df)

      # Step 6: Feature engineering
      market_df = self.add_features(market_df)
      kaggle_df = self.add_features(kaggle_df)
      local_df = self.add_features(local_df)
      mongo_df = self.add_features(mongo_df)
      github_df = self.add_features(github_df)

      # Step 7: Aggregate by date and symbol for all datasets
      market_agg = self.aggregate_data(market_df)
      kaggle_agg = self.aggregate_data(kaggle_df, date_col='date', groupby_col='ticker', company='brand_name')
      local_agg = self.aggregate_data(local_df, date_col='date', groupby_col='ticker',company='brand_name')
      mongo_agg = self.aggregate_data(mongo_df, date_col='date', groupby_col='ticker',company='brand_name')
      github_agg = self.aggregate_data(github_df, date_col='date', groupby_col='ticker',company='brand_name')

      kaggle_agg = kaggle_agg.rename(columns={'ticker': 'symbol'})
      local_agg = local_agg.rename(columns={'ticker': 'symbol'})
      mongo_agg = mongo_agg.rename(columns={'ticker': 'symbol'})
      github_agg = github_agg.rename(columns={'ticker': 'symbol'})

      # Step 8: Merge all datasets
      merged_df = self.merge_datasets(market_agg, kaggle_agg, local_agg, mongo_agg, github_agg)

      return merged_df

    def load_data(self, df):
        """
        Load final processed data to MongoDB.
        Converts date to datetime to avoid BSON encoding errors.
        """
        df['date_only'] = pd.to_datetime(df['date_only'])
        mongoclient = MongoClient('mongodb+srv://sufiyan96:bscs2016@cluster0.nnspm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
        db = mongoclient['BDA_Data']
        collection = db['Stock_New']

        records = df.to_dict(orient='records')

        if records:
            collection.insert_many(records)
            print(f"Inserted {len(records)} documents into collection.")
        else:
            print("No records to insert.")
