"""Casos de referência da regra de citação de países (paises-0.2, decisão 0003). Cada caso é uma armadilha real de manchete."""
import json
from pathlib import Path

import pytest

from stratum.domain.paises import ARQUIVO, carregar, citados, encontrados, montar

MAPA = Path(__file__).resolve().parents[2] / "web" / "public" / "geo" / "paises.geojson"

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
    ("South Americans protest", set()),
    ("New Guineans vote", set()),
    ("Inter-American Development Bank approves loan", set()),
    ("until 9:00 Moscow time", set()),
    ("Palestine Action ban", set()),
    ("Real Madrid wins", set()),
    ("A montanha-russa da bolsa", set()),
    ("Indian navy deploys ships", {"IND"}),
    # termos ambíguos ignorados
    ("Georgia governor signs bill", set()),
    ("Jordan scores 30 points", set()),
    ("fighting in eastern Congo", set()),
    ("Korean shipbuilders", set()),
    ("EU leaders meet in Brussels", set()),
    ("ICC judges in The Hague", set()),
    ("a atriz Sofia Vergara", set()),
    ("Ministro Ricardo Lima diz que", set()),
    ("Santiago Bernabéu stadium", set()),
    ("Clashes in Tripoli", set()),
    ("North Korean missile launch", {"PRK"}),
    ("DR Congo and M23 rebels", {"COD"}),
    # maiúsculas importam
    ("turkey prices rise before holiday", set()),
    ("Turkey and Türkiye are the same country", {"TUR"}),
    # capital de território dependente não conta (nome comum)
    ("Morgan Stanley cuts forecast", set()),
    ("Michael Douglas to receive award", set()),
    ("Storm hits Plymouth", set()),
    # estados e cidades que só existem em um país
    ("Shooting at elementary school in Oregon", {"USA"}),
    ("New Mexico wildfire", {"USA"}),
    ("New Jersey governor signs bill", {"USA"}),
    ("Houthi raid on presidential palace in Aden", {"YEM"}),
    ("Indian-American Congressman from Illinois", {"USA"}),
    ("U.S. Virgin Islands governor", {"VIR"}),  # o território, não as Ilhas Virgens Britânicas
    # território desenhado dentro de outro país conta para esse país
    ("Cyclone hits Réunion", {"FRA"}),
    # metonímias do Estado
    ("Kremlin says talks are possible", {"RUS"}),
    ("White House and Beijing trade barbs", {"USA", "CHN"}),
    ("aid trucks enter Gaza", {"PSE"}),
    # português
    ("Rússia ataca a Ucrânia; EUA reagem", {"RUS", "UKR", "USA"}),
    ("Estados Unidos e China retomam negociação", {"USA", "CHN"}),
    ("Houthis atacam o Iêmen; Moscou reage", {"YEM", "RUS"}),
    ("Zelenski retoma ataque a refinarias russas", {"RUS"}),
    ("o presidente americano Donald Trump", {"USA"}),
    ("Chineses e indianos negociam", {"CHN", "IND"}),
    ("O caso do jornalista brasileiro", {"BRA"}),
    ("dirigentes latino-americanos se reúnem", set()),
    ("Lojas Americanas fecham", set()),
    # apóstrofo tipográfico
    ("Côte d’Ivoire election", {"CIV"}),
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
    assert d.versao == "paises-0.2"
    assert d.nome("BRA") == "Brasil" and d.nome("XYZ") is None
    assert "Georgia" in d.ignorados and "Georgia" not in d.termos


def test_nomes_em_portugues_do_brasil_iguais_aos_do_mapa():
    d = carregar()
    mapa = json.loads(MAPA.read_text(encoding="utf-8"))
    nomes_mapa = {f["properties"]["iso"]: f["properties"]["nome"] for f in mapa["features"]}
    assert {iso: d.nome(iso) for iso in nomes_mapa} == nomes_mapa
    assert [d.nome(i) for i in ("IRN", "YEM", "KEN", "POL", "TWN", "PER", "AZE")] == [
        "Irã", "Iêmen", "Quênia", "Polônia", "Taiwan", "Peru", "Azerbaijão"]


def test_todo_pais_citavel_existe_no_mapa():
    mapa = json.loads(MAPA.read_text(encoding="utf-8"))
    no_mapa = {f["properties"]["iso"] for f in mapa["features"]}
    assert {iso for iso in carregar().termos.values() if iso} <= no_mapa


def test_arquivo_traz_a_licenca_odbl():
    dados = json.loads(ARQUIVO.read_text(encoding="utf-8"))
    assert "ODbL" in dados["licenca"] and "opendatacommons.org" in dados["licenca"]


def test_montar_dicionario_proprio():
    d = montar("teste", {"Foo": "AAA", "Foo Bar": None}, {"AAA": {"nome": "Foo", "nome_en": "Foo"}})
    assert citados("Foo and Foo Bar", d) == {"AAA"}
    assert citados("Foo Bars", d) == set()  # expressão que não é país consome o resto da palavra
    assert encontrados("Foo and Foo Bars", d) == [("Foo", "AAA"), ("Foo Bars", None)]
