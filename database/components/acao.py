from database.connection import conectar
from database.models import Acao
import pandas as pd
from sqlite3 import Error

def inserir_acao(contrato: int, bolsa: str, ticker: str, quantidade: int, montante: int, preco: int) -> None:
    sql_insert = """INSERT INTO Acao(con_id, bo_bolsa, ti_ticker, ac_quantidade, ac_montante, ac_preco)
                    VALUES (?, ?, ?, ?, ?, ?)"""
    try:
        with conectar() as conn:
            conn.execute(sql_insert, (contrato, bolsa, ticker, quantidade, montante, preco))
            conn.commit()
            print(f"Ação adicionada: {ticker} (quantidade: {quantidade}, montante: {montante}, preço: {preco})")
    except Error as e:
        print(f"Erro em inserir_acao: {e}")
        print(f"ID:{contrato} Ação: {ticker}, bolsa {bolsa} (quantidade: {quantidade}, montante: {montante}, preço: {preco})")

def selecionar_acao_ticker(ticker: str) -> Acao | None:
    sql_query = "SELECT * FROM Acao WHERE ti_ticker = ?;"
    try:
        with conectar() as conn:
            l = conn.execute(sql_query, (ticker,)).fetchone()
            if l:
                return Acao(ac_id=l["ac_id"], con_id=l["con_id"], bo_bolsa=l["bo_bolsa"], ti_ticker=l["ti_ticker"], ac_quantidade=l["ac_quantidade"], ac_preco=l["ac_preco"], ac_montante=l["ac_montante"])
            return None
    except Error as e:
        print(f"Erro ao selecionar acao por ticker: {e}")
        return None

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
def selecionar_acoes_contrato(contrato: int) -> list[Acao] | []:
    sql_query = """SELECT * FROM Acao WHERE con_id = ?"""
    try:
        with conectar() as conn:
            tabela = conn.execute(sql_query).fetchall()
            if tabela:
                return [
                    Acao(ac_id=l["ac_id"], con_id=l["con_id"],
                        bo_bolsa=l["bo_bolsa"], ti_ticker=l["ti_ticker"],
                        ac_quantidade=l["ac_quantidade"], ac_preco=l["ac_preco"],
                        ac_montante=l["ac_montante"]) for l in tabela
                        ]
            return []
    except Error as e:
        print(f"Erro ao selecionar acao: {e}")
        return []
"""
Seleciona todas as ações registradas pelo usuário e que estão disponíveis
"""
def selecionar_acoes_disp() -> list[str] | []:
    sql_query = "SELECT ti_ticker FROM Acao WHERE ac_quantidade > 0  GROUP BY ti_ticker;"
    try:
        with conectar() as conn:
            coluna = conn.execute(sql_query).fetchall()
            if coluna:
                return [l["ti_ticker"] for l in coluna]
            return []
    except Error as e:
        print(f"Erro em selecionar_acoes_disp: {e}")
        return []

def selecionar_acoes_bolsas() -> list | []:
    sql_query = "SELECT bo_bolsa FROM Acao GROUP BY bo_bolsa"
    try:
        with conectar() as conn:
            coluna = conn.execute(sql_query).fetchall()
            if coluna:
                return [l["bo_bolsa"] for l in coluna]
            return []
    except Error as e:
        print(f"Erro em selecionar_acoes_bolsas: {e}")
        return []
"""
Recebe o ticker alvo
Retorna os primeiros 5 tickers de ação registrados
"""
def selecionar_acao_primeiros_5_ticker(ticker: str) -> list[Acao] | []:
    sql_query = """
        SELECT a.ac_id, a.ac_quantidade, a.ac_montante, a.con_id, a.ti_ticker, a.ac_preco
            FROM Acao a
            JOIN Contrato c 
                ON a.con_id = c.con_id
        WHERE a.ti_ticker = ?
        ORDER BY c.con_abertura
            LIMIT 5;
    """
    try:
        with conectar() as conn:
            tabela = conn.execute(sql_query, (ticker,)).fetchall()
            if tabela:
                return [
                    Acao(ac_id=l["ac_id"], con_id=l["con_id"], bo_bolsa=l["bo_bolsa"],
                         ti_ticker=l["ti_ticker"], ac_quantidade=l["ac_quantidade"],
                         ac_preco=l["ac_preco"], ac_montante=l["ac_montante"]) for l in tabela
                ]
            return []
    except Error as e:
        print(f"Erro em selecionar_acao_primeiros_5_ticker: {e}")
        return []
"""
Atualiza a quantidade na tabela de ação

"""
def atualizar_acao_quantidade(ticker: str, contrato: int, quantidade: int, montante: int) -> int:
    select_sql = "SELECT ac_id FROM Acao WHERE ti_ticker = ? AND con_id = ?;"
    update_sql = "UPDATE Acao SET ac_quantidade = ?, ac_montante = ? WHERE ac_id = ?;"
    try:
        with conectar() as conn:
            linha = conn.execute(select_sql, (ticker, contrato)).fetchone()
            if not linha:
                print(f"Ação {ticker} do contrato {contrato} não encontrada.")
                return -1

            conn.execute(update_sql, (quantidade, montante, linha["ac_id"]))
            conn.commit()
            print(f"Ação {ticker} (ID={linha["ac_id"]}) atualizada para quantidade {quantidade}")
            return linha["ac_id"]

    except Error as e:
        print(f"Erro em atualizar_acao_quantidade: {e}")
        return -1

def atualizar_acao(quantidade: int, montante: int, contrato:int, bolsa: str, ticker: str) -> bool:
    sql_update ="""
               UPDATE Acao
               SET ac_quantidade = ac_quantidade + ?, ac_montante = ac_montante + ?
               WHERE con_id = ? AND bo_bolsa = ? AND ti_ticker = ?;
                """
    try:
        with conectar() as conn:
            conn.execute(sql_update, (quantidade, montante, contrato, bolsa, ticker))
            conn.commit()
            print(f"atualizada a ação {ticker} da {bolsa} do contrato {contrato}, adicionados {quantidade} no valor de {montante/1000000}")
            return True
    except Error as e:
        print(f"Erro ao atualizar acao: {e}")
        return False