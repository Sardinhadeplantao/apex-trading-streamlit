/** Formatação para a tela. Só apresenta o que o robô gravou; nenhuma conta sobre os dados. */

const DATA_HORA = new Intl.DateTimeFormat("pt-BR", {
  timeZone: "America/Sao_Paulo", day: "2-digit", month: "2-digit", year: "numeric", hour: "2-digit", minute: "2-digit",
});

/** "16/10/2026, 07:30" no horário de Brasília. Sem data, um traço. */
export function dataHora(iso: string | null | undefined): string {
  if (!iso) return "—";
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? "—" : DATA_HORA.format(d);
}

const CONTINENTES: Record<string, string> = {
  Africa: "África", Antarctica: "Antártida", Asia: "Ásia", Europe: "Europa", "North America": "América do Norte",
  Oceania: "Oceania", "Seven seas (open ocean)": "Oceano", "South America": "América do Sul",
};

export function continente(nome: string | null | undefined): string {
  return nome ? CONTINENTES[nome] ?? nome : "—";
}

export type Situacao = "ok" | "parcial" | "falhou" | "rodando";

const SITUACOES: Record<Situacao, string> = { ok: "Funcionando", parcial: "Parcial", falhou: "Falhou", rodando: "Rodando" };

export function situacao(s: string | null | undefined): { texto: string; classe: string } {
  if (!s || !(s in SITUACOES)) return { texto: "Sem dado", classe: "sem-dado" };
  return { texto: SITUACOES[s as Situacao], classe: `sit-${s}` };
}

const TIPOS: Record<string, string> = { oficial: "Oficial", imprensa: "Imprensa", dados: "Dados", social: "Rede social (pista)" };

export function tipoFonte(t: string): string {
  return TIPOS[t] ?? t;
}

export function numero(n: number): string {
  return n.toLocaleString("pt-BR");
}
