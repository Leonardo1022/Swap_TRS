from database.connection import conectar
#from database.utils import converter_data
from sqlite3 import Error
#import pandas as pd

def selecionar_acao_venda():
    return None

def inserir_acao_venda(acao: int, venda: int):
    sql_insert = """
                 INSERT INTO AcaoVenda(ac_id, ven_id) 
                 VALUES (?, ?);
                 """
    try:
        with conectar() as conn:
            conn.execute(sql_insert,(acao, venda))
            conn.commit()
            print(f"Sucesso ao inserir AcaoVenda")
    except Error as e:
        print(f"Erro ao inserir AcaoVenda: {e}")