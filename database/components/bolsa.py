from database.connection import conectar
from sqlite3 import Error

def selecionar_bolsa(bolsa: str):
    sql_query = "SELECT * FROM Bolsa WHERE bo_bolsa = ?"
    try:
        with conectar() as conn:
            linha = conn.execute(sql_query, (bolsa,)).fetchone()
            print(dict(linha))
            return dict(linha) if linha else {}
    except Error as e:
        print(f"Erro ao selecionar bolsa: {e}")
        return None

def selecionar_bolsas():
    sql_query = "SELECT bo_bolsa FROM Bolsa"
    try:
        with conectar() as conn:
            linhas = conn.execute(sql_query).fetchall()
            print("sucesso")
            return [linha["bo_bolsa"] for linha in linhas]
    except Error as e:
        print(f"Erro ao retornar bolsas: {e}")
        return None