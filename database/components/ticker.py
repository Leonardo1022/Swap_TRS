from database.connection import conectar
from sqlite3 import Error
import pandas as pd

def selecionar_tickers(bolsa: str) -> list[str]:
    sql_query = """SELECT ti_ticker 
                   FROM Ticker 
                   WHERE bo_bolsa = ?"""
    try:
        with conectar() as conn:
            coluna = conn.execute(sql_query, (bolsa,)).fetchall()
            print(f"Sucesso ao selecionar os tickers da bolsa {bolsa}")
            return [linha["ti_ticker"] for linha in coluna]
    except Error as e:
        print(f"Erro em selecionar_tickers: {e}")
        return []