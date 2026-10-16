from datetime import datetime

import pytest

from geomonitor.connectors import rss


def test_interpreta_rss(feed_rss):
    itens = rss.interpretar(feed_rss)
    assert [i.titulo for i in itens] == ["Conselho aprova novas sanções & restrições", "Navios desviam rota no estreito",
                                         "Navios desviam rota no estreito"]  # item sem título é ignorado
    primeiro = itens[0]
    assert primeiro.resumo == "O conselho aprovou hoje um pacote de sanções ."
    assert primeiro.publicado_em == datetime(2026, 10, 15, 12, 30)  # convertido para UTC
    assert itens[2].publicado_em is None


def test_interpreta_atom(feed_atom):
    [item] = rss.interpretar(feed_atom)
    assert item.url == "https://oficial.example.gov/comunicados/123"
    assert item.publicado_em == datetime(2026, 10, 15, 12, 0)


def test_conteudo_que_nao_e_feed_da_erro():
    with pytest.raises(ValueError):
        rss.interpretar(b"<html><body>Pagina de erro</body>")
    with pytest.raises(ValueError):
        rss.interpretar(b"<html>erro</html>")  # HTML bem formado também não é feed


def test_link_que_nao_e_web_e_descartado():
    feed = (b'<?xml version="1.0"?><rss version="2.0"><channel><title>x</title>'
            b'<item><title>A</title><link>javascript:alert(1)</link></item>'
            b'<item><title>B</title><link> https://ok.example/b </link></item></channel></rss>')
    a, b = rss.interpretar(feed)
    assert a.url is None and b.url == "https://ok.example/b"


def test_feed_valido_sem_itens_nao_e_erro():
    vazio = b'<?xml version="1.0"?><rss version="2.0"><channel><title>x</title></channel></rss>'
    assert rss.interpretar(vazio) == []
