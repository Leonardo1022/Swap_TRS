import pandas as pd
import streamlit as st
import database as db
import yfinance as yf
import datetime as dt
from datetime import datetime
from decimal import Decimal

@st.cache_data()
def inicializacao():
    bolsa_l = db.selecionar_bolsas()
    bolsa_str_l = [bolsa["bo_bolsa"] for bolsa in bolsa_l]
    indexadores_l = db.selecionar_indexadores()
    return bolsa_l, bolsa_str_l, indexadores_l

if "init_form" not in st.session_state:
    st.session_state.init_form = True
    if "bolsa_selecionada" in st.session_state:
        del st.session_state.bolsa_selecionada
        del st.session_state.bolsa
        del st.session_state.datahora_selecionada

bolsa_list, bolsa_str_list, indexadores_list = inicializacao()

def st_enviar_form(mt: Decimal):
    contrato_id_int = db.inserir_contrato(mt, data_str, st.session_state["duracao_ni"], indexador_str, spread_str)
    db.preencher_resultados(contrato_id_int, mt, st.session_state["duracao_ni"])

    for t in st.session_state.tickers_selecionados:
        db.inserir_acao(contrato_id_int, bolsa_str, t, st.session_state[f"qtd_compra_{t["ti_ticker"]}"], (st.session_state[f"valor_{t["ti_ticker"]}"]*st.session_state[f"qtd_compra_{t}"]), st.session_state[f"valor_{t["ti_ticker"]}"])
    if "init_form" in st.session_state:
        del st.session_state.init_form
    return True

#Começo
st.title("Contratos")
st.space("small")

if "tickers_selecionados" in st.session_state and st.session_state.tickers_selecionados != []:
    st.write(st.session_state.tickers_selecionados)

enviado = False
with st.expander("Comprar"):
    datahora = st.datetime_input("Coloque a data de início", key="datahora_dti", format="DD/MM/YYYY",
                                 value=(None if "init_stockView" not in st.session_state
                                    else st.session_state.datahora_selecionada), disabled="init_stockView" in st.session_state)
    if datahora:
        data_str = datahora.strftime('%Y-%m-%d')

    bolsa_str = st.selectbox("Selecione a Bolsa", bolsa_str_list, key="bolsa_sb",
                             placeholder="", index=(None if "init_stockView" not in st.session_state
                                else bolsa_str_list.index(st.session_state.bolsa_selecionada)), disabled="init_stockView" in st.session_state)
    # Página de ações
    if bolsa_str:
        if st.button("Selecionar ações"):
            # Reinicia o state da página para a configuração inicial
            if "init_stockView" in st.session_state:
                del st.session_state.init_stockView
            st.session_state.bolsa_selecionada = bolsa_str
            st.session_state.datahora_selecionada = datahora
            st.switch_page("pages/stockView.py")

    if "tickers_selecionados" in st.session_state:
        print(f"tickers: {st.session_state.tickers_selecionados}")
        for ticker in st.session_state.tickers_selecionados:
            bolsa_dict = st.session_state.bolsa
            ticker_sufixo_str = bolsa_dict["bo_sufixo"]
            qtd = st.number_input(f"Quantidade de ações de {ticker['ti_ticker']}", min_value=0, key=f"qtd_compra_{ticker['ti_ticker']}")
            valor_acao = st.number_input(f"Valor individual da ação {ticker['ti_ticker']}", min_value=0.00, key=f"valor_{ticker['ti_ticker']}", value=float(round(ticker["valor"], 2)))
            montante = valor_acao * qtd
            st.caption(f"Valor do montante da ação {ticker['ti_ticker']}: {bolsa_dict["bo_moeda"]} {montante:.2f}")

        st.number_input("Duração do contrato em meses", min_value=1, key="duracao_ni")

        st.space("small")
        st.write("Taxas")

        indexador_str = st.selectbox("Selecione o indexador", indexadores_list, key="indexador_sb", index=None, placeholder="")
        spread_str = str(st.number_input("Spread em (%)", min_value=0.0, key="spread_ni") / 100)
        taxa_unica_str = str(st.number_input("Selecione o valor da taxa de transação (se houver)", min_value=0.00, placeholder="", key="taxa_ni"))

        montante_total = Decimal("0.00")
        for ticker in st.session_state.tickers_selecionados:
            montante_total += (st.session_state[f"qtd_compra_{ticker['ti_ticker']}"] * Decimal(st.session_state[f"valor_{ticker['ti_ticker']}"]))
            print(f"montante total: {montante_total}")

        valor_final = montante_total + Decimal(taxa_unica_str)
        valor_indexador = Decimal(db.selecionar_indexador(indexador_str, data_str))
        taxa_mensal = montante_total * (valor_indexador + Decimal(spread_str))
        if valor_final != 0.0:
            st.caption(f"Valor final: {valor_final:.2f}")
        if taxa_mensal != 0.0:
            st.caption(f"Taxa mensal esperada: {taxa_mensal:.2f} de {montante_total:.2f} (com taxa {indexador_str} a {valor_indexador*100:.2f}% a.m)")
        if st.button("Adicionar", disabled=(taxa_mensal != 0.0)):
            if st_enviar_form(montante_total):
                st.success("Compra registrada com sucesso!")
            else:
                st.error("Não foi registrado nenhum ticker!")


with st.expander("Vender"):
    contratos_id = db.selecionar_contratos_id()
    if not contratos_id:
        st.error("Não tem contratos cadastrados")
        st.stop()
    #tipo = st.radio("Selecione o tipo de movimentação", options=["Compra", "Venda"], horizontal=True)
    #contrato_id = st.selectbox("Selecione o contrato", options=contratos_id, key="contrato_id")
    acao_list = db.selecionar_acoes_disp()
    if not acao_list:
        st.warning("Você não possui ações cadastradas")
        st.stop()
    st.date_input(f"Coloque a data de venda", key="data_di_2", format="DD/MM/YYYY")
    data_ven_str = st.session_state["data_di_2"].strftime("%Y-%m-%d")
    st.multiselect("Selecione as ações", acao_list, key="acao_ms", placeholder="", accept_new_options=False,
                   disabled=(acao_list is []))

    valor_dict = dict()
    for acao in st.session_state["acao_ms"]:
        acao_info = db.selecionar_acao_ticker(acao)
        acao_qtd_max = db.selecionar_acao_qtd_acumulada(acao)
        bolsa_info = db.selecionar_bolsa(acao_info.get("bo_bolsa", ""))
        acao_sufixo_str = bolsa_info.get("bo_sufixo", "")
        bolsa_moeda_str = bolsa_info.get("bo_moeda", "R$")
        acao_valor_atual = preco_acao_data(acao + acao_sufixo_str, data_ven_str)

        acao_valor = st.number_input(f"Selecione o valor de venda da ação {acao}(em {bolsa_moeda_str})", key=f"valor_venda_{acao}", min_value=0.00,
                                       placeholder="",
                                       value=float(f"{acao_valor_atual:.2f}"))
        acao_qtd = st.number_input(f"Selecione a quantidade da ação {acao} (Quantidade disponível: {acao_qtd_max})", key=f"qtd_venda_{acao}", min_value=0, max_value=acao_qtd_max)
        montante = acao_valor * acao_qtd
        taxa_valor = st.number_input("Selecione o valor da taxa de transação (se houver)", key=f"taxa_unica_{acao}", min_value=0.00, placeholder="")
        if bolsa_moeda_str not in valor_dict.keys():
            valor_dict[bolsa_moeda_str] = montante + taxa_valor
        else:
            valor_dict[bolsa_moeda_str] += montante + taxa_valor
        st.caption(f"Valor do montante da ação {acao}: {bolsa_info.get("bo_moeda", "R$")} {montante:.2f}")
        st.space("small")
    print(valor_dict)

    montante_total_venda = 0.00
    taxa_unica_total = 0.00
    for acao in st.session_state["acao_ms"]:
        montante_total_venda += (st.session_state[f"qtd_venda_{acao}"] * st.session_state[f"valor_venda_{acao}"])
        taxa_unica_total += (st.session_state[f"taxa_unica_{acao}"])

    st.write("Valor final")
    for key, valor in valor_dict.items():
        st.caption(f"{key} {valor:.2f}")

    contratos_totais_list = []
    if st.button("Registrar venda"):
        for acao in st.session_state["acao_ms"]:
            acao_venda_float = st.session_state[f"valor_venda_{acao}"]
            tickers_5_list = db.selecionar_acao_primeiros_5_ticker(acao)
            df = pd.DataFrame(tickers_5_list)
            acao_venda_list = db.calcular_venda(df, st.session_state[f"qtd_venda_{acao}"], acao_venda_float)
            #ARRUMAR: A função recebe o nome da bolsa, não o ticker
            bolsa_venda_dict = db.selecionar_bolsa(acao)
            bolsa_venda_str = bolsa_venda_dict.get("bo_bolsa", "")
            #Insere uma venda para cada ação
            contratos_set = db.inserir_venda_com_acao(st.session_state[f"qtd_venda_{acao}"], acao_venda_float, data_ven_str, acao_venda_list)
            contratos_totais_list.extend(contratos_set)

        contratos_totais_set = set(contratos_totais_list)
        for contrato in contratos_totais_set:
            acao_df = db.selecionar_acoes_contrato(contrato)
            montante = acao_df["ac_montante"].sum()
            db.recalcular_resultados(montante, contrato, data_ven_str)
        st.success("Venda registrada com sucesso")

#acao_venda_list: lista com uma dict contendo contrato(key) e quantidade total de venda(valor)