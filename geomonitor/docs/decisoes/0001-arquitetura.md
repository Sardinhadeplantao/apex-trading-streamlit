# 0001. Arquitetura sem servidor e sem custo

Data: 2026-10-16

## Contexto

Uso pessoal no começo, talvez público depois. O dono não é programador, quer o sistema online
(não no próprio PC) e não quer pagar por tokens de IA. Ele já mantém o Kondratiev Monitor
(repositório Sardinha-De-Plantao) com GitHub Actions + site estático, e esse padrão funciona.

## Decisão

- **Robô:** GitHub Actions a cada 15 minutos, repositório público (minutos ilimitados e gratuitos).
- **Banco:** PostgreSQL no Supabase, plano gratuito (500 MB). Notícias guardam título, link, trecho curto e datas;
  o texto inteiro fica na fonte (espaço e direitos autorais).
- **Site:** Next.js estático + MapLibre (globo) no GitHub Pages. Não calcula nada.
- **Avisos:** bot do Telegram.
- **IA:** nenhuma obrigatória. Bibliotecas gratuitas fazem o trabalho pesado (fase 1).
  Briefing por tarefa agendada do Claude (fase 3); API gratuita (Groq/Gemini) como ajudante opcional.
- **Python** no robô (o dono já usa; NLP e estatística estão em Python); TypeScript só no site.

## Alternativas descartadas

- **LLM local (Ollama):** exige máquina ligada e forte; o dono preferiu não depender disso.
- **Rodar no PC do dono:** o sistema para quando o PC desliga.
- **Servidor próprio (Oracle Free, VPS):** mais manutenção. Fica como saída se o GitHub apertar (~US$ 5/mês, mesmo código).
- **GitHub Models:** desativado pelo GitHub em 30/07/2026.
- **Muse (Meta):** assistente pessoal para tarefas do dia a dia, só nos EUA; não serve de peça de um sistema.
- **API paga de IA:** contraria o custo zero.

## Consequências

- Atualização a cada 15 a 30 minutos, não em tempo real. Suficiente para geopolítica.
- Código e dados (notícias públicas) ficam visíveis no repositório público; chaves ficam nos Secrets.
- 500 MB de banco: detalhe das notícias por ~90 dias, eventos para sempre (a política de retenção entra na fase 1).
- Se uma API gratuita sumir, só a peça dela para: o sistema funciona sem IA.
