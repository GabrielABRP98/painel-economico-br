"""Extração da API pública do SGS/BCB (sem autenticação).
Documentação: https://dadosabertos.bcb.gov.br — endpoint bcdata.sgs.{codigo}/dados.
Séries diárias aceitam no máximo 10 anos por consulta, por isso a janela é fatiada."""
from __future__ import annotations

import time
from datetime import date

import requests

BASE = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados"


def janelas(inicio: date, fim: date, anos: int = 9):
    atual = inicio
    while atual <= fim:
        prox = date(min(atual.year + anos, 9999), atual.month, 1)
        yield atual, min(prox, fim)
        atual = date(prox.year, prox.month, prox.day)
        if prox >= fim:
            break


def baixar_serie(codigo: int, inicio: date, fim: date, sessao=None, tentativas: int = 3) -> list[dict]:
    s = sessao or requests.Session()
    registros: list[dict] = []
    for ini, fi in janelas(inicio, fim):
        params = {"formato": "json", "dataInicial": ini.strftime("%d/%m/%Y"), "dataFinal": fi.strftime("%d/%m/%Y")}
        for n in range(1, tentativas + 1):
            try:
                r = s.get(BASE.format(codigo=codigo), params=params, timeout=30)
                r.raise_for_status()
                registros.extend(r.json())
                break
            except requests.RequestException:
                if n == tentativas:
                    raise
                time.sleep(2 ** n)
    return registros
