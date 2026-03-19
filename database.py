import sqlite3
from sqlite3 import Error, IntegrityError, Row
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
#Configurações
arquivo_bd = "swap.db"
data_hoje = datetime.today()

def converter_data(data: str):
    return datetime.strptime(data, "%Y-%m-%d")

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

def inserir_contrato(montante: float, data: str, duracao: int):
    sql_insert = """INSERT INTO Contrato(con_mont, con_abertura, con_duracao)
                    VALUES (?, ?, ?)"""
    try:
        with conectar() as conn:
            cursor = conn.execute(sql_insert, (montante, data, duracao))
            print(f"Contrato adicionado: ID {cursor.lastrowid}")
            return cursor.lastrowid
    except Error as e:
        print(f"Erro ao inserir contrato: {e}")
        return None

def inserir_taxa(contrato: int, indexador: str, spread: float):
    sql_insert = """INSERT INTO Taxa(con_id, ind_indexador, ta_spread) 
                    VALUES(?, ?, ?)"""
    try:
        with conectar() as conn:
            cursor = conn.execute(sql_insert, (contrato, indexador, spread))
            print("Taxa adicionada")
    except Error as e:
        print(f"Erro ao inserir taxa: {e}")

def inserir_acao(contrato: int, bolsa: str, ticker: str, quantidade: int, montante: float):
    sql_insert = """INSERT INTO Acao(con_id, bo_bolsa, ti_ticker, ac_quantidade, ac_montante)
                    VALUES (?, ?, ?, ?, ?)"""
    try:
        with conectar() as conn:
            conn.execute(sql_insert, (contrato, bolsa, ticker, quantidade, montante))
            print(f"Ação adicionada: {ticker} (quantidade: {quantidade}, montante: {montante})")
    except Error as e:
        print(f"Erro ao inserir acao: {e}")

def inserir_movimentacao(contrato: int, bolsa: str, ticker: str, quantidade: int, valor: float, data: str, e_venda: int):
    sql_insert = """INSERT INTO Movimentacao(con_id, bo_bolsa, ti_ticker, mov_quantidade, mov_valor, mov_data, mov_e_venda)
                    VALUES (?, ?, ?, ?, ?, ?, ?)"""
    try:
        with conectar() as conn:
            conn.execute(sql_insert, (contrato, bolsa, ticker, quantidade, valor, data, e_venda))
            conn.commit()
            print(f'{"Venda" if e_venda == 1 else "Compra"} adicionada: {quantidade} {ticker} em {bolsa}')
            if e_venda == 1:
                ""
            elif e_venda == 0:
                if atualizar_acao(quantidade, valor, contrato, bolsa, ticker):
                    return True
    except IntegrityError as e:
        #Arrumar
        if "Quantidade vendida maior" in str(e):
            print(f"Erro: não é possível realizar a movimentação {ticker} ({quantidade}). Quantidade excede a disponível.")
        else:
            print(f"Erro de integridade: {e}")
    except Error as e:
        print(f"Erro ao inserir movimentação: {e}")

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

def selecionar_tickers(bolsa: str):
    sql_query = """SELECT ti_ticker 
                   FROM Ticker 
                   WHERE bo_bolsa = ?"""
    try:
        with conectar() as conn:
            linhas = conn.execute(sql_query, (bolsa,)).fetchall()
            return [linha["ti_ticker"] for linha in linhas]
    except Error as e:
        print(f"Erro ao selecionar bolsa: {e}")
        return None

def selecionar_bolsas():
    sql_query = "SELECT bo_bolsa FROM Bolsa"
    try:
        with conectar() as conn:
            linhas = conn.execute(sql_query).fetchall()
            print("sucesso")
            return [linha["bo_bolsa"] for linha in linhas]
    except Error as e:
        print(f"Erro ao retornar bolsas: {e}")
        return None

def selecionar_bolsa(bolsa: str):
    sql_query = "SELECT * FROM Bolsa WHERE bo_bolsa = ?"
    try:
        with conectar() as conn:
            linha = conn.execute(sql_query, (bolsa,)).fetchone()
            return dict(linha) if linha else {}
    except Error as e:
        print(f"Erro ao selecionar bolsa: {e}")
        return None
"""
Recebe o id do contrato
Retorna uma lista de tickers no id do contrato
"""
def selecionar_acao(contrato: int):
    sql_query = """SELECT * FROM Acao WHERE con_id = ?"""
    try:
        with conectar() as conn:
            linhas = conn.execute(sql_query, (contrato,)).fetchall()
            return [dict(linha) for linha in linhas] if linhas else []
    except Error as e:
        print(f"Erro ao selecionar acao: {e}")
        return None
"""
Retorna uma lista de ids de Contrato
Se erro retorna uma lista vazia
"""
def selecionar_contratos_id():
    sql_query = "SELECT con_id FROM Contrato"
    try:
        with conectar() as conn:
            linhas = conn.execute(sql_query).fetchall()
            return [linha["con_id"] for linha in linhas]
    except Error as e:
        print(f"Erro ao selecionar id dos contratos: {e}")
        return None
"""
Recebe o id do contrato
Retorna uma linha de Contrato em formato de dict, pode retornar uma dict vazia
Se erro retorna None
"""
def selecionar_contrato(contrato: int):
    sql_query = "SELECT * FROM Contrato WHERE con_id = ?"
    try:
        with conectar() as conn:
            linha = conn.execute(sql_query, (contrato,)).fetchone()
            return dict(linha) if linha else {}
    except Error as e:
        print(f"Erro ao selecionar contrato: {e}")
        return None
"""
Recebe o id do contrato e a data
Retornar as linhas de Movimentacao em formato de lista de dicionários 
com as vendas feitas no mesmo mês e ano da data
"""
def selecionar_vendas_contrato_mes(contrato: int, data: str):
    sql_query = """
                SELECT * FROM Movimentacao 
                WHERE con_id = ? 
                AND STRFTIME('%m', mov_data) = ? 
                AND STRFTIME('%Y', mov_data) = ?;
                """
    try:
        with conectar() as conn:
            data_mes_str = f"{converter_data(data).month: 02d}"
            data_ano_str = str(converter_data(data).year)
            linhas = conn.execute(sql_query, (contrato, data_mes_str, data_ano_str)).fetchall()
            return [dict(linha) for linha in linhas] if linhas else []
    except Error as e:
        print(f"Erro ao selecionar vendas por data: {e}")

def selecionar_valores_resultado(contrato: int):
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
"""
Retorna o lucro total de todos os contratos, pode retornar 0.00
Se erro retorna None
"""
def lucro_total():
    sql_query = """SELECT COALESCE(SUM(mov_valor), 0.00) AS total 
                   FROM Movimentacao WHERE mov_e_venda = 1;"""
    try:
        with conectar() as conn:
            linha = conn.execute(sql_query).fetchone()
            return linha["total"]
    except Error as e:
        print(f"Erro ao selecionar lucro: {e}")
        return None
"""
Recebe o id do contrato e a data
Retorna o custo mensal da data em forma de float, pode retornar 0.00
Se erro retorna None
"""
#A terminar
def custo_mensal_contrato(contrato: int, data: str):
    sql_query = """
                SELECT c.con_mont * (t.ta_spread + i.ind_valor) AS custo_mensal 
                FROM Contrato c 
                JOIN Taxa t 
                ON c.con_id = t.con_id
                JOIN Indexador i
                ON t.ind_indexador = i.ind_indexador
                JOIN Movimentacao m
                ON c.con_id = m.con_id
                WHERE c.con_id = ?
                AND mov_e_venda = 1
                AND STRFTIME('%m', mov_data) = ? 
                AND STRFTIME('%Y', mov_data) = ?;
                """
    try:
        with conectar() as conn:
            data_mes_str = f"{converter_data(data).month: 02d}"
            data_ano_str = str(converter_data(data).year)
            linha = conn.execute(sql_query, (contrato, data_mes_str, data_ano_str)).fetchone()
            return linha["custo_mensal"] if linha else 0.00
    except Error as e:
        print(f"Erro ao selecionar custo mensal: {e}")
        return None

def lucro_mensal_contrato(contrato: int, data: str):
    sql_query_com_resultado = """
                SELECT SUM(re_lucro) AS lucro_mensal
                FROM Resultado WHERE con_id = ? AND re_data = ?
                """
    sql_query_sem_resultado = """
                              SELECT SUM(mov_valor) FROM Movimentacao
                              WHERE mov_e_venda = 1
                              AND STRFTIME('%m', mov_data) = ? 
                              AND STRFTIME('%Y', mov_data) = ?;
                              """
    try:
        with conectar() as conn:
            linha = conn.execute(sql_query_com_resultado, (contrato, data)).fetchone()
            if linha:
                return linha["lucro_mensal"]
            else:
                data_mes_str = f"{converter_data(data).month: 02d}"
                data_ano_str = str(converter_data(data).year)
                linha = conn.execute(sql_query_sem_resultado, (contrato, data_mes_str, data_ano_str)).fetchone()
                return linha["lucro_mensal"] if linha else 0.00
    except Error as e:
        print(f"Erro ao selecionar lucro mensal: {e}")
        return 0

def resultado_mensal_contrato(contrato: int, data: str):
    sql_query = """"""
"""
Retorna em float o custo mensal esperado de todos os contratos, caso não tenha nenhum retorna 0.00
Se erro retorna None
"""
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
            return linha["custo_total_mensal"] if linha else 0.00
    except Error as e:
        print(f"Erro ao selecionar custo: {e}")
        return None
"""
Recebe o id do contrato.
Retorna em int o número de meses em que a tabela Resultado está atrasada 
no contrato específico, se em dia retorna 0.
Se erro retorna None.
"""
#A terminar
def ultimo_resultado_contrato(contrato: int):
    sql_query = "SELECT re_data FROM Resultado WHERE con_id = ? ORDER BY re_data DESC;"
    sql_query_2 = "SELECT con_abertura FROM Contrato WHERE con_id = ?;"
    try:
        with conectar() as conn:
            linha = conn.execute(sql_query, (contrato,)).fetchone()
            if linha is not None and linha["re_data"] is not None:
                data_recente_resultado = converter_data(linha["re_data"])
                meses_faltantes = data_hoje.month - data_recente_resultado.month + ((data_hoje.year - data_recente_resultado.year) * 12)
                return meses_faltantes
            else:
                linha = conn.execute(sql_query_2, (contrato,)).fetchone()
                data_recente_contrato = converter_data(linha["con_abertura"])
                meses_faltantes = data_hoje.month - data_recente_contrato.month + ((data_hoje.year - data_recente_contrato.year) * 12)
                return meses_faltantes
    except Error as e:
        print(f"Erro ao selecionar contrato: {e}")
        return None


for contrato in selecionar_contratos_id():
    meses_faltantes = ultimo_resultado_contrato(contrato)
    for mes in range(meses_faltantes):
        data = data_inicial + relativedelta(months= mes + 1)
        lucro = lucro_mensal_contrato(contrato, data)
        custo = custo_mensal_contrato(contrato, data)
        inserir_resultado(contrato, data, lucro, custo, )
#Definir um jeito de colocar uma forma de automatizar "Resultado" para ser ativado ou mensalmente
#Ou ter um jeito de fazer as coisas