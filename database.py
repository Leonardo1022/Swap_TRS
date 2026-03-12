import sqlite3
from sqlite3 import Error, IntegrityError
#Corrigie em relação as alterações feitas na modelagem do db
class Database:
    def __init__(self, db_file: str):
        self.db_file = db_file
        self.conn = None
        self.conectar()

    def conectar(self):
        try:
            self.conn = sqlite3.connect(self.db_file)
            self.conn.execute("PRAGMA foreign_keys = ON")
            print(f"Conectado a base de dados: {self.db_file}")
        except Error as e:
            print(f"Erro ao se conectar: {e}")
            self.conn = None

    def fechar(self):
        if self.conn:
            self.conn.close()
            print("Conexão encerrada")

    def criar_tabelas(self, caminho_sql: str):
        if self.conn is None:
            print("Conexão não estabelecida")
            return
        try:
            with open(caminho_sql, 'r') as f:
                sql_script = f.read()
            self.conn.executescript(sql_script)
            print("Tabelas criadas")
        except Error as e:
            print(f"Erro ao criar tabelas: {e}")

    def inserir_contrato(self, montante, data, duracao, indexador, spread):
        try:
            sql_insert = """INSERT INTO Contrato(con_mont, con_data, con_dur, con_ind, con_spd)
                            VALUES (?, ?, ?, ?, ?)"""
            cursor = self.conn.execute(sql_insert, (montante, data, duracao, indexador, spread))
            self.conn.commit()
            print(f"Contrato adicionado: ID {cursor.lastrowid}")
            return cursor.lastrowid
        except Error as e:
            print(f"Erro ao inserir contrato: {e}")
            return None

    def inserir_acao(self, contrato, ticker, bolsa, quantidade):
        try:
            sql_insert = """INSERT INTO Acao(con_id, bo_ticker, bo_bolsa, ac_qtd)
                            VALUES (?, ?, ?, ?)"""
            self.conn.execute(sql_insert, (contrato, ticker, bolsa, quantidade))
            self.conn.commit()
            print(f"Ação adicionada: {ticker} ({quantidade})")
        except Error as e:
            print(f"Erro ao inserir acao: {e}")

    def inserir_venda(self, contrato, ticker, bolsa, quantidade, valor, data):
        try:
            sql_insert = """INSERT INTO Venda(con_id, bo_ticker, bo_bolsa, ven_qtd, ven_vlr, ven_data)
                            VALUES (?, ?, ?, ?, ?, ?)"""
            self.conn.execute(sql_insert, (contrato, ticker, bolsa, quantidade, valor, data))
            self.conn.commit()
            print(f"Venda adicionada: {quantidade} {ticker} em {bolsa}")
        except IntegrityError as e:
            if "Quantidade vendida maior" in str(e):
                print(f"Erro: não é possível vender {ticker} ({quantidade}). Quantidade excede a disponível.")
            else:
                print(f"Erro de integridade: {e}")
        except Error as e:
            print(f"Erro ao inserir venda: {e}")

    def selecionar_tickers(self, bolsa):
        try:
            sql_query = """SELECT bo_ticker \
                           FROM Bolsa \
                           WHERE bo_bolsa = ?"""
            query = self.conn.execute(sql_query, (bolsa,))
            rows = query.fetchall()
            for row in rows:
                print(row[0])  # imprime apenas o ticker
            return [row[0] for row in rows]  # retorna uma lista de tickers
        except Error as e:
            print(f"Erro ao selecionar bolsa: {e}")

    def renda_total(self):
        try:
            sql_query = """SELECT con_total \"""