from database.connection import conectar
from sqlite3 import Error
from database.models import Bolsa

"""
Recebe o nome de uma bolsa
Retorna as informações da bolsa em forma de Dict pré-definida
"""
def selecionar_bolsa(bolsa: str) -> Bolsa | None:
    sql_query = "SELECT * FROM Bolsa WHERE bo_bolsa = ?"
    try:
        with conectar() as conn:
            linha = conn.execute(sql_query, (bolsa,)).fetchone()
            print(f"Sucesso ao selecionar a bolsa {bolsa}")
            return Bolsa(bo_bolsa=linha["bo_bolsa"], bo_moeda=linha["bo_moeda"], bo_sufixo=linha["bo_sufixo"])
    except Error as e:
        print(f"Erro em selecionar_bolsa: {e}")
        return None
"""
Seleciona todas as bolsas registradas no BD
Retorna as bolsas em formato list com dicts
"""
def selecionar_bolsas() -> list[Bolsa]:
    sql_query = "SELECT * FROM Bolsa"
    try:
        with conectar() as conn:
            print("sucesso ao selecionar as bolsas")
            tabela = conn.execute(sql_query).fetchall()
            return [Bolsa(bo_bolsa=linha["bo_bolsa"], bo_moeda=linha["bo_moeda"], bo_sufixo=linha["bo_sufixo"]) for linha in tabela]
    except Error as e:
        print(f"Erro em selecionar_bolsas: {e}")
        return []