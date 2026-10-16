import Atualizacoes from "@/components/Atualizacoes";
import Cartoes from "@/components/Cartoes";
import Globo from "@/components/Globo";
import Indicadores from "@/components/Indicadores";
import Lateral from "@/components/Lateral";
import { NIVEIS_PADRAO } from "@/lib/constantes";
import { lerStatus } from "@/lib/status";

export default function Inicio() {
  const status = lerStatus();
  const a = status.atencao;
  return (
    <main className="painel-geral">
      <Lateral atual="/" />
      <section className="mapa-bloco bloco" aria-label="Mapa global">
        <Globo paises={status.paises} niveis={a?.niveis ?? NIVEIS_PADRAO} janelaHoras={a?.janela_horas ?? 24} />
      </section>
      <Indicadores status={status} />
      <Atualizacoes documentos={status.ultimos_documentos.slice(0, 14)} />
      <Cartoes status={status} />
    </main>
  );
}
