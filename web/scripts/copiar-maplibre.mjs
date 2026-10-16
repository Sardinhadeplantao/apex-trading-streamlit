// Copia o worker do MapLibre (e o módulo que ele importa) para public/maplibre/ com nome fixo.
// O Next renomeia os arquivos que empacota, e o worker importa "./maplibre-gl-shared.mjs" pelo nome:
// servindo os dois lado a lado, a importação funciona. Roda sozinho antes de "dev" e "build".
import { copyFileSync, mkdirSync } from "node:fs";

const origem = "node_modules/maplibre-gl/dist";
const destino = "public/maplibre";
mkdirSync(destino, { recursive: true });
for (const arquivo of ["maplibre-gl-worker.mjs", "maplibre-gl-shared.mjs"]) {
  copyFileSync(`${origem}/${arquivo}`, `${destino}/${arquivo}`);
}
console.log(`worker do MapLibre copiado para ${destino}/`);
