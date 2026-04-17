from database.utils import converter_data
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

def atualizar_resultado_lucro(lucro: float, contrato: int, data: str):
    sql_update = """
                 UPDATE Resultado SET re_lucro = re_lucro + ? 
                    WHERE con_id = ? 
                      AND STRFTIME('%Y', re_data) = ? 
                      AND STRFTIME('%m', re_data) = ?;
                 """
    try:
        with conectar() as conn:
            data_convertida = converter_data(data)
            data_mes_str = f"{data_convertida.month:02d}"
            data_ano_str = str(data_convertida.year)
            conn.execute(sql_update, (lucro, contrato, data_ano_str, data_mes_str))
            conn.commit()
            print(f"Adicionado {lucro} em resultado com contrato {contrato}")
    except Error as e:
        print(f"Erro em atualizar_resultado_lucro: {e}")