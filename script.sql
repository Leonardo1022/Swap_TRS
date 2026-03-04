-- BEGIN TRANSACTION;
-- PRAGMA foreign_keys = ON;
DROP TABLE IF EXISTS Bolsa;
DROP TABLE IF EXISTS Contrato;
DROP TABLE IF EXISTS Acao;
DROP TABLE IF EXISTS Venda;

/* Tabelas */
CREATE TABLE IF NOT EXISTS Bolsa(
bo_ticker TEXT, --PK
bo_bolsa TEXT, --PK
CONSTRAINT pk_Bolsa PRIMARY KEY(bo_ticker, bo_bolsa)
);

CREATE TABLE IF NOT EXISTS Contrato(
con_id INTEGER CONSTRAINT pk_con_id PRIMARY KEY AUTOINCREMENT, --PK
con_mont INTEGER, --dividir por 100
con_data DATE DEFAULT CURRENT_DATE,
con_dur INTEGER,
con_ind TEXT,
con_spd INTEGER --dividir por 100
);

CREATE TABLE IF NOT EXISTS Acao(
con_id INTEGER NOT NULL, --PK,FK
bo_ticker TEXT NOT NULL, --PK,FK
bo_bolsa TEXT NOT NULL, --PK,FK
ac_qtd INTEGER,
CONSTRAINT fk_Acao_con_id FOREIGN KEY(con_id)
REFERENCES Contrato(con_id) ON DELETE CASCADE,
CONSTRAINT fk_Acao_Bolsa FOREIGN KEY(bo_ticker, bo_bolsa)
REFERENCES Bolsa(bo_ticker, bo_bolsa) ON DELETE CASCADE,
CONSTRAINT pk_Acao PRIMARY KEY(con_id, bo_ticker, bo_bolsa)
);

CREATE TABLE IF NOT EXISTS Venda(
con_id INTEGER NOT NULL, --FK
bo_ticker TEXT NOT NULL, --FK
bo_bolsa TEXT NOT NULL, --FK
ven_id INTEGER CONSTRAINT pk_ven_id PRIMARY KEY AUTOINCREMENT, --PK
ven_qtd INTEGER,
ven_vlr INTEGER, --dividir por 100
ven_data DATE DEFAULT CURRENT_DATE,
CONSTRAINT fk_Venda_Acao FOREIGN KEY(con_id, bo_ticker, bo_bolsa)
REFERENCES Acao(con_id, bo_ticker, bo_bolsa) ON DELETE CASCADE
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
                      AND bo_ticker = NEW.bo_ticker
                )
                + NEW.ven_qtd
            ) >
            (
                SELECT ac_qtd
                FROM Acao
                WHERE con_id = NEW.con_id
                  AND bo_bolsa = NEW.bo_bolsa
                  AND bo_ticker = NEW.bo_ticker
            )
            THEN RAISE(ABORT, 'Quantidade vendida maior que a disponível')
        END;
END;

/* Popular */
--Bolsa
INSERT INTO Bolsa(bo_ticker, bo_bolsa)
VALUES('PETR4', 'B3');
INSERT INTO Bolsa(bo_ticker, bo_bolsa)
VALUES('VALE3', 'B3');
INSERT INTO Bolsa(bo_ticker, bo_bolsa)
VALUES('NVDA', 'NASDAQ');
--Contrato
/*INSERT INTO Contrato(con_mont, con_data, con_dur, con_ind, con_spd)
VALUES (5000000, '2025-01-10', 12, 'CDI', 200);
INSERT INTO Contrato(con_mont, con_data, con_dur, con_ind, con_spd)
VALUES (3000000, '2025-02-15', 6, 'SELIC', 150);
INSERT INTO Contrato(con_mont, con_data, con_dur, con_ind, con_spd)
VALUES (2000000, '2025-02-15', 12, 'SELIC', 150);
--Acao
INSERT INTO Acao(con_id, bo_bolsa, bo_ticker, ac_qtd)
VALUES (1, 'B3', 'PETR4', 300);
INSERT INTO Acao(con_id, bo_bolsa, bo_ticker, ac_qtd)
VALUES (1, 'B3', 'VALE3', 200);
INSERT INTO Acao(con_id, bo_bolsa, bo_ticker, ac_qtd)
VALUES (2, 'NASDAQ', 'NVDA', 50);
--Venda
INSERT INTO Venda(con_id, bo_ticker, bo_bolsa, ven_qtd, ven_vlr, ven_data)
VALUES (1, 'PETR4', 'B3', 100, 320000, '2025-03-10');
INSERT INTO Venda(con_id, bo_ticker, bo_bolsa, ven_qtd, ven_vlr, ven_data)
VALUES (1, 'VALE3', 'B3', 50, 280000, '2025-03-15');
INSERT INTO Venda(con_id, bo_ticker, bo_bolsa, ven_qtd, ven_vlr, ven_data)
VALUES (2, 'NVDA', 'NASDAQ', 10, 150000, '2025-03-20');
-- COMMIT;
 */

/* Display all the records from the table */
-- SELECT * FROM Contrato;
--SELECT * FROM Acao;
--SELECT * FROM Venda;