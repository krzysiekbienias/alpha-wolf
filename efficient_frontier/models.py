from django.db import models

# Create your models here.
class Company(models.Model):
    id = models.AutoField(primary_key=True)  # Auto-incrementing primary key
    name = models.CharField(max_length=255, unique=True)  # Company name, unique to avoid duplicates
    ticker = models.CharField(max_length=10, unique=True)  # Stock ticker, unique to ensure no duplicates
    sector = models.CharField(max_length=100)  # Sector the company belongs to

    def __str__(self):
        return f"{self.name} ({self.ticker})"