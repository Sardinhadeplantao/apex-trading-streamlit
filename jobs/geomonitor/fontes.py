"""Lista de fontes lidas pelo robô. É a única lista; o banco recebe uma cópia a cada rodada.

Regra de entrada: toda fonte tem `criterio` (por que está aqui). Nada entra por parecer interessante.
Fase 0: lista inicial para provar o caminho. Os endereços são conferidos na primeira rodada
(a tela Método mostra quais funcionaram). A lista completa, com o controle de cada veículo
(privado, público ou estatal) documentado com fonte, entra na fase 1.
"""

_FR = "https://www.federalregister.gov/api/v1/documents.rss?order=newest&conditions%5Bagencies%5D%5B%5D="
_CRITERIO_IMPRENSA = "Veículo com feed público, publicando do próprio país; a lista cobre blocos diferentes para comparar versões."

FONTES: list[dict] = [
    # Oficiais
    dict(id="onu_noticias", nome="ONU News", tipo="oficial", pais=None, idioma="en", conector="rss",
         url="https://news.un.org/feed/subscribe/en/news/all/rss.xml",
         criterio="Serviço oficial de notícias das Nações Unidas (Conselho de Segurança, Assembleia, agências)."),
    dict(id="fr_bis", nome="Federal Register: controles de exportação (BIS, EUA)", tipo="oficial", pais="USA", idioma="en",
         conector="rss", url=_FR + "industry-and-security-bureau",
         criterio="Diário oficial dos EUA; atos do órgão que controla exportações (Entity List, chips, tecnologia)."),
    dict(id="fr_ofac", nome="Federal Register: sanções (OFAC, EUA)", tipo="oficial", pais="USA", idioma="en",
         conector="rss", url=_FR + "foreign-assets-control-office",
         criterio="Diário oficial dos EUA; atos do órgão de sanções do Tesouro."),
    # Imprensa, um veículo por bloco
    dict(id="bbc_mundo", nome="BBC News: World", tipo="imprensa", pais="GBR", idioma="en", conector="rss",
         url="https://feeds.bbci.co.uk/news/world/rss.xml", criterio=_CRITERIO_IMPRENSA),
    dict(id="dw_mundo", nome="Deutsche Welle: World", tipo="imprensa", pais="DEU", idioma="en", conector="rss",
         url="https://rss.dw.com/rdf/rss-en-world", criterio=_CRITERIO_IMPRENSA),
    dict(id="france24", nome="France 24", tipo="imprensa", pais="FRA", idioma="en", conector="rss",
         url="https://www.france24.com/en/rss", criterio=_CRITERIO_IMPRENSA),
    dict(id="aljazeera", nome="Al Jazeera English", tipo="imprensa", pais="QAT", idioma="en", conector="rss",
         url="https://www.aljazeera.com/xml/rss/all.xml", criterio=_CRITERIO_IMPRENSA),
    dict(id="tass", nome="TASS", tipo="imprensa", pais="RUS", idioma="en", conector="rss",
         url="https://tass.com/rss/v2.xml", criterio=_CRITERIO_IMPRENSA),
    dict(id="cgtn_mundo", nome="CGTN: World", tipo="imprensa", pais="CHN", idioma="en", conector="rss",
         url="https://www.cgtn.com/subscribe/rss/section/world.xml", criterio=_CRITERIO_IMPRENSA),
    dict(id="the_hindu", nome="The Hindu: International", tipo="imprensa", pais="IND", idioma="en", conector="rss",
         url="https://www.thehindu.com/news/international/feeder/default.rss", criterio=_CRITERIO_IMPRENSA),
    dict(id="folha_mundo", nome="Folha de S.Paulo: Mundo", tipo="imprensa", pais="BRA", idioma="pt", conector="rss",
         url="https://feeds.folha.uol.com.br/mundo/rss091.xml", criterio=_CRITERIO_IMPRENSA),
]


def ativas(fontes: list[dict] = FONTES) -> list[dict]:
    return [f for f in fontes if f.get("ativa", True)]
