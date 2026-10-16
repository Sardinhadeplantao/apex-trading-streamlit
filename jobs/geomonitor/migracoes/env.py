"""Ambiente do Alembic. O robô passa a conexão pronta (veja db.preparar)."""
from alembic import context

from geomonitor.db import md

conexao = context.config.attributes.get("connection")
if conexao is None:
    raise SystemExit("Rode as migrações por geomonitor.db.preparar(engine).")

context.configure(connection=conexao, target_metadata=md, render_as_batch=True)
with context.begin_transaction():
    context.run_migrations()
