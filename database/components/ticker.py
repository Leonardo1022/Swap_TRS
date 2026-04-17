from database.connection import conectar
from sqlite3 import Error
import pandas as pd

def selecionar_tickers(bolsa: str):
    sql_query = """SELECT ti_ticker 
                   FROM Ticker 
                   WHERE bo_bolsa = ?"""
    try:
        with conectar() as conn:
            df = pd.read_sql_query(sql_query, conn, params=(bolsa,))
            print(f"Sucesso ao selecionar os tickers da bolsa {bolsa}")
            return df["ti_ticker"].tolist()
    except Error as e:
        print(f"Erro ao selecionar bolsa: {e}")
        return None