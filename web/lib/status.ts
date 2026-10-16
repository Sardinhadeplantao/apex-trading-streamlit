import fs from "node:fs";
import path from "node:path";

/** Formato do public/dados/status.json gravado pelo robô (jobs/geomonitor/export.py). */
export type Coleta = { em: string | null; situacao: string; itens_lidos: number; itens_novos: number; erro: string | null };
export type Fonte = {
  id: string; nome: string; tipo: string; pais: string | null; idioma: string | null; url: string; criterio: string | null;
  ativa: boolean; ultima_coleta: Coleta | null; documentos: number; documentos_24h: number;
};
export type Documento = {
  titulo: string; url: string | null; fonte: string; fonte_nome: string; publicado_em: string | null; conhecido_em: string | null;
};
export type Status = {
  versao_formato: number;
  versao_robo: string | null;
  gerado_em: string | null;
  banco: "permanente" | "temporario" | "erro" | null;
  erro_banco: string | null;
  ultima_rodada: { id: number; iniciada_em: string | null; terminada_em: string | null; situacao: string } | null;
  rodadas_recentes: { iniciada_em: string | null; situacao: string }[];
  totais: { documentos: number; documentos_24h: number; fontes: number; fontes_ok: number };
  fontes: Fonte[];
  ultimos_documentos: Documento[];
};

const VAZIO: Status = {
  versao_formato: 1, versao_robo: null, gerado_em: null, banco: null, erro_banco: null, ultima_rodada: null,
  rodadas_recentes: [], totais: { documentos: 0, documentos_24h: 0, fontes: 0, fontes_ok: 0 }, fontes: [], ultimos_documentos: [],
};

/** Lido na hora de montar o site. Sem arquivo (robô ainda não rodou), devolve o estado vazio. */
export function lerStatus(): Status {
  const arquivo = path.join(process.cwd(), "public", "dados", "status.json");
  if (!fs.existsSync(arquivo)) return VAZIO;
  return { ...VAZIO, ...JSON.parse(fs.readFileSync(arquivo, "utf8")) };
}
