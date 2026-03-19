import yfinance as yf
import database as db
from datetime import date, datetime, timedelta
if __name__ == "__main__":
    #contrato = db.selecionar_contrato(1)
    #print(contrato["con_mont"])
    data_registro = date.strptime("2025-07-31", "%Y-%m-%d")
    print(data_registro)
    if data_registro.month < date.today().month or data_registro.year < date.today().year:
        print("A data está atrasada")
        data_registro = date.today()
        number = db.ultimo_resultado_contrato(3)
        print(number)
    data_str = "2026-03-10"
    data = datetime.strptime(str(date.today()), "%Y-%m-%d")
    ticker_obj = yf.Ticker("V")
    info = ticker_obj.info
    print(info["longName"])
    data = ticker_obj.history(start=data, end=data+timedelta(days=1))
    print(data["Close"].values)