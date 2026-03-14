import yfinance as yf
from datetime import datetime, timedelta
if __name__ == "__main__":
    data_str = "2026-03-10"
    data = datetime.strptime(data_str, "%Y-%m-%d")
    ticker_obj = yf.Ticker("V")
    info = ticker_obj.info
    print(info["longName"])
    data = ticker_obj.history(start=data, end=data+timedelta(days=1))
    print(data["Close"].values)