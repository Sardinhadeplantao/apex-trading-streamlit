"use client";
import { useEffect, useMemo, useRef, useState } from "react";
import type { ExpressionSpecification, Map as Mapa, StyleSpecification } from "maplibre-gl";
import PainelPais, { type Pais } from "./PainelPais";
import { faixas } from "@/lib/formatar";
import type { PaisAtencao } from "@/lib/status";

const BASE = process.env.NEXT_PUBLIC_BASE_PATH ?? "";

/** Cor por nível de citações (calculado pelo robô). Nível 0 = medido e nenhuma notícia: o azul mais escuro. */
export const CORES_NIVEL = ["#22344d", "#1f4f78", "#2a74aa", "#3f9bd2", "#94d3f3"];
const COR_SEM_DADO = "#5d6779"; // cinza: o robô não publicou contagem (mesma cor de --sem-dado)
const COR_SELECAO = "#f5c451";
const PREENCHIMENTO: ExpressionSpecification = [
  "match", ["coalesce", ["feature-state", "nivel"], 0],
  1, CORES_NIVEL[1], 2, CORES_NIVEL[2], 3, CORES_NIVEL[3], 4, CORES_NIVEL[4], CORES_NIVEL[0],
];

type Props = { paises: Record<string, PaisAtencao>; niveis: number[]; janelaHoras: number; semDado: boolean };

function estilo(plano: boolean, semDado: boolean): StyleSpecification {
  return {
    version: 8,
    projection: { type: plano ? "mercator" : "globe" },
    sources: { paises: { type: "geojson", data: `${BASE}/geo/paises.geojson`, promoteId: "iso" } },
    layers: [
      { id: "oceano", type: "background", paint: { "background-color": "#0b1829" } },
      { id: "paises", type: "fill", source: "paises", paint: { "fill-color": semDado ? COR_SEM_DADO : PREENCHIMENTO } },
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

/** Siglas e nomes populares que a busca deve entender (o mapa só tem o nome oficial em português e inglês). */
const APELIDOS: Record<string, string> = {
  eua: "USA", us: "USA", usa: "USA", uk: "GBR", inglaterra: "GBR", "gra-bretanha": "GBR", uae: "ARE", eau: "ARE",
  holanda: "NLD", birmania: "MMR",
};

const semAcento = (s: string) => s.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();

function isoDoHash(): string | null {
  const m = /^#pais=([A-Z]{3})$/.exec(window.location.hash);
  return m ? m[1] : null;
}

export default function Globo({ paises, niveis, janelaHoras, semDado }: Props) {
  const caixa = useRef<HTMLDivElement>(null);
  const mapaRef = useRef<Mapa | null>(null);
  const selecionadoRef = useRef<string | null>(null);
  const [lista, setLista] = useState<Pais[]>([]);
  const [pais, setPais] = useState<Pais | null>(null);
  const [sobre, setSobre] = useState<{ nome: string; iso: string } | null>(null);
  const [busca, setBusca] = useState("");
  const [erro, setErro] = useState(false);
  const [camadaLigada, setCamadaLigada] = useState(true);
  const camadaRef = useRef(true);  // o mapa pode ser recriado depois de a chave mudar

  // Países para a busca, para o painel e para centralizar o globo (mesmo arquivo do mapa; o navegador reaproveita)
  useEffect(() => {
    fetch(`${BASE}/geo/paises.geojson`).then((r) => r.json()).then((geo) => {
      setLista(geo.features.map((f: { properties: Pais }) => f.properties));
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
    const item = porIso.get(iso);
    setPais(item ?? null);
    if (voar && item?.centro && mapaRef.current && caixa.current) {
      // Deixa o país fora da área que o painel cobre (à direita no computador, embaixo no celular)
      const celular = window.matchMedia("(max-width: 760px)").matches;
      const padding = celular ? { top: 0, left: 0, right: 0, bottom: caixa.current.clientHeight * 0.55 }
        : { top: 0, left: 0, bottom: 0, right: Math.min(400, caixa.current.clientWidth * 0.45) };
      mapaRef.current.flyTo({ center: item.centro, zoom: Math.max(mapaRef.current.getZoom(), 2.6), padding });
    }
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
        style: estilo(plano, semDado || !camadaRef.current),
        center: plano ? [10, 20] : [20, 25],
        // no celular o mapa é plano: zoom para o mundo inteiro caber na largura
        zoom: plano ? Math.max(Math.log2(caixa.current.clientWidth / 512), 0) : 1.45,
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
        setSobre(nome && iso ? { nome, iso } : null);
      });
      mapa.on("mouseleave", "paises", () => { mapa.getCanvas().style.cursor = ""; setSobre(null); });
      mapa.on("click", (e) => {
        const f = mapa.queryRenderedFeatures(e.point, { layers: ["paises"] })[0];
        selecionarRef.current(f ? String(f.id) : null, false);
      });
      mapa.once("idle", () => { const iso = isoDoHash(); if (iso) selecionarRef.current(iso, true); });
    }).catch(() => setErro(true));

    const aoMudarHash = () => {
      const iso = isoDoHash();
      // Clique num país das listas (fora do mapa): traz o mapa para a tela, senão o painel abre sem ninguém ver
      const r = caixa.current?.getBoundingClientRect();
      if (iso && r && (r.bottom < 80 || r.top > window.innerHeight - 80)) {
        caixa.current?.closest(".mapa-bloco")?.scrollIntoView({ behavior: "smooth", block: "start" });
      }
      selecionarRef.current(iso, true);
    };
    const aoMudarCamada = (e: Event) => {
      const mapa = mapaRef.current;
      const { id, ligada } = (e as CustomEvent<{ id: string; ligada: boolean }>).detail;
      if (id === "citacoes") { camadaRef.current = ligada; setCamadaLigada(ligada); }
      if (!mapa) return;
      if (id === "citacoes") {
        mapa.setPaintProperty("paises", "fill-color", ligada && !semDado ? PREENCHIMENTO : COR_SEM_DADO);
      }
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
  }, [paises, semDado]);

  const sugestoes = useMemo(() => {
    const q = semAcento(busca.trim());
    if (q.length < 2) return [];
    const apelido = porIso.get(APELIDOS[q] ?? "");
    const achados = lista.filter((i) => semAcento(i.nome).includes(q) || semAcento(i.nome_en).includes(q) || i.iso.toLowerCase() === q)
      .sort((a, b) => Number(!semAcento(a.nome).startsWith(q)) - Number(!semAcento(b.nome).startsWith(q)) || a.nome.localeCompare(b.nome));
    return (apelido ? [apelido, ...achados.filter((i) => i !== apelido)] : achados).slice(0, 6);
  }, [busca, lista, porIso]);

  function escolher(iso: string) {
    setBusca("");
    selecionar(iso, true);
  }

  const rotulos = faixas(niveis);
  const medido = camadaLigada && !semDado;
  const citacoes = (iso: string) => paises[iso]?.citacoes ?? 0;  // com contagem publicada, país ausente = zero medido
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
          <ul className="sugestoes">
            {sugestoes.map((s) => (
              <li key={s.iso}>
                <button type="button" onClick={() => escolher(s.iso)}>
                  {s.nome} <span className="discreto">{s.iso}{medido && paises[s.iso] ? ` · ${paises[s.iso].citacoes}` : ""}</span>
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
      <div className="legenda" aria-label="Legenda">
        <span className="rotulo">Notícias que citam o país ({janelaHoras} h)</span>
        <div className="legenda-faixas">
          {medido ? (<>
            <span><i style={{ background: CORES_NIVEL[0] }} />0</span>
            {rotulos.map((r, i) => <span key={r}><i style={{ background: CORES_NIVEL[i + 1] }} />{r}</span>)}
          </>) : (
            <span><i style={{ background: COR_SEM_DADO }} />{semDado ? "Sem dado: o robô não publicou a contagem" : "Camada desligada"}</span>
          )}
        </div>
      </div>
      {sobre && !pais && (
        <div className="globo-dica">
          {sobre.nome}{medido ? ` · ${citacoes(sobre.iso)} ${citacoes(sobre.iso) === 1 ? "notícia" : "notícias"}` : semDado ? " · sem dado" : ""}
        </div>
      )}
      {erro && <div className="globo-erro">Não foi possível carregar o mapa. Recarregue a página.</div>}
      {pais && (
        <PainelPais pais={pais} atencao={paises[pais.iso] ?? null} janelaHoras={janelaHoras} semDado={semDado}
                    fechar={() => selecionar(null, false)} />
      )}
    </div>
  );
}
