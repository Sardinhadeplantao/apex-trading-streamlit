import { hora, numero, situacao } from "@/lib/formatar";
import type { Status } from "@/lib/status";

type Indicador = { rotulo: string; valor: string; detalhe: string; semDado?: boolean; classe?: string };

/** Só números medidos. O que ainda não é medido aparece em cinza, com a fase em que entra. */
export default function Indicadores({ status }: { status: Status }) {
  const a = status.atencao;
  const rodada = status.ultima_rodada;
  const lista: Indicador[] = [
    { rotulo: `Notícias em ${a?.janela_horas ?? 24} h`, valor: a ? numero(a.documentos) : "—",
      detalhe: "publicadas pelas fontes acompanhadas", semDado: !a },
    { rotulo: "Países citados", valor: a ? numero(a.paises_citados) : "—",
      detalhe: a ? `${numero(a.documentos_com_pais)} notícias citam algum país` : "sem notícias na janela", semDado: !a },
    { rotulo: `Oficiais em ${a?.janela_horas ?? 24} h`, valor: a ? numero(a.oficiais) : "—",
      detalhe: "atos e comunicados de governos e da ONU", semDado: !a },
    { rotulo: "Fontes funcionando", valor: `${status.totais.fontes_ok} de ${status.totais.fontes}`,
      detalhe: rodada ? `última rodada às ${hora(rodada.iniciada_em)}` : "o robô ainda não rodou",
      classe: situacao(rodada?.situacao).classe, semDado: !rodada },
    { rotulo: "Mercados", valor: "—", detalhe: "moedas, juros e bolsas entram na fase 2", semDado: true },
  ];
  return (
    <section className="indicadores" aria-label="Indicadores">
      {lista.map((i) => (
        <div key={i.rotulo} className={`indicador bloco ${i.semDado ? "sem-dado-bloco" : ""}`}>
          <span className="rotulo">{i.classe && <span className={`ponto ${i.classe}`} aria-hidden />}{i.rotulo}</span>
          <strong>{i.valor}</strong>
          <span className="discreto">{i.detalhe}</span>
        </div>
      ))}
    </section>
  );
}
