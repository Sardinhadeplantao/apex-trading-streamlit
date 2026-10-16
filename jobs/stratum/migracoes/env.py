"""Ambiente do Alembic. O robô passa a conexão pronta (veja db.preparar)."""
from alembic import context

from stratum.db import md

conexao = context.config.attributes.get("connection")
if conexao is None:
    raise SystemExit("Rode as migrações por stratum.db.preparar(engine).")

context.configure(connection=conexao, target_metadata=md, render_as_batch=True)
with context.begin_transaction():
    context.run_migrations()
