from stockdex import Ticker


def get_last_close(ticker):
    """Get the last close price of a stock ticker"""
    ticker = Ticker(ticker)
    price = ticker.yahoo_api_price(range="1d", dataGranularity="1d")[
        "close"
    ].iloc[-1]
    return price


last_price = get_last_close("AAPL")
print(last_price)
