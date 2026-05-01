from datetime import datetime
from database.components import *
from dateutil.relativedelta import relativedelta
from calendar import monthrange
import requests

data_hoje = datetime.today()
ESCALA = 1_000_000 # Padrão adotado de 10^6

def multiplicar(a: int, b: int) -> int:
    return round(a * b / ESCALA)

def dividir(a: int, b: int) -> int:
    return round(a * ESCALA / b)
"""
Calcula quantos contratos serão afetados pela venda para o modelo FIFO.
Recebe o df com os dados da consulta feita pelo método selecionar_acao_primeiros_5_ticker().
Retorna os contratos e valores de venda.
"""
def calcular_venda(df: pd.DataFrame, quantidade: int, lucro_individual: int) -> list[dict[int, int]]:
    ticker = df["ti_ticker"].iloc[0]
    acao_list = []

    for _, linha in df.iterrows():
        qtd_disponivel = linha["ac_quantidade"]
        montante = linha["ac_montante"]
        preco_original = linha["ac_preco"]
        if qtd_disponivel >= quantidade:
            acao_id_int = atualizar_acao_quantidade(ticker, linha["con_id"], qtd_disponivel - quantidade, montante - (preco_original * quantidade))
            acao_list.append({acao_id_int: (lucro_individual*quantidade)}) #Dict com o id e lucro na venda
            quantidade = 0
            break
        else: #Caso o valor de venda seja maior que o registrado por um contrato
            quantidade -= qtd_disponivel
            acao_id_int = atualizar_acao_quantidade(ticker, linha["con_id"], 0, montante - (preco_original * qtd_disponivel))
            acao_list.append({acao_id_int: (lucro_individual*qtd_disponivel)})

    if quantidade > 0:
        print("Quantidade maior que disponível")
        return []
    else:
        print(f"Venda feita com sucesso")
        return acao_list

def recalcular_resultados(montante: float, contrato: int, data: str):
    atualizar_resultado_montante(montante, contrato, data)
    sql_update = """
                 UPDATE Resultado
                 SET re_custo = (SELECT con_mont * ( 
                     ( 
                         1 + COALESCE((SELECT ind_valor 
                                       FROM Indexador 
                                       WHERE ind_indexador = Contrato.con_indexador 
                                         AND STRFTIME('%Y', ind_data) = STRFTIME('%Y', re_data) 
                                         AND STRFTIME('%m', ind_data) = STRFTIME('%m', re_data) ), 0) 
                         ) * EXP(LOG(1 + Contrato.con_spread) / 12) - 1 
                     ) 
                                 FROM Contrato 
                                 WHERE Contrato.con_id = Resultado.con_id LIMIT 1)
                 WHERE con_id = ? 
                   AND STRFTIME('%Y', re_data) = ? 
                   AND STRFTIME('%m', re_data) = ?;
                 """
    meses_faltantes = calcular_meses_preencher(contrato) + 1
    data_inicial = converter_data(data)
    for mes in range(meses_faltantes):
        data_atual = data_inicial + relativedelta(months= mes + 1)
        try:
            with conectar() as conn:
                data_ano_str = str(data_atual.year)
                data_mes_str = f"{data_atual.month:02d}"
                conn.execute(sql_update, (contrato, data_ano_str, data_mes_str))
                conn.commit()
                print(f"Sucesso em atualizar_resultado_custo.\nContrato: {contrato}, Data atual: {data_atual}")
        except Error as e:
            print(f"Erro em atualizar_resultado_custo: {e}")



def inserir_venda_com_acao(quantidade: int, valor: float, data: str, acao_list: list[dict[int, float]]):
    venda_id_int = inserir_venda(quantidade, valor, data)

    contratos_list = []
    for acao_dict in acao_list:
        for key, valor in acao_dict.items():
            inserir_acao_venda(key, venda_id_int) #Key é id de contrato, não de acao
            atualizar_resultado_lucro(valor, key, data)
            contratos_list.append(key)
    print("Inserção de venda com ação realizada com sucesso")
    return set(contratos_list)

def preencher_resultados(contrato: int, montante: float, duracao_contrato: int):
    meses_faltantes = calcular_meses_preencher(contrato) + 1
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

def calcular_meses_preencher(contrato: int = None, data: str = None) -> int:
    if data is None:
        data_str = selecionar_contrato_ultimo_resultado(contrato)
    else:
        data_str = data
    if data_str != "":
        data_recente_resultado = converter_data(data_str)
        meses_faltantes = data_hoje.month - data_recente_resultado.month + (
                    (data_hoje.year - data_recente_resultado.year) * 12)
        return meses_faltantes
    else:
        raise ValueError("Erro em calcular_meses_preencher")

def tabela_acumulada(df: pd.DataFrame) -> pd.DataFrame:
    df["Custo"].cumsum()
    return df

if __name__ == "__main__":
    inserir_indexador_nome("SELIC")
    preencher_resultados(12,128.91806602478027, 3)