import streamlit as st
import database as db
import yfinance as yf
import datetime as dt
from datetime import datetime

@st.cache_data()
def inicializacao():
    lista_bolsa = db.selecionar_bolsas()
    print(lista_bolsa)
    return lista_bolsa

bolsa_list = inicializacao()

@st.cache_data(show_spinner=False, ttl="6h")
def preco_acao_data(ticker: str, data: str) -> float:
    if ticker is not None or "":
        try:
            ticker_obj = yf.Ticker(ticker)
            data_ref = datetime.strptime(data, "%Y-%m-%d")
            data_ini = data_ref - dt.timedelta(days=10) #Busca até 10 dias anteriores ao dia passado
            df = ticker_obj.history(start=data_ini, end=data_ref+dt.timedelta(days=1))
            if df.empty:
                print(f"Ticker {ticker} inexistente")
                return 0.0
            preco_acao_float = float(df["Close"].dropna().iloc[-1]) #Pega o preço mais recente disponível
            print(f"Preço da ação {ticker}: {preco_acao_float if preco_acao_float != 0.00 else '0.00'} no dia {data}")
            return preco_acao_float
        except ValueError as ve:
            print(ve)
            return 0.00
    else:
        return 0.00

def st_enviar_form(montante_total: float):
    contrato_id_int = db.inserir_contrato(montante_total, data_ab_str, st.session_state["duracao_ni"], indexador_str, spread_float)
    db.preencher_resultados(contrato_id_int, montante_total, st.session_state["duracao_ni"])

    for t in st.session_state["ticker_ms"]:
        db.inserir_acao(contrato_id_int, bolsa_str, t, st.session_state[f"qtd_compra_{t}"], (st.session_state[f"valor_{t}"]*st.session_state[f"qtd_compra_{t}"]))
    return True

#Começo
st.title("Contratos")
st.space("small")

#e_venda = st.toggle("Venda")

enviado = False
with st.expander("Comprar"):
    st.date_input("Coloque a data de início", key="data_di", format="DD/MM/YYYY")
    data_ab_str = st.session_state["data_di"].strftime("%Y-%m-%d")
    bolsa_str = st.selectbox("Selecione a Bolsa", bolsa_list, key="bolsa_sb", index=None, placeholder="")

    lista_ticker = db.selecionar_tickers(bolsa_str)
    #print(f"Esta é a lista de ticker {lista_ticker}")

    st.multiselect("Selecione o Ticker", lista_ticker, key="ticker_ms", placeholder="", accept_new_options=True, disabled=(lista_ticker is [] or bolsa_str is None))
    for ticker in st.session_state["ticker_ms"]:
        bolsa_dict = db.selecionar_bolsa(bolsa_str)
        ticker_sufixo_str = bolsa_dict["bo_sufixo"]
        valor_acao_atual = preco_acao_data(ticker+ticker_sufixo_str, data_ab_str)
        qtd = st.number_input(f"Quantidade de ações de {ticker}", min_value=0, key=f"qtd_compra_{ticker}")
        valor_acao = st.number_input(f"Valor individual da ação {ticker}", min_value=0.00, key=f"valor_{ticker}", value=valor_acao_atual)
        montante = valor_acao * qtd
        st.caption(f"Valor do montante da ação {ticker}: {bolsa_dict["bo_moeda"]} {montante:.2f}")

    st.number_input("Duração do contrato em meses", min_value=1, key="duracao_ni")
    st.space("small")
    st.write("Taxas")
    indexado_list = db.selecionar_indexadores()
    indexador_str = st.selectbox("Selecione o indexador", indexado_list, key="indexador_sb", index=None, placeholder="")
    spread_float = st.number_input("Spread em (%)", min_value=0.0, key="spread_ni") / 100
    taxa_unica = st.number_input("Selecione o valor da taxa de transação (se houver)", min_value=0.00, placeholder="", key="taxa_ni")

    montante_total = 0.00
    for ticker in st.session_state["ticker_ms"]:
        montante_total += (st.session_state[f"qtd_compra_{ticker}"] * st.session_state[f"valor_{ticker}"])
    #print(f"montante total: {montante_total}")

    valor_final = montante_total + taxa_unica
    valor_indexador = db.selecionar_indexador(indexador_str, data_ab_str)
    taxa_mensal = montante_total * (valor_indexador + spread_float)
    st.caption(f"Valor final: {valor_final:.2f}")
    st.caption(f"Taxa mensal esperada: {taxa_mensal:.2f} de {montante_total:.2f} (com taxa {indexador_str} a {valor_indexador*100:.2f}% a.m)")
    if st.button("Adicionar", disabled=(st.session_state["spread_ni"] == 0)):
        if st_enviar_form(montante_total):
            st.success("Compra registrada com sucesso!")
        else:
            st.error("Não foi registrado nenhum ticker!")


with st.expander("Vender"):
    contratos_id = db.selecionar_contratos_id()
    if not contratos_id:
        st.error("Não tem contratos cadastrados")
        st.stop()
    #tipo = st.radio("Selecione o tipo de movimentação", options=["Compra", "Venda"], horizontal=True)
    #contrato_id = st.selectbox("Selecione o contrato", options=contratos_id, key="contrato_id")
    acao_list = db.selecionar_acoes()
    if not acao_list:
        st.warning("Você não possui ações cadastradas")
        st.stop()
    st.date_input(f"Coloque a data de venda", key="data_di_2", format="DD/MM/YYYY")
    data_ven_str = st.session_state["data_di_2"].strftime("%Y-%m-%d")
    st.multiselect("Selecione as ações", acao_list, key="acao_ms", placeholder="", accept_new_options=False,
                   disabled=(acao_list is []))

    valor_dict = dict()
    for acao in st.session_state["acao_ms"]:
        acao_info = db.selecionar_acao_ticker(acao)
        acao_qtd_max = db.selecionar_acao_qtd_acumulada(acao)
        bolsa_info = db.selecionar_bolsa(acao_info.get("bo_bolsa", ""))
        acao_sufixo_str = bolsa_info.get("bo_sufixo", "")
        bolsa_moeda_str = bolsa_info.get("bo_moeda", "R$")
        acao_valor_atual = preco_acao_data(acao + acao_sufixo_str, data_ven_str)

        acao_valor = st.number_input(f"Selecione o valor de venda da ação {acao}(em {bolsa_moeda_str})", key=f"valor_venda_{acao}", min_value=0.00,
                                       placeholder="",
                                       value=float(f"{acao_valor_atual:.2f}"))
        acao_qtd = st.number_input(f"Selecione a quantidade da ação {acao}", key=f"qtd_venda_{acao}", min_value=0, max_value=acao_qtd_max)
        montante = acao_valor * acao_qtd
        taxa_valor = st.number_input("Selecione o valor da taxa de transação (se houver)", key=f"taxa_unica_{acao}", min_value=0.00, placeholder="")
        if bolsa_moeda_str not in valor_dict.keys():
            valor_dict[bolsa_moeda_str] = acao_valor + taxa_valor
        else:
            valor_dict[bolsa_moeda_str] += acao_valor + taxa_valor
        st.caption(f"Valor do montante da ação {acao}: {bolsa_info.get("bo_moeda", "R$")} {montante:.2f}")
        st.space("small")
    print(valor_dict)

    montante_total_venda = 0.00
    taxa_unica_total = 0.00
    for acao in st.session_state["acao_ms"]:
        montante_total_venda += (st.session_state[f"qtd_venda_{acao}"] * st.session_state[f"valor_venda_{acao}"])
        taxa_unica_total += (st.session_state[f"taxa_unica_{acao}"])

    st.write("Valor final")
    for key, valor in valor_dict.items():
        st.caption(f"{key} {valor:.2f}")

    if st.button("Registrar venda"):
        for acao in st.session_state["acao_ms"]:
            acao_venda_float = st.session_state[f"valor_venda_{acao}"]
            df = db.selecionar_acao_primeiros_5_ticker(acao)
            acao_venda_list = db.calcular_venda(df, st.session_state[f"qtd_venda_{acao}"], acao_venda_float)
            bolsa_venda_dict = db.selecionar_bolsa(acao)
            bolsa_venda_str = bolsa_venda_dict.get("bo_bolsa", "")
            #Insere uma venda para cada ação
            db.inserir_venda_com_acao(st.session_state[f"qtd_venda_{acao}"], acao_venda_float, data_ven_str, acao_venda_list)

        st.success("Venda registrada com sucesso")
        #st.error("Não foi possível fazer a venda")