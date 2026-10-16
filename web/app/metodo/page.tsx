import { dataHora, faixas, numero, situacao, tipoFonte } from "@/lib/formatar";
import { lerStatus, type Fonte } from "@/lib/status";

export const metadata = { title: "Método · Stratum Global" };

const BANCO: Record<string, string> = {
  permanente: "Permanente (Supabase). O que o robô coleta fica guardado.",
  temporario: "Temporário. O banco ainda não foi configurado: cada rodada começa do zero e nada fica guardado.",
  erro: "O robô não conseguiu abrir o banco nesta rodada.",
};

/** Fontes com o mesmo critério aparecem juntas, para o critério não se repetir em cada linha. */
function agruparCriterios(fontes: Fonte[]): [string, string[]][] {
  const grupos = new Map<string, string[]>();
  for (const f of fontes) {
    if (f.criterio) grupos.set(f.criterio, [...(grupos.get(f.criterio) ?? []), f.nome]);
  }
  return [...grupos.entries()];
}

export default function Metodo() {
  const s = lerStatus();
  const rodada = s.ultima_rodada;
  const sit = situacao(rodada?.situacao);
  const a = s.atencao;
  const criterios = agruparCriterios(s.fontes.filter((f) => f.ativa));
  return (
    <main className="pagina">
      <h1>Método</h1>
      <p className="lead">Posso confiar? Esta página mostra como o Stratum Global funciona, o que ele mede e o que ainda não mede.</p>

      <section>
        <h2>Regras</h2>
        <ul className="regras">
          <li><b>Toda informação tem fonte e duas datas:</b> quando aconteceu e quando o sistema soube.</li>
          <li><b>Nada é apagado nem reescrito.</b> Correção vira registro novo.</li>
          <li><b>Notícia entra com grau de confirmação.</b> Rede social é só pista, nunca fato.</li>
          <li><b>Fontes entram por critério escrito,</b> não por parecerem interessantes.</li>
          <li><b>Regra decide; IA só lê, resume e traduz.</b> O sistema funciona sem IA.</li>
          <li><b>Preço é contexto:</b> nunca ordena eventos nem dispara aviso sozinho.</li>
          <li><b>O site não calcula:</b> mostra o que o robô gravou. Cinza quer dizer sem dado.</li>
        </ul>
      </section>

      <section>
        <h2>Como contamos as citações de países</h2>
        <p>
          O globo pinta cada país pela quantidade de notícias que o citam, entre as publicadas nas últimas{" "}
          {a?.janela_horas ?? 24} horas pelas fontes acompanhadas. Uma notícia cita um país quando o título ou o resumo traz
          o nome dele (em inglês ou português), o gentílico em inglês (como <i>Russian</i>), a capital, uma sigla aceita
          (US, UK, EUA, UAE) ou uma referência direta ao governo (Kremlin, Casa Branca).
        </p>
        <ul className="regras">
          <li>Cada notícia conta uma vez por país, mesmo que cite o país várias vezes.</li>
          <li>Diferencia maiúsculas: <i>Turkey</i> é país, <i>turkey</i> não. Nome dentro de outra palavra não conta (<i>Niger</i> em <i>Nigeria</i>).</li>
          <li>O termo mais longo vence: <i>Papua New Guinea</i> não conta Guiné; <i>Latin American</i> não conta os Estados Unidos.</li>
          <li>Citação mede atenção da imprensa e dos governos, não importância nem gravidade.</li>
          <li>A regra pode errar. Toda contagem leva às notícias, para conferir.</li>
        </ul>
        {a && (
          <dl className="resumo">
            <dt>Versão da regra</dt><dd>{a.regra}</dd>
            <dt>Faixas de cor</dt><dd>{faixas(a.niveis).join(" · ")} notícias</dd>
            <dt>Nesta rodada</dt>
            <dd>{numero(a.documentos)} notícias na janela, {numero(a.documentos_com_pais)} citam algum país, {numero(a.paises_citados)} países citados</dd>
            <dt>Termos ignorados</dt><dd>{a.ignorados.join(", ")} (apontam para mais de um lugar ou pessoa)</dd>
          </dl>
        )}
      </section>

      <section>
        <h2>Saúde do robô</h2>
        {s.erro_banco && <p className="alerta">{s.erro_banco}</p>}
        <dl className="resumo">
          <dt>Última rodada</dt>
          <dd><span className={`ponto ${sit.classe}`} aria-hidden /> {sit.texto} · {dataHora(rodada?.iniciada_em)} (Brasília)</dd>
          <dt>Banco</dt><dd>{s.banco ? BANCO[s.banco] : "—"}</dd>
          <dt>Fontes funcionando</dt><dd>{s.totais.fontes_ok} de {s.totais.fontes}</dd>
          <dt>Documentos</dt><dd>{numero(s.totais.documentos)} no total · {numero(s.totais.documentos_24h)} coletados nas últimas 24h</dd>
          <dt>Versão do robô</dt><dd>{s.versao_robo ?? "—"}</dd>
        </dl>
        {s.rodadas_recentes.length > 0 && (
          <div className="rodadas" aria-label="Rodadas recentes, da mais nova para a mais antiga">
            {s.rodadas_recentes.map((r, i) => {
              const x = situacao(r.situacao);
              return <span key={i} className={`quadrado ${x.classe}`} title={`${dataHora(r.iniciada_em)}: ${x.texto}`} />;
            })}
          </div>
        )}
      </section>

      <section>
        <h2>Fontes</h2>
        {s.fontes.length === 0 ? <p className="sem-dado-texto">O robô ainda não rodou.</p> : (
          <div className="tabela-rolagem">
            <table>
              <thead>
                <tr><th>Fonte</th><th>Tipo</th><th>País</th><th>Última coleta</th><th>Situação</th><th>Novos</th><th>24h</th><th>Total</th></tr>
              </thead>
              <tbody>
                {s.fontes.filter((f) => f.ativa).map((f) => {
                  const c = f.ultima_coleta;
                  const x = situacao(c?.situacao);
                  return (
                    <tr key={f.id}>
                      <td><a href={f.url} target="_blank" rel="noreferrer">{f.nome}</a></td>
                      <td>{tipoFonte(f.tipo)}</td>
                      <td>{f.pais_nome ?? f.pais ?? "Internacional"}</td>
                      <td>{dataHora(c?.em)}</td>
                      <td><span className={`ponto ${x.classe}`} aria-hidden /> {x.texto}{c?.erro && <div className="erro">{c.erro}</div>}</td>
                      <td>{c ? numero(c.itens_novos) : "—"}</td>
                      <td>{numero(f.documentos_24h)}</td>
                      <td>{numero(f.documentos)}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
        {criterios.length > 0 && (<>
          <h3>Por que cada fonte está na lista</h3>
          <ul className="regras">
            {criterios.map(([criterio, nomes]) => <li key={criterio}>{criterio} <span className="discreto">({nomes.join(", ")})</span></li>)}
          </ul>
        </>)}
      </section>

      <section id="documentos">
        <h2>Últimas notícias coletadas</h2>
        <p className="discreto">Ainda soltas: a organização em eventos, com grau de confirmação, começa na fase 1.</p>
        {s.ultimos_documentos.length === 0 ? <p className="sem-dado-texto">Nenhum documento ainda.</p> : (
          <ul className="documentos">
            {s.ultimos_documentos.map((d, i) => (
              <li key={i}>
                {d.url ? <a href={d.url} target="_blank" rel="noreferrer">{d.titulo}</a> : d.titulo}
                <div className="discreto">
                  {d.fonte_nome} · publicado {dataHora(d.publicado_em)} · coletado {dataHora(d.conhecido_em)}
                  {d.paises && d.paises.length > 0 && <> · cita {d.paises.map((p) => p.nome).join(", ")}</>}
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section>
        <h2>O que ainda não é medido</h2>
        <ul className="regras">
          <li>Eventos (notícias agrupadas, grau de confirmação, importância): fase 1.</li>
          <li>Mercados (moedas, juros, bolsas por país, commodities): fase 2.</li>
          <li>Comércio, navios nos estreitos, sanções e conflito como séries: fase 4.</li>
          <li>Cadeias, exposição e hipóteses: fase 5.</li>
        </ul>
      </section>

      <p className="discreto rodape">
        Status gerado em {dataHora(s.gerado_em)}. Fronteiras: Natural Earth. Nomes de países: mledoze/countries (licença ODbL).
        Informação de contexto; não é recomendação de investimento.
      </p>
    </main>
  );
}
