# 📊 Swap TRS — Total Return Swap Manager

> Interface de suporte CRUD para gestão de contratos na modalidade **Total Return Swap (TRS)**, com coleta automatizada de dados de mercado e armazenamento local.

---

## 🎯 Objetivo

O **Swap TRS** é uma aplicação web desenvolvida em Python com o objetivo de facilitar o gerenciamento operacional de contratos de Swap na modalidade Total Return Swap. A ferramenta oferece uma interface intuitiva para registro, consulta, edição e exclusão de contratos, integrando dados de mercado em tempo real via Yahoo Finance.

---

## ✨ Funcionalidades

- **Cadastro de contratos** — Registro de novos contratos TRS com todas as informações relevantes (ativo de referência, partes envolvidas, datas, notional, etc.)
- **Consulta e listagem** — Visualização de contratos ativos e históricos com filtros e ordenação
- **Edição de contratos** — Atualização de dados cadastrais e condições contratuais
- **Exclusão de contratos** — Remoção segura de registros do banco de dados
- **Cotação automática de ativos** — Integração com Yahoo Finance para coleta de preços e informações de mercado das ações de referência
- **Cálculos de retorno** — Apuração de resultados financeiros com base nas variações de preço e datas de vigência do contrato

---

## 🛠️ Tecnologias

| Tecnologia | Versão recomendada | Finalidade |
|---|---|---|
| [Python](https://www.python.org/) | 3.10+ | Linguagem principal |
| [Streamlit](https://streamlit.io/) | — | Interface web (front-end) |
| [SQLite](https://www.sqlite.org/) | — | Armazenamento e persistência de dados |
| [pandas](https://pandas.pydata.org/) | — | Manipulação e exibição de dados tabulares |
| [yfinance](https://github.com/ranaroussi/yfinance) | — | Coleta de dados de mercado (ações) |
| [datetime](https://docs.python.org/3/library/datetime.html) | stdlib | Cálculos e formatação de datas |

---

## 📁 Estrutura do Projeto

```
Swap_TRS/
│
├── swap.db                  # Banco de dados SQLite
│
├── database/                # Camada de acesso a dados
│   ├── __init__.py
│   ├── connection.py        # Configuração e conexão com o banco
│   └── ...                  # Demais métodos e repositórios
│
├── app.py                   # Ponto de entrada da aplicação Streamlit
│
└── README.md
```

---

## 🚀 Como Executar

### Pré-requisitos

- Python 3.10 ou superior
- `pip` instalado

### Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/Swap_TRS.git
   cd Swap_TRS
   ```

2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

3. Execute a aplicação:
   ```bash
   streamlit run app.py
   ```

4. Acesse no navegador: `http://localhost:8501`

---

## 📌 O que é um Total Return Swap (TRS)?

Um **Total Return Swap** é um contrato de derivativo financeiro em que uma das partes (pagador do retorno total) transfere todos os retornos econômicos de um ativo de referência — incluindo valorização de preço e dividendos — para a outra parte (recebedor do retorno total), que em contrapartida paga uma taxa acordada (geralmente flutuante, como CDI ou SOFR). É amplamente utilizado para exposição sintética a ativos sem necessidade de posse direta.
