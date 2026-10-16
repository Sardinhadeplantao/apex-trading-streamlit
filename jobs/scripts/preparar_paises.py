"""Gera web/public/geo/paises.geojson a partir do Natural Earth 1:50 milhões (domínio público).

Uso (de dentro de jobs/):
    curl -sSLo /tmp/ne.geojson https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_50m_admin_0_countries.geojson
    python scripts/preparar_paises.py /tmp/ne.geojson ../web/public/geo/paises.geojson

Mantém só o que o site usa (códigos oficiais e nomes) e arredonda as coordenadas
para o arquivo ficar leve. Rodar de novo com o mesmo arquivo de entrada gera o mesmo resultado.
A escala 1:50m inclui países pequenos (Singapura, Bahrein, Malta) que a 1:110m não desenha.
"""
import json
import sys

CASAS = 2  # ~1 km: suficiente para a escala 1:110 milhões


def _codigo(p: dict, *campos: str) -> str | None:
    for c in campos:
        v = (p.get(c) or "").strip()
        if v and v != "-99":
            return v
    return None


def _arredondar(coords):
    if isinstance(coords[0], (int, float)):
        return [round(coords[0], CASAS), round(coords[1], CASAS)]
    return [_arredondar(c) for c in coords]


def _poligonos(geometria: dict) -> list:
    return [geometria["coordinates"]] if geometria["type"] == "Polygon" else geometria["coordinates"]


def preparar(entrada: dict) -> dict:
    # Partes do mesmo país (ex.: territórios da Austrália) viram um só país com várias áreas
    grupos: dict[str, list[dict]] = {}
    for f in entrada["features"]:
        iso = _codigo(f["properties"], "ISO_A3_EH", "ISO_A3", "ADM0_A3")  # sem ISO: usa o código do Natural Earth
        grupos.setdefault(iso, []).append(f)
    saida = []
    for iso, partes in grupos.items():
        f = next((x for x in partes if x["properties"].get("ISO_A3") == iso), partes[0])
        p = f["properties"]
        if len(partes) > 1:
            geometria = {"type": "MultiPolygon", "coordinates": [pol for x in partes for pol in _poligonos(x["geometry"])]}
        else:
            geometria = f["geometry"]
        saida.append({
            "type": "Feature",
            "properties": {
                "iso": iso,
                "iso_oficial": _codigo(p, "ISO_A3_EH", "ISO_A3") is not None,
                "iso2": _codigo(p, "ISO_A2_EH", "ISO_A2"),
                "nome": p.get("NAME_PT") or p.get("NAME"),
                "nome_en": p.get("NAME_EN") or p.get("NAME"),
                "wikidata": p.get("WIKIDATAID"),
                "continente": p.get("CONTINENT"),
                "regiao": p.get("SUBREGION"),
            },
            "geometry": {"type": geometria["type"], "coordinates": _arredondar(geometria["coordinates"])},
        })
    saida.sort(key=lambda x: x["properties"]["iso"])
    return {"type": "FeatureCollection", "features": saida}


if __name__ == "__main__":
    origem, destino = sys.argv[1], sys.argv[2]
    with open(origem, encoding="utf-8") as fh:
        resultado = preparar(json.load(fh))
    with open(destino, "w", encoding="utf-8") as fh:
        json.dump(resultado, fh, ensure_ascii=False, separators=(",", ":"))
    print(f"{len(resultado['features'])} países gravados em {destino}")
