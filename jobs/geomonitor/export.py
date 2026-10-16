"""Gera o status.json que o site mostra. O site não calcula nada: só lê este arquivo."""
import json
import os
from datetime import timedelta

from sqlalchemy import func, select

from geomonitor import VERSAO, db

VERSAO_FORMATO = 1
ULTIMOS_DOCUMENTOS = 40
RODADAS_RECENTES = 24


def _iso(d):
    return d.isoformat(timespec="seconds") + "Z" if d else None


def montar(engine, agora=db.agora) -> dict:
    limite_24h = agora() - timedelta(hours=24)
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
        nomes = {f["id"]: f["nome"] for f in fontes}
        docs = c.execute(select(db.documento).order_by(db.documento.c.conhecido_em.desc(), db.documento.c.id.desc())
                         .limit(ULTIMOS_DOCUMENTOS)).mappings().all()

    lista_fontes = []
    for f in fontes:
        col = coletas.get(f["id"])
        lista_fontes.append({
            "id": f["id"], "nome": f["nome"], "tipo": f["tipo"], "pais": f["pais"], "idioma": f["idioma"],
            "url": f["url"], "criterio": f["criterio"], "ativa": f["ativa"],
            "ultima_coleta": None if col is None else {
                "em": _iso(col["iniciada_em"]), "situacao": col["situacao"], "itens_lidos": col["itens_lidos"],
                "itens_novos": col["itens_novos"], "erro": col["erro"]},
            "documentos": total_por_fonte.get(f["id"], 0),
            "documentos_24h": dia_por_fonte.get(f["id"], 0),
        })

    return {
        "versao_formato": VERSAO_FORMATO,
        "versao_robo": VERSAO,
        "gerado_em": _iso(agora()),
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
        "ultimos_documentos": [{
            "titulo": d["titulo"], "url": d["url"], "fonte": d["fonte_id"], "fonte_nome": nomes.get(d["fonte_id"], d["fonte_id"]),
            "publicado_em": _iso(d["publicado_em"]), "conhecido_em": _iso(d["conhecido_em"])} for d in docs],
    }


def _gravar_json(caminho: str, dados: dict) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(caminho)), exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as fh:
        json.dump(dados, fh, ensure_ascii=False, indent=1)


def escrever(engine, caminho: str) -> None:
    _gravar_json(caminho, montar(engine))
    print(f"Status gravado em {caminho}")


def escrever_falha_banco(caminho: str, tipo_erro: str) -> None:
    """Quando o banco não abre, o site ainda é publicado e diz isso."""
    _gravar_json(caminho, {
        "versao_formato": VERSAO_FORMATO, "versao_robo": VERSAO, "gerado_em": _iso(db.agora()), "banco": "erro",
        "erro_banco": f"Não foi possível abrir o banco ({tipo_erro}).", "ultima_rodada": None, "rodadas_recentes": [],
        "totais": {"documentos": 0, "documentos_24h": 0, "fontes": 0, "fontes_ok": 0}, "fontes": [], "ultimos_documentos": [],
    })
