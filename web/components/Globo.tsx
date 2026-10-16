"use client";
import { useEffect, useMemo, useRef, useState } from "react";
import type { ExpressionSpecification, Map as Mapa, StyleSpecification } from "maplibre-gl";
import PainelPais, { type Pais } from "./PainelPais";
import { faixas } from "@/lib/formatar";
import type { PaisAtencao } from "@/lib/status";

const BASE = process.env.NEXT_PUBLIC_BASE_PATH ?? "";

/** Cor por nível de citações (calculado pelo robô). Nível 0 = nenhuma citação: cinza. */
export const CORES_NIVEL = ["#333d4f", "#1f4f78", "#2a74aa", "#3f9bd2", "#94d3f3"];
const COR_SELECAO = "#f5c451";
const PREENCHIMENTO: ExpressionSpecification = [
  "match", ["coalesce", ["feature-state", "nivel"], 0],
  1, CORES_NIVEL[1], 2, CORES_NIVEL[2], 3, CORES_NIVEL[3], 4, CORES_NIVEL[4], CORES_NIVEL[0],
];

type Item = { iso: string; nome: string; nome_en: string; centro: [number, number] | null };
type Props = { paises: Record<string, PaisAtencao>; niveis: number[]; janelaHoras: number };

function estilo(plano: boolean): StyleSpecification {
  return {
    version: 8,
    projection: { type: plano ? "mercator" : "globe" },
    sources: { paises: { type: "geojson", data: `${BASE}/geo/paises.geojson`, promoteId: "iso" } },
    layers: [
      { id: "oceano", type: "background", paint: { "background-color": "#0b1829" } },
      { id: "paises", type: "fill", source: "paises", paint: { "fill-color": PREENCHIMENTO } },
      { id: "fronteiras", type: "line", source: "paises", paint: { "line-color": "#5f6f8c", "line-width": 0.5 } },
      {
        id: "selecao", type: "line", source: "paises",
        paint: {
          "line-color": COR_SELECAO,
          "line-width": ["case", ["boolean", ["feature-state", "selecionado"], false], 2, 0],
        },
      },
    ],
    sky: { "atmosphere-blend": ["interpolate", ["linear"], ["zoom"], 0, 1, 5, 1, 7, 0] },
  };
}

const semAcento = (s: string) => s.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();

function isoDoHash(): string | null {
  const m = /^#pais=([A-Z]{3})$/.exec(window.location.hash);
  return m ? m[1] : null;
}

export default function Globo({ paises, niveis, janelaHoras }: Props) {
  const caixa = useRef<HTMLDivElement>(null);
  const mapaRef = useRef<Mapa | null>(null);
  const selecionadoRef = useRef<string | null>(null);
  const [lista, setLista] = useState<Item[]>([]);
  const [pais, setPais] = useState<Pais | null>(null);
  const [sobre, setSobre] = useState<{ nome: string; citacoes: number } | null>(null);
  const [busca, setBusca] = useState("");
  const [erro, setErro] = useState(false);

  // Lista de países para a busca e para centralizar o globo (mesmo arquivo do mapa; o navegador reaproveita)
  useEffect(() => {
    fetch(`${BASE}/geo/paises.geojson`).then((r) => r.json()).then((geo) => {
      setLista(geo.features.map((f: { properties: Pais }) => ({
        iso: f.properties.iso, nome: f.properties.nome, nome_en: f.properties.nome_en, centro: f.properties.centro ?? null,
      })));
    }).catch(() => setErro(true));
  }, []);
  const porIso = useMemo(() => new Map(lista.map((i) => [i.iso, i])), [lista]);

  function marcar(iso: string | null) {
    const mapa = mapaRef.current;
    if (!mapa) return;
    if (selecionadoRef.current) mapa.setFeatureState({ source: "paises", id: selecionadoRef.current }, { selecionado: false });
    selecionadoRef.current = iso;
    if (iso) mapa.setFeatureState({ source: "paises", id: iso }, { selecionado: true });
  }

  function selecionar(iso: string | null, voar: boolean) {
    marcar(iso);
    if (!iso) {
      setPais(null);
      if (window.location.hash) history.replaceState(null, "", window.location.pathname + window.location.search);
      return;
    }
    if (window.location.hash !== `#pais=${iso}`) history.replaceState(null, "", `#pais=${iso}`);
    const feicao = mapaRef.current?.querySourceFeatures("paises", { filter: ["==", ["get", "iso"], iso] })[0];
    const item = porIso.get(iso);
    setPais(feicao ? (feicao.properties as Pais) : item ? ({ iso, nome: item.nome, nome_en: item.nome_en } as Pais) : null);
    if (voar && item?.centro) mapaRef.current?.flyTo({ center: item.centro, zoom: Math.max(mapaRef.current.getZoom(), 2.6) });
  }
  const selecionarRef = useRef(selecionar);
  selecionarRef.current = selecionar;

  useEffect(() => {
    let cancelado = false;
    import("maplibre-gl").then((maplibregl) => {  // a versão 6 só tem importação por nome (sem "default")
      if (cancelado || !caixa.current) return;
      // Worker copiado para public/maplibre/ por scripts/copiar-maplibre.mjs; "v" evita usar um worker de versão antiga em cache
      maplibregl.setWorkerUrl(`${location.origin}${BASE}/maplibre/maplibre-gl-worker.mjs?v=${maplibregl.getVersion()}`);
      const plano = window.matchMedia("(max-width: 760px)").matches;
      const mapa = new maplibregl.Map({
        container: caixa.current,
        style: estilo(plano),
        center: [20, 25],
        zoom: plano ? 0.3 : 1.45,
        attributionControl: { compact: true, customAttribution: "Fronteiras: Natural Earth" },
      });
      mapaRef.current = mapa;
      mapa.addControl(new maplibregl.NavigationControl({ showCompass: false }), "top-right");
      mapa.on("error", (e) => { if (String(e.error?.message ?? "").includes("paises")) setErro(true); });
      mapa.on("load", () => {
        for (const [iso, p] of Object.entries(paises)) mapa.setFeatureState({ source: "paises", id: iso }, { nivel: p.nivel });
      });
      mapa.on("mousemove", "paises", (e) => {
        mapa.getCanvas().style.cursor = "pointer";
        const iso = e.features?.[0]?.properties?.iso as string | undefined;
        const nome = e.features?.[0]?.properties?.nome as string | undefined;
        setSobre(nome && iso ? { nome, citacoes: paises[iso]?.citacoes ?? 0 } : null);
      });
      mapa.on("mouseleave", "paises", () => { mapa.getCanvas().style.cursor = ""; setSobre(null); });
      mapa.on("click", (e) => {
        const f = mapa.queryRenderedFeatures(e.point, { layers: ["paises"] })[0];
        selecionarRef.current(f ? String(f.id) : null, false);
      });
      mapa.once("idle", () => { const iso = isoDoHash(); if (iso) selecionarRef.current(iso, true); });
    }).catch(() => setErro(true));

    const aoMudarHash = () => selecionarRef.current(isoDoHash(), true);
    const aoMudarCamada = (e: Event) => {
      const mapa = mapaRef.current;
      const { id, ligada } = (e as CustomEvent<{ id: string; ligada: boolean }>).detail;
      if (!mapa) return;
      if (id === "citacoes") mapa.setPaintProperty("paises", "fill-color", ligada ? PREENCHIMENTO : CORES_NIVEL[0]);
      if (id === "fronteiras") mapa.setLayoutProperty("fronteiras", "visibility", ligada ? "visible" : "none");
    };
    window.addEventListener("hashchange", aoMudarHash);
    window.addEventListener("stratum:camada", aoMudarCamada);
    return () => {
      cancelado = true;
      window.removeEventListener("hashchange", aoMudarHash);
      window.removeEventListener("stratum:camada", aoMudarCamada);
      mapaRef.current?.remove();
      mapaRef.current = null;
    };
  }, [paises]);

  const sugestoes = useMemo(() => {
    const q = semAcento(busca.trim());
    if (q.length < 2) return [];
    return lista.filter((i) => semAcento(i.nome).includes(q) || semAcento(i.nome_en).includes(q) || i.iso.toLowerCase() === q)
      .sort((a, b) => Number(!semAcento(a.nome).startsWith(q)) - Number(!semAcento(b.nome).startsWith(q)) || a.nome.localeCompare(b.nome))
      .slice(0, 6);
  }, [busca, lista]);

  function escolher(iso: string) {
    setBusca("");
    selecionar(iso, true);
  }

  const rotulos = faixas(niveis);
  return (
    <div className="globo">
      <div ref={caixa} className="globo-mapa" aria-label="Globo. Clique num país ou use a busca para ver o painel." />
      <div className="globo-titulo">
        <span className="rotulo">Visão global</span>
        <span>Países pela quantidade de notícias que os citam nas últimas {janelaHoras} horas</span>
      </div>
      <div className="globo-busca">
        <input
          type="search" value={busca} placeholder="Buscar país…" aria-label="Buscar país"
          onChange={(e) => setBusca(e.target.value)}
          onKeyDown={(e) => { if (e.key === "Enter" && sugestoes[0]) escolher(sugestoes[0].iso); }}
        />
        {sugestoes.length > 0 && (
          <ul className="sugestoes" role="listbox">
            {sugestoes.map((s) => (
              <li key={s.iso}>
                <button type="button" onClick={() => escolher(s.iso)}>
                  {s.nome} <span className="discreto">{s.iso}{paises[s.iso] ? ` · ${paises[s.iso].citacoes}` : ""}</span>
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
      <div className="legenda" aria-label="Legenda">
        <span className="rotulo">Notícias que citam o país ({janelaHoras} h)</span>
        <div className="legenda-faixas">
          <span><i style={{ background: CORES_NIVEL[0] }} />0</span>
          {rotulos.map((r, i) => <span key={r}><i style={{ background: CORES_NIVEL[i + 1] }} />{r}</span>)}
        </div>
      </div>
      {sobre && !pais && <div className="globo-dica">{sobre.nome} · {sobre.citacoes} {sobre.citacoes === 1 ? "notícia" : "notícias"}</div>}
      {erro && <div className="globo-erro">Não foi possível carregar o mapa. Recarregue a página.</div>}
      {pais && <PainelPais pais={pais} atencao={paises[pais.iso] ?? null} janelaHoras={janelaHoras} fechar={() => selecionar(null, false)} />}
    </div>
  );
}
