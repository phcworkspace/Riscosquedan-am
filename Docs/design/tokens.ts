// Riscos que Dançam — as constantes que o TypeScript precisa.
// Copie para src/engine/tokens.ts
//
// As cores e medidas da INTERFACE vivem no @theme do globals.css (Tailwind 4).
// Aqui ficam só os valores que o motor lê em runtime — o canvas e os SVGs não
// enxergam utilitários do Tailwind.

export type Banda = 'grave' | 'medio' | 'agudo' | 'brilho';

export const BANDAS = [
  { id: 'grave',  nome: 'Grave',  cor: '#FF3B30', hz: [20, 150] },
  { id: 'medio',  nome: 'Médio',  cor: '#FFB300', hz: [150, 700] },
  { id: 'agudo',  nome: 'Agudo',  cor: '#0A84FF', hz: [700, 3200] },
  { id: 'brilho', nome: 'Brilho', cor: '#5AC8FA', hz: [3200, 11000] },
] as const satisfies ReadonlyArray<{
  id: Banda; nome: string; cor: string; hz: readonly [number, number];
}>;

export const CORES_BANDA: Record<Banda, string> = {
  grave: '#FF3B30', medio: '#FFB300', agudo: '#0A84FF', brilho: '#5AC8FA',
};

/** Paleta livre dos elementos. A cor da banda vem pré-selecionada. */
export const PALETA = [
  '#FF3B30', '#FF7A1A', '#FFB300', '#30D158',
  '#0A84FF', '#5AC8FA', '#C77DFF', '#F2F2F7',
] as const;

/** Cores que o canvas desenha e o Tailwind não alcança. */
export const PALCO = {
  fundo: '#141417',
  cursor: '#FFFFFF',
  loop: '#FFD60A',
  sprocket: '#202026',
} as const;

/** Medidas fixas do layout. O palco é o que sobra — não o fixe. */
export const MEDIDAS = {
  cabecalho: 52,
  linhaDoTempo: 148,   // régua 18 + onda 54 + trilhas 44 + transporte 32
  painel: 300,
  regua: 18,
  onda: 54,
  trilhas: 44,
  transporte: 32,
  alturaTrilha: 7,
  passoTrilha: 10,     // 4 linhas empilhadas
  sprocketPasso: 34,
} as const;

/** Brilho do elemento no canvas, a partir do valor da banda (0..1). */
export function brilho(v: number) {
  return {
    shadowBlur: 7 + v * 9,          // repouso 7px → reagindo 16px
    globalAlpha: 0.62 + v * 0.33,   // repouso 0.62 → reagindo 0.95
    escala: 1 + v * 0.35,
  };
}

export const MAX_ELEMENTOS = 120;
