"""Quais países um texto cita. Regra de dicionário, sem IA: dá para conferir termo a termo.

- Os termos (nomes em inglês e português, gentílicos, capitais, siglas) vêm de dados/nomes_paises.json,
  gerado por scripts/preparar_nomes_paises.py, onde ficam as escolhas manuais e os termos ignorados por ambiguidade.
- Diferencia maiúsculas: "Turkey" é país, "turkey" não. Palavra inteira: "Niger" não casa dentro de "Nigeria".
- O termo mais longo vence: "Papua New Guinea" não conta "Guinea"; "Latin American" não conta os EUA.
- Expressão que não é país aceita plural e gênero: "South Americans" também não conta os EUA
  (só esses finais, para "Moscow timeline" continuar contando a Rússia).
- Apóstrofo tipográfico vale como o reto: "Côte d’Ivoire" = "Côte d'Ivoire".
- Cada texto conta no máximo uma vez para cada país.
"""
import json
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

SUFIXO = r"(?:ns|os|as|n|s|o|a)?"  # finais aceitos depois de uma expressão que não é país
ARQUIVO = Path(__file__).resolve().parent.parent / "dados" / "nomes_paises.json"


@dataclass(frozen=True)
class Dicionario:
    versao: str
    termos: dict[str, str | None]   # termo -> código do país (None = expressão que não é país, ex.: "Indian Ocean")
    nomes: dict[str, dict]          # código -> {"nome": em português, "nome_en": em inglês}
    ignorados: tuple[str, ...]
    padrao: re.Pattern

    def nome(self, iso: str | None) -> str | None:
        return (self.nomes.get(iso) or {}).get("nome") if iso else None


def montar(versao: str, termos: dict, nomes: dict, ignorados=()) -> Dicionario:
    ordenados = sorted(termos, key=len, reverse=True)  # mais longo primeiro: a alternância do regex respeita a ordem
    alternativas = "|".join(re.escape(t) + (SUFIXO if termos[t] is None else "") for t in ordenados)
    # Antes: não pode ser letra/número. Depois: nem letra/número nem "$" (US$ é moeda, não os EUA)
    padrao = re.compile(rf"(?<!\w)(?:{alternativas})(?![\w$])")
    return Dicionario(versao, dict(termos), dict(nomes), tuple(ignorados), padrao)


@lru_cache(maxsize=1)
def carregar() -> Dicionario:
    with open(ARQUIVO, encoding="utf-8") as fh:
        d = json.load(fh)
    return montar(d["versao"], d["termos"], d["nomes"], d["ignorados"])


def encontrados(texto: str | None, dicionario: Dicionario | None = None) -> list[tuple[str, str | None]]:
    """Cada termo achado no texto, com o país (None = expressão que não é país). Serve para conferir a regra."""
    if not texto:
        return []
    d = dicionario or carregar()
    texto = texto.replace("\u2019", "'").replace("\u2018", "'")
    return [(m.group(0), d.termos.get(m.group(0))) for m in d.padrao.finditer(texto)]


def citados(texto: str | None, dicionario: Dicionario | None = None) -> set[str]:
    """Códigos dos países citados no texto."""
    return {iso for _, iso in encontrados(texto, dicionario) if iso}
