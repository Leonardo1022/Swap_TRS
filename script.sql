-- PRAGMA foreign_keys = ON;
DROP TABLE IF EXISTS Indexador;
DROP TABLE IF EXISTS Bolsa;
DROP TABLE IF EXISTS Ticker;
DROP TABLE IF EXISTS Contrato;
DROP TABLE IF EXISTS Acao;
DROP TABLE IF EXISTS Venda;

/* Tabelas */
CREATE TABLE IF NOT EXISTS Indexador(
ind_indexador TEXT CONSTRAINT pk_Indexador PRIMARY KEY, --PK
ind_valor REAL NOT NULL --porcentagem,a.a
);

CREATE TABLE IF NOT EXISTS Bolsa(
bo_bolsa TEXT CONSTRAINT pk_Bolsa PRIMARY KEY, --PK
bo_moeda TEXT NOT NULL,
bo_sufixo TEXT NOT NULL --Necessário para o Yahoo Finance
);

CREATE TABLE IF NOT EXISTS Ticker(
bo_bolsa TEXT, --PK,FK
ti_ticker TEXT, --PK
CONSTRAINT fk_Ticker_Bolsa FOREIGN KEY(bo_bolsa)
REFERENCES Bolsa(bo_bolsa) ON DELETE CASCADE,
CONSTRAINT pk_Ticker PRIMARY KEY(bo_bolsa, ti_ticker)
);

CREATE TABLE IF NOT EXISTS Contrato(
con_id INTEGER CONSTRAINT pk_con_id PRIMARY KEY AUTOINCREMENT, --PK
ind_indexador TEXT NOT NULL, --FK
con_mont REAL, --moeda
con_data DATE DEFAULT CURRENT_DATE,
con_dur INTEGER NOT NULL, --mes
con_spd REAL, --porcentagem
CONSTRAINT fk_Contrato_Indexador FOREIGN KEY(ind_indexador)
REFERENCES Indexador(ind_indexador) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Acao(
con_id INTEGER, --PK,FK
bo_bolsa TEXT, --PK,FK
ti_ticker TEXT, --PK,FK
ac_qtd INTEGER NOT NULL,
ac_mont REAL NOT NULL, --moeda
CONSTRAINT fk_Acao_Contrato FOREIGN KEY(con_id)
REFERENCES Contrato(con_id) ON DELETE CASCADE,
CONSTRAINT fk_Acao_Ticker FOREIGN KEY(bo_bolsa, ti_ticker)
REFERENCES Ticker(bo_bolsa, ti_ticker) ON DELETE CASCADE,
CONSTRAINT pk_Acao PRIMARY KEY(con_id, ti_ticker, bo_bolsa)
);

CREATE TABLE IF NOT EXISTS Venda(
ven_id INTEGER CONSTRAINT pk_ven_id PRIMARY KEY AUTOINCREMENT, --PK
con_id INTEGER, --FK
ti_ticker TEXT, --FK
bo_bolsa TEXT, --FK
ven_qtd INTEGER NOT NULL,
ven_vlr REAL NOT NULL, --moeda
ven_data DATE DEFAULT CURRENT_DATE,
CONSTRAINT fk_Venda_Acao FOREIGN KEY(con_id, ti_ticker, bo_bolsa)
REFERENCES Acao(con_id, ti_ticker, bo_bolsa) ON DELETE CASCADE
);

/* Triggers */
CREATE TRIGGER IF NOT EXISTS trg_verifica_venda
BEFORE INSERT ON Venda
FOR EACH ROW
BEGIN
    SELECT
        CASE
            WHEN (
                (
                    SELECT COALESCE(SUM(ven_qtd), 0)
                    FROM Venda
                    WHERE con_id = NEW.con_id
                      AND bo_bolsa = NEW.bo_bolsa
                      AND ti_ticker = NEW.ti_ticker
                )
                + NEW.ven_qtd
            ) >
            (
                SELECT ac_qtd
                FROM Acao
                WHERE con_id = NEW.con_id
                  AND bo_bolsa = NEW.bo_bolsa
                  AND ti_ticker = NEW.ti_ticker
            )
            THEN RAISE(ABORT, 'Quantidade vendida maior que a disponível')
        END;
END;