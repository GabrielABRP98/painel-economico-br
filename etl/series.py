"""Séries do Sistema Gerenciador de Séries Temporais (SGS) do Banco Central do Brasil."""
SERIES = {
    "ipca_mensal": {"codigo": 433, "nome": "IPCA – variação mensal (%)", "frequencia": "mensal"},
    "selic_meta": {"codigo": 432, "nome": "Meta da taxa Selic (% a.a.)", "frequencia": "diaria"},
    "dolar_ptax": {"codigo": 1, "nome": "Dólar comercial PTAX – venda (R$)", "frequencia": "diaria"},
    "ibc_br": {"codigo": 24363, "nome": "IBC-Br – índice dessazonalizado", "frequencia": "mensal"},
}
