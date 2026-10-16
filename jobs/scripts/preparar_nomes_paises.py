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

VERSAO = "paises-0.1"

# O mapa usa o código do Natural Earth onde o ISO não existe
CODIGO_NO_MAPA = {"UNK": "KOS"}

# Siglas aceitas. Outras siglas de duas letras (IN, TO, ME...) dariam falso positivo em qualquer texto
SIGLAS = {"US": "USA", "U.S.": "USA", "USA": "USA", "U.S.A.": "USA", "EUA": "USA", "UK": "GBR", "U.K.": "GBR",
          "UAE": "ARE", "EAU": "ARE", "DRC": "COD", "DPRK": "PRK", "PRC": "CHN", "ROK": "KOR"}

# Nomes de uso comum que a base não traz, ou metonímias diretas do Estado
EXTRAS = {
    "GBR": ["Britain", "Great Britain", "England", "Scotland", "Wales", "Northern Ireland", "Northern Irish", "Scottish",
            "Welsh", "Downing Street", "Grã-Bretanha", "Inglaterra", "Escócia"],
    "USA": ["White House", "Pentagon", "Casa Branca", "Pentágono"],
    "RUS": ["Kremlin", "Kremlim"],
    "PSE": ["Gaza", "West Bank", "Palestinian", "Palestinians", "Palestine", "Faixa de Gaza", "Cisjordânia", "palestinos"],
    "TUR": ["Turkey", "Türkiye", "Turquia"],
    "CZE": ["Czech Republic"],
    "CIV": ["Ivory Coast", "Côte d'Ivoire", "Costa do Marfim"],
    "MMR": ["Burma"],
    "TLS": ["East Timor"],
    "SWZ": ["Swaziland"],
    "COD": ["DR Congo", "Democratic Republic of Congo", "Democratic Republic of the Congo", "Congo-Kinshasa", "Kinshasa"],
    "COG": ["Republic of the Congo", "Congo-Brazzaville", "Brazzaville"],
    "PRK": ["North Korea", "North Korean", "North Koreans", "Pyongyang", "Coreia do Norte"],
    "KOR": ["South Korea", "South Korean", "South Koreans", "Seoul", "Coreia do Sul"],
    "UKR": ["Kyiv", "Kiev", "Kiev", "Ucrânia"],
    "TWN": ["Taipei"],
    "VAT": ["Vatican", "Holy See", "Vaticano"],
    "NGA": ["Niger Delta"],
    "SAU": ["Saudi", "Saudis", "Riyadh"],
    "ARE": ["Emirati", "Emiratis"],
    "NLD": ["The Hague", "Holanda"],
    "CHN": ["Beijing", "Pequim"],
    "IRN": ["Tehran", "Teerã", "Irã"],
    "ISR": ["Israelis"],
    "CYN": ["Northern Cyprus", "Turkish Cypriot"],
    "SOL": ["Somaliland", "Hargeisa"],
    "KOS": ["Kosovo", "Pristina"],
}

# Termos ignorados porque apontam para mais de um lugar ou pessoa
AMBIGUOS = {
    "Georgia", "Georgian", "Georgians",       # também estado dos EUA
    "Jordan",                                  # também nome de pessoa
    "Congo", "Congolese",                      # dois países
    "Korea", "Korean", "Koreans", "Coreia",    # duas Coreias
    "Dominican", "Dominicans",                 # República Dominicana e Dominica
    "Washington",                              # estado dos EUA, pessoas, jornal
    "Victoria", "Kingston", "Georgetown", "Hamilton", "San José", "Male", "Malé",  # capitais com nome muito comum
    "Jerusalem", "Jerusalém",                  # disputada
    "Macedonia", "Macedonian",                 # também região da Grécia
    "English",                                 # idioma
    "Guinean", "Guineans",                     # quatro países com "Guinea" no nome
}

# Expressões que contêm nome de país mas não se referem a ele (consumidas antes, para não contar o país)
SEM_PAIS = ["Indian Ocean", "Latin America", "Latin American", "Latin Americans", "South America", "South American",
            "North America", "North American", "Central America", "Central American", "American Indian",
            "Pan-American", "New Mexico", "New Guinea", "Oceano Índico", "América Latina", "América do Sul",
            "América do Norte", "América Central", "Novo México"]

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
    for capital in c.get("capital", []):
        termos.add(capital)
    return {t.strip() for t in termos if t and t.strip()}


def preparar(base: list[dict], mapa: dict) -> dict:
    nomes_mapa = {f["properties"]["iso"]: f["properties"] for f in mapa["features"]}
    termos: dict[str, str | None] = {}
    nomes: dict[str, dict] = {}
    conflitos = []

    def adicionar(termo: str, iso: str, soberano: bool = True):
        if termo in AMBIGUOS or not _SO_LATIM.match(termo):
            return
        if termo in termos and termos[termo] != iso:
            if soberano:
                conflitos.append(termo)  # o mesmo termo para dois países soberanos: ambíguo, sai da lista
            return  # território dependente não toma o termo do país soberano ("French", "Dutch", "American")
        termos[termo] = iso

    soberanos = [c for c in base if c.get("independent")]
    dependentes = [c for c in base if not c.get("independent")]
    for grupo, soberano in ((soberanos, True), (dependentes, False)):
        for c in grupo:
            iso = CODIGO_NO_MAPA.get(c["cca3"], c["cca3"])
            nomes[iso] = {"nome": (c.get("translations", {}).get("por", {}) or {}).get("common") or c["name"]["common"],
                          "nome_en": c["name"]["common"]}
            for t in _termos_da_base(c):
                adicionar(t, iso, soberano)
    for iso, extras in EXTRAS.items():
        for t in extras:
            adicionar(t, iso)
    for iso, p in nomes_mapa.items():  # países do mapa que a base não tem (ex.: Somalilândia)
        nomes.setdefault(iso, {"nome": p["nome"], "nome_en": p["nome_en"]})
        for t in (p["nome"], p["nome_en"]):
            if t:
                adicionar(t, iso, soberano=False)
    for conflito in set(conflitos):
        termos.pop(conflito, None)
    for sigla, iso in SIGLAS.items():
        termos[sigla] = iso
    for expressao in SEM_PAIS:
        termos[expressao] = None
    return {
        "versao": VERSAO,
        "fonte": "mledoze/countries (ODbL) e Natural Earth 1:50m; escolhas manuais em jobs/scripts/preparar_nomes_paises.py",
        "termos": dict(sorted(termos.items())),
        "nomes": dict(sorted(nomes.items())),
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
