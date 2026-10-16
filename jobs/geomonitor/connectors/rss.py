"""Lê feeds RSS e Atom."""
import calendar
from datetime import datetime, timezone

import feedparser
import requests

from geomonitor.connectors import Item
from geomonitor.domain.documento import TAMANHO_RESUMO, limpar_texto

TEMPO_LIMITE = 20  # segundos


def _data(entrada) -> datetime | None:
    for campo in ("published_parsed", "updated_parsed", "created_parsed"):
        t = entrada.get(campo)
        if t:
            return datetime.fromtimestamp(calendar.timegm(t), timezone.utc).replace(tzinfo=None)
    return None


def interpretar(conteudo: bytes) -> list[Item]:
    """Transforma o conteúdo do feed em itens. Feed ilegível e vazio é erro; item sem título é ignorado."""
    feed = feedparser.parse(conteudo)
    if not feed.entries and (feed.bozo or not feed.version):  # página comum (HTML de erro, aviso) não é feed vazio
        motivo = type(feed.bozo_exception).__name__ if feed.bozo else "não é RSS nem Atom"
        raise ValueError(f"feed ilegível: {motivo}")
    itens = []
    for e in feed.entries:
        titulo = limpar_texto(e.get("title"))
        if not titulo:
            continue
        resumo = limpar_texto(e.get("summary") or e.get("description"), TAMANHO_RESUMO)
        itens.append(Item(url=_link_seguro(e.get("link")), titulo=titulo, resumo=resumo, publicado_em=_data(e)))
    return itens


def _link_seguro(link: str | None) -> str | None:
    """Só endereços web: um feed não pode pôr javascript: ou data: num link do site."""
    link = (link or "").strip()
    return link if link.lower().startswith(("https://", "http://")) else None


def ler(fonte: dict, session, user_agent: str) -> list[Item]:
    r = session.get(fonte["url"], headers={"User-Agent": user_agent, "Accept": "application/rss+xml, application/atom+xml, application/xml;q=0.9, */*;q=0.5"},
                    timeout=TEMPO_LIMITE)
    if r.status_code >= 400:
        raise RuntimeError(f"HTTP {r.status_code}")
    return interpretar(r.content)


def nova_sessao() -> requests.Session:
    return requests.Session()
