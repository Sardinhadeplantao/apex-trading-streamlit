import assert from "node:assert/strict";
import { test } from "node:test";
import { continente, dataHora, diaHora, faixas, hora, plural, situacao, tipoFonte } from "./formatar.ts";

test("datas em horário de Brasília", () => {
  assert.equal(dataHora("2026-10-16T10:30:00Z"), "16/10/2026, 07:30");
  assert.equal(diaHora("2026-10-16T10:30:00Z"), "16/10, 07:30");
  assert.equal(hora("2026-10-16T10:30:00Z"), "07:30");
  assert.equal(dataHora(null), "—");
  assert.equal(hora("não é data"), "—");
});

test("situação desconhecida aparece como sem dado (cinza)", () => {
  assert.deepEqual(situacao("ok"), { texto: "Funcionando", classe: "sit-ok" });
  assert.deepEqual(situacao(undefined), { texto: "Sem dado", classe: "sem-dado" });
  assert.deepEqual(situacao("xyz"), { texto: "Sem dado", classe: "sem-dado" });
});

test("nomes em português", () => {
  assert.equal(continente("South America"), "América do Sul");
  assert.equal(continente("Atlântida"), "Atlântida");
  assert.equal(tipoFonte("social"), "Rede social (pista)");
  assert.equal(tipoFonte(null), "—");
});

test("faixas da legenda vêm dos limites do robô", () => {
  assert.deepEqual(faixas([1, 3, 10, 30]), ["1–2", "3–9", "10–29", "30+"]);
  assert.deepEqual(faixas([1, 2, 5]), ["1", "2–4", "5+"]);
});

test("plural", () => {
  assert.equal(plural(1, "notícia", "notícias"), "1 notícia");
  assert.equal(plural(1200, "notícia", "notícias"), "1.200 notícias");
});
