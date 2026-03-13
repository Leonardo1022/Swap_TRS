import streamlit as st
from database import Database
import yfinance as yf
d = Database("swap.db")

st.title("Página inicial")

layout_sup = st.columns([1,3])

top_esq_con = layout_sup[0].container(
    border=True, height="stretch", vertical_alignment="center"
)

with top_esq_con:
    sub_layout_sup = st.columns(2)
    sub_layout_sup[0].metric("Balanço geral", f"R${d.lucro_total()}", width="content")
    sub_layout_sup[1].metric("Custo mensal previsto", f"R$", width="content")