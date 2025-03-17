# alpha-wolf
This project implements an asset management system based on the Markowitz Modern Portfolio Theory (MPT). The application helps investors find the optimal portfolio by balancing risk and return. It uses historical market data, calculates efficient frontiers, and identifies the portfolio with the best risk-adjusted returns.
# Project Structure
```
📂 .git
📂 .idea
📂 base
  📄 __init__.py
  📄 asgi.py
  📄 settings.py
  📄 urls.py
  📄 wsgi.py
📂 efficient_frontier
  📄 __init__.py
  📂 __pycache__
  📄 admin.py
  📄 apps.py
  📂 migrations
    📄 0001_initial.py
    📄 0002_equityprice_ticker_delete_company_and_more.py
    📄 __init__.py
    📂 __pycache__
  📄 models.py
  📂 services
    📄 __init__.py
    📂 __pycache__
    📄 data_preparation_client.py
    📄 market_data_client.py
  📄 tests.py
  📄 views.py
📂 jupyter
📄 main.py
📄 manage.py
📂 theme
  📄 __init__.py
  📄 apps.py
📂 tool_kit
  📂 __pycache__
  📄 config_loader.py
  📄 database_api.py
  📄 plots.py
📂 venv
```
# Contact
If you have questions or suggestions, feel free to reach out:
* Email: krzysiek.bienias.kr@email.com
*  GitHub Issues: Submit an Issue