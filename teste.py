import yfinance as yf
if __name__ == "__main__":
    ticker_obj = yf.Ticker("V")
    info = ticker_obj.info
    print(info["longName"])
    data = ticker_obj.history(period="5d")
    print(data["Close"])