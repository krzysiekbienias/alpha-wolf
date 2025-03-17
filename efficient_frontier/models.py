from django.db import models


# Create your models here.
class Ticker(models.Model):
    """
    Stores unique stock tickers.
    """
    symbol = models.CharField(max_length=10, unique=True)  # e.g., 'AAPL', 'MSFT'
    name = models.CharField(max_length=100, null=True, blank=True)  # Optional: Company Name
    created_at = models.DateTimeField(auto_now_add=True)  # When the ticker was added

    def __str__(self):
        return self.symbol  # Sector the company belongs to


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
