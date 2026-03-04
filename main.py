# Parte de base

import streamlit as st
import yfinance as yf
#uv run streamlit run main.py

# Streamlit
st.set_page_config(page_title="Data manager", page_icon=":material/edit:")

pag_form = st.Page("form.py", title="Criar Contrato")
pag_home = st.Page("home.py", title="Home")

pg = st.navigation({
    "Criar": [pag_form],
    "Home": [pag_home],
})

pg.run()