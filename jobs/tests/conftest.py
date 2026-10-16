from datetime import datetime, timedelta
from pathlib import Path

import pytest

from geomonitor import config, db

FIXTURES = Path(__file__).parent / "fixtures"


class Resposta:
    def __init__(self, conteudo: bytes, status: int = 200):
        self.content, self.status_code = conteudo, status


class SessaoFalsa:
    """Responde a cada URL com um arquivo de exemplo; URL desconhecida dá erro de rede."""

    def __init__(self, respostas: dict[str, bytes | int]):
        self.respostas, self.chamadas = respostas, []

    def get(self, url, headers=None, timeout=None):
        self.chamadas.append(url)
        r = self.respostas.get(url)
        if r is None:
            raise ConnectionError(f"sem rede para {url}")
        return Resposta(b"", r) if isinstance(r, int) else Resposta(r)


class Relogio:
    """Relógio controlado pelo teste: cada chamada avança um segundo."""

    def __init__(self, inicio=datetime(2026, 10, 16, 12, 0, 0)):
        self.t = inicio

    def __call__(self):
        self.t += timedelta(seconds=1)
        return self.t


@pytest.fixture
def feed_rss() -> bytes:
    return (FIXTURES / "feed_rss.xml").read_bytes()


@pytest.fixture
def feed_atom() -> bytes:
    return (FIXTURES / "feed_atom.xml").read_bytes()


@pytest.fixture
def engine(tmp_path):
    e = db.conectar(f"sqlite:///{tmp_path / 'teste.db'}")
    db.preparar(e)
    return e


@pytest.fixture
def cfg() -> config.Config:
    return config.Config(database_url=None, telegram_token=None, telegram_chat=None, user_agent="teste")


def fonte(id_: str, url: str, **extra) -> dict:
    return dict(id=id_, nome=id_, tipo="imprensa", pais="BRA", idioma="pt", conector="rss", url=url, criterio="teste") | extra
