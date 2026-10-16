"""Avisos pelo Telegram. Sem token configurado, nada é enviado e nada quebra.

Teste manual:  python -m stratum.avisos teste
"""
import sys

import requests

from stratum import config

API = "https://api.telegram.org/bot{token}/sendMessage"


def enviar(texto: str, cfg: config.Config | None = None, session=None) -> bool:
    """Envia uma mensagem. Devolve False se o Telegram não está configurado ou recusou."""
    cfg = cfg or config.ler()
    if not cfg.telegram_configurado:
        return False
    s = session or requests
    try:
        r = s.post(API.format(token=cfg.telegram_token), timeout=15,
                   json={"chat_id": cfg.telegram_chat, "text": texto, "disable_web_page_preview": True})
    except requests.RequestException as exc:  # a mensagem de erro do requests pode conter a URL com o token
        print(f"Telegram: falha de rede ({type(exc).__name__})")
        return False
    if r.status_code != 200:
        print(f"Telegram: recusado (HTTP {r.status_code})")
        return False
    return True


if __name__ == "__main__":
    if sys.argv[1:] == ["teste"]:
        cfg = config.ler()
        if not cfg.telegram_configurado:
            print("Telegram não configurado: faltam TELEGRAM_BOT_TOKEN e/ou TELEGRAM_CHAT_ID nos Secrets.")
            sys.exit(1)
        ok = enviar("Stratum Global: o robô está conectado ao seu Telegram.", cfg)
        print("Mensagem de teste enviada." if ok else "Não foi possível enviar a mensagem de teste.")
        sys.exit(0 if ok else 1)
    print("Uso: python -m stratum.avisos teste")
    sys.exit(2)
