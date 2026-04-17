-- PRAGMA foreign_keys = ON;
DROP TABLE IF EXISTS Indexador;
DROP TABLE IF EXISTS Bolsa;
DROP TABLE IF EXISTS Ticker;
DROP TABLE IF EXISTS Contrato;
DROP TABLE IF EXISTS Resultado;
--DROP TABLE IF EXISTS Taxa;
DROP TABLE IF EXISTS Acao;
DROP TABLE IF EXISTS Venda;
DROP TABLE IF EXISTS AcaoVenda;
DROP TRIGGER IF EXISTS trg_verifica_venda;

/* Tabelas */
CREATE TABLE IF NOT EXISTS Indexador(
ind_indexador TEXT, --PK
ind_data DATE, --PK --AAA-MM-DD
ind_valor REAL NOT NULL, --Porcentagem,a.m
CONSTRAINT pk_Indexador PRIMARY KEY(ind_indexador, ind_data)
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
con_mont REAL, --moeda
con_abertura DATE DEFAULT CURRENT_DATE, --AAAA-MM-DD
con_duracao INTEGER NOT NULL, --mes
con_indexador TEXT NOT NULL,
con_spread REAL NOT NULL,
con_status INTEGER DEFAULT 1 --Bool
);

CREATE TABLE IF NOT EXISTS Resultado(
con_id INTEGER, --PK,FK
re_data DATE, --PK --AAAA-MM-DD
re_lucro REAL,
re_custo REAL,
re_montante REAL,
CONSTRAINT pk_Resultado PRIMARY KEY(con_id, re_data),
CONSTRAINT fk_Resultado_Contrato FOREIGN KEY(con_id)
REFERENCES Contrato(con_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Acao(
ac_id INTEGER CONSTRAINT pk_Acao PRIMARY KEY AUTOINCREMENT, --PK
con_id INTEGER NOT NULL, --UK,FK
bo_bolsa TEXT NOT NULL, --UK,FK
ti_ticker TEXT NOT NULL, --UK,FK
ac_quantidade INTEGER NOT NULL,
ac_montante REAL NOT NULL, --moeda
CONSTRAINT fk_Acao_Contrato FOREIGN KEY(con_id)
REFERENCES Contrato(con_id) ON DELETE CASCADE,
CONSTRAINT fk_Acao_Ticker FOREIGN KEY(bo_bolsa, ti_ticker)
REFERENCES Ticker(bo_bolsa, ti_ticker) ON DELETE CASCADE,
CONSTRAINT uk_Acao UNIQUE(con_id, bo_bolsa, ti_ticker)
);

CREATE TABLE IF NOT EXISTS Venda(
ven_id INTEGER CONSTRAINT pk_Venda PRIMARY KEY AUTOINCREMENT, --PK
ven_quantidade INTEGER NOT NULL,
ven_valor REAL NOT NULL, --moeda
ven_data DATE DEFAULT CURRENT_DATE
);

CREATE TABLE IF NOT EXISTS AcaoVenda(
ac_id INTEGER, --PK,FK
ven_id INTEGER, --PK,FK
CONSTRAINT pk_AcaoVenda PRIMARY KEY(ac_id, ven_id),
CONSTRAINT fk_AcaoVenda_Acao FOREIGN KEY(ac_id)
REFERENCES Acao(ac_id) ON DELETE CASCADE,
CONSTRAINT fk_AcaoVenda_Venda FOREIGN KEY(ven_id)
REFERENCES Venda(ven_id) ON DELETE CASCADE
);
--Arrumar
/* Triggers */
CREATE TRIGGER IF NOT EXISTS trg_calcula_venda
    BEFORE UPDATE ON Acao
    FOR EACH ROW
    BEGIN
        SELECT CASE
            WHEN NEW.ac_quantidade > OLD.ac_quantidade
            THEN
    end;

/*
CREATE TRIGGER IF NOT EXISTS trg_verifica_venda
BEFORE INSERT ON Venda
FOR EACH ROW
BEGIN
    SELECT
        CASE
            WHEN (
                (
                    SELECT COALESCE(SUM(ven_quantidade), 0)
                    FROM Venda
                    WHERE con_id = NEW.con_id
                      AND bo_bolsa = NEW.bo_bolsa
                      AND ti_ticker = NEW.ti_ticker
                )
                + NEW.ven_quantidade
            ) >
            (
                SELECT ac_quantidade
                FROM Acao
                WHERE con_id = NEW.con_id
                  AND bo_bolsa = NEW.bo_bolsa
                  AND ti_ticker = NEW.ti_ticker
            )
            THEN RAISE(ABORT, 'Quantidade vendida maior que a disponível')
        END;
END;
 */