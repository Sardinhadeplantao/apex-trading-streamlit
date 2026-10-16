"""Casos de referência da regra de citação de países (paises-0.1). Cada caso é uma armadilha real de manchete."""
import pytest

from stratum.domain.paises import carregar, citados, montar

CASOS = [
    # nomes, gentílicos, possessivo, hífen
    ("Russia's drones hit Ukrainian grid", {"RUS", "UKR"}),
    ("pro-Russian separatists", {"RUS"}),
    ("Ukraine-Russia talks", {"UKR", "RUS"}),
    # siglas aceitas e moeda
    ("US and UK impose new sanctions", {"USA", "GBR"}),
    ("U.S. Treasury targets Iranian oil network", {"USA", "IRN"}),
    ("Petrobras investe US$ 2 bilhões no pré-sal", set()),
    # o termo mais longo vence
    ("Papua New Guinea election", {"PNG"}),
    ("South Sudan ceasefire", {"SSD"}),
    ("Equatorial Guinea and Guinea-Bissau", {"GNQ", "GNB"}),
    ("Nigeria and Niger close border", {"NGA", "NER"}),
    ("Northern Ireland protocol", {"GBR"}),
    ("Dominican Republic", {"DOM"}),
    # expressões que não são o país
    ("Latin American leaders meet", set()),
    ("storm moves across the Indian Ocean", set()),
    ("New Mexico wildfire", set()),
    ("Indian navy deploys ships", {"IND"}),
    # termos ambíguos ignorados
    ("Georgia governor signs bill", set()),
    ("Jordan scores 30 points", set()),
    ("fighting in eastern Congo", set()),
    ("Korean shipbuilders", set()),
    ("North Korean missile launch", {"PRK"}),
    ("DR Congo and M23 rebels", {"COD"}),
    # maiúsculas importam
    ("turkey prices rise before holiday", set()),
    ("Turkey and Türkiye are the same country", {"TUR"}),
    # metonímias do Estado
    ("Kremlin says talks are possible", {"RUS"}),
    ("White House and Beijing trade barbs", {"USA", "CHN"}),
    ("aid trucks enter Gaza", {"PSE"}),
    # português
    ("Rússia ataca a Ucrânia; EUA reagem", {"RUS", "UKR", "USA"}),
    ("Estados Unidos e China retomam negociação", {"USA", "CHN"}),
    # país dependente não toma o gentílico do país soberano
    ("French and Dutch ministers", {"FRA", "NLD"}),
    ("American officials", {"USA"}),
    # nome dentro de outra palavra não conta
    ("Omani", {"OMN"}),
    ("Romanian", {"ROU"}),
]


@pytest.mark.parametrize("texto,esperado", CASOS)
def test_casos_de_referencia(texto, esperado):
    assert citados(texto) == esperado


def test_cada_pais_conta_uma_vez_por_texto():
    assert citados("Russia, Russian forces and Moscow") == {"RUS"}


def test_texto_vazio():
    assert citados(None) == set() and citados("") == set()


def test_dicionario_publica_versao_nomes_e_ignorados():
    d = carregar()
    assert d.versao.startswith("paises-")
    assert d.nome("BRA") == "Brasil" and d.nome("XYZ") is None
    assert "Georgia" in d.ignorados and "Georgia" not in d.termos


def test_montar_dicionario_proprio():
    d = montar("teste", {"Foo": "AAA", "Foo Bar": None}, {"AAA": {"nome": "Foo", "nome_en": "Foo"}})
    assert citados("Foo and Foo Bar", d) == {"AAA"}
