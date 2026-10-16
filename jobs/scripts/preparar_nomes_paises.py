"""Gera jobs/stratum/dados/nomes_paises.json: os termos que identificam cada país num texto.

Uso (de dentro de jobs/):
    curl -sSLo /tmp/countries.json https://raw.githubusercontent.com/mledoze/countries/master/countries.json
    python scripts/preparar_nomes_paises.py /tmp/countries.json ../web/public/geo/paises.geojson stratum/dados/nomes_paises.json

Fontes: mledoze/countries (licença ODbL: nomes em inglês e português, siglas, gentílicos, capitais) e o mapa do
Natural Earth (para usar os mesmos códigos do globo). As escolhas manuais ficam aqui, cada uma com o motivo.
Mudou alguma lista? Suba VERSAO: a contagem de citações publica a versão da regra que a produziu.
"""
import json
import re
import sys

VERSAO = "paises-0.2"
LICENCA = ("Open Database License (ODbL) 1.0, https://opendatacommons.org/licenses/odbl/1.0/. "
           "Derivado de https://github.com/mledoze/countries (ODbL) e do Natural Earth (domínio público).")

# O mapa usa o código do Natural Earth onde o ISO não existe. Territórios que o mapa desenha dentro de outro país
# contam para esse país (Réunion e Guiana Francesa fazem parte da França; Svalbard, da Noruega)
CODIGO_NO_MAPA = {"UNK": "KOS", "GUF": "FRA", "GLP": "FRA", "MTQ": "FRA", "MYT": "FRA", "REU": "FRA", "SJM": "NOR",
                  "BVT": "NOR", "CCK": "AUS", "CXR": "AUS", "BES": "NLD", "TKL": "NZL", "UMI": "USA", "GIB": "GBR"}

# Siglas aceitas. Outras siglas de duas letras (IN, TO, ME...) dariam falso positivo em qualquer texto
SIGLAS = {"US": "USA", "U.S.": "USA", "USA": "USA", "U.S.A.": "USA", "EUA": "USA", "UK": "GBR", "U.K.": "GBR",
          "UAE": "ARE", "EAU": "ARE", "DRC": "COD", "DPRK": "PRK", "PRC": "CHN", "ROK": "KOR"}

# Estados dos EUA: notícia sobre o Oregon é notícia dos EUA. Fora: Georgia e Washington (ambíguos)
ESTADOS_USA = [
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware", "Florida", "Hawaii",
    "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts",
    "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey",
    "New Mexico", "New Mexican", "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon",
    "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont", "Virginia",
    "West Virginia", "Wisconsin", "Wyoming", "Califórnia", "Flórida", "Havaí", "Nova York", "Nova Jersey", "Novo México",
    "Carolina do Norte", "Carolina do Sul", "Pensilvânia", "Luisiana",
]

# Gentílicos em português dos países mais presentes no noticiário. Em minúsculas, como se escreve no meio da frase;
# no começo da frase, o plural ("Russos atacam"); o singular com maiúscula só entra quando é forma própria ("Francês")
_GENTILICOS_PT = {
    "RUS": "russo", "USA": "norte-americano americano", "CHN": "chinês", "UKR": "ucraniano", "ISR": "israelense",
    "IRN": "iraniano", "YEM": "iemenita", "BRA": "brasileiro", "ARG": "argentino", "IND": "indiano", "PSE": "palestino",
    "FRA": "francês", "DEU": "alemão", "GBR": "britânico", "JPN": "japonês", "VEN": "venezuelano", "MEX": "mexicano",
    "TUR": "turco", "SAU": "saudita", "SYR": "sírio", "LBN": "libanês", "EGY": "egípcio", "KOR": "sul-coreano",
    "PRK": "norte-coreano", "TWN": "taiwanês", "IRQ": "iraquiano", "AFG": "afegão", "PAK": "paquistanês",
    "CUB": "cubano", "COL": "colombiano", "CHL": "chileno", "QAT": "catariano", "POL": "polonês", "ITA": "italiano",
    "ESP": "espanhol", "CAN": "canadense",
}


def _flexoes(masculino: str) -> list[str]:
    """russo -> russo, russa, russos, russas; chinês -> chinês, chinesa, chineses, chinesas; alemão -> alemã, alemães."""
    if masculino.endswith("ês"):
        raiz = masculino[:-2]
        return [masculino, raiz + "esa", raiz + "eses", raiz + "esas"]
    if masculino.endswith("ão"):
        raiz = masculino[:-2]
        return [masculino, raiz + "ã", raiz + ("ães" if masculino == "alemão" else "ãos"), raiz + "ãs"]
    if masculino.endswith("o"):
        raiz = masculino[:-1]
        return [masculino, raiz + "a", raiz + "os", raiz + "as"]
    if masculino.endswith(("e", "a")):  # israelense, iemenita, saudita, canadense
        return [masculino, masculino + "s"]
    if masculino.endswith("ol"):  # espanhol
        return [masculino, masculino + "a", masculino[:-2] + "óis", masculino + "as"]
    return [masculino]


def _gentilicos_pt(texto: str) -> list[str]:
    formas = [f for m in texto.split() for f in _flexoes(m)]
    plurais = [f for f in formas if f.endswith("s") and f[0].islower()]
    return formas + [p[0].upper() + p[1:] for p in plurais if p != "americanas"]  # Americanas: a rede de lojas


# Nomes de uso comum que a base não traz: metonímias do Estado, grafias e capitais do Brasil, estados e cidades
# que só existem em um país. Escolha manual: vence a base e os conflitos
EXTRAS = {
    "GBR": ["Britain", "Great Britain", "England", "Scotland", "Wales", "Northern Ireland", "Northern Irish", "Scottish",
            "Welsh", "Downing Street", "Grã-Bretanha", "Inglaterra", "Escócia", "País de Gales", "Londres", "Irlanda do Norte"],
    "USA": ["White House", "Pentagon", "Capitol Hill", "Casa Branca", "Pentágono", "Washington, D.C.", "Washington DC",
            "Washington D.C.", "Los Angeles", "Chicago", "Boston", "San Francisco", "Houston", "New England",
            "Indian-American", "Indian-Americans", "Indian American", "Indian Americans", *ESTADOS_USA, "Alasca", "Jersey City"],
    "RUS": ["Kremlin", "Kremlim", "Moscou", "Kaliningrad", "Kaliningrado"],
    "PSE": ["Gaza", "West Bank", "Palestinian", "Palestinians", "Palestine", "Faixa de Gaza", "Cisjordânia", "Ramallah"],
    "TUR": ["Turkey", "Türkiye", "Turquia", "Istanbul", "Istambul", "Ancara"],
    "CZE": ["Czech Republic", "Czechia", "Tchéquia", "República Tcheca", "Praga"],
    "CIV": ["Ivory Coast", "Côte d'Ivoire", "Costa do Marfim"],
    "MMR": ["Burma", "Mianmar"],
    "TLS": ["East Timor"],
    "IDN": ["West Timor", "Jacarta"],
    "SWZ": ["Swaziland"],
    "COD": ["DR Congo", "Democratic Republic of Congo", "Democratic Republic of the Congo", "Congo-Kinshasa", "Kinshasa", "RDC"],
    "COG": ["Republic of the Congo", "Congo-Brazzaville", "Brazzaville"],
    "PRK": ["North Korea", "North Korean", "North Koreans", "Pyongyang", "Coreia do Norte"],
    "KOR": ["South Korea", "South Korean", "South Koreans", "Seoul", "Coreia do Sul", "Seul"],
    "UKR": ["Kyiv", "Kiev", "Ucrânia", "Kharkiv", "Kharkov", "Carcóvia", "Odesa"],
    "TWN": ["Taipei", "Taipé"],
    "VAT": ["Vatican", "Holy See", "Vaticano"],
    "SAU": ["Saudi", "Saudis", "Riyadh", "Riad"],
    "ARE": ["Emirati", "Emiratis", "Abu Dabi"],
    "NLD": ["Holanda"],
    "CHN": ["Beijing", "Pequim", "Shanghai", "Xangai", "Hainan"],
    "IRN": ["Tehran", "Teerã", "Irã"],
    "ISR": ["Israelis", "Tel Aviv"],
    "YEM": ["Iêmen", "Aden", "Áden", "Sanaa", "Sana'a"],
    "KEN": ["Quênia"],
    "VNM": ["Vietnã"],
    "POL": ["Polônia", "Varsóvia"],
    "SVN": ["Eslovênia"],
    "ARM": ["Armênia"],
    "MCO": ["Mônaco"],
    "SGP": ["Cingapura"],
    "EST": ["Estônia"],
    "LVA": ["Letônia"],
    "MKD": ["Macedônia do Norte", "North Macedonia"],
    "GRL": ["Groenlândia", "Nuuk"],
    "TJK": ["Tadjiquistão"],
    "ROU": ["Romênia", "Bucareste"],
    "DEU": ["Berlim"],
    "ESP": ["Madri"],
    "PRT": ["Lisboa"],
    "JPN": ["Tóquio"],
    "SYR": ["Damasco"],
    "IRQ": ["Bagdá"],
    "LBN": ["Beirute"],
    "GRC": ["Atenas"],
    "AUT": ["Viena"],
    "HUN": ["Budapeste"],
    "BGR": ["Sófia"],
    "SRB": ["Belgrado"],
    "MDA": ["Chisinau", "Chişinău"],
    "AFG": ["Cabul"],
    "IND": ["Delhi", "Nova Délhi"],
    "CHE": ["Zurich", "Zurique"],
    "NGA": ["Niger Delta", "Benin City"],
    "MEX": ["Baja California", "Baixa Califórnia"],
    "NOR": ["Svalbard"],
    "ITA": ["em Roma"],  # "Roma" sozinho em inglês é o povo roma
    "VIR": ["U.S. Virgin Islands", "US Virgin Islands"],
    "CYN": ["Northern Cyprus", "Turkish Cypriot"],
    "SOL": ["Somaliland", "Hargeisa"],
    "KOS": ["Kosovo", "Pristina"],
}
for _iso, _masc in _GENTILICOS_PT.items():
    EXTRAS.setdefault(_iso, []).extend(_gentilicos_pt(_masc))

# Termos ignorados porque apontam para mais de um lugar ou pessoa
AMBIGUOS = {
    "Georgia", "Georgian", "Georgians", "Geórgia",  # também estado dos EUA
    "Jordan",                                  # também nome de pessoa
    "Congo", "Congolese",                      # dois países
    "Korea", "Korean", "Koreans", "Coreia",    # duas Coreias
    "Dominican", "Dominicans",                 # República Dominicana e Dominica
    "Washington",                              # estado dos EUA, pessoas, jornal
    "Brussels", "Bruxelas",                    # sede da União Europeia: quase sempre quer dizer a UE, não a Bélgica
    "Victoria", "Kingston", "Georgetown", "Hamilton", "San José", "Male", "Malé",  # capitais com nome muito comum
    "Lima", "Santiago", "Sofia", "Sucre", "Praia", "Nassau", "Tripoli", "Trípoli",  # nomes de pessoa ou de outros lugares
    "Granada", "Guadalupe", "Reunion", "Reunião", "Mann", "Thais", "Diego Garcia", "Maurício",
    "Jerusalem", "Jerusalém",                  # disputada
    "Macedonia", "Macedonian",                 # também região da Grécia
    "English", "inglês",                       # idioma
    "Guinean", "Guineans",                     # quatro países com "Guinea" no nome
}

# Expressões que contêm nome de país mas não se referem a ele. Aceitam plural e gênero ("South Americans", "latino-americanas")
SEM_PAIS = [
    "Indian Ocean", "Latin America", "South America", "North America", "Central America", "American Indian",
    "Pan-American", "Pan American", "Inter-American", "Organization of American States", "New Guinea", "New South Wales",
    "Moscow time", "Beijing time", "Palestine Action", "France 24", "FRANCE 24", "New York Times", "Real Madrid",
    "Atlético Madrid", "Atletico Madrid", "Paris Saint-Germain", "Shanghai Cooperation", "Russian roulette",
    "Oceano Índico", "América Latina", "América do Sul", "América do Norte", "América Central", "latino-american",
    "Latino-american", "sul-american", "Sul-american", "centro-american", "Centro-american", "montanha-russa",
    "montanhas-russas", "roleta-russa", "roleta russa", "futebol americano", "café americano",
    # mares, golfos, acordos e nomes próprios com país dentro
    "Sea of Japan", "Mar do Japão", "Gulf of Guinea", "Golfo da Guiné", "Gulf of California", "Golfo da Califórnia",
    "South China Sea", "East China Sea", "Mar do Sul da China", "Mar da China Oriental", "Paris Agreement",
    "Acordo de Paris", "Rome Statute", "Estatuto de Roma", "Oslo Accords", "Acordos de Oslo", "Colorado Party",
    "Partido Colorado", "France-Presse", "France Presse", "Ibero-American", "ibero-american", "Hispano-American",
    "hispano-american", "pan-american", "Latin-American", "Anglo American", "Nova Guiné", "Cooperação de Xangai",
    "horário de Moscou", "Atlético de Madrid",
]

_SO_LATIM = re.compile(r"^[A-Za-zÀ-ÖØ-öø-ÿĀ-ž'’.\- ]+$")


def _plural(gentilico: str) -> list[str]:
    if gentilico.endswith(("s", "sh", "ch", "ese", "x")):
        return [gentilico]
    return [gentilico, gentilico + "s"]


def _termos_da_base(c: dict) -> set[str]:
    termos = {c["name"]["common"], c["name"]["official"]}
    por = c.get("translations", {}).get("por", {})
    termos |= {por.get("common"), por.get("official")}
    for alt in c.get("altSpellings", []):
        if len(alt) > 3 and "," not in alt and _SO_LATIM.match(alt):
            termos.add(alt)
    for g in (c.get("demonyms", {}).get("eng", {}) or {}).values():
        if g:
            termos.update(_plural(g))
    if c.get("independent"):  # capital de território dependente costuma ser nome comum (Stanley, Douglas, Plymouth)
        termos.update(c.get("capital", []))
    return {t.strip() for t in termos if t and t.strip()}


def preparar(base: list[dict], mapa: dict) -> dict:
    # Nome exibido: o do mapa, para o globo e as listas dizerem o mesmo (já corrigido para o Brasil em preparar_paises.py)
    nomes = {p["iso"]: {"nome": p["nome"], "nome_en": p["nome_en"]}
             for p in sorted((f["properties"] for f in mapa["features"]), key=lambda p: p["iso"])}
    termos: dict[str, str | None] = {}
    de_soberano: dict[str, bool] = {}
    conflitos = []

    def adicionar(termo: str, iso: str, soberano: bool):
        if termo in AMBIGUOS or not _SO_LATIM.match(termo):
            return
        if termo not in termos:
            termos[termo], de_soberano[termo] = iso, soberano
        elif termos[termo] != iso and not (de_soberano[termo] and not soberano):
            conflitos.append(termo)  # dois donos do mesmo nível: ambíguo, sai da lista
        # território dependente não toma o termo do país soberano ("French", "Dutch", "American")

    soberanos = [c for c in base if c.get("independent")]
    dependentes = [c for c in base if not c.get("independent")]
    for grupo, soberano in ((soberanos, True), (dependentes, False)):
        for c in grupo:
            iso = CODIGO_NO_MAPA.get(c["cca3"], c["cca3"])
            for t in _termos_da_base(c):
                adicionar(t, iso, soberano)
    for iso, p in nomes.items():  # os nomes do mapa também contam (Somalilândia, Irã, Quênia)
        for t in (p["nome"], p["nome_en"]):
            if t:
                adicionar(t, iso, soberano=False)
    for conflito in set(conflitos):
        termos.pop(conflito, None)
    for iso, extras in EXTRAS.items():
        for t in extras:
            termos[t] = iso
    for sigla, iso in SIGLAS.items():
        termos[sigla] = iso
    for expressao in SEM_PAIS:
        termos[expressao] = None
    fora_do_mapa = sorted({iso for iso in termos.values() if iso and iso not in nomes})
    if fora_do_mapa:
        raise SystemExit(f"Códigos sem desenho no mapa (inclua em CODIGO_NO_MAPA): {fora_do_mapa}")
    return {
        "versao": VERSAO,
        "licenca": LICENCA,
        "fonte": "mledoze/countries e Natural Earth 1:50m; escolhas manuais em jobs/scripts/preparar_nomes_paises.py",
        "termos": dict(sorted(termos.items())),
        "nomes": nomes,
        "ignorados": sorted(AMBIGUOS | set(conflitos)),
    }


if __name__ == "__main__":
    with open(sys.argv[1], encoding="utf-8") as fh:
        base = json.load(fh)
    with open(sys.argv[2], encoding="utf-8") as fh:
        mapa = json.load(fh)
    resultado = preparar(base, mapa)
    with open(sys.argv[3], "w", encoding="utf-8") as fh:
        json.dump(resultado, fh, ensure_ascii=False, indent=0)
    print(f"{len(resultado['termos'])} termos, {len(resultado['nomes'])} países, {len(resultado['ignorados'])} ignorados")
