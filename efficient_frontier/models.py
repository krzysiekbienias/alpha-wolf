from django.db import models


# Create your models here.
class Ticker(models.Model):
    """
    Represents a stock ticker with metadata retrieved from Polygon.io.

    This model stores essential information about publicly traded companies,
    including their stock symbol, name, industry classification, market details,
    and other relevant metadata.

    Fields:
    -------
    ticker : CharField (max_length=10, unique=True)
        The stock symbol used to identify the company (e.g., "AAPL", "TSLA").

    name : CharField (max_length=255)
        The full company name associated with the stock ticker.

    description : TextField (null=True, blank=True)
        A detailed description of the company.

    market : CharField (max_length=50, null=True, blank=True)
        The market in which the stock is traded (e.g., "stocks", "ETFs").

    sic_code : CharField (max_length=10, null=True, blank=True)
        The Standard Industry Classification (SIC) code representing the company’s industry.

    sic_description : CharField (max_length=255, null=True, blank=True)
        A textual description of the industry based on the SIC code.

    address : CharField (max_length=255, null=True, blank=True)
        The primary business address of the company.

    city : CharField (max_length=100, null=True, blank=True)
        The city in which the company is headquartered.

    currency_name : CharField (max_length=20, null=True, blank=True)
        The currency in which the stock is traded (e.g., "USD", "EUR").

    last_updated : DateTimeField (auto_now=True)
        A timestamp indicating when the ticker data was last updated.

    Meta:
    -----
    - An index is created on the `ticker` field to optimize search queries.

    Methods:
    --------
    __str__() -> str:
        Returns a human-readable string representation of the ticker.
    """
    ticker = models.CharField(max_length=10, unique=True)  # Stock symbol (e.g., "AAPL")
    name = models.CharField(max_length=255)  # Full company name
    description = models.TextField(null=True, blank=True)  # Company description
    market = models.CharField(max_length=50, null=True, blank=True)  # Market (e.g., "stocks")
    sic_code = models.CharField(max_length=10, null=True, blank=True)  # Standard Industry Code (SIC)
    sic_description = models.CharField(max_length=255, null=True, blank=True)  # Industry description
    address = models.CharField(max_length=255, null=True, blank=True)  # Company address
    city = models.CharField(max_length=100, null=True, blank=True)  # City
    currency_name = models.CharField(max_length=20, null=True, blank=True)  # Currency (e.g., "usd")
    last_updated = models.DateTimeField(auto_now=True)  # Auto-update timestamp

    class Meta:
        indexes = [
            models.Index(fields=["ticker"]),  # Optimized indexing for queries by ticker
        ]

    def __str__(self):
        return f"{self.ticker} - {self.name}"


class EquityPrice(models.Model):
    """
    Stores historical equity prices for multiple stock tickers.

    This model maintains daily trading data for each stock, including open, high,
    low, and close prices, as well as trading volume. Each record is linked to a
    specific ticker.

    Fields:
    -------
    ticker : ForeignKey (Ticker, on_delete=models.CASCADE)
        A foreign key linking the price entry to the corresponding Ticker.

    date : DateField
        The date for which the trading data is recorded.

    open_price : DecimalField (max_digits=10, decimal_places=2)
        The stock's opening price on the specified date.

    high_price : DecimalField (max_digits=10, decimal_places=2)
        The highest price reached during the trading day.

    low_price : DecimalField (max_digits=10, decimal_places=2)
        The lowest price reached during the trading day.

    close_price : DecimalField (max_digits=10, decimal_places=2)
        The closing price of the stock at the end of the trading session.

    volume : BigIntegerField
        The total number of shares traded during the day.

    Meta:
    -----
    - The `unique_together` constraint ensures that each (ticker, date) combination is unique.
    - An index is created on the `date` field for faster date-based queries.
    - Another index is created on `(ticker, date)` for efficient searches by ticker and date.

    Methods:
    --------
    __str__() -> str:
        Returns a human-readable string representation of the equity price record.
    """
    ticker = models.ForeignKey(Ticker, on_delete=models.CASCADE)  # Relationship to Ticker
    date = models.DateField()  # Trading date
    open_price = models.DecimalField(max_digits=10, decimal_places=2)
    high_price = models.DecimalField(max_digits=10, decimal_places=2)
    low_price = models.DecimalField(max_digits=10, decimal_places=2)
    close_price = models.DecimalField(max_digits=10, decimal_places=2)
    volume = models.BigIntegerField()

    class Meta:
        unique_together = ("ticker", "date")  # Prevents duplicate entries
        ordering = ["-date"]  # Latest data first
        indexes = [
            models.Index(fields=["date"]),  # Optimizes date queries
            models.Index(fields=["ticker", "date"]),  # Optimizes queries for a ticker on a given date
        ]

    def __str__(self):
        return f"{self.ticker.symbol} - {self.date}"
