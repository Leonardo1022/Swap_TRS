import streamlit as st
# Streamlit
st.set_page_config(page_title="Data manager", page_icon=":material/edit:")

pag_form = st.Page("form.py", title="Criar Contrato")
pag_home = st.Page("home.py", title="Home")
pag_stock = st.Page("pages/stockView.py", title="Ações")

# Sobrescreve a sidebar para ocultar páginas específicas
st.markdown("""
<style>
    [data-testid="stSidebarNav"] a[href*="stockView"] {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

pg = st.navigation({
    "Criar": [pag_form],
    "Home": [pag_home],
    "": [pag_stock], # Páginas ocultas
})
pg.run()