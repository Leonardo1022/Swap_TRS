from database import atualizar_contrato_montante
from database.connection import conectar
from database.utils import converter_data
from sqlite3 import Error, IntegrityError
import pandas as pd

def inserir_movimentacao(contrato: int, bolsa: str, ticker: str, quantidade: int, valor: float, data: str, e_venda: int):
    sql_insert = """INSERT INTO Movimentacao(con_id, bo_bolsa, ti_ticker, mov_quantidade, mov_valor, mov_data, mov_e_venda)
                    VALUES (?, ?, ?, ?, ?, ?, ?)"""
    try:
        with conectar() as conn:
            conn.execute(sql_insert, (contrato, bolsa, ticker, quantidade, valor, data, e_venda))
            conn.commit()
            print(f'{"Venda" if e_venda == 1 else "Compra"} adicionada: {quantidade} {ticker} em {bolsa}')
    except IntegrityError as e:
        #Arrumar
        if "Quantidade vendida maior" in str(e):
            print(f"Erro: não é possível realizar a movimentação {ticker} ({quantidade}). Quantidade excede a disponível.")
        else:
            print(f"Erro de integridade: {e}")
    except Error as e:
        print(f"Erro ao inserir movimentação: {e}")
"""
Recebe o id do contrato e a data
Retornar as linhas de Movimentacao em formato de lista de dicionários 
com as vendas feitas no mesmo mês e ano da data
"""
def selecionar_movimentacao_contrato_mes(contrato: int, data: str):
    sql_query = """
                SELECT * FROM Movimentacao 
                WHERE con_id = ? 
                AND STRFTIME('%m', mov_data) = ? 
                AND STRFTIME('%Y', mov_data) = ?;
                """
    try:
        with conectar() as conn:
            data_convertida = converter_data(data)
            data_mes_str = f"{data_convertida.month: 02d}"
            data_ano_str = str(data_convertida.year)
            df = pd.read_sql_query(sql_query, conn, params=(contrato, data_mes_str, data_ano_str))
            return df
    except Error as e:
        print(f"Erro ao selecionar vendas por data: {e}")
"""
Retorna o lucro total de todos os contratos, pode retornar 0.00
Se erro retorna None
"""
def selecionar_movimentacao_lucro_total():
    sql_query = """SELECT COALESCE(SUM(mov_valor), 0.00) AS total 
                   FROM Movimentacao WHERE mov_e_venda = 1;"""
    try:
        with conectar() as conn:
            linha = conn.execute(sql_query).fetchone()
            return linha["total"]
    except Error as e:
        print(f"Erro ao selecionar lucro: {e}")
        return None