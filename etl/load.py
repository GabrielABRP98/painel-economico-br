"""Carga idempotente em SQLite (reexecutar o pipeline não duplica linhas)."""
from __future__ import annotations

import math
import sqlite3
from pathlib import Path

import pandas as pd

SQL_DIR = Path(__file__).resolve().parent.parent / "sql"


def conectar(caminho: str | Path) -> sqlite3.Connection:
    con = sqlite3.connect(caminho)
    # Garante LN/EXP mesmo em builds do SQLite sem funções matemáticas (comum no Windows).
    con.create_function("LN", 1, lambda x: math.log(x) if x and x > 0 else None, deterministic=True)
    con.create_function("EXP", 1, lambda x: math.exp(x) if x is not None else None, deterministic=True)
    con.executescript((SQL_DIR / "schema.sql").read_text(encoding="utf-8"))
    return con


def gravar(con: sqlite3.Connection, df: pd.DataFrame, tabela: str = "observacoes") -> int:
    linhas = [(r.serie, r.data.strftime("%Y-%m-%d"), float(r.valor)) for r in df.itertuples()]
    con.executemany(
        f"INSERT INTO {tabela}(serie, data, valor) VALUES (?, ?, ?) "
        "ON CONFLICT(serie, data) DO UPDATE SET valor = excluded.valor",
        linhas,
    )
    con.commit()
    return len(linhas)


def criar_views(con: sqlite3.Connection) -> None:
    con.executescript((SQL_DIR / "views.sql").read_text(encoding="utf-8"))
