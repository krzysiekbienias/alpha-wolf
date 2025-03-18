import pandas as pd
from typing import List, Dict, Optional, Tuple
from efficient_frontier.models import EquityPrice, Ticker
from tool_kit.plots import PlotUsingMatplotLib
import matplotlib.pyplot as plt
import numpy as np

class StockTimeSeriesProcessor:
    """
    A class to process time series data for multiple tickers from the SQLite database (Django Model).

    This class fetches historical stock price data, processes it using Pandas, and provides
    various utilities for analysis and export.
    """

    def __init__(self, tickers: List[str] | None = None):
        """
        Initializes the TimeSeriesProcessor with one or more stock tickers.

        Parameters:
        -----------
        tickers : List[str]
            A list of stock ticker symbols to fetch time series data for.
        """
        self.__tickers = tickers  # Private attribute storing tickers
        self.df_dict = {}  # Dictionary to store DataFrames

        if tickers:
            self.load_data()
        else:
            print("⚠️ WARNING: No tickers provided. You must call `set_tickers()` before loading data.")
            # Dictionary of DataFrames (one per ticker)

    def load_data(self) -> Dict[str, pd.DataFrame]:
        """
        Fetches time series data for all tickers from the database and loads them into Pandas DataFrames.

        Raises:
        -------
        ValueError:
            If no tickers have been provided before calling this method.
        """
        if not self.__tickers:
            print("⚠️ WARNING: No tickers set. Use `set_tickers()` to provide tickers before loading data.")
            return  # Simply exit instead of raising an error

        self.df_dict = {}  # Reset data dictionary

        for ticker in self.__tickers:
            ticker_object = Ticker.objects.get(ticker=ticker)
            time_series = EquityPrice.objects.filter(ticker=ticker_object).values("date", "close_price")
            df = pd.DataFrame(list(time_series))

            if not df.empty:
                df["date"] = pd.to_datetime(df["date"])
                df = df.sort_values(by="date").reset_index(drop=True)

            self.df_dict[ticker] = df

    # ===========================================
    # REGION: Getter & Setter for Tickers
    # ===========================================

    @property
    def get_tickers(self) -> List[str]:
        """Returns the list of tickers."""
        return self.__tickers

    def set_tickers(self, new_tickers: List[str]):
        """
        Updates the tickers and reloads the data.

        Parameters:
        -----------
        new_tickers : List[str]
            The new list of stock ticker symbols.
        """
        if not new_tickers:
            raise ValueError("Ticker list must not be empty.")

        self.__tickers = new_tickers
        self.load_data()
        print(f"Tickers updated to {new_tickers}. Data reloaded.")

    # ===========================================
    # REGION: Data Processing Methods
    # ===========================================
    def get_data(self, ticker: str) -> pd.DataFrame:
        """
        Returns the time series data for a specific ticker.

        Parameters:
        -----------
        ticker : str
            The stock ticker symbol.

        Returns:
        --------
        pd.DataFrame
            A DataFrame with columns ['date', 'close_price'].
        """
        return self.df_dict.get(ticker, pd.DataFrame())

    def get_latest_price(self, ticker: str) -> float | None:
        """
        Returns the latest available close price for a given ticker.

        Parameters:
        -----------
        ticker : str
            The stock ticker symbol.

        Returns:
        --------
        float or None
            The most recent close price, or None if no data exists.
        """
        df = self.df_dict.get(ticker)
        return df["close_price"].iloc[-1] if df is not None and not df.empty else None

    def get_summary_statistics(self, ticker: str) -> pd.DataFrame:
        """
        Returns summary statistics of the close price time series for a given ticker.

        Parameters:
        -----------
        ticker : str
            The stock ticker symbol.

        Returns:
        --------
        pd.DataFrame
            A DataFrame containing statistics like mean, median, min, max, and standard deviation.
        """
        df = self.df_dict.get(ticker)
        return df["close_price"].describe() if df is not None and not df.empty else pd.DataFrame()

    def plot_time_series(self,
                         nrows: Optional[int] = None,
                         ncols: Optional[int] = None,
                         figsize: Tuple[int, int] = (12, 6)) -> Tuple[plt.Figure, plt.Axes]:
        """
        Plots the close price time series for all loaded tickers.

        This method prepares the data from `df_dict` and uses `PlotUsingMatplotLib` to
        generate a time series plot.

        Parameters:
        -----------
        nrows : int, optional
            Number of rows in the subplot grid. Defaults to `None` (single plot).

        ncols : int, optional
            Number of columns in the subplot grid. Defaults to `None` (single plot).

        figsize : Tuple[int, int], optional
            Figure size in inches (width, height). Defaults to `(12, 6)`.

        Returns:
        --------
        Tuple[plt.Figure, plt.Axes]
            A tuple containing the Matplotlib Figure and Axes objects.

        Raises:
        -------
        ValueError:
            If no data is available for plotting.
        """
        if not self.df_dict:
            raise ValueError("No data available for plotting. Load data first.")

        ts_df_list = []
        ts_labels_list = []

        for ticker, df in self.df_dict.items():
            if not df.empty:
                ts_df_list.append(df[["date", "close_price"]])
                ts_labels_list.append(ticker)

        if not ts_df_list:
            raise ValueError("All loaded tickers have empty data. Cannot plot.")

        return PlotUsingMatplotLib.plot(ts_df_list, ts_labels_list, "Date", "Close Price",
                                        nrows=nrows, ncols=ncols, figsize=figsize)

    def calculate_returns(self, tickers: Optional[list] = None, method: str = "simple", frequency: str = "daily") -> \
    Dict[str, pd.DataFrame]:
        """
        Calculates log or simple returns for multiple tickers at a specified frequency.
        Uses NumPy for efficient calculations and returns a dictionary of Pandas DataFrames.

        Parameters:
        -----------
        tickers : list, optional
            A list of stock ticker symbols. If None, it calculates for all loaded tickers.

        method : str, optional, default="simple"
            - `"simple"`: Simple returns as `(P_t / P_(t-1)) - 1`
            - `"log"`: Log returns as `log(P_t / P_(t-1))`

        frequency : str, optional, default="daily"
            - `"daily"`: Computes daily returns
            - `"weekly"`: Computes weekly returns
            - `"monthly"`: Computes monthly returns

        Returns:
        --------
        Dict[str, pd.DataFrame]
            A dictionary where:
            - **Keys** = Ticker symbols (str)
            - **Values** = Pandas DataFrames containing the calculated returns.

        Raises:
        -------
        ValueError:
            - If no tickers are provided or loaded.
            - If an invalid method or frequency is provided.

        Example:
        --------
        >>> processor.calculate_returns(["AAPL", "TSLA"], method="log", frequency="weekly")
        """

        if tickers is None:
            tickers = self.__tickers  # Use all tickers if not provided

        if not tickers:
            raise ValueError("⚠️ ERROR: No tickers provided. Use `set_tickers()` to load data first.")

        # Frequency mapping
        frequency_map = {"daily": "D", "weekly": "W", "monthly": "M"}
        if frequency not in frequency_map:
            raise ValueError("⚠️ ERROR: Invalid frequency. Choose from 'daily', 'weekly', or 'monthly'.")

        returns_dict = {}  # Dictionary to store results

        for ticker in tickers:
            if ticker not in self.df_dict:
                print(f"⚠️ WARNING: Ticker '{ticker}' not found. Skipping...")
                continue

            df = self.df_dict[ticker].copy()

            if df.empty:
                print(f"⚠️ WARNING: No data available for '{ticker}'. Skipping...")
                continue

            df["close_price"] = df["close_price"].astype(float)
            # ✅ Fix: Ensure 'date' column is set as index
            if "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"])  # Convert to Datetime
                df.set_index("date", inplace=True)  # Set 'date' as index

            if not isinstance(df.index, pd.DatetimeIndex):
                raise ValueError(f"⚠️ ERROR: Index for '{ticker}' is not a DatetimeIndex. Check data formatting.")

            # Resample for different frequencies
            df_resampled = df["close_price"].resample(frequency_map[frequency]).last().dropna()

            # Convert to NumPy for efficient calculations
            prices = df_resampled.values

            # Calculate returns using NumPy
            if method == "simple":
                returns = prices[1:] / prices[:-1] - 1
            elif method == "log":
                returns = np.log(prices[1:] / prices[:-1])
            else:
                raise ValueError("⚠️ ERROR: Invalid method. Choose 'simple' or 'log'.")

            # Convert back to Pandas for reporting
            returns_df = pd.DataFrame(returns, index=df_resampled.index[1:], columns=["returns"])

            # Store results in dictionary
            returns_dict[ticker] = returns_df

        return returns_dict

    def export_to_csv(self, ticker: str, file_name: str):
        """
        Exports the time series data of a specific ticker to a CSV file.

        Parameters:
        -----------
        ticker : str
            The stock ticker symbol.
        file_name : str
            The file path where the CSV should be saved.
        """
        df = self.df_dict.get(ticker)
        if df is not None and not df.empty:
            df.to_csv(file_name, index=False)
            print(f"Data for {ticker} exported to {file_name}")
        else:
            print(f"No data found for {ticker}. Cannot export.")
