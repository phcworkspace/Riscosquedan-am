// Riscos que Dançam — contratos de dados do motor.
// engine/ não importa nada de React: são só tipos e constantes puras.

export type Banda = 'grave' | 'medio' | 'agudo' | 'brilho';

/** Ordem canônica das quatro bandas — usada para iterar (UI, testes, etc). */
export const BANDAS: Banda[] = ['grave', 'medio', 'agudo', 'brilho'];

export interface Secao {
  inicio: number;
  fim: number;
  rotulo: string;
}

export interface MapaDaFaixa {
  arquivo: string;
  duracaoSeg: number;
  fps: number;
  quadros: number;
  bandas: Record<Banda, number[]>;
  faixasDeBanda: Record<Banda, [number, number]>;
  rms: number[];
  picos: number[];
  ataques: number[];
  secoes: Secao[];
  pulso: {
    bpmEstimado: number;
    contrasteDeAtaque: number;
    temPulsoClaro: boolean;
    batidas: number[];
    nota: string;
  };
}

export interface Faixa {
  id: string;
  titulo: string;
  caracter: string;
  arquivo: string;
  mapa: string;
  duracaoSeg: number;
  credito: { autor: string; licenca: string; url: string };
}

export interface Regiao {
  inicio: number;
  fim: number;
}
