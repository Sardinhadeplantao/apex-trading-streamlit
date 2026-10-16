"""Gera o status.json que o site mostra. O site não calcula nada: só lê este arquivo."""
import json
import os
from datetime import timedelta

from sqlalchemy import func, select

from stratum import VERSAO, db
from stratum.domain import paises

VERSAO_FORMATO = 2
ULTIMOS_DOCUMENTOS = 40
RODADAS_RECENTES = 24

# Citações de países: quantas notícias publicadas na janela citam cada país (regra em domain/paises.py)
JANELA_HORAS = 24
TOLERANCIA_FUTURO = timedelta(hours=1)  # feeds com relógio adiantado; além disso a data é ignorada
NIVEIS = (1, 3, 10, 30)                  # 1-2 citações = nível 1; 3-9 = 2; 10-29 = 3; 30 ou mais = 4
DOCUMENTOS_POR_PAIS = 5
MAIS_CITADOS = 8


def _iso(d):
    return d.isoformat(timespec="seconds") + "Z" if d else None


def nivel(citacoes: int) -> int:
    return sum(1 for limite in NIVEIS if citacoes >= limite)


def montar(engine, agora=db.agora) -> dict:
    momento = agora()
    limite_24h = momento - timedelta(hours=24)
    inicio_janela = momento - timedelta(hours=JANELA_HORAS)
    quando = func.coalesce(db.documento.c.publicado_em, db.documento.c.conhecido_em)  # sem data da fonte, vale a da coleta
    with engine.connect() as c:
        ultima = c.execute(select(db.rodada).order_by(db.rodada.c.id.desc()).limit(1)).mappings().first()
        recentes = c.execute(select(db.rodada.c.iniciada_em, db.rodada.c.situacao)
                             .order_by(db.rodada.c.id.desc()).limit(RODADAS_RECENTES)).mappings().all()

        ultima_coleta_id = (select(db.coleta.c.fonte_id, func.max(db.coleta.c.id).label("id"))
                            .group_by(db.coleta.c.fonte_id).subquery())
        coletas = {r["fonte_id"]: r for r in c.execute(
            select(db.coleta).join(ultima_coleta_id, db.coleta.c.id == ultima_coleta_id.c.id)).mappings()}
        total_por_fonte = dict(c.execute(select(db.documento.c.fonte_id, func.count())
                                         .group_by(db.documento.c.fonte_id)).all())
        dia_por_fonte = dict(c.execute(select(db.documento.c.fonte_id, func.count())
                                       .where(db.documento.c.conhecido_em >= limite_24h)
                                       .group_by(db.documento.c.fonte_id)).all())
        fontes = c.execute(select(db.fonte).order_by(db.fonte.c.tipo, db.fonte.c.nome)).mappings().all()
        janela = c.execute(select(db.documento, quando.label("quando"))
                           .where(quando >= inicio_janela, quando <= momento + TOLERANCIA_FUTURO)
                           .order_by(quando.desc(), db.documento.c.id.desc())).mappings().all()
        if len(janela) < ULTIMOS_DOCUMENTOS:  # janela curta (fontes paradas): mostra os mais recentes mesmo assim
            ultimos = c.execute(select(db.documento, quando.label("quando"))
                                .where(quando <= momento + TOLERANCIA_FUTURO)
                                .order_by(quando.desc(), db.documento.c.id.desc()).limit(ULTIMOS_DOCUMENTOS)).mappings().all()
        else:
            ultimos = janela[:ULTIMOS_DOCUMENTOS]

    dicionario = paises.carregar()
    por_fonte = {f["id"]: f for f in fontes}

    def citados(d) -> list[str]:
        return sorted(paises.citados(f"{d['titulo']}\n{d['resumo'] or ''}", dicionario))

    def resumo_documento(d) -> dict:
        f = por_fonte.get(d["fonte_id"]) or {}
        return {
            "titulo": d["titulo"], "url": d["url"], "fonte": d["fonte_id"], "fonte_nome": f.get("nome", d["fonte_id"]),
            "fonte_tipo": f.get("tipo"), "fonte_pais": f.get("pais"), "fonte_pais_nome": dicionario.nome(f.get("pais")),
            "publicado_em": _iso(d["publicado_em"]), "conhecido_em": _iso(d["conhecido_em"]),
            "paises": [{"iso": iso, "nome": dicionario.nome(iso) or iso} for iso in citados(d)],
        }

    contagem: dict[str, int] = {}
    documentos_do_pais: dict[str, list] = {}
    origem: dict[str | None, int] = {}
    com_pais = oficiais = 0
    for d in janela:  # do mais recente para o mais antigo
        isos = citados(d)
        com_pais += bool(isos)
        f = por_fonte.get(d["fonte_id"]) or {}
        oficiais += f.get("tipo") == "oficial"
        origem[f.get("pais")] = origem.get(f.get("pais"), 0) + 1
        for iso in isos:
            contagem[iso] = contagem.get(iso, 0) + 1
            lista = documentos_do_pais.setdefault(iso, [])
            if len(lista) < DOCUMENTOS_POR_PAIS:
                lista.append(resumo_documento(d))
    maximo = max(contagem.values(), default=0)
    ranking = sorted(contagem.items(), key=lambda kv: (-kv[1], dicionario.nome(kv[0]) or kv[0]))

    lista_fontes = []
    for f in fontes:
        col = coletas.get(f["id"])
        lista_fontes.append({
            "id": f["id"], "nome": f["nome"], "tipo": f["tipo"], "pais": f["pais"], "pais_nome": dicionario.nome(f["pais"]),
            "idioma": f["idioma"], "url": f["url"], "criterio": f["criterio"], "ativa": f["ativa"],
            "ultima_coleta": None if col is None else {
                "em": _iso(col["iniciada_em"]), "situacao": col["situacao"], "itens_lidos": col["itens_lidos"],
                "itens_novos": col["itens_novos"], "erro": col["erro"]},
            "documentos": total_por_fonte.get(f["id"], 0),
            "documentos_24h": dia_por_fonte.get(f["id"], 0),
        })

    return {
        "versao_formato": VERSAO_FORMATO,
        "versao_robo": VERSAO,
        "gerado_em": _iso(momento),
        "banco": ultima["banco"] if ultima else None,
        "erro_banco": None,
        "ultima_rodada": None if ultima is None else {
            "id": ultima["id"], "iniciada_em": _iso(ultima["iniciada_em"]), "terminada_em": _iso(ultima["terminada_em"]),
            "situacao": ultima["situacao"]},
        "rodadas_recentes": [{"iniciada_em": _iso(r["iniciada_em"]), "situacao": r["situacao"]} for r in recentes],
        "totais": {
            "documentos": sum(total_por_fonte.values()),
            "documentos_24h": sum(dia_por_fonte.values()),
            "fontes": len([f for f in fontes if f["ativa"]]),
            "fontes_ok": len([f for f in lista_fontes if f["ativa"] and f["ultima_coleta"] and f["ultima_coleta"]["situacao"] == "ok"]),
        },
        "fontes": lista_fontes,
        "ultimos_documentos": [resumo_documento(d) for d in ultimos],
        "atencao": {
            "regra": dicionario.versao,
            "janela_horas": JANELA_HORAS,
            "inicio": _iso(inicio_janela),
            "fim": _iso(momento),
            "niveis": list(NIVEIS),
            "documentos": len(janela),
            "documentos_com_pais": com_pais,
            "oficiais": oficiais,
            "paises_citados": len(contagem),
            "ignorados": list(dicionario.ignorados),
        },
        "paises": {iso: {"nome": dicionario.nome(iso) or iso, "citacoes": n, "nivel": nivel(n),
                         "documentos": documentos_do_pais[iso]} for iso, n in ranking},
        "mais_citados": [{"iso": iso, "nome": dicionario.nome(iso) or iso, "citacoes": n,
                          "proporcao": round(n / maximo, 4)} for iso, n in ranking[:MAIS_CITADOS]],
        "origem_fontes": [{"pais": p, "nome": dicionario.nome(p) or "Internacional", "documentos": n}
                          for p, n in sorted(origem.items(), key=lambda kv: (-kv[1], kv[0] or ""))],
    }


def _gravar_json(caminho: str, dados: dict) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(caminho)), exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as fh:
        json.dump(dados, fh, ensure_ascii=False, indent=1)


def diagnostico(engine, agora=db.agora) -> list[str]:
    """Uma linha por notícia da janela com os países encontrados, para conferir a regra com manchetes reais."""
    momento = agora()
    quando = func.coalesce(db.documento.c.publicado_em, db.documento.c.conhecido_em)
    with engine.connect() as c:
        docs = c.execute(select(db.documento.c.fonte_id, db.documento.c.titulo, db.documento.c.resumo)
                         .where(quando >= momento - timedelta(hours=JANELA_HORAS), quando <= momento + TOLERANCIA_FUTURO)
                         .order_by(db.documento.c.fonte_id, db.documento.c.id)).all()
    dicionario = paises.carregar()
    linhas = []
    for fonte_id, titulo, resumo in docs:
        texto = f"{titulo}\n{resumo or ''}"
        termos = sorted({m.group(0) for m in dicionario.padrao.finditer(texto)})
        isos = sorted(paises.citados(texto, dicionario))
        linhas.append(f"[{','.join(isos) or '-'}] ({'; '.join(termos)}) {fonte_id}: {titulo} || {(resumo or '')[:160]}")
    return linhas


def escrever(engine, caminho: str) -> None:
    dados = montar(engine)
    _gravar_json(caminho, dados)
    if os.environ.get("STRATUM_DIAGNOSTICO"):
        print("::group::Diagnóstico da regra de países (uma linha por notícia)")
        print("\n".join(diagnostico(engine)))
        print("::endgroup::")
    a = dados["atencao"]
    destaque = ", ".join(f"{p['iso']} {p['citacoes']}" for p in dados["mais_citados"][:5]) or "nenhum"
    print(f"Citações ({a['regra']}): {a['documentos']} notícias em {a['janela_horas']}h, "
          f"{a['documentos_com_pais']} citam algum país, {a['paises_citados']} países. Mais citados: {destaque}.")
    print(f"Status gravado em {caminho}")


def escrever_falha_banco(caminho: str, tipo_erro: str) -> None:
    """Quando o banco não abre, o site ainda é publicado e diz isso."""
    _gravar_json(caminho, {
        "versao_formato": VERSAO_FORMATO, "versao_robo": VERSAO, "gerado_em": _iso(db.agora()), "banco": "erro",
        "erro_banco": f"Não foi possível abrir o banco ({tipo_erro}).", "ultima_rodada": None, "rodadas_recentes": [],
        "totais": {"documentos": 0, "documentos_24h": 0, "fontes": 0, "fontes_ok": 0}, "fontes": [], "ultimos_documentos": [],
        "atencao": None, "paises": {}, "mais_citados": [], "origem_fontes": [],
    })
