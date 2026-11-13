"""Executa extração -> transformação -> carga.  Uso: python -m etl.pipeline [--desde 2015-01-01] [--db data/economia.db]"""
from __future__ import annotations

import argparse
import logging
from datetime import date

from .extract import baixar_serie
from .load import conectar, criar_views, gravar
from .series import SERIES
from .transform import mensal, para_dataframe

log = logging.getLogger("pipeline")


def executar(db: str, desde: date, ate: date | None = None) -> dict[str, int]:
    ate = ate or date.today()
    con = conectar(db)
    resumo = {}
    for chave, meta in SERIES.items():
        bruto = baixar_serie(meta["codigo"], desde, ate)
        df = para_dataframe(bruto, chave)
        gravar(con, df, "observacoes")
        if meta["frequencia"] == "diaria":
            gravar(con, mensal(df, "last" if chave == "selic_meta" else "mean"), "mensal")
        else:
            gravar(con, df, "mensal")
        resumo[chave] = len(df)
        log.info("%s: %d observações", chave, len(df))
    criar_views(con)
    con.close()
    return resumo


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default="data/economia.db")
    ap.add_argument("--desde", default="2015-01-01")
    a = ap.parse_args()
    print(executar(a.db, date.fromisoformat(a.desde)))
