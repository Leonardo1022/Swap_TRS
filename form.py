import streamlit as st
from database import Database

if "mostrar_form" not in st.session_state:
    st.session_state["mostrar_form"] = False

def st_trocar_form():
    st.session_state["mostrar_form"] = not st.session_state["mostrar_form"]

def st_enviar_form():
    if not st.session_state["ticker_ms"]:
        st.error("Não foi registrado nenhum ticker!")
    else:
        st.success("Contrato adicionado com sucesso!")
        st_trocar_form()
        d = Database("swap.db")
        #Alterar para st., alterar o metodo para atualizar a arquitetura do banco
        d.inserir_contrato(montante_c, dt_compra_c, duracao_c, indexador_c, spread_c)
        d.fechar()


lista_bolsa = ["B3", "NASDAQ"]
lista_ticker = []
lista_ticker_b3 = ["PETR4", "VALE3"]
lista_ticker_nasdaq = ["NVDA", "MSFT"]

st.title("Contratos")
st.write("Adicionar contrato")

st.button("Adicionar contrato", on_click=st_trocar_form)

enviado = False
if st.session_state.mostrar_form:
    st.selectbox("Selecione a Bolsa", lista_bolsa, key="bolsa_sb", index=None, placeholder="")

    if st.session_state["bolsa_sb"] == "B3":
         lista_ticker = lista_ticker_b3
    elif st.session_state["bolsa_sb"] == "NASDAQ":
         lista_ticker = lista_ticker_nasdaq
    else:
        lista_ticker = None

    st.multiselect("Selecione o Ticker", lista_ticker, placeholder="", accept_new_options=True, key="ticker_ms", disabled=(lista_ticker is None))
    for ticker in st.session_state["ticker_ms"]:
        st.number_input(f"Quantidade de ações de {ticker}", min_value=0, key=f"qtd_compra_{ticker}")
        st.number_input(f"Valor do montante de {ticker}", min_value=0.00, key=f"montante_{ticker}")
    dt_compra_c = st.date_input("Coloque a data de início", format="DD/MM/YYYY")
    duracao_c = st.number_input("Duração do contrato em meses", min_value=0)
    st.write("Taxas")
    indexador_c = st.selectbox("Selecione o indexador", ["CDI", "SELIC"], index=None, placeholder="")
    st.number_input("Spread em (%)", min_value=0.0, key="spread_ni")
    if st.session_state["spread_ni"] != 0:
        st.button("Adicionar", on_click=st_trocar_form)