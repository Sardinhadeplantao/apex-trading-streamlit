"""Robô: uma rodada lê cada fonte, grava só o que é novo e registra tudo. Uma fonte falhar não para as outras.

Uso:  python -m stratum.robo [--exportar CAMINHO/status.json]
"""
import argparse
import sys
from dataclasses import dataclass, field

import requests
from sqlalchemy import select

from stratum import VERSAO, avisos, config, db, export
from stratum import fontes as catalogo
from stratum.connectors import rss
from stratum.domain.documento import hash_documento

CONECTORES = {"rss": rss.ler}


@dataclass
class Resultado:
    rodada_id: int
    situacao: str                       # ok | parcial | falhou
    novos: int = 0
    falhas: list[str] = field(default_factory=list)


def rodar(engine, fontes: list[dict], session, cfg: config.Config, agora=db.agora, conectores=CONECTORES) -> Resultado:
    banco = "permanente" if cfg.banco_permanente else "temporario"
    with engine.begin() as c:
        db.gravar_fontes(c, fontes)
        rid = c.execute(db.rodada.insert().values(iniciada_em=agora(), situacao="rodando", banco=banco, versao=VERSAO)
                        ).inserted_primary_key[0]

    resultado = Resultado(rodada_id=rid, situacao="rodando")
    ativas = catalogo.ativas(fontes)
    for f in ativas:
        inicio = agora()
        try:
            itens = conectores[f["conector"]](f, session, cfg.user_agent)
            novos = _gravar(engine, f["id"], itens, rid, agora())
            linha = dict(situacao="ok", itens_lidos=len(itens), itens_novos=novos, erro=None)
            resultado.novos += novos
        except Exception as exc:  # isola a falha: as outras fontes seguem
            resultado.falhas.append(f["id"])
            linha = dict(situacao="falhou", itens_lidos=0, itens_novos=0, erro=erro_legivel(exc))
        with engine.begin() as c:
            c.execute(db.coleta.insert().values(rodada_id=rid, fonte_id=f["id"], iniciada_em=inicio, terminada_em=agora(), **linha))
        print(f"{f['id']}: {linha['situacao']}, {linha['itens_lidos']} lidos, {linha['itens_novos']} novos"
              + (f" ({linha['erro']})" if linha["erro"] else ""), flush=True)

    if not resultado.falhas:
        resultado.situacao = "ok"
    else:
        resultado.situacao = "falhou" if len(resultado.falhas) == len(ativas) else "parcial"
    with engine.begin() as c:
        c.execute(db.rodada.update().where(db.rodada.c.id == rid).values(terminada_em=agora(), situacao=resultado.situacao))
    return resultado


def erro_legivel(exc: Exception) -> str:
    """Mensagem curta para a tela Método. O nome técnico fica entre parênteses para quem for consertar."""
    nome = type(exc).__name__
    if isinstance(exc, requests.Timeout):
        return f"O site demorou demais para responder ({nome})."
    if isinstance(exc, (requests.ConnectionError, ConnectionError)):
        return f"Não foi possível conectar ao site ({nome})."
    texto = str(exc)
    if texto.startswith("HTTP "):
        return f"O site recusou o pedido ({texto})."
    if isinstance(exc, ValueError) and "feed" in texto:
        return f"O endereço não devolveu um feed válido ({texto})."
    return f"{nome}: {texto[:160]}"


def _gravar(engine, fonte_id: str, itens, rodada_id: int, conhecido_em) -> int:
    """Grava os itens que o banco ainda não tem. Devolve quantos eram novos."""
    por_hash = {}
    for it in itens:
        h = hash_documento(it.url, fonte_id, it.titulo)
        por_hash.setdefault(h, it)  # repetido dentro do mesmo feed: fica o primeiro
    if not por_hash:
        return 0
    with engine.begin() as c:
        existentes = set()
        hashes = list(por_hash)
        for i in range(0, len(hashes), 500):
            existentes |= set(c.execute(select(db.documento.c.hash).where(db.documento.c.hash.in_(hashes[i:i + 500]))).scalars())
        linhas = [dict(hash=h, fonte_id=fonte_id, rodada_id=rodada_id, url=it.url, titulo=it.titulo, resumo=it.resumo or None,
                       publicado_em=it.publicado_em, conhecido_em=conhecido_em)
                  for h, it in por_hash.items() if h not in existentes]
        db.inserir_ignorando_repetidos(c, db.documento, linhas, "hash")
    return len(linhas)


def situacao_anterior(engine, rodada_id: int) -> str | None:
    with engine.connect() as c:
        return c.execute(select(db.rodada.c.situacao).where(db.rodada.c.id < rodada_id)
                         .order_by(db.rodada.c.id.desc()).limit(1)).scalar()


def avisar_mudanca(anterior: str | None, resultado: Resultado, enviar=avisos.enviar) -> bool:
    """Avisa só quando a situação muda (evita uma mensagem a cada 15 minutos)."""
    if resultado.situacao == "falhou" and anterior != "falhou":
        return enviar("Stratum Global: todas as fontes falharam nesta rodada. Veja a tela Método do site.")
    if resultado.situacao != "falhou" and anterior == "falhou":
        return enviar("Stratum Global: a coleta voltou a funcionar.")
    return False


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Uma rodada do robô do Stratum Global.")
    p.add_argument("--exportar", help="grava o status para o site neste caminho (JSON)")
    args = p.parse_args(argv)
    cfg = config.ler()
    print(f"Stratum Global {VERSAO}. Banco: {'permanente' if cfg.banco_permanente else 'temporário (DATABASE_URL não configurado)'}.")

    try:
        engine = db.conectar(cfg.database_url)
        db.preparar(engine)
    except Exception as exc:  # nunca imprime a mensagem crua: ela pode conter dados da conexão
        print(f"Banco indisponível ({type(exc).__name__}). Confira o DATABASE_URL nos Secrets do repositório.")
        if args.exportar:
            export.escrever_falha_banco(args.exportar, type(exc).__name__)
        return 1

    resultado = rodar(engine, catalogo.FONTES, rss.nova_sessao(), cfg)
    print(f"Rodada {resultado.rodada_id}: {resultado.situacao}, {resultado.novos} documentos novos.")
    avisar_mudanca(situacao_anterior(engine, resultado.rodada_id), resultado, lambda t: avisos.enviar(t, cfg))
    if args.exportar:
        export.escrever(engine, args.exportar)
    return 1 if resultado.situacao == "falhou" else 0


if __name__ == "__main__":
    sys.exit(main())
