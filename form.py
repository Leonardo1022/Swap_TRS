import streamlit as st
from database import Database

if "mostrar_form" not in st.session_state:
    st.session_state["mostrar_form"] = False

def st_trocar_form():
    st.session_state["mostrar_form"] = not st.session_state["mostrar_form"]


lista_bolsa = ["B3", "NASDAQ"]
lista_ticker = []
lista_ticker_b3 = ["PETR4", "VALE3"]
lista_ticker_nasdaq = ["NVDA", "MSFT"]

st.title("Contratos")
st.write("Adicionar contrato")

st.button("Adicionar contrato", on_click=st_trocar_form)

if st.session_state.mostrar_form:
    bolsa_c = st.selectbox("Selecione a Bolsa", lista_bolsa, key=1, index=None, placeholder="")

    if st.session_state[1] == "B3":
         lista_ticker = lista_ticker_b3
    elif st.session_state[1] == "NASDAQ":
         lista_ticker = lista_ticker_nasdaq
    else:
        lista_ticker = None

        ticker_c = st.multiselect("Selecione o Ticker", lista_ticker, placeholder="", accept_new_options=True, key=2, disabled=(lista_ticker is None))

        montante_c = st.number_input("Valor do montante", min_value=0.00)
        qtd_compra_c = st.number_input("Quantidade de ações", min_value=0)
        dt_compra_c = st.date_input("Coloque a data de início", format="DD/MM/YYYY")
        duracao_c = st.number_input("Duração do contrato em meses", min_value=0)
        st.write("Taxas")
        indexador_c = st.selectbox("Selecione o indexador", ["CDI", "SELIC"], index=None, placeholder="")
        spread_c = st.number_input("Spread em (%)", min_value=0.0)
"""        
        enviado = True

    if enviado:
        if not ticker_c:
            st.error("Não foi registrado nenhum ticker!")
        elif qtd_compra_c == 0 or dt_compra_c == 0 or duracao_c == 0 or montante_c == 0 or spread_c == 0:
            st.error("Um dos campos tem valor 0")
        elif not indexador_c:
            st.error("Não foi registrado nenhum indexador!")
        else:
            st.success("Contrato adicionado com sucesso!")
            st_trocar_form()
            d = Database("swap.db")
            d.inserir_contrato(montante_c, dt_compra_c, duracao_c, indexador_c, spread_c)
            d.fechar()
"""