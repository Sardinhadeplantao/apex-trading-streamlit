/** Site estático publicado no GitHub Pages em /<nome-do-repositório>. O site não calcula nada: só mostra o que o robô gravou. */
const base = process.env.BASE_PATH ?? "";
export default {
  output: "export",
  basePath: base,
  trailingSlash: true,
  images: { unoptimized: true },
  env: { NEXT_PUBLIC_BASE_PATH: base },
};
