from database.connection import conectar
from sqlite3 import Error
import pandas as pd

def selecionar_bolsa(bolsa: str) -> dict:
    sql_query = "SELECT * FROM Bolsa WHERE bo_bolsa = ?"
    try:
        with conectar() as conn:
            linha = conn.execute(sql_query, (bolsa,)).fetchone()
            print(f"Sucesso ao selecionar a bolsa {bolsa}")
            return dict(linha) if linha else {}
    except Error as e:
        print(f"Erro ao selecionar bolsa: {e}")
        return {}
"""
Seleciona todas as bolsas registradas no BD
Retorna as bolsas em formato list
"""
def selecionar_bolsas():
    sql_query = "SELECT bo_bolsa FROM Bolsa"
    try:
        with conectar() as conn:
            print("sucesso ao selecionar as bolsas")
            df = pd.read_sql_query(sql_query, conn)
            return df["bo_bolsa"].tolist()
    except Error as e:
        print(f"Erro ao retornar bolsas: {e}")
        return None