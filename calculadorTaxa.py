import pandas as pd
import requests

codigo_serie_dict = [{"taxa": "CDI a.d", "codigo": 12},
                     {"taxa": "SELIC a.d", "codigo": 11}]

def tabela_juros_acumulado_mensal( codio_serie, data_inicial, data_final):
    url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codio_serie}/dados?formato=json&{data_inicial}&{data_final}"
    try:
        df = pd.DataFrame(requests.get(url).json())
        df["data"] = pd.to_datetime(df["data"], dayfirst=True)
        df["valor"] = df["valor"].astype(float)

        df["valor"] = df["valor"] / 100

        # Agrupar por mês (taxa acumulada)
        df["mes"] = df["data"].dtypes.to_period("M")
        taxa_mensal = df.groupby("mes")["valor"].apply(
            lambda x: (1 + x).prod() - 1
        ).reset_index()

        taxa_mensal["data"] = taxa_mensal["mes"].dt.to_timestamp("M")
        taxa_mensal = taxa_mensal[["data", "valor"]]
        return taxa_mensal
    except:
        return None
