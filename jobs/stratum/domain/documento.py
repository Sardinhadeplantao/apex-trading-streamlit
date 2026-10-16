"""Identidade de um documento: a mesma notícia lida duas vezes precisa gerar o mesmo hash."""
import hashlib
import html
import re
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

# Parâmetros que só servem para rastrear cliques: não mudam o conteúdo da página
_RASTREIO = re.compile(r"^(utm_.*|fbclid|gclid|dclid|msclkid|mc_cid|mc_eid|ocid|cmpid|at_.*|ns_.*|xtor|smid)$", re.I)
_TAG = re.compile(r"<[^>]+>")
_ESPACOS = re.compile(r"\s+")

TAMANHO_RESUMO = 600  # guardamos só um trecho; o texto inteiro fica na fonte


def url_canonica(url: str) -> str:
    """Normaliza a URL: esquema e domínio em minúsculas, sem âncora, sem parâmetros de rastreio, parâmetros em ordem."""
    partes = urlsplit(url.strip())
    esquema = (partes.scheme or "https").lower()
    if esquema == "http":
        esquema = "https"
    dominio = partes.netloc.lower()
    if dominio.endswith(":443") or dominio.endswith(":80"):
        dominio = dominio.rsplit(":", 1)[0]
    caminho = partes.path or "/"
    if len(caminho) > 1 and caminho.endswith("/"):
        caminho = caminho[:-1]
    params = sorted((k, v) for k, v in parse_qsl(partes.query, keep_blank_values=True) if not _RASTREIO.match(k))
    return urlunsplit((esquema, dominio, caminho, urlencode(params), ""))


def hash_documento(url: str | None, fonte_id: str, titulo: str) -> str:
    """Pela URL canônica quando existe; sem URL, pela fonte e pelo título."""
    base = url_canonica(url) if url else f"{fonte_id}|{limpar_texto(titulo).lower()}"
    return hashlib.sha256(base.encode("utf-8")).hexdigest()


def limpar_texto(texto: str | None, limite: int | None = None) -> str:
    """Remove HTML, desfaz entidades (&amp;) e junta espaços. Corta no limite sem quebrar palavra."""
    if not texto:
        return ""
    limpo = _ESPACOS.sub(" ", html.unescape(_TAG.sub(" ", texto))).strip()
    if limite and len(limpo) > limite:
        limpo = limpo[:limite].rsplit(" ", 1)[0].rstrip(",.;:") + "…"
    return limpo
