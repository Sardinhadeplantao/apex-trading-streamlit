import { continente } from "@/lib/formatar";

/** Propriedades de cada país em public/geo/paises.geojson (gerado por jobs/scripts/preparar_paises.py). */
export type Pais = {
  iso: string; iso_oficial: boolean; iso2: string | null; nome: string; nome_en: string;
  wikidata: string | null; continente: string | null; regiao: string | null;
};

export default function PainelPais({ pais, fechar }: { pais: Pais; fechar: () => void }) {
  return (
    <aside className="painel" aria-label={`Painel de ${pais.nome}`}>
      <div className="painel-topo">
        <div>
          <h2>{pais.nome}</h2>
          {pais.nome_en !== pais.nome && <p className="discreto">{pais.nome_en}</p>}
        </div>
        <button onClick={fechar} className="fechar" aria-label="Fechar painel">×</button>
      </div>

      <dl className="codigos">
        <dt>{pais.iso_oficial ? "ISO 3166" : "Código"}</dt>
        <dd>{pais.iso}{pais.iso2 ? ` · ${pais.iso2}` : ""}{!pais.iso_oficial && <span className="discreto"> (sem código ISO; código do Natural Earth)</span>}</dd>
        <dt>Continente</dt><dd>{continente(pais.continente)}</dd>
        {pais.wikidata && (<>
          <dt>Wikidata</dt>
          <dd><a href={`https://www.wikidata.org/wiki/${pais.wikidata}`} target="_blank" rel="noreferrer">{pais.wikidata}</a></dd>
        </>)}
      </dl>

      <section>
        <h3>Eventos</h3>
        <p className="sem-dado-texto">Nenhum evento ligado a este país ainda. A organização das notícias em eventos começa na fase 1.</p>
      </section>
      <section>
        <h3>Mercados</h3>
        <p className="sem-dado-texto">Sem medição ainda. Moeda, juros e bolsa do país entram na fase 2.</p>
      </section>
    </aside>
  );
}
