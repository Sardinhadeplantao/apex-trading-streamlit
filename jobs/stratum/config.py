"""Configuração lida do ambiente. Nenhuma chave fica no código, em log ou em arquivo do repositório."""
import os
from dataclasses import dataclass

USER_AGENT_PADRAO = "stratum-global/0.1 (+https://github.com/Sardinhadeplantao/stratum-global)"


@dataclass(frozen=True)
class Config:
    database_url: str | None      # Supabase em produção. Sem ela, o robô usa um banco temporário
    telegram_token: str | None
    telegram_chat: str | None
    user_agent: str

    @property
    def banco_permanente(self) -> bool:
        return self.database_url is not None

    @property
    def telegram_configurado(self) -> bool:
        return bool(self.telegram_token and self.telegram_chat)


def _env(nome: str) -> str | None:
    return (os.environ.get(nome) or "").strip() or None


def ler() -> Config:
    return Config(
        database_url=_env("DATABASE_URL"),
        telegram_token=_env("TELEGRAM_BOT_TOKEN"),
        telegram_chat=_env("TELEGRAM_CHAT_ID"),
        user_agent=_env("STRATUM_USER_AGENT") or USER_AGENT_PADRAO,
    )
