import assert from "node:assert/strict";
import { test } from "node:test";
import { continente, dataHora, situacao, tipoFonte } from "./formatar.ts";

test("data em horário de Brasília", () => {
  assert.equal(dataHora("2026-10-16T10:30:00Z"), "16/10/2026, 07:30");
  assert.equal(dataHora(null), "—");
  assert.equal(dataHora("não é data"), "—");
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
});
