"""Conectores: um por tipo de fonte. Cada um devolve itens; quem grava é o robô."""
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Item:
    url: str | None
    titulo: str
    resumo: str
    publicado_em: datetime | None  # UTC, sem fuso
