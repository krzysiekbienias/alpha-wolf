from django.db import models


# Create your models here.
class Ticker(models.Model):
    """
    Stores metadata for stock tickers retrieved from Polygon.io.
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
    Stores historical equity prices for multiple tickers.
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
