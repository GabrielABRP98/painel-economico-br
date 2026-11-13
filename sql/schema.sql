CREATE TABLE IF NOT EXISTS observacoes (
    serie TEXT NOT NULL,
    data  TEXT NOT NULL,          -- ISO 8601 (AAAA-MM-DD)
    valor REAL NOT NULL,
    PRIMARY KEY (serie, data)
);
CREATE TABLE IF NOT EXISTS mensal (
    serie TEXT NOT NULL,
    data  TEXT NOT NULL,          -- primeiro dia do mês
    valor REAL NOT NULL,
    PRIMARY KEY (serie, data)
);
