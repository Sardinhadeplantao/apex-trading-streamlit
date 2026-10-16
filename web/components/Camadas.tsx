"use client";
import { useState } from "react";

/** Camadas do mapa. As ligadas avisam o globo por um evento; as futuras aparecem com a fase em que entram. */
const ATIVAS = [
  { id: "citacoes", nome: "Citações por país" },
  { id: "fronteiras", nome: "Fronteiras" },
];
const FUTURAS = [
  { nome: "Eventos e confirmação", fase: "fase 1" },
  { nome: "Mercados", fase: "fase 2" },
  { nome: "Rotas e estreitos", fase: "fase 4" },
  { nome: "Conflitos", fase: "fase 4" },
  { nome: "Cadeias industriais", fase: "fase 5" },
];

export default function Camadas() {
  const [ligadas, setLigadas] = useState<Record<string, boolean>>({ citacoes: true, fronteiras: true });
  function alternar(id: string) {
    const ligada = !ligadas[id];
    setLigadas({ ...ligadas, [id]: ligada });
    window.dispatchEvent(new CustomEvent("stratum:camada", { detail: { id, ligada } }));
  }
  return (
    <ul className="camadas">
      {ATIVAS.map((c) => (
        <li key={c.id}>
          <span>{c.nome}</span>
          <button type="button" role="switch" aria-checked={ligadas[c.id]} aria-label={c.nome}
                  className={`chave ${ligadas[c.id] ? "ligada" : ""}`} onClick={() => alternar(c.id)}>
            <i />
          </button>
        </li>
      ))}
      {FUTURAS.map((c) => (
        <li key={c.nome} className="futura">
          <span>{c.nome}</span>
          <span className="fase">{c.fase}</span>
        </li>
      ))}
    </ul>
  );
}
