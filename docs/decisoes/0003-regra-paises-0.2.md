# 0003. Regra de citação de países 0.2

Data: 2026-10-16

## Contexto

A revisão da regra `paises-0.1` com 295 manchetes reais (logs do robô de 16/10) mediu:

- 84% das manchetes citam algum país.
- Cerca de 3% das citações estavam erradas. Sete delas eram a Bélgica contada por "Brussels" em notícias da cúpula da UE.
  As outras vinham de "Moscow time", "Palestine Action" e "Indian-American".
- 23 manchetes perdiam um país:
  - 17 falavam de um estado ou cidade dos EUA (o tiroteio no Oregon saiu sem país em 6 fontes).
  - Na Folha, 4 de 20 manchetes perdiam o país por causa do português do Brasil ("Iêmen", "russas", "americano").
- Fora da amostra, a regra também contava nomes de pessoa e de outros lugares:
  - Morgan Stanley contava as Malvinas.
  - New Jersey contava Jersey.
  - Sofia Coppola contava a Bulgária.
  - Lima contava o Peru.
- Os nomes na tela vinham em português de Portugal ("Irão", "Quénia"), e o cartão e o painel do mesmo país traziam nomes diferentes ("Ilha Formosa" e "Taiwan").

## Decisão

A regra passa a `paises-0.2`, com estas mudanças. Os motivos estão no próprio `jobs/scripts/preparar_nomes_paises.py`.

- **Sedes internacionais não contam o país**: "Brussels"/"Bruxelas" (sede da UE) entram nos ignorados, como "Washington".
  "The Hague" sai, porque quase sempre quer dizer os tribunais de Haia.
- **Capital de território dependente não conta**. Elas costumam ser nomes comuns (Stanley, Douglas, Plymouth, Saint-Denis).
- **Mais nomes ambíguos ignorados**: Lima, Santiago, Sofia, Sucre, Praia, Nassau, Trípoli, Granada, Geórgia e outros.
- **Estados dos EUA contam os EUA**. Ficam de fora Georgia e Washington, que são ambíguos.
  Isso muda o caso de referência "New Mexico wildfire", que antes não contava país.
- **Cidades que só existem num país** contam esse país: Los Angeles, Chicago, Áden, Zurique, Kaliningrado, Xangai.
  Miami fica de fora: "Miami-based" aparece em notícias de furacão que não são sobre os EUA.
- **Português do Brasil**: grafias (Iêmen, Quênia, Polônia), capitais (Moscou, Londres, Pequim já existia) e
  gentílicos dos países mais presentes no noticiário ("russo", "americanos", "chinesa").
  Isso antecipa uma parte do que a decisão 0002 deixava para a fase 1.
  Como já acontece com "Russian", o nome do idioma ("em russo") também conta o país.
- **Expressões que não são país** consomem o resto da palavra:
  - "South Americans" e "New Guineans" não contam os EUA nem a Guiné.
  - Também entram expressões novas: "Moscow time", "Palestine Action", "France 24", "Real Madrid", "montanha-russa".
- **Territórios que o mapa desenha dentro de outro país** contam para esse país, porque o globo não consegue pintá-los
  separados: Réunion e Guiana Francesa contam para a França, Svalbard para a Noruega.
- **Um nome por país**: o robô usa o nome do mapa, corrigido para o português do Brasil (Irã, Quênia, Taiwan, Peru).
- **Apóstrofo tipográfico** (’) vale como o reto: "Côte d’Ivoire" conta a Costa do Marfim.
- **Fonte do tipo rede social não entra na contagem** (regra 4), mesmo que um dia seja incluída na lista.
- **Notícia com data mais de 1 hora no futuro** usa a hora da coleta, em vez de sumir da janela.
- **Licença**: `nomes_paises.json` é derivado da mledoze/countries e fica sob a ODbL 1.0. O arquivo diz isso,
  e o README e a tela Método também.

## Consequências

- Nas 295 manchetes, 30 mudaram de resultado, todas para o certo. A conferência foi feita com o script de
  comparação da revisão, não com estimativa.
- Riscos conhecidos, aceitos:
  - "Virginia Woolf" e "Indiana Jones" contam os EUA.
  - "Gulf of Aden" conta o Iêmen.
  - Notícia sobre Bruxelas como cidade, sem dizer "Belgium", deixa de contar a Bélgica.
- Nomes de pessoas (Netanyahu, Trump) continuam sem contar o país. Eles mudam com o tempo e colidem com outras coisas
  ("Trump Tower"). A tela Método diz isso.
- "South and North Korea" ainda conta só a Coreia do Norte. Para resolver, um termo teria de apontar para dois
  países, o que é mudança de código para outra versão.
- As citações continuam recalculadas a cada exportação com a regra do momento.
  Quando virarem dado (fase 1), serão gravadas por documento com a versão da regra.
