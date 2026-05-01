from typing import TypedDict

class Ticker(TypedDict):
    ti_ticker: str
    ti_empresa: str

class Bolsa(TypedDict):
    bo_bolsa: str
    bo_moeda: str
    bo_sufixo: str

class Indexador(TypedDict):
    ind_indexador: str
    ind_data: str
    ind_valor: int

class Resultado(TypedDict):
    con_id: int
    re_data: str
    re_lucro: int
    re_custo: int
    re_montante: int

class Venda(TypedDict):
    ven_id: int
    ven_quantidade: int
    ven_valor: int
    ven_data: str

class Acao(TypedDict):
    ac_id: int
    con_id: int
    bo_bolsa: str
    ti_ticker: str
    ac_quantidade: int
    ac_preco: int
    ac_montante: int