from datetime import datetime
from dateutil.relativedelta import relativedelta

ticker_list = []
ticker_list_test = [{'nome': 'PETR4', 'preco': 2.0, 'quantidade': 50}, {'nome': 'VALE3', 'preco': 30.0, 'quantidade': 2}]
montante_total = 0.00

data_hoje = datetime.today()

def calcular_valor_total_taxa(historico: list):
    valor_total_taxa = 0.00
    for item in historico:
        valor_total_taxa += item["taxa"]
    return valor_total_taxa

def montar_historico(contrato: dict):
    historico = []
    meses_faltantes = calcular_meses_diferenca(data_hoje, contrato['data'])
    print(f"meses faltantes: {meses_faltantes}")
    data_calculada = contrato['data']
    for mes in range(meses_faltantes):
        dt = data_calculada + relativedelta(months=mes + 1)
        taxa_anual = contrato['taxa']
        taxa_mensal = (1 + taxa_anual) ** (1 / 12) - 1
        custo_mensal = contrato['montante'] * taxa_mensal
        #print(dt)
        historico.append({'taxa': custo_mensal, 'data':dt, 'montante': contrato['montante']})
    return {'historico_list': historico, 'meses_faltantes_int':meses_faltantes}

def calcular_meses_diferenca(data_recente: datetime, data_antiga: datetime):
    ano_diferenca = data_recente.year - data_antiga.year
    return (data_recente.month + (ano_diferenca * 12)) - data_antiga.month

if __name__ == "__main__":
    resp = input("Usar modelo? (s/n)\n")
    #Para caso de testes
    if resp == "s":
        contrato_dict = {'data': datetime.strptime("2025-01-01", "%Y-%m-%d"), 'taxa': 0.17, 'tickers': ticker_list_test, 'montante': 160.00}
        print(contrato_dict)
        output_dict = montar_historico(contrato_dict)
        print(output_dict['historico_list'])
        valor_taxa = calcular_valor_total_taxa(output_dict['historico_list'])
        print(f"Valor total cobrado em {output_dict['meses_faltantes_int']} mes(es): {valor_taxa:.2f}")

    elif resp == "n":
        counter = int(input("Quantos tickers tem no contrato?\n"))
        for i in range(counter):
            ticker = {'nome': "", 'preco': 0.00, 'quantidade': 0}
            ticker['nome'] = input(f"Selecione o nome do ticker {i+1}\n")
            ticker['preco'] = float(input(f"Selecione o valor do ticker {ticker['nome']}\n"))
            ticker['quantidade'] = int(input(f"Selecione a quantidade do ticker {ticker['nome']}\n"))
            montante = ticker['quantidade'] * ticker['preco']
            print(f"Valor do montante da ação: {(ticker['quantidade'] * ticker['preco']):.2f}\n")
            montante_total += montante

            ticker_list.append(ticker)
        data_str = input("Selecione a data (YYYY-MM-DD)\n")
        data = datetime.strptime(data_str, "%Y-%m-%d")

        indexador_taxa = float(input("Qual o valor do indexador (a.a.)?\n"))
        spread_taxa = float(input("E o spread?\n"))
        taxa = indexador_taxa + spread_taxa
        contrato_dict = {'data': data, 'taxa': taxa, 'tickers': ticker_list, 'montante': montante_total}
        historico_dict = montar_historico(contrato_dict)
        print(historico_dict)

    #print(f"Resumo:\n")

    #print(ticker_list)