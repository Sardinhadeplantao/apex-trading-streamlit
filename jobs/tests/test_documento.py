from stratum.domain.documento import hash_documento, limpar_texto, url_canonica


def test_url_canonica_tira_rastreio_ancora_e_normaliza():
    assert url_canonica("HTTP://Exemplo.ORG/a/b/?utm_source=rss&id=7&fbclid=x#topo") == "https://exemplo.org/a/b?id=7"


def test_url_canonica_ordena_parametros():
    assert url_canonica("https://x.org/p?b=2&a=1") == url_canonica("https://x.org/p?a=1&b=2")


def test_url_canonica_mantem_parametro_que_muda_conteudo():
    assert url_canonica("https://x.org/p?id=1") != url_canonica("https://x.org/p?id=2")


def test_hash_estavel_e_independe_do_rastreio():
    a = hash_documento("https://x.org/n?utm_medium=feed", "f", "T")
    b = hash_documento("https://x.org/n", "f", "Outro título")  # a URL manda, não o título
    assert a == b and len(a) == 64


def test_hash_sem_url_usa_fonte_e_titulo():
    assert hash_documento(None, "f", " Título  <b>X</b> ") == hash_documento(None, "f", "título x")
    assert hash_documento(None, "f", "T") != hash_documento(None, "g", "T")


def test_limpar_texto_remove_html_e_corta_sem_quebrar_palavra():
    assert limpar_texto("<p>Olá &amp;   mundo</p>") == "Olá & mundo"
    assert limpar_texto("um dois três quatro", 9) == "um dois…"
    assert limpar_texto(None) == ""
