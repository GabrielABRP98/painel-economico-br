from datetime import date

import pytest

from etl.extract import janelas
from etl.load import conectar, criar_views, gravar
from etl.transform import mensal, para_dataframe


def test_transform_limpa_datas_valores_e_duplicatas():
    bruto = [{"data": "01/01/2024", "valor": "0,42"}, {"data": "01/02/2024", "valor": "0.83"},
             {"data": "01/02/2024", "valor": "0.80"}, {"data": "xx", "valor": "1"}, {"data": "01/03/2024", "valor": ""}]
    df = para_dataframe(bruto, "ipca_mensal")
    assert list(df.valor) == [0.42, 0.80]
    assert df.data.dt.month.tolist() == [1, 2]


def test_mensal_media_e_ultimo():
    df = para_dataframe([{"data": "02/01/2024", "valor": "5"}, {"data": "31/01/2024", "valor": "7"},
                         {"data": "01/02/2024", "valor": "6"}], "dolar_ptax")
    assert mensal(df, "mean").valor.tolist() == [6.0, 6.0]
    assert mensal(df, "last").valor.tolist() == [7.0, 6.0]


def test_janelas_cobrem_periodo_sem_ultrapassar_10_anos():
    js = list(janelas(date(2000, 1, 1), date(2026, 11, 13)))
    assert js[0][0] == date(2000, 1, 1) and js[-1][1] == date(2026, 11, 13)
    assert all((f - i).days <= 3660 for i, f in js)


def _base(tmp_path):
    con = conectar(tmp_path / "t.db")
    ipca = [{"data": f"01/{m:02d}/2024", "valor": "1"} for m in range(1, 13)]
    selic = [{"data": f"01/{m:02d}/2024", "valor": "10"} for m in range(1, 13)]
    gravar(con, para_dataframe(ipca, "ipca_mensal"), "mensal")
    gravar(con, para_dataframe(selic, "selic_meta"), "mensal")
    criar_views(con)
    return con


def test_carga_idempotente(tmp_path):
    con = _base(tmp_path)
    gravar(con, para_dataframe([{"data": "01/01/2024", "valor": "1"}], "ipca_mensal"), "mensal")
    assert con.execute("SELECT COUNT(*) FROM mensal WHERE serie='ipca_mensal'").fetchone()[0] == 12


def test_ipca_12m_e_juro_real(tmp_path):
    con = _base(tmp_path)
    ipca12 = con.execute("SELECT ipca_12m FROM v_juro_real WHERE data='2024-12-01'").fetchone()[0]
    assert ipca12 == pytest.approx((1.01 ** 12 - 1) * 100, abs=0.01)  # 12,68%
    juro = con.execute("SELECT juro_real FROM v_juro_real WHERE data='2024-12-01'").fetchone()[0]
    assert juro == pytest.approx((1.10 / 1.1268 - 1) * 100, abs=0.02)
    assert con.execute("SELECT COUNT(*) FROM v_juro_real").fetchone()[0] == 1  # só meses com 12 meses de histórico
