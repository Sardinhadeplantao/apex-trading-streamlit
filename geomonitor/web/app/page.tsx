import Link from "next/link";
import Globo from "@/components/Globo";
import { dataHora, numero, situacao } from "@/lib/formatar";
import { lerStatus } from "@/lib/status";

export default function Inicio() {
  const status = lerStatus();
  const rodada = status.ultima_rodada;
  const sit = situacao(rodada?.situacao);
  return (
    <main className="inicio">
      <Globo />
      <Link href="/metodo/" className="robo-resumo">
        <span className={`ponto ${sit.classe}`} aria-hidden />
        {rodada
          ? <>Robô: {sit.texto.toLowerCase()} · {dataHora(rodada.iniciada_em)} · {numero(status.totais.documentos_24h)} documentos em 24h</>
          : <>Robô: ainda não rodou</>}
      </Link>
    </main>
  );
}
