from datetime import datetime
from database.components import *
from dateutil.relativedelta import relativedelta
from calendar import monthrange
import requests

data_hoje = datetime.today()

"""
Calcula quantos contratos serão afetados pela venda para o modelo FIFO.
Recebe o df com os dados da consulta feita pelo método selecionar_acao_primeiros_5_ticker().
Retorna os contratos e valores de venda.
"""
def calcular_venda(df: pd.DataFrame, quantidade: int, lucro_individual: float) -> list[dict[int, float]]:
    ticker = df["ti_ticker"].iloc[0]
    acao_list = []

    for _, linha in df.iterrows():
        qtd_disponivel = linha["ac_quantidade"]
        if qtd_disponivel >= quantidade:
            acao_id_int = atualizar_acao_quantidade(ticker, linha["con_id"], qtd_disponivel - quantidade)
            quantidade = 0
            acao_list.append({acao_id_int: (lucro_individual*quantidade)}) #Dict com o id e lucro na venda
            break
        else: #Caso o valor de venda seja maior que o registrado por um contrato
            quantidade -= qtd_disponivel
            acao_id_int = atualizar_acao_quantidade(ticker, linha["con_id"], 0)
            acao_list.append({acao_id_int: (lucro_individual*qtd_disponivel)})

    if quantidade > 0:
        print("Quantidade maior que disponível")
        return []
    else:
        print(f"Venda feita com sucesso")
        return acao_list

def inserir_venda_com_acao(quantidade: int, valor: float, data: str, acao_list: list[dict[int, float]]):
    venda_id_int = inserir_venda(quantidade, valor, data)
    print(acao_list) #Está saindo um valor vazio
    for acao_dict in acao_list:
        for key, valor in acao_dict.items():
            inserir_acao_venda(key, venda_id_int)
            atualizar_resultado_lucro(valor, key, data)
    print("Inserção de venda com ação realizada com sucesso")

def preencher_resultados(contrato: int, montante: float, duracao_contrato: int):
    meses_faltantes = calcular_meses_preencher(contrato)
    if meses_faltantes > duracao_contrato:
        meses_faltantes = duracao_contrato
    data_inicial = data_hoje - relativedelta(months=meses_faltantes)
    for mes in range(meses_faltantes):
        data = data_inicial + relativedelta(months= mes + 1)

        ultimo_dia = monthrange(data.year, data.month)[1]
        fim_do_mes = data.replace(day=ultimo_dia)
        if data.year == data_hoje.year and data.month == data_hoje.month:
            data_registro = data_hoje
        else:
            data_registro = fim_do_mes

        custo_fixo = selecionar_contrato_custo_mensal(contrato, data_registro.strftime("%Y-%m-%d"))
        inserir_resultado(contrato, data_registro.strftime("%Y-%m-%d"), 0.00, custo_fixo, montante)
    print("Finalizado os preenchimentos dos resultados")

def selecionar_venda_contrato_lucro_mensal(contrato: int, data: str) -> float:
    sql_query = """
                SELECT coalesce(SUM(v.ven_valor), 0.00) AS lucro_mensal FROM Venda v
                JOIN AcaoVenda av
                    ON v.ven_id = av.ven_id
                JOIN Acao a 
                    ON av.ac_id = a.ac_id
                WHERE STRFTIME('%Y', v.ven_data) = ? 
                  AND STRFTIME('%m', v.ven_data) = ? 
                  AND a.con_id = ?;
                """
    try:
        with conectar() as conn:
            data_convertida = converter_data(data)
            data_mes_str = f"{data_convertida.month:02d}"
            data_ano_str = str(data_convertida.year)
            linha = conn.execute(sql_query, (data_ano_str, data_mes_str, contrato)).fetchone()
            if linha is None:
                return -1
            return linha["lucro_mensal"]
    except Error as e:
        print(f"Falha em selecionar_venda_contrato_lucro_mensal: {e}")
        return -1

def tabela_juros_acumulado_mensal( codio_serie: int, data_inicial: str, data_final: str = "") -> pd.DataFrame:
    url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codio_serie}/dados?formato=json&dataInicial={data_inicial}{'&dataFinal=' if data_final != "" else ""}{data_final}"
    try:
        response = requests.get(url).json()
        df = pd.DataFrame(response)
        df["data"] = pd.to_datetime(df["data"], dayfirst=True)
        datas: pd.Series = df["data"]
        df["valor"] = df["valor"].astype(float) / 100

        # Agrupar por mês (taxa acumulada)
        df["mes"] = datas.dt.to_period("M")
        taxa_mensal = df.groupby("mes")["valor"].apply(
            lambda x: (1 + x).prod() - 1
        ).reset_index()

        taxa_mensal["data"] = taxa_mensal["mes"].dt.to_timestamp("M")
        taxa_mensal["data"] = taxa_mensal["data"].dt.strftime("%Y-%m-%d")
        taxa_mensal = taxa_mensal[["data", "valor"]]
        return taxa_mensal
    except Error as e:
        print(f"Erro ao se conectar com a API de juros: {e}")
        return pd.DataFrame()

def inserir_indexador_nome(indexador: str):
    codigo_serie_dict = [{"taxa": "CDI", "ocorrencia": "a.d", "codigo": 12},
                         {"taxa": "SELIC", "ocorrencia": "a.d", "codigo": 11}]
    codigo_int = None
    for codigo in codigo_serie_dict:
        if indexador == codigo["taxa"]:
            codigo_int = codigo["codigo"]
            break
    if codigo_int is None:
        raise ValueError("Indexador inválido")
    try:
        tabela_indexador = tabela_juros_acumulado_mensal(codigo_int, "01/01/2021")
        for _, row in tabela_indexador.iterrows():
            inserir_indexador(indexador, str(row["data"]), float(row["valor"]))
    except AttributeError as ae:
        print(f"Erro ao inserir indexadores, o retorno esperado foi de um tipo diferente: {ae}")

# A função está faltando parâmetros e está referenciando a venda, não a compra
def inserir_custo_mensal(data: str):
    ven_df = selecionar_venda_data(data)
    soma_custo_variavel = ven_df.loc["ven_valor"].sum()

    sql_insert = """
                INSERT INTO Resultado(con_id, re_data, re_custo, re_montante) 
                VALUES (?, ?, ?, ?);
                """
    try:
        with conectar() as conn:
            conn.execute(sql_insert, (contrato, data))
            print(f"Inserido o custo mensal ({data}) do contrato: ({contrato})")
    except Error as e:
        print(f"Não foi possível adicionar custo mensal: {e}")
#Corrigir ou deletar, não faz sentido essa função
def tipo_movimentacao(e_venda: int, contrato: int, quantidade: int, valor: float, bolsa: str, ticker: str):
    if e_venda == 1:
        ""
        return True
    elif e_venda == 0:
        if atualizar_contrato_montante(contrato, valor):
            if atualizar_acao(quantidade, valor, contrato, bolsa, ticker):
                return True
            return False
        return False
    else:
        return False

def calcular_meses_preencher(contrato: int) -> int:
    data_str = selecionar_contrato_ultimo_resultado(contrato)
    if data_str != "":
        data_recente_resultado = converter_data(data_str)
        meses_faltantes = data_hoje.month - data_recente_resultado.month + (
                    (data_hoje.year - data_recente_resultado.year) * 12)
        return meses_faltantes
    else:
        raise ValueError("Não foi possível calcular os meses faltantes")

if __name__ == "__main__":
    inserir_indexador_nome("SELIC")
    preencher_resultados(12,128.91806602478027, 3)