import streamlit as st
import database as db
import yfinance as yf
st.session_state["contrato_total"] = db.selecionar_contrato_id()
st.session_state["lucro_total"] = db.lucro_total()
if "lucro_total" not in st.session_state or "custo_total_mensal" not in st.session_state:
    st.session_state["lucro_total"] = db.lucro_total()
    st.session_state["custo_total_mensal"] = db.custo_total_mensal()
    st.session_state["contrato_total"] = db.selecionar_contrato_id()

st.title("Página inicial")

st.space("small")

layout_sup = st.columns([2,2])

top_esq_con = layout_sup[0].container(
    border=True, height="stretch", vertical_alignment="center"
)

with top_esq_con:
    sub_layout_sup = st.columns(2)
    sub_layout_sup[0].metric("Balanço geral", f"R${st.session_state["lucro_total"]:.2f}")
    sub_layout_sup[1].metric("Custo mensal previsto", f"R${st.session_state["custo_total_mensal"]:.2f}", width="content")

st.title("Contratos")

for id in st.session_state["contrato_total"]:
    with st.container(key=f"card_contrato_{id}", border=True):
        card_layout = st.columns([2, 3])
        with card_layout[0]:
            st.subheader(f"Contrato {id}")
            st.write(" / ".join(db.selecionar_acao(id)))
        with card_layout[1]:
            custo_mensal = db.custo_mensal_contrato(id)
            st.metric(label="Custo mensal", value=f"R${custo_mensal:.2f}")
        with st.expander("See explanation"):
            st.write('''
                The chart above shows some numbers I picked for you.
                I rolled actual dice for these, so they're *guaranteed* to
                be random.
            ''')