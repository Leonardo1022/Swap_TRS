from database.connection import conectar
from sqlite3 import Error
import pandas as pd

def inserir_indexador(indexador: str, data: str, taxa: float):
    sql_insert = """
                 INSERT INTO Indexador(ind_indexador, ind_data, ind_valor)
                 VALUES (?, ?, ?)
                 """
    try:
        with conectar() as conn:
            conn.execute(sql_insert, (indexador, data, taxa))
            conn.commit()
            print(f"Inserido indexador {indexador} com taxa {taxa}a.m na data {data}")
    except Error as e:
        print(f"Erro ao inserir Indexador: {e}")

def selecionar_indexadores():
    sql_query = "SELECT * FROM Indexador;"
    try:
        with conectar() as conn:
            df = pd.read_sql_query(sql_query, conn)
            return df
    except Error as e:
        print(f"Erro ao selecionar indexador: {e}")
        return None

def selecionar_ultimo_indexador_data():
    sql_query = """
                SELECT * FROM Indexador
                ORDER BY ind_data DESC
                LIMIT 1;
                """
    try:
        with conectar() as conn:
            linha = pd.read_sql_query(sql_query, conn)
            return linha
    except Error as e:
        print(f"Erro ao selecionar o último indexador: {e}")
        return None