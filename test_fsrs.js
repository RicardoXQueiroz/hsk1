/**
 * Simulador do FSRS — roda no Node, sem depender do navegador.
 * Uso: node test_fsrs.js
 *
 * Serve pra validar visualmente se o algoritmo se comporta como esperado
 * antes de confiar nele em produção. Testa 3 cenários:
 *   1. Sempre "Fácil" — intervalo deveria crescer rápido.
 *   2. Sempre "Bom" — crescimento mais moderado.
 *   3. Alterna "Bom" e "Esqueci" — deveria oscilar, sem nunca disparar.
 */

const W = [0.4, 0.6, 2.4, 5.8, 4.93, 0.94, 0.86, 0.01, 1.49, 0.14, 0.94, 2.18, 0.05, 0.34, 1.26, 0.29, 2.61];
const REQUESTED_RETENTION = 0.9;
const RATING_LABEL = { 1: "Esqueci", 2: "Difícil", 3: "Bom  ", 4: "Fácil" };

function clampD(d) { return Math.min(10, Math.max(1, d)); }
function initS(r) { return W[r - 1]; }
function initD(r) { return clampD(W[4] - Math.exp(W[5] * (r - 1)) + 1); }
function meanRev(init, cur) { return W[7] * init + (1 - W[7]) * cur; }
function nextD(D, r) { return clampD(meanRev(initD(4), D - W[6] * (r - 3))); }
function retr(t, S) { return Math.pow(1 + t / (9 * S), -1); }

function recallS(D, S, R, r) {
  const hard = r === 2 ? W[15] : 1;
  const easy = r === 4 ? W[16] : 1;
  return S * (1 + Math.exp(W[8]) * (11 - D) * Math.pow(S, -W[9]) * (Math.exp((1 - R) * W[10]) - 1) * hard * easy);
}

function forgetS(D, S, R) {
  return W[11] * Math.pow(D, -W[12]) * (Math.pow(S + 1, W[13]) - 1) * Math.exp((1 - R) * W[14]);
}

function step(state, rating) {
  let D, S;
  if (!state) {
    D = initD(rating);
    S = initS(rating);
  } else {
    const R = retr(state.intervalDays, state.S);
    D = nextD(state.D, rating);
    S = rating === 1 ? forgetS(state.D, state.S, R) : recallS(state.D, state.S, R, rating);
  }
  const intervalDays = Math.max(1, Math.round(S * (9 * (1 / REQUESTED_RETENTION - 1))));
  return { D, S, intervalDays };
}

function simular(nome, sequenciaDeRatings) {
  console.log(`\n=== ${nome} ===`);
  console.log("rodada | avaliação | S (dias) | D    | próximo intervalo");
  let state = null;
  sequenciaDeRatings.forEach((rating, i) => {
    state = step(state, rating);
    console.log(
      `${String(i + 1).padStart(6)} | ${RATING_LABEL[rating]}    | ${state.S.toFixed(2).padStart(8)} | ${state.D.toFixed(2)} | +${state.intervalDays}d`
    );
  });
}

simular("Sempre Fácil (4)", [4, 4, 4, 4, 4, 4]);
simular("Sempre Bom (3)", [3, 3, 3, 3, 3, 3]);
simular("Bom, Bom, Esqueci, Bom, Bom", [3, 3, 1, 3, 3]);
simular("Sempre Difícil (2)", [2, 2, 2, 2, 2, 2]);
simular("Esqueci sempre (pior caso)", [1, 1, 1, 1, 1]);

console.log("\nO que checar:");
console.log("- 'Sempre Fácil' deve crescer mais rápido que 'Sempre Bom'.");
console.log("- No cenário com 'Esqueci' no meio, S deve cair bastante naquela rodada e voltar a crescer depois.");
console.log("- 'Sempre Difícil' deve crescer bem mais devagar que 'Sempre Bom'.");
console.log("- 'Esqueci sempre' nunca deveria ultrapassar poucos dias de intervalo.");
