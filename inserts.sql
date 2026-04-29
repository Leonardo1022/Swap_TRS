--Indexador
INSERT INTO Indexador VALUES('SELIC', '', 0.15);
INSERT INTO Indexador VALUES('SOFR', '', 0.0367);
INSERT INTO Indexador VALUES('TONAR', '', 0.00728);
--Bolsa
INSERT INTO Bolsa VALUES('B3', 'BRL', '.SA');
INSERT INTO Bolsa VALUES('NASDAQ', 'USD', '');
INSERT INTO Bolsa VALUES('NYSE', 'USD', '');
INSERT INTO Bolsa VALUES('TSE', 'JPY', '.T');
--Ticker
----B3
INSERT INTO Ticker VALUES('B3', 'PETR4');
INSERT INTO Ticker VALUES('B3', 'ITUB4');
INSERT INTO Ticker VALUES('B3', 'VALE3');
INSERT INTO Ticker VALUES('B3', 'BPAC11');
INSERT INTO Ticker VALUES('B3', 'WEGE3');
----NASDAQ
INSERT INTO Ticker VALUES('NASDAQ', 'AAPL');
INSERT INTO Ticker VALUES('NASDAQ', 'MSFT');
INSERT INTO Ticker VALUES('NASDAQ', 'NVDA');
INSERT INTO Ticker VALUES('NASDAQ', 'AMZN');
INSERT INTO Ticker VALUES('NASDAQ', 'GOOG');
----NYSE
INSERT INTO Ticker VALUES('NYSE', 'BRK-B');
INSERT INTO Ticker VALUES('NYSE', 'V');
INSERT INTO Ticker VALUES('NYSE', 'JPM');
INSERT INTO Ticker VALUES('NYSE', 'WMT');
INSERT INTO Ticker VALUES('NYSE', 'JNJ');
----TSE
INSERT INTO Ticker VALUES('TSE', '7203');
INSERT INTO Ticker VALUES('TSE', '8306');
INSERT INTO Ticker VALUES('TSE', '6758');
INSERT INTO Ticker VALUES('TSE', '6501');
INSERT INTO Ticker VALUES('TSE', '7974');
--Contrato
INSERT INTO Contrato(CON_MONT, con_duracao, con_indexador, con_spread) VALUES(500.00, 3, 'SELIC', 2);
INSERT INTO Contrato(con_mont, con_abertura, con_duracao, con_indexador, con_spread) VALUES(800.00, '2025-01-01', 6, 'TORIC', 0);
INSERT INTO Contrato(con_mont, con_abertura, con_duracao, con_indexador, con_spread) VALUES(1000.00, '2025-12-01', 12, 'SELIC', 1);
--Acao
INSERT INTO Acao VALUES(1, 'B3', 'PETR4', 12, 500.00);
INSERT INTO Acao VALUES(2, 'NYSE', 'JNJ', 20, 800.00);
INSERT INTO Acao VALUES(3, 'TSE', '7203', 10, 500.00);
INSERT INTO Acao VALUES(3, 'TSE', '8306', 10, 500.00);

INSERT INTO Indexador(ind_indexador, ind_data, ind_valor)
    VALUES ('SELIC', '01-01-2025', 9.1);

SELECT con_mont * ((1 + (
                     SELECT ind_valor FROM Indexador
                         WHERE ind_indexador = con_indexador
                           AND STRFTIME('%Y',ind_data) = '2026'
                           AND STRFTIME('%m',ind_data) = '02'
                 )) * (POWER(1 + con_spread, (1.0/12))))
                            AS custo_mensal FROM Contrato WHERE con_id = 2;

SELECT coalesce(SUM(v.ven_valor), 0.00) AS lucro_mensal FROM Venda v
                JOIN AcaoVenda av
                    ON v.ven_id = av.ven_id
                JOIN Acao a
                    ON av.ac_id = a.ac_id
                WHERE STRFTIME('%Y', v.ven_data) = '2026'
                  AND STRFTIME('%m', v.ven_data) = '03'
                  AND a.con_id = 3;

SELECT COALESCE(SUM(ven_valor), 0.00) AS total
                   FROM Venda;

ALTER TABLE Acao ADD COLUMN ac_preco REAL;

UPDATE Resultado SET re_montante = 200 WHERE con_id = 11 AND re_data > '2026-02-01';

UPDATE Resultado
    SET re_custo = (
        SELECT con_mont * (
            (
                1 + COALESCE((
                    SELECT ind_valor
                    FROM Indexador
                    WHERE ind_indexador = Contrato.con_indexador
                      AND STRFTIME('%Y', ind_data) = STRFTIME('%Y', re_data)
                      AND STRFTIME('%m', ind_data) = STRFTIME('%m', re_data)
                ), 0)
            ) * EXP(LOG(1 + Contrato.con_spread) / 12) - 1
        )
        FROM Contrato
        WHERE Contrato.con_id = Resultado.con_id
    )
    WHERE con_id = 11 AND re_data > '2026-02-01';