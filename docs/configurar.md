# Configurar (passo a passo, sem programar)

Faça na ordem. Cada passo leva poucos minutos. Senhas e chaves vão **só** nos Secrets do GitHub:
nunca cole em conversa (nem com o Claude), em arquivo ou em print.

## 1. Ligar o site

1. Abra https://github.com/Sardinhadeplantao/apex-trading-streamlit/settings/pages
2. Em **Build and deployment**, no campo **Source**, escolha **GitHub Actions**. (Salva sozinho; não há botão.)

Pronto: em até 15 minutos o robô publica o site em https://sardinhadeplantao.github.io/apex-trading-streamlit/

## 2. Criar o banco (Supabase, gratuito)

1. Entre em https://supabase.com e crie uma conta (dá para usar a do GitHub).
2. **New project**: nome `geomonitor`; crie uma senha forte para o banco e guarde num gerenciador de senhas;
   região: uma do leste dos EUA (fica perto de onde o robô roda); plano **Free**.
3. Com o projeto pronto, clique em **Connect** (no topo da página do projeto).
4. Na lista de tipos de conexão, escolha **Session pooler**. É importante: o GitHub não consegue usar o endereço "Direct connection".
5. Copie o endereço que começa com `postgresql://` e troque `[YOUR-PASSWORD]` pela senha do passo 2.

## 3. Criar o bot do Telegram

1. No Telegram, abra **@BotFather**, envie `/newbot`, escolha um nome e um usuário terminado em `bot`.
   Ele responde com um **token** (uma sequência longa de letras e números).
2. Abra o seu bot novo e mande "oi". Bots só podem escrever para quem falou com eles antes.
3. Abra **@userinfobot** e envie `/start`. Ele responde com o seu **Id** (um número).

## 4. Guardar as chaves no GitHub

No repositório: **Settings → Secrets and variables → Actions → New repository secret**. Crie três:

| Nome | Valor |
|---|---|
| `DATABASE_URL` | o endereço do passo 2, já com a senha |
| `TELEGRAM_BOT_TOKEN` | o token do passo 3.1 |
| `TELEGRAM_CHAT_ID` | o número do passo 3.3 |

## 5. Testar

1. No repositório: **Actions → Robô (coleta e site) → Run workflow**.
2. Marque **Mandar uma mensagem de teste no Telegram** e clique em **Run workflow**.
3. Em uns 5 minutos:
   - chega no Telegram: "Geomonitor: o robô está conectado ao seu Telegram.";
   - a tela **Método** do site mostra "Banco: Permanente" e as fontes que funcionaram.

Se algo não funcionar, a tela Método diz o que falhou. Numa sessão do Claude, peça:
"veja a última execução do robô do geomonitor e me diga o que falhou".
