from database.connection import conectar
from database.utils import converter_data
from sqlite3 import Error
import pandas as pd

def inserir_contrato(montante: float, data: str, duracao: int, indexador: str, spread: float):
    sql_insert = """INSERT INTO Contrato(con_mont, con_abertura, con_duracao, con_indexador, con_spread)
                    VALUES (?, ?, ?, ?, ?)"""
    try:
        with conectar() as conn:
            cursor = conn.execute(sql_insert, (montante, data, duracao, indexador, spread))
            conn.commit()
            print(f"Contrato adicionado: ID {cursor.lastrowid}, data: {data}, duração: {duracao}, indexador: {indexador}, spread: {spread}")
            return cursor.lastrowid
    except Error as e:
        print(f"Erro ao inserir contrato: {e}")
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
Recebe o id do contrato.
Retorna em int o número de meses em que a tabela Resultado está atrasada 
no contrato específico, se em dia retorna 0.
Se erro retorna None.
"""
#A terminar
def selecionar_contrato_ultimo_resultado(contrato: int) -> str:
    sql_query = "SELECT re_data FROM Resultado WHERE con_id = ? ORDER BY re_data DESC;"
    sql_query_2 = "SELECT con_abertura FROM Contrato WHERE con_id = ?;"
    try:
        with conectar() as conn:
            linha = conn.execute(sql_query, (contrato,)).fetchone()
            if linha is not None: #Caso tenham resultados registrados
                return linha["re_data"]
            else: #Caso não
                linha = conn.execute(sql_query_2, (contrato,)).fetchone()
                return linha["con_abertura"]
    except Error as e:
        print(f"Erro ao selecionar contrato: {e}")
        return ""
"""
Recebe o id do contrato e a data
Retorna o custo mensal da data em forma de float, se estiver vazia retorna -1
Se erro retorna -1
"""
def selecionar_contrato_custo_mensal(contrato: int, data: str) -> float:
    sql_query = """
                 SELECT con_mont * (((1 + (
                     SELECT ind_valor FROM Indexador 
                         WHERE ind_indexador = con_indexador 
                           AND STRFTIME('%Y',ind_data) = ? 
                           AND STRFTIME('%m',ind_data) = ?
                 )) * (POWER(1 + con_spread, (1.0/12))))- 1)
                            AS custo_mensal FROM Contrato WHERE con_id = ?;"""
    try:
        with conectar() as conn:
            data_convertida = converter_data(data)
            data_mes_str = f"{data_convertida.month:02d}"
            data_ano_str = str(data_convertida.year)
            linha = conn.execute(sql_query, (data_ano_str, data_mes_str, contrato)).fetchone()
            if linha is None:
                return -1
            return linha["custo_mensal"] if linha["custo_mensal"] != 0.0 else -1
    except Error as e:
        print(f"Erro ao selecionar custo mensal: {e}")
        return -1
"""
Retorna em float o custo mensal esperado de todos os contratos, caso não tenha nenhum retorna 0.00
Se erro retorna None
"""
def selecionar_contratos_custo_mensal():
    sql_query = """
                SELECT SUM(c.con_mont * (c.con_spread + i.ind_valor)) AS custo_total_mensal 
                FROM Contrato c 
                JOIN Indexador i
                ON c.con_indexador = i.ind_indexador
                """
    try:
        with conectar() as conn:
            linha = conn.execute(sql_query).fetchone()
            return linha["custo_total_mensal"] if linha else 0.00
    except Error as e:
        print(f"Erro ao selecionar custo: {e}")
        return None

def selecionar_contrato_lucro_mensal(contrato: int, data: str):
    sql_query_com_resultado = """
                SELECT SUM(re_lucro) AS lucro_mensal
                FROM Resultado WHERE con_id = ? AND re_data = ?
                """
    sql_query_sem_resultado = """
                              SELECT SUM(ven_valor) FROM Venda
                              WHERE STRFTIME('%m', ven_data) = ? 
                              AND STRFTIME('%Y', ven_data) = ?;
                              """
    try:
        with conectar() as conn:
            linha = conn.execute(sql_query_com_resultado, (contrato, data)).fetchone()
            if linha:
                return linha["lucro_mensal"]
            else:
                data_convertida = converter_data(data)
                data_mes_str = f"{data_convertida.month:02d}"
                data_ano_str = str(data_convertida.year)
                linha = conn.execute(sql_query_sem_resultado, (contrato, data_mes_str, data_ano_str)).fetchone()
                return linha["lucro_mensal"] if linha else 0.00
    except Error as e:
        print(f"Erro ao selecionar lucro mensal: {e}")
        return 0

def atualizar_contrato_montante(contrato: int, montante:float):
    sql_update = "UPDATE Contrato SET con_mont = con_mont + ? WHERE con_id = ?;"
    try:
        with conectar() as conn:
            conn.execute(sql_update, (montante, contrato))
            conn.commit()
            print(f"Montante do contrato {contrato} atualizado em {montante}")
            return True
    except Error as e:
        print(f"Erro ao atualizar montante do contrato: {e}")

if __name__ == "__main__":
    print(selecionar_contrato_ultimo_resultado(13))