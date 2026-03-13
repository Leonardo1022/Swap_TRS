import sqlite3
from sqlite3 import Error, IntegrityError, Row
#Corrigir em relação as alterações feitas na modelagem do db

arquivo_bd = "swap.db"


def conectar():
    conn = sqlite3.connect(arquivo_bd)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = Row
    return conn

def executar_script(caminho_sql):
    try:
        with open(caminho_sql, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        with conectar() as conn:
            conn.executescript(sql_script)
            print("Tabelas criadas")
    except FileNotFoundError:
        print("Arquivo SQL não encontrado")
    except Error as e:
        print(f"Erro ao criar tabelas: {e}")

def inserir_contrato(montante: float, data: int, duracao: int):
    sql_insert = """INSERT INTO Contrato(con_mont, con_abertura, con_dur)
                    VALUES (?, ?, ?)"""
    try:
        with conectar() as conn:
            cursor = conn.execute(sql_insert, (montante, data, duracao))
            print(f"Contrato adicionado: ID {cursor.lastrowid}")
            return cursor.lastrowid
    except Error as e:
        print(f"Erro ao inserir contrato: {e}")
        return None

def inserir_acao(contrato, bolsa, ticker, quantidade, montante):
    sql_insert = """INSERT INTO Acao(con_id, bo_bolsa, ti_ticker, ac_qtd, ac_mont)
                    VALUES (?, ?, ?, ?, ?)"""
    try:
        with conectar() as conn:
            conn.execute(sql_insert, (contrato, bolsa, ticker, quantidade, montante))
            print(f"Ação adicionada: {ticker} (quantidade: {quantidade}, montante: {montante})")
    except Error as e:
        print(f"Erro ao inserir acao: {e}")

def inserir_venda(contrato, bolsa, ticker, quantidade, valor, data):
    sql_insert = """INSERT INTO Venda(con_id, bo_bolsa, ti_ticker, ven_qtd, ven_valor, ven_data)
                    VALUES (?, ?, ?, ?, ?, ?)"""
    try:
        with conectar() as conn:
            conn.execute(sql_insert, (contrato, ticker, bolsa, quantidade, valor, data))
            conn.commit()
            print(f"Venda adicionada: {quantidade} {ticker} em {bolsa}")
    except IntegrityError as e:
        if "Quantidade vendida maior" in str(e):
            print(f"Erro: não é possível vender {ticker} ({quantidade}). Quantidade excede a disponível.")
        else:
            print(f"Erro de integridade: {e}")
    except Error as e:
        print(f"Erro ao inserir venda: {e}")

def selecionar_tickers(bolsa: str):
    sql_query = """SELECT ti_ticker 
                   FROM Ticker 
                   WHERE bo_bolsa = ?"""
    try:
        with conectar() as conn:
            linhas = conn.execute(sql_query, bolsa).fetchall()
            return [linha["ti_ticker"] for linha in linhas]
    except Error as e:
        print(f"Erro ao selecionar bolsa: {e}")
        return None

def selecionar_bolsas():
    sql_query = "SELECT bo_bolsa FROM Bolsa"
    try:
        with conectar() as conn:
            linhas = conn.execute(sql_query).fetchall()
            return [linha["bo_bolsa"] for linha in linhas]
    except Error as e:
        print(f"Erro ao retornar bolsas: {e}")
        return None

def lucro_total():
    sql_query = """SELECT SUM(ven_valor) AS total 
                   FROM Venda"""
    try:
        with conectar() as conn:
            linha = conn.execute(sql_query).fetchone()
            return linha["total"] if linha else 0
    except Error as e:
        print(f"Erro ao selecionar lucro: {e}")
        return None

def custo_total_mensal():
    sql_query = """
                SELECT SUM(c.con_mont * (t.ta_spread + i.ind_valor)) AS custo_total_mensal 
                FROM Contrato c 
                JOIN Taxa t 
                ON c.con_id = t.con_id
                JOIN Indexador i
                ON t.ind_indexador = i.ind_indexador
                """
    try:
        with conectar() as conn:
            linha = conn.execute(sql_query).fetchone()
            return linha["custo_total_mensal"] if linha else 0
    except Error as e:
        print(f"Erro ao selecionar custo: {e}")
        return None