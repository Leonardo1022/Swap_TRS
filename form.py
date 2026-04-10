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

bolsas_str = db.selecionar_bolsas()
lista_bolsa = inicializacao()

@st.cache_data(show_spinner=False, ttl="6h")
def preco_acao_data(ticker: str, data: str):
    if ticker is not None or "":
        ticker_obj = yf.Ticker(ticker)
        data = datetime.strptime(data, "%Y-%m-%d")
        dado = ticker_obj.history(start=data, end=data+dt.timedelta(days=1))
        return float(dado["Close"].iloc[0]) if not dado.empty else 0.00
    else:
        return None

def st_enviar_form(montante_total: float):
    contrato_id = db.inserir_contrato(montante_total, str(st.session_state["data_di"]), st.session_state["duracao_ni"])
    db.preencher_resultado(contrato_id, montante, st.session_state["duracao_ni"])
    db.inserir_taxa(contrato_id, st.session_state["indexador_sb"], st.session_state["spread_ni"])

    for t in st.session_state["ticker_ms"]:
        db.inserir_acao(contrato_id, t, st.session_state["bolsa_sb"], st.session_state[f"qtd_compra_{t}"], (st.session_state[f"valor_{t}"]*st.session_state[f"qtd_compra_{t}"]))
    return True

#Começo
st.title("Contratos")
st.space("small")

enviado = False
with st.expander("Adicionar contrato"):
    st.date_input("Coloque a data de início", key="data_di", format="DD/MM/YYYY")
    bolsa_str = st.selectbox("Selecione a Bolsa", lista_bolsa, key="bolsa_sb", index=None, placeholder="")

    lista_ticker = db.selecionar_tickers(bolsa_str)

    st.multiselect("Selecione o Ticker", lista_ticker, placeholder="", accept_new_options=True, key="ticker_ms", disabled=(lista_ticker is None))
    for ticker in st.session_state["ticker_ms"]:
        ticker_sufixo_str = db.selecionar_bolsa(bolsa_str)["bo_sufixo"]
        valor_acao_atual = preco_acao_data(ticker+ticker_sufixo_str, st.session_state["data_di"].strftime("%Y-%m-%d"))
        qtd = st.number_input(f"Quantidade de ações de {ticker}", min_value=0, key=f"qtd_compra_{ticker}")
        valor_acao = st.number_input(f"Valor individual da ação {ticker}", min_value=0.00, key=f"valor_{ticker}", value=valor_acao_atual)
        montante = valor_acao * qtd
        st.caption(f"Valor do montante da ação {ticker}: {montante:.2f}")
        #st.number_input(f"Valor do montante de {ticker}", min_value=0.00, key=f"montante_{ticker}", value=montante)
    st.number_input("Duração do contrato em meses", min_value=0, key="duracao_ni")
    st.write("Taxas")
    indexador_str = st.selectbox("Selecione o indexador", ["SOFR", "SELIC", "TONAR"], index=None, placeholder="", key="indexador_sb")
    spread_float = st.number_input("Spread em (%)", min_value=0.0, key="spread_ni")
    taxa_unica = st.number_input("Selecione o valor da taxa de transação (se houver)", min_value=0.00, placeholder="", key="taxa_ni")
    montante_total = 0.00
    for ticker in st.session_state["ticker_ms"]:
        montante_total += (st.session_state[f"qtd_compra_{ticker}"] * st.session_state[f"valor_{ticker}"])
    valor_final = montante_total + taxa_unica
    df_ind = db.selecionar_indexadores()
    if not df_ind.loc[df_ind["ind_indexador"] == indexador_str, "ind_valor"].empty:
        indexador_valor = df_ind.loc[df_ind["ind_indexador"] == indexador_str, "ind_valor"].iloc[0]
    else:
        indexador_valor = 0
    taxa_mensal = (valor_final - taxa_unica) * (indexador_valor + (spread_float / 100))
    st.caption(f"Valor final: {valor_final:.2f}")
    st.caption(f"Taxa mensal esperada: {taxa_mensal:.2f} (com taxa {indexador_str} a {indexador_valor*100:.2f}% a.a)")
    if st.button("Adicionar", disabled=(st.session_state["spread_ni"] == 0)):
        if st_enviar_form(montante_total):
            st.success("Contrato adicionado com sucesso!")
        else:
            st.error("Não foi registrado nenhum ticker!")


with st.expander("Adicionar Movimentação"):
    contratos_id = db.selecionar_contratos_id()
    if not contratos_id:
        st.error("Não tem contratos cadastrados")
        st.stop()
    tipo = st.radio("Selecione o tipo de movimentação", options=["Compra", "Venda"], horizontal=True)
    contrato_id = st.selectbox("Selecione o contrato", options=contratos_id, key="contrato_id")
    acoes_list = db.selecionar_acao(contrato_id)
    #st.write(acoes_list)
    if not acoes_list:
        st.warning("Esse contrato não possui ações cadastradas")
        st.stop()
    ticker_str = st.selectbox("Selecione o ticker", options=[acao["ti_ticker"] for acao in acoes_list])
    data = st.date_input(f"Coloque a data de {"venda" if tipo == "Venda" else "compra"}", format="DD/MM/YYYY", key="data_di_2")
    ticker_qtd = st.number_input("Selecione a quantidade", min_value=0)
    bolsa_info = db.selecionar_bolsa(acoes_list[0]["bo_bolsa"])
    ticker_sufixo_str = bolsa_info.get("bo_sufixo", "")
    bolsa_moeda_str = bolsa_info.get("bo_moeda", "R$")
    ticker_valor = st.number_input(f"Selecione o valor de cada ação (em {bolsa_moeda_str})", min_value=0.00, placeholder="", value=float(f"{preco_acao_data(ticker_str+ticker_sufixo_str, str(data)):.2f}"))
    taxa_unica = st.number_input("Selecione o valor da taxa de transação (se houver)", min_value=0.00, placeholder="")
    st.caption(f"Valor final: {((ticker_valor*ticker_qtd)+taxa_unica):.2f}")
    if st.button("Registrar movimentação"):
        if tipo == "Compra":
            e_venda = 0
        elif tipo == "Venda":
            e_venda = 1
        if db.inserir_movimentacao(contrato_id, acoes_list[0]["bo_bolsa"], ticker_str, ticker_qtd, (ticker_valor*ticker_qtd), data.strftime("%Y-%m-%d"), e_venda):
            st.success("Movimentação registrada com sucesso")
        else:
            st.error("Não foi possível fazer a movimentação")