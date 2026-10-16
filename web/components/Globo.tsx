"use client";
import { useEffect, useRef, useState } from "react";
import type { Map as Mapa, StyleSpecification } from "maplibre-gl";
import PainelPais, { type Pais } from "./PainelPais";

const BASE = process.env.NEXT_PUBLIC_BASE_PATH ?? "";

/** Cinza = sem medição. Cor só entra quando houver mudança medida (fase 2). */
function estilo(plano: boolean): StyleSpecification {
  return {
    version: 8,
    projection: { type: plano ? "mercator" : "globe" },
    sources: { paises: { type: "geojson", data: `${BASE}/geo/paises.geojson`, promoteId: "iso" } },
    layers: [
      { id: "oceano", type: "background", paint: { "background-color": "#0c1a2c" } },
      {
        id: "paises", type: "fill", source: "paises",
        paint: { "fill-color": ["case", ["boolean", ["feature-state", "selecionado"], false], "#5d7ba3", "#3a4354"] },
      },
      { id: "fronteiras", type: "line", source: "paises", paint: { "line-color": "#6d7a92", "line-width": 0.6 } },
    ],
    sky: { "atmosphere-blend": ["interpolate", ["linear"], ["zoom"], 0, 1, 5, 1, 7, 0] },
  };
}

export default function Globo() {
  const caixa = useRef<HTMLDivElement>(null);
  const [pais, setPais] = useState<Pais | null>(null);
  const [sobre, setSobre] = useState<string | null>(null);
  const [erro, setErro] = useState(false);
  const limpar = useRef<() => void>(() => {});

  useEffect(() => {
    let mapa: Mapa | undefined;
    let cancelado = false;
    let selecionado: string | number | null = null;

    const selecionar = (id: string | number | null) => {
      if (!mapa) return;
      if (selecionado !== null) mapa.setFeatureState({ source: "paises", id: selecionado }, { selecionado: false });
      selecionado = id;
      if (id !== null) mapa.setFeatureState({ source: "paises", id }, { selecionado: true });
    };
    limpar.current = () => { selecionar(null); setPais(null); };

    import("maplibre-gl").then((maplibregl) => {  // a versão 6 só tem importação por nome (sem "default")
      if (cancelado || !caixa.current) return;
      // Worker copiado para public/maplibre/ por scripts/copiar-maplibre.mjs; "v" evita usar um worker de versão antiga em cache
      maplibregl.setWorkerUrl(`${location.origin}${BASE}/maplibre/maplibre-gl-worker.mjs?v=${maplibregl.getVersion()}`);
      const plano = window.matchMedia("(max-width: 700px)").matches;
      mapa = new maplibregl.Map({
        container: caixa.current,
        style: estilo(plano),
        center: [10, 20],
        zoom: plano ? 0.4 : 1.9,
        attributionControl: { compact: true, customAttribution: "Fronteiras: Natural Earth" },
      });
      mapa.addControl(new maplibregl.NavigationControl({ showCompass: false }), "top-left");
      mapa.on("error", (e) => { if (String(e.error?.message ?? "").includes("paises")) setErro(true); });
      mapa.on("mousemove", "paises", (e) => {
        mapa!.getCanvas().style.cursor = "pointer";
        setSobre((e.features?.[0]?.properties?.nome as string) ?? null);
      });
      mapa.on("mouseleave", "paises", () => { mapa!.getCanvas().style.cursor = ""; setSobre(null); });
      mapa.on("click", (e) => {
        const f = mapa!.queryRenderedFeatures(e.point, { layers: ["paises"] })[0];
        if (!f || f.id === undefined) { selecionar(null); setPais(null); return; }
        selecionar(f.id);
        setPais(f.properties as Pais);
      });
    }).catch(() => setErro(true));

    return () => { cancelado = true; mapa?.remove(); };
  }, []);

  return (
    <div className="globo">
      <div ref={caixa} className="globo-mapa" aria-label="Mapa do mundo. Clique num país para ver o painel." />
      {sobre && !pais && <div className="globo-dica">{sobre}</div>}
      {erro && <div className="globo-erro">Não foi possível carregar o mapa. Recarregue a página.</div>}
      {pais && <PainelPais pais={pais} fechar={() => limpar.current()} />}
    </div>
  );
}
