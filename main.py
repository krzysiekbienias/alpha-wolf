
import os
import django
import pandas as pd
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'base.settings')
django.setup()
from efficient_frontier.services.yahoo_finance_client import YahooDataExtractor,import_data_from_csv


if __name__ == '__main__':
    yahoo_extractor: dict = YahooDataExtractor(tickers=['TSLA','AAPL'], start_period='2023-01-24',
                                               end_period='2025-01-24').extract_data()
    print("Hello World")