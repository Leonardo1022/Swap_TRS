#import pandas as pd
from database.components import *
from dateutil.relativedelta import relativedelta
#import datetime as dt
import requests

"""
Calcula quantos contratos serão afetados pela venda.
Recebe o df com os dados dos primeiros 5 resultados da consulta feita pelo método ultimo_5_ticker().
Retorna os contratos e valores.
"""
def calcular_venda(df: pd.DataFrame, quantidade: int):
    ticker = df["ti_ticker"].iloc[0]

    for _, linha in df.iterrows():
        qtd = linha["ac_quantidade"]

        if qtd >= quantidade:
            atualizar_acao_quantidade(ticker, linha["con_id"], qtd - quantidade)
            quantidade = 0
            break
        else:
            quantidade -= qtd
            atualizar_acao_quantidade(ticker, linha["con_id"], 0)
    if quantidade > 0:
        raise ValueError("Quantidade maior que disponível")

def preencher_resultado(contrato: int, montante: float, duracao_contrato: int):
    meses_faltantes = selecionar_contrato_ultimo_resultado(contrato)
    if meses_faltantes > duracao_contrato:
        meses_faltantes = duracao_contrato
    data_inicial = data_hoje - relativedelta(months=meses_faltantes)
    for mes in range(meses_faltantes):
        data = data_inicial + relativedelta(months= mes + 1)
        print(f"{data} Tipo: {type(data)}")
        custo_fixo = selecionar_contrato_custo_mensal(contrato, data.strftime("%Y-%m-%d"))
        inserir_resultado(contrato, data.strftime("%Y-%m-%d"), 0.00, custo_fixo, montante)

codigo_serie_dict = [{"taxa": "CDI a.d", "codigo": 12},
                     {"taxa": "SELIC a.d", "codigo": 11}]

def tabela_juros_acumulado_mensal( codio_serie, data_inicial, data_final):
    url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codio_serie}/dados?formato=json&{data_inicial}&{data_final}"
    try:
        df = pd.DataFrame(requests.get(url).json())
        df["data"] = pd.to_datetime(df["data"], dayfirst=True)
        datas: pd.Series = df["data"]
        df["valor"] = df["valor"].astype(float) / 100

        # Agrupar por mês (taxa acumulada)
        df["mes"] = datas.dt.to_period("M")
        taxa_mensal = df.groupby("mes")["valor"].apply(
            lambda x: (1 + x).prod() - 1
        ).reset_index()

        taxa_mensal["data"] = taxa_mensal["mes"].dt.to_timestamp("M")
        taxa_mensal = taxa_mensal[["data", "valor"]]
        return taxa_mensal
    except:
        return None

def inserir_indexador_nome(indexador: str):
    try:
        tabela_indexador = tabela_juros_acumulado_mensal(11, "dataInicial=01/01/2020", "")
        for _, row in tabela_indexador.iterrows():
            inserir_indexador(indexador, row["data"], float(row["valor"]))
    except AttributeError as ae:
        print(f"Erro ao inserir indexadores, o retorno esperado foi de um tipo diferente: {ae}")

# A função está faltando parâmetros
def inserir_custo_mensal_contrato(contrato: int, data: str):
    df_mov = selecionar_movimentacao_contrato_mes(contrato, data)
    soma_custo_variavel = df_mov.loc[df_mov["mov_e_venda"] == 0, "mov_valor"].sum()

    sql_insert = """
                INSERT INTO Resultado(con_id, re_data, re_custo, re_montante) 
                VALUES (?, ?, ?, ?);
                """
    try:
        with conectar() as conn:
            conn.execute(sql_insert, (contrato, data))
    except Error as e:
        print(f"Não foi possível adicionar custo mensal: {e}")

def tipo_movimentacao(e_venda: int, contrato: int, quantidade: int, valor: float, bolsa: str, ticker: str):
    if e_venda == 1:
        ""
        return True
    elif e_venda == 0:
        if atualizar_contrato_montante(contrato, valor):
            if atualizar_acao(quantidade, valor, contrato, bolsa, ticker):
                return True
    else:
        return False