from database.connection import conectar
from database.utils import converter_data
from database.models import Indexador
from sqlite3 import Error
import pandas as pd

def inserir_indexador(indexador: str, data: str, taxa: int) -> None:
    sql_insert = """
                 INSERT INTO Indexador(ind_indexador, ind_data, ind_valor)
                 VALUES (?, ?, ?)
                 """
    try:
        with conectar() as conn:
            conn.execute(sql_insert, (indexador, data, taxa))
            conn.commit()
            print(f"Inserido indexador {indexador} com taxa {taxa/1000000}a.m na data {data}")
    except Error as e:
        print(f"Erro ao inserir Indexador: {e}, {indexador, taxa, data}")

def selecionar_indexador(indexador: str, data: str) -> int:
    data_convertida = converter_data(data)
    data_ano_str = str(data_convertida.year)
    data_mes_str = f"{data_convertida.month:02d}"
    sql_query = """
                SELECT ind_valor FROM Indexador 
                    WHERE ind_indexador = ? 
                        AND STRFTIME('%Y', ind_data) = ?
                        AND STRFTIME('%m', ind_data) = ?;
                """
    try:
        with conectar() as conn:
            df = pd.read_sql_query(sql_query, conn, params=(indexador, data_ano_str, data_mes_str))
            print(df)
            print(f"Valores[\nindexador: {indexador}\ndata_ano: {data_ano_str}\ndata_mes: {data_mes_str}\n]")
            return df["ind_valor"].iloc[0] if not df.empty else 0
    except Error as e:
        print(f"Erro ao selecionar indexador: {e}")
        return -1

def selecionar_indexadores() -> list:
    sql_query = "SELECT ind_indexador FROM Indexador GROUP BY ind_indexador;"
    try:
        with conectar() as conn:
            df = pd.read_sql_query(sql_query, conn)
            return df["ind_indexador"].tolist()
    except Error as e:
        print(f"Erro ao selecionar indexadores: {e}")
        return []

def selecionar_ultimo_indexador_data() -> Indexador | None:
    sql_query = """
                SELECT * FROM Indexador
                ORDER BY ind_data DESC
                LIMIT 1;
                """
    try:
        with conectar() as conn:
            linha = conn.execute(sql_query).fetchone()
            return Indexador(ind_indexador=linha["ind_indexador"], ind_data=linha["ind_data"], ind_valor=linha["ind_valor"])
    except Error as e:
        print(f"Erro em selecionar_ultimo_indexador_data: {e}")
        return None