# 0002. Nome Stratum Global, página inicial e citações de países

Data: 2026-10-16

## Contexto

O dono definiu o nome do site, **Stratum Global**, e que o painel APEX deixa de existir. Mandou um esboço da página
inicial (globo no centro, menu e camadas à esquerda, últimas atualizações à direita, indicadores e cartões embaixo),
"meramente ilustrativo, não necessariamente com os mesmos dados". O esboço mostra números que o sistema ainda não mede
(conflitos ativos, rotas em risco, teses).

## Decisão

- **Nome**: tudo vira Stratum Global (pacote Python `stratum`, textos, mensagens). A pasta `apex-antigo/` foi apagada;
  continua no histórico do git. O repositório será renomeado `stratum-global` pelo dono; o endereço do site acompanha.
- **Página inicial**: segue a estrutura do esboço, mas só com o que é medido. O que ainda não existe aparece em cinza,
  com a fase em que entra (camadas, seções, indicador de mercados, cartão de próximas camadas).
- **Citações de países (regra `paises-0.1`)**: para o globo ter cor medida desde já, o robô conta quantas notícias
  publicadas nas últimas 24 horas citam cada país. Dicionário, sem IA: nomes em inglês e português, gentílicos em
  inglês, capitais, siglas aceitas e metonímias do Estado (Kremlin, Casa Branca). Termos ambíguos são ignorados
  (Georgia, Jordan, Congo, Korea...). Território dependente não toma o gentílico do país soberano.
  Termos vêm de mledoze/countries (licença ODbL), com as escolhas manuais em `jobs/scripts/preparar_nomes_paises.py`.
- **Cores**: o robô publica o nível de cada país (limites 1, 3, 10 e 30 notícias); o site só pinta.
- **Mapa**: Natural Earth 1:50m (240 países, inclui Singapura, Bahrein, Malta), ~440 KB comprimido.
- **Destaque**: o país mais citado, por regra, nunca por escolha.

## Consequências

- Citação mede atenção, não importância. A tela Método diz isso e mostra a regra, as faixas e os termos ignorados.
- Gentílicos em português ("russo", "chinês") ainda não contam: textos em português só casam pelo nome do país.
  Entra quando a fase 1 trouxer o reconhecimento de nomes com modelo (GLiNER).
- Fora da main, o robô imprime no log do GitHub cada notícia com os países encontrados, para conferir a regra com dados reais.
- Sem o Supabase, a janela de 24 horas usa só as notícias que os feeds trazem na rodada (o banco temporário não guarda histórico).
