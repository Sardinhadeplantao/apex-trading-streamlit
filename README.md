# Geomonitor

Monitor de geopolítica e mercados globais: o que está acontecendo no mundo, com fonte e grau de confirmação,
ligado ao que se mede nos mercados.

**Site:** https://sardinhadeplantao.github.io/apex-trading-streamlit/

O painel antigo de trading (APEX, em Streamlit) foi guardado em `apex-antigo/`.

## Como funciona

```
A cada 15 min                          Toda manhã (fase 3)
Robô (GitHub Actions)                  Redator (tarefa agendada do Claude)
  lê as fontes → grava o que é novo      lê os eventos do dia
  → banco (Supabase)                     → escreve o briefing com links
  → atualiza o site → avisa no Telegram
                  ↓
        Site com o globo (GitHub Pages)
```

Custo: zero, dentro dos planos gratuitos do GitHub, Supabase e Telegram.

## Onde está cada coisa

- `jobs/`: robô em Python (coleta, banco, status). Testes em `jobs/tests`.
- `web/`: site (Next.js estático + MapLibre).
- `docs/plano.md`: as fases e o que conta como pronto.
- `docs/configurar.md`: passo a passo para ligar banco, Telegram e site.
- `docs/decisoes/`: decisões de projeto, com data e motivo.
- `CLAUDE.md`: regras que toda sessão de IA segue ao mexer no projeto.

*Informação de contexto baseada em fontes públicas. Não é recomendação de investimento.*
