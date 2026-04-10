from database.connection import conectar
from sqlite3 import Error

def selecionar_tickers(bolsa: str):
    sql_query = """SELECT ti_ticker 
                   FROM Ticker 
                   WHERE bo_bolsa = ?"""
    try:
        with conectar() as conn:
            linhas = conn.execute(sql_query, (bolsa,)).fetchall()
            return [linha["ti_ticker"] for linha in linhas]
    except Error as e:
        print(f"Erro ao selecionar bolsa: {e}")
        return None