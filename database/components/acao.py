from database.connection import conectar
import pandas as pd
from sqlite3 import Error

def inserir_acao(contrato: int, bolsa: str, ticker: str, quantidade: int, montante: float):
    sql_insert = """INSERT INTO Acao(con_id, bo_bolsa, ti_ticker, ac_quantidade, ac_montante)
                    VALUES (?, ?, ?, ?, ?)"""
    try:
        with conectar() as conn:
            conn.execute(sql_insert, (contrato, bolsa, ticker, quantidade, montante))
            print(f"Ação adicionada: {ticker} (quantidade: {quantidade}, montante: {montante})")
    except Error as e:
        print(f"Erro ao inserir acao: {e}")
"""
Recebe o id do contrato
Retorna uma lista de tickers no id do contrato
"""
def selecionar_acao(contrato: int):
    sql_query = """SELECT * FROM Acao WHERE con_id = ?"""
    try:
        with conectar() as conn:
            return pd.read_sql_query(sql_query, conn, params=(contrato,))
    except Error as e:
        print(f"Erro ao selecionar acao: {e}")
        return None
"""
Recebe o ticker alvo
Retorna os primeiros 5 tickers de ação registrados
"""
def selecionar_acao_primeiros_5_ticker(ticker: str):
    sql = """
        SELECT a.ac_quantidade, a.ac_montante, a.con_id, a.ti_ticker
        FROM Acao a
        JOIN Contrato c ON a.con_id = c.con_id
        WHERE a.ti_ticker = ?
        ORDER BY c.con_abertura
        LIMIT 5;
    """
    with conectar() as conn:
        return pd.read_sql_query(sql, conn, params=(ticker,))
"""
Atualiza a quantidade na tabela de ação, o valor padrão para a quantidade é 0 caso tenha que zerá-lo

"""
def atualizar_acao_quantidade(ticker: str, contrato: int, quantidade: int):
    sql = """
        UPDATE Acao SET ac_quantidade = ?
        WHERE ti_ticker = ? AND con_id = ?
    """
    with conectar() as conn:
        conn.execute(sql, (quantidade, ticker, contrato))
        conn.commit()

def atualizar_acao(quantidade: int, montante: float, contrato:int, bolsa: str, ticker: str):
    sql_update ="""
               UPDATE Acao
               SET ac_quantidade = ac_quantidade + ?, ac_montante = ac_montante + ?
               WHERE con_id = ? AND bo_bolsa = ? AND ti_ticker = ?;
                """
    try:
        with conectar() as conn:
            conn.execute(sql_update, (quantidade, montante, contrato, bolsa, ticker))
            print(f"atualizada a ação {ticker} da {bolsa} do contrato {contrato}, adicionados {quantidade} no valor de {montante}")
            return True
    except Error as e:
        print(f"Erro ao atualizar acao: {e}")