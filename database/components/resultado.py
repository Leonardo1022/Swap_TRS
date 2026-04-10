from database.connection import conectar
from sqlite3 import Error
import pandas as pd

def inserir_resultado(contrato: int, data: str, lucro: float, custo: float, montante: float):
    sql_insert = """
                 INSERT INTO Resultado(con_id, re_data, re_lucro, re_custo, re_montante)
                 VALUES (?, ?, ?, ?, ?);
                 """
    try:
        with conectar() as conn:
            conn.execute(sql_insert, (contrato, data, lucro, custo, montante))
            conn.commit()
            print(f"Resultado adicionado (contrato:{contrato}, data:{data}, lucro:{lucro}, custo:{custo}, montante:{montante})")
    except Error as e:
        print(f"Erro ao inserir resultado: {e}")

def selecionar_resultado_valores(contrato: int):
    sql_query = """
                SELECT re_data, re_lucro, re_custo, re_montante FROM Resultado 
                WHERE con_id = ?
                """
    try:
        with conectar() as conn:
            return pd.read_sql_query(sql_query, conn, params=(contrato,))
    except Error as e:
        print(f"Erro ao selecionar tabela resultado: {e}")
        return None

def selecionar_resultado_mensal_contrato(contrato: int, data: str):
    sql_query = """"""