"use client";
import { useEffect, useState } from "react";

const FORMATO = new Intl.DateTimeFormat("pt-BR", {
  timeZone: "America/Sao_Paulo", day: "2-digit", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit",
});

/** Data e hora de agora, no horário de Brasília. Só aparece no navegador (a página é montada antes). */
export default function Relogio() {
  const [agora, setAgora] = useState<Date | null>(null);
  useEffect(() => {
    setAgora(new Date());
    const t = setInterval(() => setAgora(new Date()), 30_000);
    return () => clearInterval(t);
  }, []);
  return (
    <time className="relogio" suppressHydrationWarning>
      {agora ? FORMATO.format(agora).replace(",", " ·") : ""}
      {agora && <span className="discreto"> Brasília</span>}
    </time>
  );
}
