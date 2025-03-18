import pandas as pd
from typing import List, Dict
from efficient_frontier.models import EquityPrice,Ticker


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
            ticker_object=Ticker.objects.get(ticker=ticker)
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
