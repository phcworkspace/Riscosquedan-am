import { afterEach, describe, expect, it, vi } from 'vitest';
import { Mapa } from './Mapa';
import type { MapaDaFaixa } from './tipos';

export const mapaFixture: MapaDaFaixa = {
  arquivo: 'fixture.mp3',
  duracaoSeg: 1,
  fps: 10,
  quadros: 10,
  bandas: {
    grave:  [0, 0.2, 0.4, 0.6, 0.8, 1.0, 0.8, 0.6, 0.4, 0.2],
    medio:  [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
    agudo:  [0, 0, 0, 0, 0, 1, 1, 1, 1, 1],
    brilho: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
  },
  faixasDeBanda: {
    grave: [20, 150], medio: [150, 700], agudo: [700, 3200], brilho: [3200, 11000],
  },
  rms: [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.4, 0.3, 0.2, 0.1],
  picos: [],
  ataques: [],
  secoes: [
    { inicio: 0, fim: 0.5, rotulo: 'A' },
    { inicio: 0.5, fim: 1, rotulo: 'B' },
  ],
  pulso: {
    bpmEstimado: 120,
    contrasteDeAtaque: 5,
    temPulsoClaro: true,
    batidas: [0.2, 0.5, 0.8],
    nota: 'fixture de teste',
  },
};

describe('Mapa.valor', () => {
  it('interpola linearmente entre dois quadros', () => {
    const mapa = Mapa.__criarParaTeste(mapaFixture);
    // t=0.05 -> q=0.5 -> entre grave[0]=0 e grave[1]=0.2, metade do caminho
    expect(mapa.valor('grave', 0.05)).toBeCloseTo(0.1, 5);
  });

  it('retorna o primeiro valor para t negativo', () => {
    const mapa = Mapa.__criarParaTeste(mapaFixture);
    expect(mapa.valor('grave', -1)).toBe(0);
  });

  it('trava no último valor além da duração', () => {
    const mapa = Mapa.__criarParaTeste(mapaFixture);
    expect(mapa.valor('grave', 5)).toBe(0.2);
  });

  it('banda sem variação (brilho) é sempre 0 nesta fixture', () => {
    const mapa = Mapa.__criarParaTeste(mapaFixture);
    expect(mapa.valor('brilho', 0.3)).toBe(0);
  });
});

describe('Mapa.energia', () => {
  it('interpola o rms como valor faz com as bandas', () => {
    const mapa = Mapa.__criarParaTeste(mapaFixture);
    expect(mapa.energia(0.05)).toBeCloseTo(0.05, 5);
  });
});

describe('Mapa.acumulado', () => {
  it('acumula a soma da banda até o quadro correspondente a t', () => {
    const mapa = Mapa.__criarParaTeste(mapaFixture);
    // medio = 0.1 constante; em t=0.1s (quadro 1) a soma dos quadros 0 e 1 é 0.2
    expect(mapa.acumulado('medio', 0.1)).toBeCloseTo(0.2, 5);
  });

  it('no fim da faixa, acumula a soma total da banda', () => {
    const mapa = Mapa.__criarParaTeste(mapaFixture);
    // medio = 0.1 x 10 quadros = 1.0
    expect(mapa.acumulado('medio', 1)).toBeCloseTo(1.0, 5);
  });

  it('em t=0, acumula só o primeiro quadro', () => {
    const mapa = Mapa.__criarParaTeste(mapaFixture);
    expect(mapa.acumulado('medio', 0)).toBeCloseTo(0.1, 5);
  });
});

describe('Mapa.secaoEm', () => {
  it('encontra a seção A no início', () => {
    const mapa = Mapa.__criarParaTeste(mapaFixture);
    expect(mapa.secaoEm(0)?.rotulo).toBe('A');
  });

  it('encontra a seção B logo após a fronteira', () => {
    const mapa = Mapa.__criarParaTeste(mapaFixture);
    expect(mapa.secaoEm(0.5)?.rotulo).toBe('B');
  });

  it('inclui o instante exato da duração na última seção', () => {
    const mapa = Mapa.__criarParaTeste(mapaFixture);
    expect(mapa.secaoEm(1)?.rotulo).toBe('B');
  });

  it('retorna null antes do início da faixa', () => {
    const mapa = Mapa.__criarParaTeste(mapaFixture);
    expect(mapa.secaoEm(-1)).toBeNull();
  });

  it('retorna null depois do fim da faixa', () => {
    const mapa = Mapa.__criarParaTeste(mapaFixture);
    expect(mapa.secaoEm(2)).toBeNull();
  });
});

describe('Mapa.encaixe', () => {
  it('encaixa na batida mais próxima quando há pulso claro', () => {
    const mapa = Mapa.__criarParaTeste(mapaFixture);
    expect(mapa.encaixe(0.44)).toBeCloseTo(0.5, 5);
  });

  it('retorna null fora da tolerância', () => {
    const mapa = Mapa.__criarParaTeste(mapaFixture);
    expect(mapa.encaixe(1.0)).toBeNull(); // batida mais próxima é 0.8, dist 0.2
  });

  it('usa fronteiras de seção quando não há pulso claro', () => {
    const semPulso = {
      ...mapaFixture,
      pulso: { ...mapaFixture.pulso, temPulsoClaro: false },
    };
    const mapa = Mapa.__criarParaTeste(semPulso);
    // fronteiras: 0, 0.5, 0.5, 1 — mais próxima de 0.44 é 0.5
    expect(mapa.encaixe(0.44)).toBeCloseTo(0.5, 5);
  });

  it('respeita uma tolerância customizada', () => {
    const mapa = Mapa.__criarParaTeste(mapaFixture);
    expect(mapa.encaixe(0.44, 0.03)).toBeNull(); // dist real é 0.06
  });
});

describe('Mapa.carregar', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('busca e faz parse do JSON', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mapaFixture),
    }));

    const mapa = await Mapa.carregar('/audio/fixture.map.json');
    expect(mapa.dados.arquivo).toBe('fixture.mp3');
    expect(mapa.valor('grave', 0.05)).toBeCloseTo(0.1, 5);
  });

  it('lança erro quando a resposta não é ok', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: false, status: 404 }));
    await expect(Mapa.carregar('/audio/inexistente.map.json')).rejects.toThrow('404');
  });
});
