import streamlit as st
import database as db
import yfinance as yf
st.session_state["contrato_total"] = db.selecionar_contratos()
if "lucro_total" not in st.session_state or "custo_total_mensal" not in st.session_state:
    st.session_state["lucro_total"] = db.lucro_total()
    st.session_state["custo_total_mensal"] = db.custo_total_mensal()
    st.session_state["contrato_total"] = db.selecionar_contratos()

st.title("Página inicial")

st.space("small")

layout_sup = st.columns([2,2])

top_esq_con = layout_sup[0].container(
    border=True, height="stretch", vertical_alignment="center"
)

with top_esq_con:
    sub_layout_sup = st.columns(2)
    sub_layout_sup[0].metric("Balanço geral", f"R${st.session_state["lucro_total"]}")
    sub_layout_sup[1].metric("Custo mensal previsto", f"R${st.session_state["custo_total_mensal"]}", width="content")

st.title("Contratos")

for id in st.session_state["contrato_total"]:
    with st.container(height=100, key=f"card_contrato_{id}"):
        st.subheader(f"Contratos {id}")
        st.write(" / ".join(db.selecionar_acao(id)))