"""Fundação: fontes, rodadas, coletas e documentos.

Revision ID: 0001
Revises:
Create Date: 2026-10-16
"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

Id = sa.BigInteger().with_variant(sa.Integer, "sqlite")


def upgrade() -> None:
    op.create_table(
        "fonte",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("nome", sa.Text, nullable=False),
        sa.Column("tipo", sa.String(16), nullable=False),
        sa.Column("pais", sa.String(3)),
        sa.Column("idioma", sa.String(8)),
        sa.Column("url", sa.Text, nullable=False),
        sa.Column("criterio", sa.Text),
        sa.Column("ativa", sa.Boolean, nullable=False),
    )
    op.create_table(
        "rodada",
        sa.Column("id", Id, primary_key=True, autoincrement=True),
        sa.Column("iniciada_em", sa.DateTime, nullable=False),
        sa.Column("terminada_em", sa.DateTime),
        sa.Column("situacao", sa.String(16), nullable=False),
        sa.Column("banco", sa.String(16), nullable=False),
        sa.Column("versao", sa.String(32), nullable=False),
    )
    op.create_table(
        "coleta",
        sa.Column("id", Id, primary_key=True, autoincrement=True),
        sa.Column("rodada_id", Id, sa.ForeignKey("rodada.id"), nullable=False),
        sa.Column("fonte_id", sa.String(64), sa.ForeignKey("fonte.id"), nullable=False),
        sa.Column("iniciada_em", sa.DateTime, nullable=False),
        sa.Column("terminada_em", sa.DateTime),
        sa.Column("situacao", sa.String(16), nullable=False),
        sa.Column("itens_lidos", sa.Integer, nullable=False),
        sa.Column("itens_novos", sa.Integer, nullable=False),
        sa.Column("erro", sa.Text),
    )
    op.create_index("ix_coleta_fonte", "coleta", ["fonte_id", "iniciada_em"])
    op.create_table(
        "documento",
        sa.Column("id", Id, primary_key=True, autoincrement=True),
        sa.Column("hash", sa.String(64), nullable=False, unique=True),
        sa.Column("fonte_id", sa.String(64), sa.ForeignKey("fonte.id"), nullable=False),
        sa.Column("rodada_id", Id, sa.ForeignKey("rodada.id")),
        sa.Column("url", sa.Text),
        sa.Column("titulo", sa.Text, nullable=False),
        sa.Column("resumo", sa.Text),
        sa.Column("publicado_em", sa.DateTime),
        sa.Column("conhecido_em", sa.DateTime, nullable=False),
    )
    op.create_index("ix_documento_conhecido", "documento", ["conhecido_em"])
    op.create_index("ix_documento_fonte", "documento", ["fonte_id", "conhecido_em"])


def downgrade() -> None:
    raise NotImplementedError("Nada é apagado: corrija com uma migração nova.")
