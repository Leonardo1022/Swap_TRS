import streamlit as st
import database as db
from datetime import datetime

data_hoje = datetime.today()
st.session_state["contrato_total"] = db.selecionar_contratos_id()
st.session_state["lucro_total"] = db.selecionar_movimentacao_lucro_total()
if "lucro_total" not in st.session_state or "custo_total_mensal" not in st.session_state:
    st.session_state["lucro_total"] = db.selecionar_movimentacao_lucro_total()
    st.session_state["custo_total_mensal"] = db.selecionar_contratos_custo_mensal()
    st.session_state["contrato_total"] = db.selecionar_contratos_id()

st.title("Página inicial")

st.space("small")

layout_sup = st.columns([2,2])

top_esq_con = layout_sup[0].container(
    border=True, height="stretch", vertical_alignment="center"
)

with top_esq_con:
    sub_layout_sup = st.columns(2)
    sub_layout_sup[0].metric("Balanço geral", f"R${st.session_state["lucro_total"]:.2f}")
    sub_layout_sup[1].metric("Custo mensal previsto", f"R${st.session_state["custo_total_mensal"] if not None else 0:.2f}", width="content")

st.title("Contratos")

for contrato_id in st.session_state["contrato_total"]:
    acoes_list = db.selecionar_acao(contrato_id)
    with st.container(key=f"card_contrato_{contrato_id}", border=True):
        card_layout = st.columns([2, 3])
        with card_layout[0]:
            st.subheader(f"Contrato {contrato_id}")
            st.write(" / ".join([acao["ti_ticker"] for acao in acoes_list]))
        with card_layout[1]:
            custo_mensal_atual = db.selecionar_contrato_custo_mensal(contrato_id, data_hoje.strftime("%Y-%m-%d"))
            st.metric(label="Custo mensal", value=f"R${custo_mensal_atual if custo_mensal_atual else -1.00:.2f}")
        with st.expander("Ver detalhes"):
            st.write("Tabela de histórico do contrato")
            #Uma coluna de custo, outra de preço e outra de resultado
            df = db.selecionar_resultado_valores(contrato_id)
            st.line_chart(df, width="stretch")