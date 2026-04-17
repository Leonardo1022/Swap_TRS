import sqlite3
from sqlite3 import Error, Row

arquivo_bd = r"C:\Users\leona\PycharmProjects\Swap_TRS\swap.db"

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