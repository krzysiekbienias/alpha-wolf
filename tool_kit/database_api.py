from polygon import RESTClient
from efficient_frontier.models import Ticker, EquityPrice
from django.db import IntegrityError
from tool_kit.config_loader import CONFIG
import pandas as pd
import time


# Set your Polygon API Key

def fetch_and_store_company_info(ticker_symbol):
    """
    Fetch and update company information from Polygon.io based on the given ticker.

    Parameters:
    -----------
    ticker_symbol : str
        The stock ticker symbol (e.g., "AAPL").

    Returns:
    --------
    CompanyInfo instance or None
        The updated or created CompanyInfo object, or None if the request fails.
    """
    client = RESTClient(CONFIG["POLYGON_IO_API_KEY"])
    request_count = 0

    try:
        response = client.get_ticker_details(ticker_symbol)

        if not response:
            print(f"No data found for {ticker_symbol}.")
            return None

        # Extract relevant fields
        company_data = {
            "name": response.name,
            "description": response.description,
            "market": response.market,
            "sic_code": response.sic_code,
            "sic_description": response.sic_description,
            "address": response.address.address1,
            "city": response.address.city,
            "currency_name": response.currency_name
        }

        try:
            # Update or create company information in the database
            company_obj, created = Ticker.objects.update_or_create(
                ticker=ticker_symbol,
                defaults=company_data
            )
            action = "Created" if created else "Updated"
            print(f"{action} company info for {ticker_symbol} successfully.")
            return company_obj
        except IntegrityError as e:
            print(f"Database error while storing company info for {ticker_symbol}: {e}")
            # **RATE LIMIT HANDLING: Sleep after every 5 requests**
        request_count += 1
        if request_count >= 5:
            print(f"Reached 5 API calls. Sleeping for 70 seconds...")
            time.sleep(70)  # Respect API rate limit
            request_count = 0  # Reset counter after sleep
    except Exception as e:
        print(f"Error fetching company info for {ticker_symbol} from Polygon.io: {e}")
        return None


def fetch_and_store_equity_prices(ticker_symbols, start_date, end_date):
    """
    Fetch and store historical equity prices from Polygon.io.
    Implements rate limit handling (5 requests per minute).

    Parameters:
    -----------
    ticker_symbols : list[str]
        List of stock ticker symbols (e.g., ["AAPL", "MSFT"]).
    start_date : str
        The start date for fetching data (YYYY-MM-DD).
    end_date : str
        The end date for fetching data (YYYY-MM-DD).

    Returns:
    --------
    None
    """
    client = RESTClient(CONFIG["POLYGON_IO_API_KEY"])
    request_count = 0  # Track API request count

    for index, ticker_symbol in enumerate(ticker_symbols, start=1):
        try:
            # Ensure the ticker exists in the DB
            ticker_obj, created = Ticker.objects.get_or_create(ticker=ticker_symbol)

            # Fetch historical data
            aggs = client.get_aggs(
                ticker=ticker_symbol,
                multiplier=1,
                timespan="day",
                from_=start_date,
                to=end_date
            )

            if not aggs:
                print(f"No data found for {ticker_symbol}.")
                continue

            df = pd.DataFrame(aggs)
            df["date"] = pd.to_datetime(df["timestamp"], unit="ms").dt.date  # Convert timestamp to date only

            # Store data in the database
            for _, row in df.iterrows():
                try:
                    EquityPrice.objects.update_or_create(
                        ticker=ticker_obj,
                        date=row['date'],  # Ensure correct date format
                        defaults={
                            "open_price": row["open"],
                            "high_price": row["high"],
                            "low_price": row["low"],
                            "close_price": row["close"],
                            "volume": row["volume"],
                        },
                    )
                except IntegrityError as e:
                    print(f"Database error while storing equity prices for {ticker_symbol}: {e}")

            print(f"Equity price data for {ticker_symbol} saved successfully!")

            # **Rate Limit Handling: Sleep after every 5 requests**
            request_count += 1
            if request_count >= 5:
                print(f"Reached 5 API calls. Sleeping for 70 seconds...")
                time.sleep(70)  # Respect API rate limit
                request_count = 0  # Reset counter after sleep

        except Exception as e:
            print(f"Error fetching equity prices for {ticker_symbol} from Polygon.io: {e}")
