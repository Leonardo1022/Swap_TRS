# Parte de contratos

import streamlit as st
import yfinance as yf
import sqlite3
from sqlite3 import Error, IntegrityError
#uv run streamlit run main.py

# SqLite
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

    def criarTabelas(self, caminho_sql: str):
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

    def inserirContrato(self, montante, data, duracao, indexador, spread):
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

    def inserirAcao(self, contrato, ticker, bolsa, quantidade):
        try:
            sql_insert = """INSERT INTO Acao(con_id, bo_ticker, bo_bolsa, ac_qtd)
                            VALUES (?, ?, ?, ?)"""
            self.conn.execute(sql_insert, (contrato, ticker, bolsa, quantidade))
            self.conn.commit()
            print(f"Ação adicionada: {ticker} ({quantidade})")
        except Error as e:
            print(f"Erro ao inserir acao: {e}")

    def inserirVenda(self, contrato, ticker, bolsa, quantidade, valor, data):
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

    def selecionarTickers(self, bolsa):
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


if __name__ == "__main__":
    db = Database("example.db")
    db.fechar()

# Streamlit
lista_bolsa = ["B3", "NASDAQ"]
lista_ticker = []
lista_ticker_b3 = ["PETR4", "VALE3"]
lista_ticker_nasdaq = ["NVDA", "MSFT"]

st.write("Contratos")
st.write("Adicionar contrato")
with st.form("form_contrato", clear_on_submit=True, enter_to_submit=False):
    bolsa_c = st.selectbox("Selecione a Bolsa", lista_bolsa)

    if bolsa_c == "B3":
        # lista_ticker = lista_ticker_b3
        ticker_c = st.multiselect("Selecione o Ticker", lista_ticker_b3, index=None, accept_new_options=True,
                                  placeholder="")
    elif bolsa_c == "NASDAQ":
        # lista_ticker = lista_ticker_nasdaq
        ticker_c = st.multiselect("Selecione o Ticker", lista_ticker_nasdaq, index=None, accept_new_options=True,
                                  placeholder="")

    montante_c = st.number_input("Valor do montante", min_value=0.00)
    qtd_compra_c = st.number_input("Quantidade de ações", min_value=0)
    dt_compra_c = st.date_input("Coloque a data de início", format="DD/MM/YYYY")
    duracao_c = st.number_input("Duração do contrato em meses", min_value=0)
    st.write("Taxas")
    indexador_c = st.selectbox("Selecione o indexador", ["CDI", "SELIC"], index=None, placeholder="")
    spread_c = st.number_input("Spread em (%)", min_value=0.0)
    st.form_submit_button("Adicionar contrato")
