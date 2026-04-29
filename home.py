import streamlit as st
import database as db
from database import tabela_acumulada
from database.utils import data_hoje

st.session_state["contrato_total"] = db.selecionar_contratos_id()
st.session_state["lucro_total"] = db.selecionar_venda_lucro_total()
if "lucro_total" not in st.session_state or "custo_total_mensal" not in st.session_state:
    st.session_state["lucro_total"] = db.selecionar_venda_lucro_total()
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
    valor = st.session_state.get("custo_total_mensal", 0) or 0
    sub_layout_sup[1].metric("Custo mensal previsto", f"R${valor:.2f}", width="content")

st.title("Contratos")

for contrato_id in st.session_state["contrato_total"]:
    acoes_df = db.selecionar_acoes_contrato(contrato_id)
    with st.container(key=f"card_contrato_{contrato_id}", border=True):
        card_layout = st.columns([2, 3])
        with card_layout[0]:
            st.subheader(f"Contrato {contrato_id}")
            st.write(" / ".join([acao["ti_ticker"] for _,acao in acoes_df.iterrows()]))
        with card_layout[1]:
            custo_mensal_atual = db.selecionar_contrato_custo_mensal(contrato_id, data_hoje().strftime("%Y-%m-%d"))
            st.metric(label="Custo mensal", value=f"R${custo_mensal_atual if custo_mensal_atual else -1.00:.2f}")
        with st.expander("Ver detalhes"):
            #Uma coluna de custo, outra de preço e outra de resultado
            df = db.selecionar_resultado_valores(contrato_id)
            df = df.rename(columns={"re_data":"Data", "re_custo":"Custo", "re_lucro":"Lucro", "re_montante":"Montante"})
            df = df.round(2)
            if df.empty:
                st.warning("Não foi possível carregar as informações do contrato")
            else:
                st.write("Tabela de histórico do contrato")
                if st.toggle("Acumulado", key=f"toggle_acumulado_{contrato_id}"):
                    df["Custo"] = df["Custo"].cumsum()
                    df["Lucro"] = df["Lucro"].cumsum()

                st.line_chart(df, width="stretch", x="Data", y_label="Valor")