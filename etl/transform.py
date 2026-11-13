"""Limpeza e padronização: datas dd/mm/aaaa -> ISO, vírgula/ponto, duplicatas e agregação mensal."""
from __future__ import annotations

import pandas as pd


def para_dataframe(registros: list[dict], serie: str) -> pd.DataFrame:
    df = pd.DataFrame(registros, columns=["data", "valor"])
    df["data"] = pd.to_datetime(df["data"], format="%d/%m/%Y", errors="coerce")
    df["valor"] = pd.to_numeric(df["valor"].astype(str).str.replace(",", ".", regex=False), errors="coerce")
    df = df.dropna().drop_duplicates(subset="data", keep="last").sort_values("data")
    df.insert(0, "serie", serie)
    return df.reset_index(drop=True)


def mensal(df: pd.DataFrame, como: str = "mean") -> pd.DataFrame:
    """Converte série diária em mensal (média ou último valor do mês)."""
    if df.empty:
        return df
    serie = df["serie"].iloc[0]
    g = df.set_index("data")["valor"].resample("MS")
    out = (g.mean() if como == "mean" else g.last()).dropna().reset_index()
    out.insert(0, "serie", serie)
    return out
