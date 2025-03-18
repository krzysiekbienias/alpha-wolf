import os
import django
import pandas as pd

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'base.settings')
django.setup()
from efficient_frontier.services.market_data_client import DataProviderFactory, MarketDataExtractor
from typing import List
from tool_kit.database_api import fetch_and_store_company_info, fetch_and_store_equity_prices

if __name__ == '__main__':
    # ===========================================
    # REGION: Input
    # ===========================================
    provider = 'PolygonIO'
    company_tickers: List[str] | str | None = None
    start_time_window: str | None = '2025-03-07'
    end_time_window: str | None = '2025-03-17'

    # ===========================================
    # END REGION: Input
    # ===========================================
    extractor = DataProviderFactory.get_extractor(provider)
    extractor.set_start_period(start_time_window)
    extractor.get_fx_close_price(fx_pair="C:EURGBP",
                                 date=start_time_window)

    print("Hello World")
