import abc
import yfinance as yf
import matplotlib.pyplot as plt
from typing import TypeVar, Iterable, Tuple, Dict, List
import QuantLib as ql
import pandas as pd
from tool_kit.config_loader import CONFIG
import pandas_datareader.data as web
from polygon import RESTClient

FRED_SERIES_IDS = {
    # Treasury Yields
    "10Y": "DGS10",  # 10-Year Treasury Constant Maturity Rate
    "5Y": "DGS5",  # 5-Year Treasury Constant Maturity Rate
    "2Y": "DGS2",  # 2-Year Treasury Constant Maturity Rate
    "1Y": "DGS1",  # 1-Year Treasury Constant Maturity Rate
    "6M": "DGS6MO",  # 6-Month Treasury Constant Maturity Rate
    "3M": "DGS3MO",  # 3-Month Treasury Constant Maturity Rate
    "1M": "DGS1MO",  # 1-Month Treasury Constant Maturity Rate

    # Treasury Bills
    "3M_TBILL": "DTB3",  # 3-Month Treasury Bill Secondary Market Rate
    "6M_TBILL": "DTB6",  # 6-Month Treasury Bill Secondary Market Rate

    # Federal Funds
    "FEDFUNDS": "FEDFUNDS",  # Effective Federal Funds Rate

    # Inflation Rates
    "CPI": "CPIAUCSL",  # Consumer Price Index for All Urban Consumers
    "CORE_CPI": "CPILFESL",  # Core Consumer Price Index (excluding food and energy)

    # Unemployment Rates
    "UNRATE": "UNRATE",  # Unemployment Rate

    # Exchange Rates
    "EURUSD": "DEXUSEU",  # US Dollar to Euro Exchange Rate
    "GBPUSD": "DEXUSUK",  # US Dollar to British Pound Exchange Rate
    "JPYUSD": "DEXJPUS",  # US Dollar to Japanese Yen Exchange Rate

    # Commodities
    "GOLD": "GOLDAMGBD228NLBM",  # Gold Fixing Price in London (USD per Troy Ounce)
    "SILVER": "SLVPRUSD",  # Silver Price (USD per Troy Ounce)
    "OIL": "DCOILWTICO",  # Crude Oil Prices: West Texas Intermediate (WTI)

    # Stock Market Indices
    "SP500": "SP500",  # S&P 500 Index
    "DJIA": "DJIA",  # Dow Jones Industrial Average
    "NASDAQ": "NASDAQCOM",  # NASDAQ Composite Index
}


#
# client=RESTClient('2I8_POlvy5wQLpOUZIwIsl7LH9Hm8yPp')
#aggs = client.get_daily_open_close_agg()


class MarketDataExtractor(abc.ABC):
    """
    Market Data Extraction Utility.

    This class provides an interface for retrieving market data from various sources,
    such as Yahoo Finance and the Federal Reserve Economic Data (FRED) system.

    Features:
    ---------
    - Extract historical equity prices from Yahoo Finance.
    - Fetch interest rate data from FRED.
    - Support for both single and multiple tickers.
    - Provides statistical analysis utilities.

    Parameters:
    -----------
    equity_tickers : str or List[str], optional, default="TSLA"
        The ticker symbol(s) of the equities to fetch data for.

    instrument_id : str, optional, default='1Y'
        The identifier for economic indicators (e.g., Treasury yields, inflation rates).

    start_period : str, optional, default=None
        The start date for data retrieval (YYYY-MM-DD format).

    end_period : str, optional, default=None
        The end date for data retrieval (YYYY-MM-DD format). If `None`, fetches the latest available data.

    Methods:
    --------
    __init__(equity_tickers: str | List[str], instrument_id: str, start_period: str, end_period: str)
        Initializes the extractor with the specified tickers, instrument ID, and time range.

    extract_equity_price(column_name="Close") -> Dict[str, pd.DataFrame | List]
        Extracts historical market data for a given ticker or list of tickers.

    fetch_interest_rate_data() -> float | pd.DataFrame
        Fetches interest rate or economic indicator data from the FRED database.

    df_info(df: pd.DataFrame) -> pd.DataFrame
        Displays and returns basic statistical information about the extracted time series.

    basic_statistic(df: pd.DataFrame)
        Prints metadata and summary statistics of the provided DataFrame.

    Raises:
    -------
    NotImplementedError:
        - If unsupported data retrieval scenarios are encountered.

    RuntimeError:
        - If data fetching fails due to network issues or incorrect API keys.

    Usage:
    ------
    ```python
    extractor = MarketDataExtractor(equity_tickers=["AAPL", "MSFT"], start_period="2023-01-01", end_period="2023-12-31")
    stock_data = extractor.extract_equity_price()

    interest_rate = MarketDataExtractor(instrument_id="FEDFUNDS", start_period="2023-01-01", end_period="2023-01-01")
    rate_value = interest_rate.fetch_interest_rate_data()
    ```
    """

    def __init__(self, data_provider: str,
                 tickers: (str, List[str]) = "TSLA",
                 start_period: str = None,
                 end_period: str = None):
        """
        Initializes the MarketDataExtractor.

        Parameters:
        -----------
        equity_tickers : str or List[str], optional, default="TSLA"
            The ticker symbol(s) of the equities to fetch data for.

        instrument_id : str, optional, default='1Y'
            The identifier for economic indicators (e.g., Treasury yields, inflation rates).

        start_period : str, optional, default=None
            The start date for data retrieval (YYYY-MM-DD format).

        end_period : str, optional, default=None
            The end date for data retrieval (YYYY-MM-DD format).
        """
        self.__data_provider = data_provider
        self.__tickers = tickers or []
        self.__start_period = start_period
        self.__end_period = end_period
        self.extracted_data = None

    # ===========================================
    # REGION: Setters
    # ===========================================
    def set_data_provider(self, data_provider):
        self.__data_provider = data_provider

    def set_tickers(self, tickers):
        self.__tickers = tickers

    def set_start_period(self, start_period):
        self.__start_period = start_period

    def set_end_period(self, end_date):
        self.__end_period = end_date

    def set_data(self, data: dict | pd.DataFrame):
        self.extracted_data = data

    # ===========================================
    # END REGION: Setters
    # ===========================================

    # ===========================================
    # REGION: Getters
    # ===========================================
    @property
    def get_data_provider(self):
        return self.__data_provider

    @property
    def get_tickers(self):
        return self.__tickers

    @property
    def get_start_period(self):
        return self.__start_period

    @property
    def get_end_period(self):
        return self.__end_period

    # ===========================================
    # END REGION: Getters
    # ===========================================
    @abc.abstractmethod
    def fetch_data(self):
        """Abstract method to be implemented in child class to fetch market data from various sources."""
        pass


class YahooFinanceExtractor(MarketDataExtractor):
    def __init__(self, start_date, end_date, tickers):
        super().__init__("YahooFinance", start_date, end_date, tickers)

    def fetch_data(self,
                   column_name="Close",
                   offset='1d') -> Dict[str, pd.DataFrame | List]:
        # TODO refactor this method!
        """
        Extracts historical market data from Yahoo Finance.

        This method fetches the specified column of historical market data (e.g., "Close" prices)
        over the defined time period. It supports different cases:

        - Multiple tickers over a time range.
        - A single ticker at a specific date.
        - Fetching the latest available price from a start date.

        Parameters:
        -----------
        column_name : str, optional, default="Close"
            The column name to extract from Yahoo Finance data.

        Returns:
        --------
        dict :
            A dictionary where keys are ticker symbols and values are either:
            - DataFrames (for historical ranges).
            - Lists containing a date and a price (for single timestamps).

        Raises:
        -------
        NotImplementedError:
            If an unsupported extraction case is encountered.
        """
        if isinstance(self.get_tickers, str):
            tickers = [self.get_tickers]
        else:
            tickers = self.get_tickers

        underlier_prices_dict = {}

        # Fetching data for each ticker
        for ticker in tickers:
            if self.get_start_period and self.get_end_period and self.get_start_period != self.get_end_period:
                df = yf.Ticker(ticker).history(start=self.get_start_period, end=self.get_end_period)[[column_name]]
                underlier_prices_dict[ticker] = df

            elif self.get_start_period and (
                    self.get_end_period is None or self.get_start_period == self.get_end_period):
                # Determine the actual end period only if None using QuantLib
                if self.get_end_period is None:
                    ql_start_date = ql.DateParser.parseISO(self.get_start_period)
                    # if we choose days as offset we move one day forward
                    if offset.endswith("d"):
                        days_back = int(offset[:-1])
                        ql_end_date = ql_start_date + ql.Period(days_back, ql.Days)
                    # if we choose months as offset we move backwards
                    elif offset.endswith("mo"):
                        months_back = int(offset[:-2])
                        ql_end_date = ql_start_date - ql.Period(months_back, ql.Months)
                    else:
                        raise ValueError("Unsupported offset format. Use 'Xd' for days or 'Xmo' for months.")

                    computed_end_period = ql_end_date.ISO()
                else:
                    computed_end_period = self.get_end_period
                if offset.endswith("d"):
                    df = yf.Ticker(ticker).history(start=self.get_start_period, end=computed_end_period)
                else:
                    df = yf.Ticker(ticker).history(start=computed_end_period, end=self.get_start_period)

                if not df.empty:
                    underlier_prices_dict[ticker] = [df.index[0].date(), df.iloc[0][column_name]]
                else:
                    underlier_prices_dict[ticker] = None  # Handle case where data isn't available
            else:
                raise NotImplementedError("Unsupported extraction case.")

        return underlier_prices_dict


class FREDExtractor(MarketDataExtractor):
    def __init__(self, start_date, end_date, tickers):
        super().__init__("FRED", start_date, end_date, tickers)
        self.__api_key = CONFIG.FRED_API_KEY

    def fetch_data(self) -> float | pd.DataFrame:
        """
        Fetches interest rate data from FRED.

        This method retrieves economic indicators such as Treasury Yields, CPI, and Federal Funds Rate.

        Returns:
        --------
        float or pd.DataFrame :
            - If fetching data for a single date, returns a float value.
            - Otherwise, returns a DataFrame containing time-series data.

        Raises:
        -------
        RuntimeError:
            If data retrieval fails due to incorrect API configuration or network issues.
        """

        try:
            if self.get_start_period == self.get_end_period:

                # Fetch data from FRED
                data = web.DataReader(FRED_SERIES_IDS[self.get_tickers],
                                      "fred", self.get_start_period,
                                      self.get_end_period,
                                      api_key=CONFIG['FRED_API_KEY'])
                return data.values[0][0] / 100
            else:
                NotImplementedError("Another cases are not implemented yet")
        except Exception as e:
            raise RuntimeError(f"Failed to fetch data: {e}")


class PolygonIoExtractor(MarketDataExtractor):

    """
    Description
    -----------
    Extracts historical equity data from Polygon.io.

    This class retrieves time-series market data for specified tickers using the Polygon.io API.
    It fetches data within a given date range and stores it as a Pandas DataFrame.

    Parameters:
    -----------
    start_date : str
        The start date for data retrieval (YYYY-MM-DD format).

    end_date : str
        The end date for data retrieval (YYYY-MM-DD format).

    tickers : str or List[str]
        A single stock ticker or a list of tickers to extract historical data.

    Attributes:
    -----------
    __api_key : str
        The API key used for authenticating requests to Polygon.io.

    __client : polygon.RESTClient
        The client instance for interacting with the Polygon.io API.

    Methods:
    --------
    fetch_data() -> Dict[str, pd.DataFrame]
        Fetches historical market data for the specified tickers and time range.
        Returns a dictionary where keys are tickers and values are Pandas DataFrames
        containing Open, High, Low, Close, and Volume data.

    Raises:
    -------
    ValueError:
        If no tickers are provided.

    RuntimeError:
        If the API request fails due to an invalid key or network issues.

    Example Usage:
    --------------
    ```python
    extractor = PolygonIoExtractor(start_date="2025-02-18", end_date="2025-03-12", tickers=["AAPL", "GOOGL"])
    extractor.fetch_data()
    ```
    """


    def __init__(self, start_date, end_date, tickers):
        super().__init__("PolygonIO", start_date, end_date, tickers)
        self.__api_key = CONFIG["POLYGON_IO_API_KEY"]
        self.__client = RESTClient(self.__api_key)

    def get_company_details(self, ticker: str) -> pd.DataFrame:
        """
        Fetch company information such as name, sector, industry, and description from Polygon.io.

        Returns:
        --------
        dict :
            A dictionary containing company details.

        Raises:
        -------
        RuntimeError:
            If the API request fails due to network issues.
        """
        if not self.get_tickers:
            raise ValueError("No tickers specified for Polygon.io extractor.")

        company_info = {}
        for ticker in self.get_tickers:
            try:
                response = self.__client.get_ticker_details(ticker)
                if not response:
                    print(f"No company info found for {ticker}.")
                    continue

                # Extract relevant fields
                company_info[ticker] = {
                    "name": response.name,
                    "description": response.description,
                    "market": response.market,
                    "sic_code": response.sic_code,
                    "sic_description": response.sic_description,
                    "address": response.address.address1,
                    "city": response.address.city,
                    "currency_name": response.currency_name,
                    "phone_number": response.phone_number,
                    "homepage_url": response.homepage_url,
                    "market_cap": response.market_cap,
                    "employees": response.total_employees,
                    "list_date": response.list_date,
                    "exchange": response.primary_exchange,
                    "logo_url": response.branding.logo_url,
                    "icon_url": response.branding.icon_url
                }

            except Exception as e:
                print(f"Error fetching company info for {ticker} from Polygon.io: {e}")

        return company_info

    def fetch_data(self):
        """Fetch historical stock data from Polygon.io."""
        if not self.get_tickers:
            raise ValueError("No tickers specified for Polygon.io extractor.")

        all_data = dict()
        for ticker in self.get_tickers:
            aggs = self.__client.get_aggs(
                ticker=ticker, multiplier=1, timespan="day",
                from_=self.get_start_period, to=self.get_end_period
            )
            df = pd.DataFrame(aggs)
            df["date"] = pd.to_datetime(df["timestamp"], unit="ms").dt.date
            df.set_index("date", inplace=True)
            df["ticker"] = ticker
            all_data[ticker] = df

        for ticker in all_data.keys():
            if all_data[ticker].empty:
                print(f"No data available for {ticker}")
            else:
                print(f"For {ticker} and for time window {self.get_start_period} to {self.get_end_period}"
                      f" {len(all_data[ticker])} has been extracted.")

        print(f"Fetching data from Polygon.io has been completed!!")


class DataProviderFactory:
    """Factory to create the appropriate MarketDataExtractor instance."""

    @staticmethod
    def get_extractor(provider, start_date, end_date, tickers):
        """
         Description
         -----------

         Factory method to return an appropriate MarketDataExtractor instance
         based on the specified provider.

         Parameters:
         -----------
         provider : str
             The name of the data provider. Must be one of:
            -"YahooFinance" : Fetches stock market data from Yahoo Finance.

            -"FRED" : Fetches economic indicators from Federal Reserve Economic Data (FRED).

            -"PolygonIO" : Fetches stock market data from Polygon.io.

         start_date : str
             The start date of the data extraction period (format: "YYYY-MM-DD").

         end_date : str
             The end date of the data extraction period (format: "YYYY-MM-DD").

         tickers : list[str]
             A list of stock symbols or economic indicators to extract.

         Returns:
         --------
         MarketDataExtractor
             An instance of the appropriate subclass of MarketDataExtractor
             (YahooFinanceExtractor, FREDExtractor, or PolygonIOExtractor).

         Raises:
         -------
         ValueError
             If the provided `provider` is not one of the available extractors.

         Examples:
         ---------
         >>> extractor = DataProviderFactory.get_extractor("YahooFinance", "2025-02-18", "2025-03-12", ["AAPL", "MSFT"])
         >>> extractor.fetch_data()
         >>> print(extractor.data.head())

         >>> extractor = DataProviderFactory.get_extractor("FRED", "2025-01-01", "2025-03-12", ["FRED/GDP"])
         >>> extractor.fetch_data()
         >>> print(extractor.data.head())

        """

        extractors = {
            "YahooFinance": YahooFinanceExtractor,
            "FRED": FREDExtractor,
            "PolygonIO": PolygonIoExtractor
        }

        if provider not in extractors:
            raise ValueError(f"Invalid provider: {provider}. Choose from {list(extractors.keys())}")

        return extractors[provider](start_date, end_date, tickers)
