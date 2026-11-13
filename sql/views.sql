-- Visão "larga": uma linha por mês com todos os indicadores
DROP VIEW IF EXISTS v_indicadores_mensais;
CREATE VIEW v_indicadores_mensais AS
SELECT data,
       MAX(CASE WHEN serie = 'ipca_mensal' THEN valor END) AS ipca_mensal,
       MAX(CASE WHEN serie = 'selic_meta'  THEN valor END) AS selic_meta,
       MAX(CASE WHEN serie = 'dolar_ptax'  THEN valor END) AS dolar_medio,
       MAX(CASE WHEN serie = 'ibc_br'      THEN valor END) AS ibc_br
FROM mensal
GROUP BY data;

-- IPCA acumulado em 12 meses: produto de (1 + taxa) com função de janela via soma de logaritmos não existe no SQLite,
-- então usamos uma subconsulta correlacionada sobre os 12 meses anteriores.
DROP VIEW IF EXISTS v_ipca_12m;
CREATE VIEW v_ipca_12m AS
SELECT a.data,
       a.ipca_mensal,
       (SELECT COUNT(*) FROM v_indicadores_mensais b
         WHERE b.ipca_mensal IS NOT NULL AND b.data > date(a.data, '-12 months') AND b.data <= a.data) AS meses,
       a.ipca_12m_aprox
FROM (
    SELECT m.data, m.ipca_mensal,
           (SELECT ROUND((EXP(SUM(LN(1 + b.ipca_mensal / 100.0))) - 1) * 100, 2)
              FROM v_indicadores_mensais b
             WHERE b.ipca_mensal IS NOT NULL AND b.data > date(m.data, '-12 months') AND b.data <= m.data) AS ipca_12m_aprox
    FROM v_indicadores_mensais m
    WHERE m.ipca_mensal IS NOT NULL
) a;

-- Juro real ex-post aproximado: ((1 + Selic) / (1 + IPCA 12m) - 1)
DROP VIEW IF EXISTS v_juro_real;
CREATE VIEW v_juro_real AS
SELECT i.data, m.selic_meta, i.ipca_12m_aprox AS ipca_12m,
       ROUND(((1 + m.selic_meta / 100.0) / (1 + i.ipca_12m_aprox / 100.0) - 1) * 100, 2) AS juro_real
FROM v_ipca_12m i
JOIN v_indicadores_mensais m USING (data)
WHERE i.meses = 12 AND m.selic_meta IS NOT NULL;
