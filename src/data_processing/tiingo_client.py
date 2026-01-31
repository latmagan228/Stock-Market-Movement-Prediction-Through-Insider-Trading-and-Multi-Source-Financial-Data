"""
Tiingo API Client with persistent caching for ML projects.
Designed to minimize API calls and respect rate limits.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import yaml
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Union
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class TiingoClient:
    """
    Client for fetching stock price data from Tiingo API with intelligent caching.
    
    Features:
    - Persistent disk-based cache (Parquet format)
    - Incremental updates (only fetch missing date ranges)
    - Rate limiting and retry logic
    - Compatible with insider trading data merge
    """
    
    BASE_URL = "https://api.tiingo.com/tiingo/daily"
    
    def __init__(self, 
                 api_key: Optional[str] = None,
                 cache_dir: str = "data/tiingo_cache",
                 config_path: Optional[str] = None,
                 requests_per_second: float = 5.0):
        """
        Initialize Tiingo client.
        
        Args:
            api_key: Tiingo API key. If None, reads from TIINGO_API_KEY env var
            cache_dir: Directory for cache storage
            config_path: Optional path to config.yaml
            requests_per_second: Rate limit for API calls
        """
        self.api_key = api_key or os.getenv('TIINGO_API_KEY')
        if not self.api_key:
            raise ValueError(
                "Tiingo API key not found. Set TIINGO_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        # Setup cache directory
        if config_path:
            project_root = Path(config_path).parent.parent
        else:
            project_root = Path(__file__).resolve().parent.parent.parent
            
        self.cache_dir = project_root / cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Rate limiting
        self.requests_per_second = requests_per_second
        self.last_request_time = 0
        
        # Setup logging
        self.logger = logging.getLogger('tiingo_client')
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
        
        # Setup session with retry logic
        self.session = self._create_session()
    
    def enable_debug(self):
        """Enable debug logging to see detailed API responses."""
        self.logger.setLevel(logging.DEBUG)
    
    def _create_session(self) -> requests.Session:
        """Create a requests session with retry logic."""
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=2,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return session
    
    def _rate_limit(self):
        """Enforce rate limiting between requests."""
        if self.requests_per_second > 0:
            time_since_last = time.time() - self.last_request_time
            min_interval = 1.0 / self.requests_per_second
            if time_since_last < min_interval:
                time.sleep(min_interval - time_since_last)
        self.last_request_time = time.time()
    
    def _get_cache_path(self, ticker: str) -> Path:
        """Get cache file path for a ticker."""
        return self.cache_dir / f"{ticker.upper()}.parquet"
    
    
    def _load_cache(self, ticker: str) -> Optional[pd.DataFrame]:
        """Load cached data for a ticker."""
        cache_path = self._get_cache_path(ticker)
        if cache_path.exists():
            try:
                df = pd.read_parquet(cache_path)
                df['date'] = pd.to_datetime(df['date'])
                # Remove timezone info for consistent comparisons
                if df['date'].dt.tz is not None:
                    df['date'] = df['date'].dt.tz_localize(None)
                self.logger.info(f"Loaded cache for {ticker}: {len(df)} records")
                return df
            except Exception as e:
                self.logger.warning(f"Failed to load cache for {ticker}: {e}")
                return None
        return None
    
    def _save_cache(self, ticker: str, df: pd.DataFrame):
        """Save data to cache."""
        cache_path = self._get_cache_path(ticker)
        df.to_parquet(cache_path, index=False)
        self.logger.info(f"Saved cache for {ticker}: {len(df)} records")
    
    def _fetch_from_api(self, ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Fetch data from Tiingo API.
        
        Args:
            ticker: Stock ticker symbol
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            DataFrame with columns: date, close, high, low, open, volume, adjClose, etc.
        """
        self._rate_limit()
        
        url = f"{self.BASE_URL}/{ticker}/prices"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Token {self.api_key}'
        }
        params = {
            'startDate': start_date,
            'endDate': end_date,
            'format': 'json'
        }
        
        try:
            self.logger.info(f"Fetching {ticker} from {start_date} to {end_date}")
            response = self.session.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            if not data:
                self.logger.warning(f"No data returned for {ticker}")
                return pd.DataFrame()
            
            df = pd.DataFrame(data)
            df['date'] = pd.to_datetime(df['date'])
            # Remove timezone info for consistent comparisons
            if df['date'].dt.tz is not None:
                df['date'] = df['date'].dt.tz_localize(None)
            df['ticker'] = ticker.upper()
            
            self.logger.info(f"Fetched {len(df)} records for {ticker}")
            return df
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                self.logger.error(f"Ticker {ticker} not found on Tiingo")
            else:
                self.logger.error(f"HTTP error fetching {ticker}: {e}")
            return pd.DataFrame()
        except Exception as e:
            self.logger.error(f"Error fetching {ticker}: {e}")
            return pd.DataFrame()
    
    def get_prices(self, 
                   ticker: str, 
                   start_date: Union[str, datetime], 
                   end_date: Union[str, datetime]) -> pd.DataFrame:
        """
        Get price data for a ticker, using cache when possible.
        
        Args:
            ticker: Stock ticker symbol
            start_date: Start date (YYYY-MM-DD or datetime)
            end_date: End date (YYYY-MM-DD or datetime)
            
        Returns:
            DataFrame with price data
        """
        # Validar ticker
        if ticker is None or ticker == '' or str(ticker).strip() == '':
            self.logger.warning(f"Invalid ticker: {ticker}")
            return pd.DataFrame()
            
        ticker = str(ticker).upper()
        
        # Convert dates to strings
        if isinstance(start_date, datetime):
            start_date = start_date.strftime('%Y-%m-%d')
        if isinstance(end_date, datetime):
            end_date = end_date.strftime('%Y-%m-%d')
        
        start_dt = pd.to_datetime(start_date)
        end_dt = pd.to_datetime(end_date)
        
        # Load cache
        cached_df = self._load_cache(ticker)
        
        if cached_df is None or len(cached_df) == 0:
            # No cache, fetch everything
            self.logger.info(f"⚠️ {ticker}: No cache found, fetching all data")
            df = self._fetch_from_api(ticker, start_date, end_date)
            if not df.empty:
                self._save_cache(ticker, df)
            return df
        
        # Check what's missing
        cached_start = cached_df['date'].min()
        cached_end = cached_df['date'].max()
        
        dfs_to_merge = [cached_df]
        
        # Fetch data before cached range  
        # Only fetch if gap is > 3 days (avoid API calls for weekends)
        gap_before = (cached_start - start_dt).days
        if gap_before > 3:
            before_end = (cached_start - timedelta(days=1)).strftime('%Y-%m-%d')
            self.logger.info(f"Gap of {gap_before} days detected before cache, fetching")
            df_before = self._fetch_from_api(ticker, start_date, before_end)
            if not df_before.empty:
                dfs_to_merge.append(df_before)
        elif gap_before > 0:
            self.logger.debug(f"Small gap of {gap_before} days before cache, skipping")
        
        # Fetch data after cached range
        # Only fetch if gap is > 3 days (avoid API calls for weekends)
        gap_days = (end_dt - cached_end).days
        made_api_call = False
        
        # Check if cache was recently updated (avoid redundant API calls)
        cache_path = self._get_cache_path(ticker)
        cache_age_hours = (datetime.now() - datetime.fromtimestamp(cache_path.stat().st_mtime)).total_seconds() / 3600
        
        if gap_days > 3:
            # Only fetch if cache is old (> 1 hour) or gap is very large (> 7 days)
            if cache_age_hours > 1.0 or gap_days > 7:
                after_start = (cached_end + timedelta(days=1)).strftime('%Y-%m-%d')
                self.logger.warning(f"🔄 {ticker}: Gap of {gap_days} days (cache age: {cache_age_hours:.1f}h)")
                df_after = self._fetch_from_api(ticker, after_start, end_date)
                made_api_call = True
                
                if not df_after.empty:
                    dfs_to_merge.append(df_after)
                    self.logger.info(f"   → Got {len(df_after)} new records")
                else:
                    self.logger.info(f"   → No new data available")
            else:
                self.logger.info(f"✓ {ticker}: Gap of {gap_days}d but cache is fresh ({cache_age_hours:.1f}h old), skipping")
        elif gap_days > 0:
            self.logger.debug(f"✓ {ticker}: Small gap of {gap_days} days (weekend), using cache only")
        
        # Merge and save
        if len(dfs_to_merge) > 1:
            df = pd.concat(dfs_to_merge, ignore_index=True)
            df = df.drop_duplicates(subset=['date']).sort_values('date')
            self._save_cache(ticker, df)
            self.logger.info(f"✓ {ticker}: Cache updated with new data")
        elif made_api_call and len(dfs_to_merge) == 1:
            # Hicimos API call pero no hubo datos nuevos
            # Aún así guardamos el caché para evitar reintentos
            df = cached_df
            self._save_cache(ticker, df)  # Re-guardar actualiza el timestamp del archivo
            self.logger.info(f"✓ {ticker}: Cache refreshed (no new data available)")
        else:
            df = cached_df
            self.logger.info(f"✓ {ticker}: Using cache only (no API call needed)")
        
        # Filter to requested range
        df = df[(df['date'] >= start_dt) & (df['date'] <= end_dt)]
        return df
    
    def get_prices_bulk(self, 
                        tickers: List[str], 
                        start_date: Union[str, datetime],
                        end_date: Union[str, datetime]) -> pd.DataFrame:
        """
        Get price data for multiple tickers.
        
        Args:
            tickers: List of ticker symbols
            start_date: Start date
            end_date: End date
            
        Returns:
            Combined DataFrame with all tickers
        """
        all_dfs = []
        for ticker in tickers:
            df = self.get_prices(ticker, start_date, end_date)
            if not df.empty:
                all_dfs.append(df)
        
        if all_dfs:
            return pd.concat(all_dfs, ignore_index=True)
        return pd.DataFrame()
    
    def clear_cache(self, ticker: Optional[str] = None):
        """
        Clear cache data.
        
        Args:
            ticker: If specified, clear only this ticker's cache.
                   If None, clear all cache (with confirmation).
        """
        if ticker:
            cache_path = self._get_cache_path(ticker)
            if cache_path.exists():
                cache_path.unlink()
                self.logger.info(f"Cleared cache for {ticker}")
            else:
                self.logger.info(f"No cache found for {ticker}")
        else:
            # Clear all cache
            cache_files = list(self.cache_dir.glob("*.parquet"))
            if cache_files:
                self.logger.warning(f"About to delete {len(cache_files)} cache files")
                for file in cache_files:
                    file.unlink()
                self.logger.info(f"Cleared all cache ({len(cache_files)} files)")
            else:
                self.logger.info("No cache files found")
    
    def get_price_at_date(self, ticker: str, date: Union[str, datetime]) -> Optional[float]:
        """
        Get closing price for a specific date.
        Useful for merging with insider data.
        
        Args:
            ticker: Stock ticker
            date: Target date
            
        Returns:
            Closing price or None if not available
        """
        if isinstance(date, str):
            date = pd.to_datetime(date)
        elif isinstance(date, pd.Timestamp) and date.tz is not None:
            date = date.tz_localize(None)
        
        # Fetch a small window around the date
        start = (date - timedelta(days=5)).strftime('%Y-%m-%d')
        end = (date + timedelta(days=5)).strftime('%Y-%m-%d')
        
        df = self.get_prices(ticker, start, end)
        if df.empty:
            return None
        
        # Find closest date
        df['date_diff'] = (df['date'] - date).abs()
        closest = df.loc[df['date_diff'].idxmin()]
        return closest['adjClose']
