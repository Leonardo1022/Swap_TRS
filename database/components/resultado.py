from database.utils import converter_data
from database.connection import conectar
from database.models import Resultado
from sqlite3 import Error
import pandas as pd

def inserir_resultado(contrato: int, data: str, lucro: int, custo: int, montante: int) -> None:
    sql_insert = """
                 INSERT INTO Resultado(con_id, re_data, re_lucro, re_custo, re_montante)
                 VALUES (?, ?, ?, ?, ?);
                 """
    try:
        with conectar() as conn:
            conn.execute(sql_insert, (contrato, data, lucro, custo, montante))
            conn.commit()
            print(f"Resultado adicionado (contrato:{contrato}, data:{data}, lucro:{lucro}, custo:{custo/1000000}, montante:{montante/1000000})")
    except Error as e:
        print(f"Erro ao inserir resultado: {e}")

def selecionar_resultado_valores(contrato: int) -> list[Resultado] | []:
    sql_query = """
                SELECT * FROM Resultado 
                WHERE con_id = ?
                """
    try:
        with conectar() as conn:
            tabela = conn.execute(sql_query, (contrato,)).fetchall()
            if tabela:
                return [Resultado(con_id=l["con_id"], re_data=l["re_data"], re_lucro=l["re_lucro"], re_custo=l["re_custo"], re_montante=l["re_montante"]) for l in tabela]
            return []
    except Error as e:
        print(f"Erro ao selecionar tabela resultado: {e}")
        return []

def atualizar_resultado_lucro(lucro: int, contrato: int, data: str) -> None:
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
            print(f"Adicionado {lucro/1000000} em resultado com contrato {contrato}")
    except Error as e:
        print(f"Erro em atualizar_resultado_lucro: {e}")

def atualizar_resultado_montante(montante: int, contrato: int, data: str) -> None:
    sql_update = """
                 UPDATE Resultado SET re_montante = ? 
                    WHERE con_id = ? AND re_data > ?;
                 """
    try:
        with conectar() as conn:
            conn.execute(sql_update, (montante, contrato, data))
            conn.commit()
            print(f"Sucesso em atualizar_resultado_montante.\nMontante: {montante/1000000}, Contrato: {contrato}, Data: {data}")
    except Error as e:
        print(f"Erro em atualizar_resultado_montante: {e}")