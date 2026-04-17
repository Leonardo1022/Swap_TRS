from database.connection import conectar
import pandas as pd
from sqlite3 import Error

def inserir_acao(contrato: int, bolsa: str, ticker: str, quantidade: int, montante: float):
    sql_insert = """INSERT INTO Acao(con_id, bo_bolsa, ti_ticker, ac_quantidade, ac_montante)
                    VALUES (?, ?, ?, ?, ?)"""
    try:
        with conectar() as conn:
            conn.execute(sql_insert, (contrato, bolsa, ticker, quantidade, montante))
            conn.commit()
            print(f"Ação adicionada: {ticker} (quantidade: {quantidade}, montante: {montante})")
    except Error as e:
        print(f"Erro ao inserir acao: {e}")
        print(f"ID:{contrato} Ação: {ticker}, bolsa {bolsa} (quantidade: {quantidade}, montante: {montante})")

def selecionar_acao_ticker(ticker: str) -> dict:
    sql_query = "SELECT * FROM Acao WHERE ti_ticker = ?;"
    try:
        with conectar() as conn:
            linha = conn.execute(sql_query, (ticker,)).fetchone()
            return dict(linha) if linha else {}
    except Error as e:
        print(f"Erro ao selecionar acao por ticker: {e}")
        return {}

def selecionar_acao_qtd_acumulada(ticker: str) -> int:
    sql_query = "SELECT SUM(ac_quantidade) AS qtd_total FROM Acao WHERE ti_ticker = ?;"
    try:
        with conectar() as conn:
            linha = conn.execute(sql_query, (ticker,)).fetchone()
            return linha["qtd_total"]
    except Error as e:
        print(f"Erro ao selecionar a quantidade total do ticker {ticker}: {e}")
        return 0
"""
Recebe o id do contrato
Retorna uma lista de tickers no id do contrato
"""
def selecionar_acoes_contrato(contrato: int) -> pd.DataFrame:
    sql_query = """SELECT * FROM Acao WHERE con_id = ?"""
    try:
        with conectar() as conn:
            return pd.read_sql_query(sql_query, conn, params=(contrato,))
    except Error as e:
        print(f"Erro ao selecionar acao: {e}")
        return pd.DataFrame()
"""
Seleciona todas as ações registradas pelo usuário
"""
def selecionar_acoes():
    sql_query = "SELECT ti_ticker FROM Acao GROUP BY ti_ticker;"
    try:
        with conectar() as conn:
            df = pd.read_sql_query(sql_query, conn)
            return df["ti_ticker"].tolist()
    except Error as e:
        print(f"Erro ao selecionar ações: {e}")
        return []

def selecionar_acoes_bolsas():
    sql_query = "SELECT bo_bolsa FROM Acao GROUP BY bo_bolsa"
    try:
        with conectar() as conn:
            df = pd.read_sql_query(sql_query, conn)
            return df["bo_bolsa"].tolist()
    except Error as e:
        print(f"Erro ao selecionar bolsas de ações: {e}")
        return []
"""
Recebe o ticker alvo
Retorna os primeiros 5 tickers de ação registrados
"""
def selecionar_acao_primeiros_5_ticker(ticker: str):
    sql = """
        SELECT a.ac_quantidade, a.ac_montante, a.con_id, a.ti_ticker
            FROM Acao a
            JOIN Contrato c 
                ON a.con_id = c.con_id
        WHERE a.ti_ticker = ?
        ORDER BY c.con_abertura
            LIMIT 5;
    """
    with conectar() as conn:
        return pd.read_sql_query(sql, conn, params=(ticker,))
"""
Atualiza a quantidade na tabela de ação

"""


def atualizar_acao_quantidade(ticker: str, contrato: int, quantidade: int) -> int:
    select_sql = "SELECT ac_id FROM Acao WHERE ti_ticker = ? AND con_id = ?;"
    update_sql = "UPDATE Acao SET ac_quantidade = ? WHERE ac_id = ?;"

    try:
        with conectar() as conn:
            linha = conn.execute(select_sql, (ticker, contrato)).fetchone()
            if not linha:
                print(f"Ação {ticker} do contrato {contrato} não encontrada.")
                return -1

            conn.execute(update_sql, (quantidade, linha["ac_id"]))
            conn.commit()
            print(f"Ação {ticker} (ID={linha["ac_id"]}) atualizada para quantidade {quantidade}")
            return linha["ac_id"]

    except Error as e:
        print(f"Erro ao atualizar a quantidade da acao: {e}")
        return -1

def atualizar_acao(quantidade: int, montante: float, contrato:int, bolsa: str, ticker: str):
    sql_update ="""
               UPDATE Acao
               SET ac_quantidade = ac_quantidade + ?, ac_montante = ac_montante + ?
               WHERE con_id = ? AND bo_bolsa = ? AND ti_ticker = ?;
                """
    try:
        with conectar() as conn:
            conn.execute(sql_update, (quantidade, montante, contrato, bolsa, ticker))
            conn.commit()
            print(f"atualizada a ação {ticker} da {bolsa} do contrato {contrato}, adicionados {quantidade} no valor de {montante}")
            return True
    except Error as e:
        print(f"Erro ao atualizar acao: {e}")