import yfinance as yf
import database as db

from datetime import date, datetime, timedelta

#from form import bolsa_moeda_str

if __name__ == "__main__":
    ticker_obj = yf.Ticker('PETR4.SA')
    ticker_info = ticker_obj.info
    for key, value in ticker_info.items():
        print(f"{key}: {value}")