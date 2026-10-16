"use client";
import { useEffect, useState } from "react";
import { dataHora } from "@/lib/formatar";

/**
 * O site é refeito a cada rodada do robô. Se o robô parar, a página fica com a última foto e parece atual.
 * O robô publica até quando a foto vale (avisar_atraso_apos); passado esse horário, o aviso aparece.
 */
export default function AvisoAtraso({ ate, gerado }: { ate: string | null | undefined; gerado: string | null }) {
  const [atrasado, setAtrasado] = useState(false);
  useEffect(() => {
    if (!ate) return;
    const conferir = () => setAtrasado(Date.now() > new Date(ate).getTime());
    conferir();
    const t = setInterval(conferir, 60_000);
    return () => clearInterval(t);
  }, [ate]);
  if (!atrasado) return null;
  return (
    <p className="aviso-atraso" role="status">
      Dados parados desde {dataHora(gerado)} (Brasília). O robô pode estar desligado ou com falha: veja a tela Método.
    </p>
  );
}
