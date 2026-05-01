from database.connection import conectar
from database.utils import converter_data
from database.models import Venda
from sqlite3 import Error, IntegrityError
import pandas as pd

def inserir_venda(quantidade: int, valor: int, data: str) -> int:
    sql_insert = """INSERT INTO Venda(ven_quantidade, ven_valor, ven_data)
                    VALUES (?, ?, ?)"""
    try:
        with conectar() as conn:
            cursor = conn.execute(sql_insert, (quantidade, valor, data))
            conn.commit()
            print(f'Venda adicionada {cursor.lastrowid}: {quantidade} em {data}')
            return cursor.lastrowid
    except IntegrityError as e:
        #Arrumar Trigger
        if "Quantidade vendida maior" in str(e):
            print(f"Erro: não é possível realizar a venda ({quantidade}). Quantidade excede a disponível.")
        else:
            print(f"Erro de integridade: {e}")
        return 0
    except Error as e:
        print(f"Erro ao inserir venda: {e}")
        return 0
"""
Recebe a data
Retornar as linhas de Movimentacao em formato de lista de dicionários 
com as vendas feitas no mesmo mês e ano da data
"""
def selecionar_venda_data(data: str) -> list[Venda] | []:
    sql_query = """
                SELECT * FROM Venda 
                WHERE STRFTIME('%m', ven_data) = ? 
                    AND STRFTIME('%Y', ven_data) = ?;
                """
    try:
        with conectar() as conn:
            data_convertida = converter_data(data)
            data_mes_str = f"{data_convertida.month:02d}"
            data_ano_str = str(data_convertida.year)
            tabela = conn.execute(sql_query, (data_mes_str, data_ano_str)).fetchall()
            if tabela:
                return [Venda(ven_id=l["ven_id"], ven_quantidade=l["ven_quantidade"], ven_valor=l["ven_valor"], ven_data=l["ven_data"]) for l in tabela]
            return []
    except Error as e:
        print(f"Erro em selecionar_venda_data: {e}")
        return []
"""
Retorna o lucro total de todos os contratos, pode retornar 0.00
Se erro retorna 0.00
"""
def selecionar_venda_lucro_total() -> int:
    sql_query = """
                SELECT COALESCE(SUM(ven_valor), 0) AS total 
                   FROM Venda;
                """
    try:
        with conectar() as conn:
            linha = conn.execute(sql_query).fetchone()
            return linha["total"]
    except Error as e:
        print(f"Erro em selecionar_venda_lucro_total: {e}")
        return 0
