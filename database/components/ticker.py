from database.connection import conectar
from sqlite3 import Error
from database.models import Ticker

"""
Recebe o nome de uma bolsa
Retorna todos os tickers pertencentes a ela em formato de list com dict definido
"""
def selecionar_tickers(bolsa: str) -> list[Ticker]:
    sql_query = """
                SELECT ti_ticker, ti_empresa 
                   FROM Ticker 
                   WHERE bo_bolsa = ?;
                """
    try:
        with conectar() as conn:
            tabela = conn.execute(sql_query, (bolsa,)).fetchall()
            print(f"Sucesso ao selecionar os tickers da bolsa {bolsa}")
            if tabela:
                return [Ticker(ti_ticker=linha["ti_ticker"], ti_empresa=linha["ti_empresa"]) for linha in tabela]
            return []
    except Error as e:
        print(f"Erro em selecionar_tickers: {e}")
        return []