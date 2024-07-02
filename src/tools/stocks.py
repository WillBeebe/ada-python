import json

import yfinance as yf
from requests.models import HTTPError


def get_stock_price(symbol):
  try:
    ticker = yf.Ticker(symbol).info
    market_price = ticker['currentPrice']
    previous_close_price=ticker['regularMarketPreviousClose']
    info = {
        "symbol":symbol,
        "current_price":market_price,
        "previous_close_price": previous_close_price
    }
    return json.dumps(info)
  except HTTPError:
    return None
