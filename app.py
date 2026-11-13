"""Painel Econômico Brasil — Streamlit.  Rode o pipeline antes: python -m etl.pipeline"""
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from etl.load import conectar

DB = Path("data/economia.db")
st.set_page_config(page_title="Painel Econômico Brasil", page_icon="📈", layout="wide")
st.title("📈 Painel Econômico Brasil")
st.caption("Fonte: Banco Central do Brasil – SGS (dados abertos). Atualize com `python -m etl.pipeline`.")

if not DB.exists():
    st.warning("Banco não encontrado. Execute `python -m etl.pipeline` para baixar os dados.")
    st.stop()

con = conectar(DB)
ind = pd.read_sql("SELECT * FROM v_indicadores_mensais ORDER BY data", con, parse_dates=["data"])
real = pd.read_sql("SELECT * FROM v_juro_real ORDER BY data", con, parse_dates=["data"])

ini, fim = st.slider("Período", min_value=ind.data.min().to_pydatetime(), max_value=ind.data.max().to_pydatetime(),
                     value=(ind.data.min().to_pydatetime(), ind.data.max().to_pydatetime()), format="MM/YYYY")
ind = ind[(ind.data >= ini) & (ind.data <= fim)]
real = real[(real.data >= ini) & (real.data <= fim)]

ult = real.dropna().iloc[-1] if not real.empty else None
c1, c2, c3, c4 = st.columns(4)
if ult is not None:
    c1.metric("Selic meta", f"{ult.selic_meta:.2f}% a.a.")
    c2.metric("IPCA 12 meses", f"{ult.ipca_12m:.2f}%")
    c3.metric("Juro real (ex-post)", f"{ult.juro_real:.2f}%")
d = ind.dropna(subset=["dolar_medio"])
if not d.empty:
    c4.metric("Dólar PTAX (média do mês)", f"R$ {d.dolar_medio.iloc[-1]:.4f}",
              f"{(d.dolar_medio.iloc[-1] / d.dolar_medio.iloc[-2] - 1) * 100:.2f}% no mês" if len(d) > 1 else None)

st.subheader("Selic × inflação × juro real")
st.plotly_chart(px.line(real, x="data", y=["selic_meta", "ipca_12m", "juro_real"],
                        labels={"value": "% ", "data": "", "variable": "Indicador"}), width="stretch")
a, b = st.columns(2)
a.subheader("Dólar PTAX (média mensal)")
a.plotly_chart(px.line(ind, x="data", y="dolar_medio", labels={"dolar_medio": "R$", "data": ""}), width="stretch")
b.subheader("Atividade econômica (IBC-Br)")
b.plotly_chart(px.line(ind, x="data", y="ibc_br", labels={"ibc_br": "índice", "data": ""}), width="stretch")

with st.expander("Ver dados e SQL"):
    st.dataframe(real.sort_values("data", ascending=False), width="stretch")
    st.code(Path("sql/views.sql").read_text(encoding="utf-8"), language="sql")
    st.download_button("Baixar CSV", real.to_csv(index=False).encode("utf-8"), "juro_real.csv", "text/csv")
