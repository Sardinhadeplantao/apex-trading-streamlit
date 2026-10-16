from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext

from stratum import db, fontes


def test_migracoes_batem_com_o_esquema(engine):
    with engine.connect() as c:
        diferencas = compare_metadata(MigrationContext.configure(c), db.md)
    assert diferencas == []


def test_preparar_de_novo_nao_muda_nada(engine):
    db.preparar(engine)  # o robô faz isso a cada rodada


def test_conectar_converte_url_do_supabase():
    e = db.conectar("postgresql://u:senha@host:5432/postgres")
    assert e.url.drivername == "postgresql+psycopg"


def test_toda_fonte_tem_criterio_e_ids_unicos():
    ids = [f["id"] for f in fontes.FONTES]
    assert len(ids) == len(set(ids))
    for f in fontes.FONTES:
        assert f["criterio"] and f["tipo"] in {"oficial", "imprensa", "dados", "social"} and f["conector"] == "rss"
        assert f["url"].startswith("https://")
