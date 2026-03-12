import streamlit as st
import yfinance as yf

st.title("Página inicial")

layout_sup = st.columns([1,3])

top_esq_con = layout_sup[0].container(
    border=True, height="stretch", vertical_alignment="center"
)

with top_esq_con:
    sub_layout_sup = st.columns(2)
    sub_layout_sup[0].metric("Balanço geral", )
