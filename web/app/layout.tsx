import type { ReactNode } from "react";
import Link from "next/link";
import "maplibre-gl/dist/maplibre-gl.css";
import "./globals.css";

export const metadata = {
  title: "Geomonitor",
  description: "Eventos do mundo com fonte e grau de confirmação, ligados ao que se mede nos mercados.",
  robots: { index: false, follow: false }, // uso pessoal por enquanto
};

export default function Layout({ children }: { children: ReactNode }) {
  return (
    <html lang="pt-BR">
      <body>
        <header className="topo">
          <Link href="/" className="marca">Geomonitor</Link>
          <nav>
            <Link href="/">Globo</Link>
            <Link href="/metodo/">Método</Link>
          </nav>
        </header>
        {children}
      </body>
    </html>
  );
}
