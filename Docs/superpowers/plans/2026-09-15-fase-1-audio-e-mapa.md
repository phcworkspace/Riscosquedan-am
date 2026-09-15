# Fase 1 — Motor de Áudio e Mapa — Plano de Implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Provar que o motor consegue tocar uma faixa, fazer loop de uma região arbitrária, reportar a posição exata do áudio, e consultar as quatro curvas de banda (grave/médio/agudo/brilho) naquele instante — sem interface real, apenas uma página de teste que expõe os números e quatro barras.

**Architecture:** Duas classes TypeScript puras (`Mapa`, `Audio`) em `src/engine/`, zero React, seguindo exatamente os contratos de `Docs/SPEC-fase-1.md`. `Mapa` é 100% testável por unidade (interpolação sobre arrays). `Audio` envolve `AudioContext`/`AudioBufferSourceNode` (APIs de navegador, indisponíveis em Node/Vitest); sua matemática de posição é extraída para uma função pura testável (`posicaoNaRegiao`), e o restante é verificado manualmente pelos 6 testes de aceite que a própria SPEC já define (T1–T6) na página `/teste`.

**Tech Stack:** Next.js 16 (App Router) · React 19 · TypeScript · Web Audio API pura · Vitest (novo, só para `engine/`) · pnpm.

---

## Notas de arquitetura (leia antes de começar)

1. **Por que Vitest.** O projeto não tem test runner. `engine/Mapa.ts` é lógica pura (interpolação sobre arrays) — testável sem navegador, sem mocks pesados. Adicionar Vitest é a única forma de aplicar TDD de verdade aqui, e não conflita com nenhuma proibição do `AGENTS.md` (que veta bibliotecas de **áudio**, não de teste). Escopo: só `engine/`, não testamos componentes React nesta fase.

2. **Por que `Audio.ts` não tem teste automatizado de classe.** `AudioContext` e `AudioBufferSourceNode` não existem em Node; simulá-los员 esconderia exatamente o comportamento que importa verificar (timing real, autoplay policy). A própria SPEC já resolveu isso com os testes de aceite T1–T6, manuais, ouvindo o áudio de verdade. O que **é** extraído e testado por unidade é a parte matemática pura e traiçoeira: o cálculo de posição dentro de uma região de loop (função `posicaoNaRegiao`).

3. **Renomeação em `tokens.ts`:** o array `BANDAS` de `tokens.ts` (objetos ricos com `nome`/`cor`/`hz`, para UI futura) colide de nome com o `BANDAS: Banda[]` simples que `Docs/SPEC-fase-1.md` pede em `engine/tipos.ts` (a ordem canônica das bandas, usada para iterar). Como nada ainda importa `tokens.ts::BANDAS` (confirmado por busca no código), ele é renomeado para `BANDAS_INFO` antes que a colisão vire um bug de import silencioso em fases futuras.

4. **`secaoEm` no limite exato da duração.** Quando `t === duracaoSeg` (final exato da faixa), a regra ingênua `t < secao.fim` deixaria a última seção sem cobrir esse ponto. A implementação trata a última seção como fechada nos dois extremos (`t <= fim`).

---

## Estrutura de arquivos

```
src/engine/
  tipos.ts          NOVO — contratos: Banda, BANDAS, Secao, MapaDaFaixa, Faixa, Regiao
  tokens.ts         MODIFICADO — importa Banda de tipos.ts; BANDAS → BANDAS_INFO
  Mapa.ts           NOVO — classe Mapa (testada por unidade)
  Mapa.test.ts      NOVO
  Audio.ts          NOVO — classe Audio + função pura posicaoNaRegiao (só ela é testada)
  Audio.test.ts     NOVO
src/app/
  layout.tsx        MODIFICADO — metadata (título/descrição do projeto, nada visual)
  page.tsx          MODIFICADO — remove boilerplate do create-next-app
  teste/page.tsx    NOVO — bancada de teste da Fase 1
vitest.config.ts    NOVO
package.json        MODIFICADO — +devDependency vitest, +scripts test/test:watch
Docs/
  09-fase-1-implementacao.md   NOVO — documentação acadêmica do que foi implementado
```

---

## Task 0: Ambiente de testes (Vitest)

**Files:**
- Modify: `package.json`
- Create: `vitest.config.ts`

- [ ] **Step 1: Instalar o Vitest como devDependency**

```bash
pnpm add -D vitest
```

- [ ] **Step 2: Criar `vitest.config.ts`**

```ts
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    environment: 'node', // engine/ é TypeScript puro, sem DOM
    include: ['src/**/*.test.ts'],
  },
});
```

- [ ] **Step 3: Adicionar scripts em `package.json`**

No bloco `"scripts"`, acrescentar:

```json
"test": "vitest run",
"test:watch": "vitest"
```

- [ ] **Step 4: Verificar que o runner sobe (sem testes ainda)**

Run: `pnpm test`
Expected: `No test files found` (ou similar) — sem erro de configuração.

- [ ] **Step 5: Commit**

```bash
git add package.json pnpm-lock.yaml vitest.config.ts
git commit -m "chore: adiciona Vitest para testar engine/ por unidade"
```

---

## Task 1: `engine/tipos.ts` — contratos de dados

**Files:**
- Create: `src/engine/tipos.ts`

- [ ] **Step 1: Escrever o arquivo**

```ts
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
```

> Nota: `Faixa` aqui inclui `caracter` porque é o formato real de `public/audio/faixas.json`
> (conferido nos dados existentes) e já está em `Docs/SPEC-fase-1.md` seção 3. É
> `02-PRD-arquitetura-tecnica.md` seção 4 que omite o campo, por ter sido escrito antes
> das faixas finais existirem.

- [ ] **Step 2: Verificar que compila**

Run: `pnpm exec tsc --noEmit`
Expected: sem erros relacionados a `tipos.ts`.

- [ ] **Step 3: Commit**

```bash
git add src/engine/tipos.ts
git commit -m "feat(engine): contratos de dados (tipos.ts)"
```

---

## Task 2: `tokens.ts` — remover colisão de nome com `BANDAS`

**Files:**
- Modify: `src/engine/tokens.ts`

- [ ] **Step 1: Importar `Banda` de `tipos.ts` e renomear o array rico**

Substituir:

```ts
export type Banda = 'grave' | 'medio' | 'agudo' | 'brilho';

export const BANDAS = [
  { id: 'grave',  nome: 'Grave',  cor: '#FF3B30', hz: [20, 150] },
  { id: 'medio',  nome: 'Médio',  cor: '#FFB300', hz: [150, 700] },
  { id: 'agudo',  nome: 'Agudo',  cor: '#0A84FF', hz: [700, 3200] },
  { id: 'brilho', nome: 'Brilho', cor: '#5AC8FA', hz: [3200, 11000] },
] as const satisfies ReadonlyArray<{
  id: Banda; nome: string; cor: string; hz: readonly [number, number];
}>;
```

por:

```ts
import type { Banda } from './tipos';

/**
 * Metadados de UI por banda (nome exibido, cor, faixa de Hz).
 * Não confundir com `BANDAS` de `./tipos` — aquele é só a ordem canônica
 * (Banda[]) usada para iterar; este é o objeto rico para o painel e a legenda.
 */
export const BANDAS_INFO = [
  { id: 'grave',  nome: 'Grave',  cor: '#FF3B30', hz: [20, 150] },
  { id: 'medio',  nome: 'Médio',  cor: '#FFB300', hz: [150, 700] },
  { id: 'agudo',  nome: 'Agudo',  cor: '#0A84FF', hz: [700, 3200] },
  { id: 'brilho', nome: 'Brilho', cor: '#5AC8FA', hz: [3200, 11000] },
] as const satisfies ReadonlyArray<{
  id: Banda; nome: string; cor: string; hz: readonly [number, number];
}>;
```

O restante do arquivo (`CORES_BANDA`, `PALETA`, `PALCO`, `MEDIDAS`, `brilho()`, `MAX_ELEMENTOS`) fica igual.

- [ ] **Step 2: Verificar que compila (nada mais referencia o nome antigo)**

Run: `pnpm exec tsc --noEmit`
Expected: sem erros.

- [ ] **Step 3: Commit**

```bash
git add src/engine/tokens.ts
git commit -m "refactor(engine): tokens.ts usa Banda de tipos.ts; BANDAS -> BANDAS_INFO"
```

---

## Task 3: `engine/Mapa.ts` — `valor()` e `energia()`

**Files:**
- Create: `src/engine/Mapa.ts`
- Create: `src/engine/Mapa.test.ts`

- [ ] **Step 1: Escrever a fixture e os testes de `valor`/`energia`**

```ts
// src/engine/Mapa.test.ts
import { describe, expect, it } from 'vitest';
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
    const mapa = new (Mapa as any)(mapaFixture); // ver Step 2 sobre o construtor
    // t=0.05 -> q=0.5 -> entre grave[0]=0 e grave[1]=0.2, metade do caminho
    expect(mapa.valor('grave', 0.05)).toBeCloseTo(0.1, 5);
  });

  it('retorna o primeiro valor para t negativo', () => {
    const mapa = new (Mapa as any)(mapaFixture);
    expect(mapa.valor('grave', -1)).toBe(0);
  });

  it('trava no último valor além da duração', () => {
    const mapa = new (Mapa as any)(mapaFixture);
    expect(mapa.valor('grave', 5)).toBe(0.2);
  });

  it('banda sem variação (brilho) é sempre 0 nesta fixture', () => {
    const mapa = new (Mapa as any)(mapaFixture);
    expect(mapa.valor('brilho', 0.3)).toBe(0);
  });
});

describe('Mapa.energia', () => {
  it('interpola o rms como valor faz com as bandas', () => {
    const mapa = new (Mapa as any)(mapaFixture);
    expect(mapa.energia(0.05)).toBeCloseTo(0.05, 5);
  });
});
```

> `new (Mapa as any)(...)` é temporário só para destravar o TDD com o construtor
> privado da SPEC; o Step 3 troca por um factory de teste exportado — sem isso o
> arquivo de teste não compila antes da classe existir.

- [ ] **Step 2: Rodar e confirmar que falha por módulo inexistente**

Run: `pnpm test`
Expected: FAIL — `Cannot find module './Mapa'`

- [ ] **Step 3: Implementar `Mapa` com `valor()` e `energia()`**

```ts
// src/engine/Mapa.ts
import { BANDAS, type Banda, type MapaDaFaixa, type Secao } from './tipos';

function interpolar(curva: number[] | Float64Array, fps: number, t: number): number {
  if (!curva?.length) return 0;
  const q = t * fps;
  const i = Math.floor(q);
  if (i < 0) return curva[0];
  if (i >= curva.length - 1) return curva[curva.length - 1];
  return curva[i] + (curva[i + 1] - curva[i]) * (q - i);
}

export class Mapa {
  readonly dados: MapaDaFaixa;
  private acumuladas: Record<Banda, Float64Array>;

  private constructor(dados: MapaDaFaixa) {
    this.dados = dados;
    this.acumuladas = this.calcularAcumuladas(dados);
  }

  /** Só para teste — expõe o construtor privado sem abrir mão dele em produção. */
  static __criarParaTeste(dados: MapaDaFaixa): Mapa {
    return new Mapa(dados);
  }

  static async carregar(url: string): Promise<Mapa> {
    const resposta = await fetch(url);
    if (!resposta.ok) {
      throw new Error(`Falha ao carregar o mapa em ${url}: ${resposta.status}`);
    }
    const dados = (await resposta.json()) as MapaDaFaixa;
    return new Mapa(dados);
  }

  private calcularAcumuladas(dados: MapaDaFaixa): Record<Banda, Float64Array> {
    const resultado = {} as Record<Banda, Float64Array>;
    for (const banda of BANDAS) {
      const curva = dados.bandas[banda] ?? [];
      const soma = new Float64Array(curva.length);
      let acc = 0;
      for (let i = 0; i < curva.length; i++) {
        acc += curva[i];
        soma[i] = acc;
      }
      resultado[banda] = soma;
    }
    return resultado;
  }

  valor(banda: Banda, t: number): number {
    return interpolar(this.dados.bandas[banda], this.dados.fps, t);
  }

  energia(t: number): number {
    return interpolar(this.dados.rms, this.dados.fps, t);
  }

  acumulado(banda: Banda, t: number): number {
    return interpolar(this.acumuladas[banda], this.dados.fps, t);
  }

  secaoEm(t: number): Secao | null {
    const secoes = this.dados.secoes;
    for (let i = 0; i < secoes.length; i++) {
      const s = secoes[i];
      const ehUltima = i === secoes.length - 1;
      if (t >= s.inicio && (ehUltima ? t <= s.fim : t < s.fim)) return s;
    }
    return null;
  }

  encaixe(t: number, tolerancia = 0.12): number | null {
    const candidatos = this.dados.pulso.temPulsoClaro
      ? this.dados.pulso.batidas
      : this.dados.secoes.flatMap(s => [s.inicio, s.fim]);

    let melhor: number | null = null;
    let menorDist = Infinity;
    for (const c of candidatos) {
      const dist = Math.abs(c - t);
      if (dist < menorDist) { menorDist = dist; melhor = c; }
    }
    return melhor !== null && menorDist <= tolerancia ? melhor : null;
  }
}
```

Trocar, no teste, `new (Mapa as any)(mapaFixture)` por `Mapa.__criarParaTeste(mapaFixture)` em todos os pontos.

- [ ] **Step 4: Rodar e confirmar que passa**

Run: `pnpm test`
Expected: PASS — 5 testes verdes.

- [ ] **Step 5: Commit**

```bash
git add src/engine/Mapa.ts src/engine/Mapa.test.ts
git commit -m "feat(engine): Mapa.valor e Mapa.energia com interpolação linear"
```

---

## Task 4: `Mapa.acumulado()`

**Files:**
- Modify: `src/engine/Mapa.test.ts`

- [ ] **Step 1: Escrever os testes**

```ts
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
```

(`Mapa` já está implementado desde a Task 3 — `acumulado()` já existe. Este passo é o teste que faltava para ele.)

- [ ] **Step 2: Rodar — já deve passar, sem tocar em `Mapa.ts`**

Run: `pnpm test`
Expected: PASS. Se falhar, o bug está em `calcularAcumuladas` — não em `interpolar` (já coberta na Task 3).

- [ ] **Step 3: Commit**

```bash
git add src/engine/Mapa.test.ts
git commit -m "test(engine): cobre Mapa.acumulado"
```

---

## Task 5: `Mapa.secaoEm()` — incluindo o limite exato da duração

**Files:**
- Modify: `src/engine/Mapa.test.ts`

- [ ] **Step 1: Escrever os testes**

```ts
describe('Mapa.secaoEm', () => {
  const mapa = Mapa.__criarParaTeste(mapaFixture);

  it('encontra a seção A no início', () => {
    expect(mapa.secaoEm(0)?.rotulo).toBe('A');
  });

  it('encontra a seção B logo após a fronteira', () => {
    expect(mapa.secaoEm(0.5)?.rotulo).toBe('B');
  });

  it('inclui o instante exato da duração na última seção', () => {
    expect(mapa.secaoEm(1)?.rotulo).toBe('B');
  });

  it('retorna null antes do início da faixa', () => {
    expect(mapa.secaoEm(-1)).toBeNull();
  });

  it('retorna null depois do fim da faixa', () => {
    expect(mapa.secaoEm(2)).toBeNull();
  });
});
```

- [ ] **Step 2: Rodar**

Run: `pnpm test`
Expected: PASS (implementação já cobre o caso da última seção — Task 3, Step 3).

- [ ] **Step 3: Commit**

```bash
git add src/engine/Mapa.test.ts
git commit -m "test(engine): cobre Mapa.secaoEm, incluindo o limite exato da duração"
```

---

## Task 6: `Mapa.encaixe()`

**Files:**
- Modify: `src/engine/Mapa.test.ts`

- [ ] **Step 1: Escrever os testes (pulso claro e sem pulso claro)**

```ts
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
```

- [ ] **Step 2: Rodar**

Run: `pnpm test`
Expected: PASS.

- [ ] **Step 3: Commit**

```bash
git add src/engine/Mapa.test.ts
git commit -m "test(engine): cobre Mapa.encaixe (com e sem pulso claro)"
```

---

## Task 7: `Mapa.carregar()` com `fetch` mockado

**Files:**
- Modify: `src/engine/Mapa.test.ts`

- [ ] **Step 1: Escrever os testes**

```ts
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
```

Adicionar ao topo do arquivo: `import { afterEach, describe, expect, it, vi } from 'vitest';` (substituindo o import anterior de `describe, expect, it`).

- [ ] **Step 2: Rodar**

Run: `pnpm test`
Expected: PASS — 19 testes verdes no total em `Mapa.test.ts` (5 de valor/energia + 3 de
acumulado + 5 de secaoEm + 4 de encaixe + 2 de carregar).

- [ ] **Step 3: Commit**

```bash
git add src/engine/Mapa.test.ts
git commit -m "test(engine): cobre Mapa.carregar com fetch mockado"
```

---

## Task 8: função pura `posicaoNaRegiao` (a parte testável de `Audio.ts`)

**Files:**
- Create: `src/engine/Audio.ts` (só a função pura por enquanto)
- Create: `src/engine/Audio.test.ts`

- [ ] **Step 1: Escrever os testes**

```ts
// src/engine/Audio.test.ts
import { describe, expect, it } from 'vitest';
import { posicaoNaRegiao } from './Audio';

describe('posicaoNaRegiao', () => {
  it('no início do loop, decorrido=0, retorna o próprio início do offset', () => {
    expect(posicaoNaRegiao(10, 10, 18, 0)).toBe(10);
  });

  it('avança normalmente dentro da janela', () => {
    expect(posicaoNaRegiao(10, 10, 18, 5)).toBe(15);
  });

  it('dá a volta exatamente no fim da janela (8s de região)', () => {
    expect(posicaoNaRegiao(10, 10, 18, 8)).toBeCloseTo(10, 10);
  });

  it('dá a volta e continua depois do wrap', () => {
    expect(posicaoNaRegiao(10, 10, 18, 8.5)).toBeCloseTo(10.5, 10);
  });

  it('funciona quando o offset inicial não é o início da região', () => {
    // offset=12, região [10,18] (janela 8), decorrido=20 -> 12-10+20=22; 22 % 8 = 6
    expect(posicaoNaRegiao(12, 10, 18, 20)).toBeCloseTo(16, 10);
  });

  it('janela inválida (fim <= início) retorna o início, defensivamente', () => {
    expect(posicaoNaRegiao(5, 10, 10, 3)).toBe(10);
  });
});
```

- [ ] **Step 2: Rodar e confirmar que falha (módulo/exportação inexistente)**

Run: `pnpm test`
Expected: FAIL — `Cannot find module './Audio'` (ele ainda não existe).

- [ ] **Step 3: Criar `Audio.ts` só com a função pura**

```ts
// src/engine/Audio.ts
// A classe Audio (Web Audio real) vem na Task 9. Esta função vem primeiro e
// sozinha porque é a única parte de Audio.ts testável fora do navegador —
// ver "Notas de arquitetura" no topo do plano.

/**
 * Posição dentro de uma região de loop, dado o offset onde a reprodução atual
 * começou e o tempo decorrido desde então. Pura: não depende de AudioContext,
 * por isso é a peça de Audio.ts coberta por teste de unidade.
 */
export function posicaoNaRegiao(
  offset: number,
  inicio: number,
  fim: number,
  decorrido: number,
): number {
  const janela = fim - inicio;
  if (janela <= 0) return inicio;
  const bruta = offset - inicio + decorrido;
  const dentro = ((bruta % janela) + janela) % janela; // evita módulo negativo
  return inicio + dentro;
}
```

- [ ] **Step 4: Rodar e confirmar que passa**

Run: `pnpm test`
Expected: PASS — 6 testes verdes em `Audio.test.ts`.

- [ ] **Step 5: Commit**

```bash
git add src/engine/Audio.ts src/engine/Audio.test.ts
git commit -m "feat(engine): posicaoNaRegiao — matemática pura do loop, testada"
```

---

## Task 9: classe `Audio` completa (Web Audio real)

**Files:**
- Modify: `src/engine/Audio.ts`

Sem testes automatizados nesta etapa (ver "Notas de arquitetura", item 2). A verificação é manual, na Task 12.

- [ ] **Step 1: Acrescentar a classe abaixo de `posicaoNaRegiao`, no mesmo arquivo**

```ts
import type { Regiao } from './tipos';

export type EstadoAudio = 'vazio' | 'carregando' | 'pronto' | 'tocando';

export class Audio {
  private ctx: AudioContext;
  private ganho: GainNode;
  private buffer: AudioBuffer | null = null;
  private src: AudioBufferSourceNode | null = null;
  private reg: Regiao | null = null;
  private estadoAtual: EstadoAudio = 'vazio';

  private offset = 0;      // posição do buffer onde a reprodução atual começou
  private iniciadoEm = 0;  // ctx.currentTime em que a reprodução atual começou
  private pausadoEm = 0;   // posição guardada ao pausar/parar

  private constructor(ctx: AudioContext) {
    this.ctx = ctx;
    this.ganho = ctx.createGain();
    this.ganho.connect(ctx.destination);
  }

  /** Precisa ser chamado dentro de um gesto do usuário (política de autoplay). */
  static async iniciar(): Promise<Audio> {
    const ctx = new AudioContext();
    if (ctx.state === 'suspended') await ctx.resume();
    return new Audio(ctx);
  }

  get estado(): EstadoAudio { return this.estadoAtual; }
  get duracao(): number { return this.buffer?.duration ?? 0; }
  get regiao(): Regiao | null { return this.reg; }
  get tocando(): boolean { return this.estadoAtual === 'tocando'; }

  async carregar(url: string): Promise<void> {
    this.pararSource();
    this.estadoAtual = 'carregando';
    this.buffer = null;
    this.reg = null;
    this.offset = 0;
    this.pausadoEm = 0;

    try {
      const resposta = await fetch(url);
      if (!resposta.ok) throw new Error(`Falha ao carregar ${url}: ${resposta.status}`);
      const arrayBuffer = await resposta.arrayBuffer();
      this.buffer = await this.ctx.decodeAudioData(arrayBuffer);
      this.estadoAtual = 'pronto';
    } catch (erro) {
      this.estadoAtual = 'vazio'; // sem isto, uma falha trava para sempre em 'carregando'
      throw erro;
    }
  }

  private pararSource(): void {
    this.src?.stop();
    this.src?.disconnect();
    this.src = null;
  }

  /** AudioBufferSourceNode é descartável: toda mudança recria o node (SPEC seção 5). */
  private criarSource(de: number): void {
    if (!this.buffer) return;
    this.pararSource();

    const src = this.ctx.createBufferSource();
    src.buffer = this.buffer;
    if (this.reg) {
      src.loop = true;
      src.loopStart = this.reg.inicio;
      src.loopEnd = this.reg.fim;
    }
    src.connect(this.ganho);
    src.start(0, de);
    if (!src.loop) {
      // sem loop, o node termina sozinho ao fim do buffer — sem isto o estado
      // fica travado em 'tocando' mesmo com o som já parado (SPEC não cobre
      // este caso, mas afeta o que a bancada de teste mostra).
      src.onended = () => {
        if (this.src === src) {
          this.pausadoEm = this.duracao;
          this.estadoAtual = 'pronto';
        }
      };
    }

    this.src = src;
    this.offset = de;
    this.iniciadoEm = this.ctx.currentTime;
    this.estadoAtual = 'tocando';
  }

  tocar(de?: number): void {
    if (!this.buffer) return;
    this.criarSource(de ?? this.pausadoEm);
  }

  pausar(): void {
    if (!this.tocando) return;
    this.pausadoEm = this.posicao();
    this.pararSource();
    this.estadoAtual = 'pronto';
  }

  /** Pausa e volta ao início da região (ou a 0). */
  parar(): void {
    this.pararSource();
    this.pausadoEm = this.reg?.inicio ?? 0;
    this.estadoAtual = this.buffer ? 'pronto' : 'vazio';
  }

  definirRegiao(r: Regiao | null): void {
    const posAtual = this.posicao();
    this.reg = r;

    if (!this.tocando) {
      if (r && (posAtual < r.inicio || posAtual >= r.fim)) this.pausadoEm = r.inicio;
      return;
    }

    // Tocando: fora da nova região, recomeça no início dela;
    // dentro, recria o node na posição atual (SPEC seção 5, regra 5).
    const foraDaRegiao = r && (posAtual < r.inicio || posAtual >= r.fim);
    this.criarSource(foraDaRegiao ? r.inicio : posAtual);
  }

  buscar(t: number): void {
    const alvo = Math.min(Math.max(t, 0), this.duracao || t);
    if (this.tocando) this.criarSource(alvo);
    else this.pausadoEm = alvo;
  }

  volume(v: number): void {
    this.ganho.gain.value = Math.min(Math.max(v, 0), 1);
  }

  /** Sempre calculada de ctx.currentTime — nunca acumulada (SPEC seção 5, regra 3). */
  posicao(): number {
    if (!this.tocando) return this.pausadoEm;
    const decorrido = this.ctx.currentTime - this.iniciadoEm;
    if (!this.reg) return Math.min(this.offset + decorrido, this.duracao);
    return posicaoNaRegiao(this.offset, this.reg.inicio, this.reg.fim, decorrido);
  }

  destruir(): void {
    this.pararSource();
    this.ganho.disconnect();
    void this.ctx.close();
    this.estadoAtual = 'vazio';
  }
}
```

- [ ] **Step 2: Verificar que compila**

Run: `pnpm exec tsc --noEmit`
Expected: sem erros. (`AudioContext`, `GainNode`, `AudioBufferSourceNode`, `AudioBuffer` vêm do `lib: ["dom", ...]` do `tsconfig.json`, já presente.)

- [ ] **Step 3: Rodar os testes existentes — não podem quebrar**

Run: `pnpm test`
Expected: PASS — os 6 testes de `posicaoNaRegiao` continuam verdes.

- [ ] **Step 4: Commit**

```bash
git add src/engine/Audio.ts
git commit -m "feat(engine): classe Audio (Web Audio puro) — carregar, tocar, loop de região, posicao"
```

---

## Task 10: limpar o boilerplate do `create-next-app`

**Files:**
- Modify: `src/app/layout.tsx`
- Modify: `src/app/page.tsx`

- [ ] **Step 1: Ajustar só a metadata em `layout.tsx`** (nada visual — proibido nesta fase)

Trocar:

```ts
export const metadata: Metadata = {
  title: "Create Next App",
  description: "Generated by create next app",
};
```

por:

```ts
export const metadata: Metadata = {
  title: "Riscos que Dançam",
  description: "Protótipo de mestrado — escute uma faixa e desenhe o que percebe.",
};
```

- [ ] **Step 2: Substituir `page.tsx`** pelo placeholder mínimo (sem cores, sem design — isso é Fase 5)

```tsx
export default function Home() {
  return (
    <main style={{ padding: 24, fontFamily: 'monospace' }}>
      <h1>Riscos que Dançam</h1>
      <p>
        Fase 1 em andamento. Bancada de teste do motor de áudio:{' '}
        <a href="/teste">/teste</a>
      </p>
    </main>
  );
}
```

- [ ] **Step 3: Verificar visualmente**

Run: `pnpm dev`, abrir `http://localhost:3000/`
Expected: título da aba "Riscos que Dançam"; página mostra o texto acima e o link para `/teste` (que ainda dá 404 — normal, vem na próxima task).

- [ ] **Step 4: Commit**

```bash
git add src/app/layout.tsx src/app/page.tsx
git commit -m "chore: remove boilerplate do create-next-app da raiz"
```

---

## Task 11: `app/teste/page.tsx` — a bancada de teste da Fase 1

**Files:**
- Create: `src/app/teste/page.tsx`

- [ ] **Step 1: Escrever a página**

```tsx
'use client';

import { useEffect, useRef, useState } from 'react';
import { Audio, type EstadoAudio } from '@/engine/Audio';
import { Mapa } from '@/engine/Mapa';
import { BANDAS, type Banda, type Faixa } from '@/engine/tipos';
import { CORES_BANDA } from '@/engine/tokens';

type ValoresBanda = Record<Banda, number>;
const ZERADO: ValoresBanda = { grave: 0, medio: 0, agudo: 0, brilho: 0 };

export default function PaginaDeTeste() {
  const audioRef = useRef<Audio | null>(null);
  const mapaRef = useRef<Mapa | null>(null);
  const rafRef = useRef<number | null>(null);

  const [iniciado, setIniciado] = useState(false);
  const [faixas, setFaixas] = useState<Faixa[]>([]);
  const [faixaId, setFaixaId] = useState('');
  const [estado, setEstado] = useState<EstadoAudio>('vazio');
  const [posicao, setPosicao] = useState(0);
  const [valores, setValores] = useState<ValoresBanda>(ZERADO);
  const [secaoAtual, setSecaoAtual] = useState('—');

  const [regiaoInicio, setRegiaoInicio] = useState('');
  const [regiaoFim, setRegiaoFim] = useState('');
  const [seekAlvo, setSeekAlvo] = useState('');
  const [volumeValor, setVolumeValor] = useState(0.8);

  useEffect(() => {
    fetch('/audio/faixas.json')
      .then(r => r.json())
      .then((lista: Faixa[]) => setFaixas(lista));
  }, []);

  useEffect(() => {
    // Fast Refresh remonta em dev; sem isto, contextos de áudio se acumulam
    // e o som dobra (SPEC seção 8, armadilhas conhecidas).
    return () => {
      if (rafRef.current !== null) cancelAnimationFrame(rafRef.current);
      audioRef.current?.destruir();
    };
  }, []);

  function loopDeQuadro() {
    const audio = audioRef.current;
    const mapa = mapaRef.current;
    if (audio) setEstado(audio.estado);
    if (audio && mapa) {
      const t = audio.posicao();
      setPosicao(t);
      setValores({
        grave: mapa.valor('grave', t),
        medio: mapa.valor('medio', t),
        agudo: mapa.valor('agudo', t),
        brilho: mapa.valor('brilho', t),
      });
      setSecaoAtual(mapa.secaoEm(t)?.rotulo ?? '—');
    }
    rafRef.current = requestAnimationFrame(loopDeQuadro);
  }

  async function comecar() {
    if (audioRef.current) return;
    audioRef.current = await Audio.iniciar();
    setIniciado(true);
    rafRef.current = requestAnimationFrame(loopDeQuadro);
  }

  async function escolherFaixa(id: string) {
    const audio = audioRef.current;
    const faixa = faixas.find(f => f.id === id);
    if (!audio || !faixa) return;
    setFaixaId(id);
    const [, mapa] = await Promise.all([
      audio.carregar(faixa.arquivo),
      Mapa.carregar(faixa.mapa),
    ]);
    mapaRef.current = mapa;
  }

  function definirRegiao() {
    const inicio = Number(regiaoInicio);
    const fim = Number(regiaoFim);
    if (Number.isFinite(inicio) && Number.isFinite(fim) && fim > inicio) {
      audioRef.current?.definirRegiao({ inicio, fim });
    }
  }

  function irPara() {
    const alvo = Number(seekAlvo);
    if (Number.isFinite(alvo)) audioRef.current?.buscar(alvo);
  }

  function mudarVolume(v: number) {
    setVolumeValor(v);
    audioRef.current?.volume(v);
  }

  return (
    <main style={{ padding: 24, fontFamily: 'monospace', color: '#eee', background: '#111', minHeight: '100vh' }}>
      <h1>Fase 1 — bancada de teste (áudio e mapa)</h1>
      <p style={{ opacity: 0.6, fontSize: 12 }}>Feia de propósito — o design entra na Fase 5.</p>

      {!iniciado && <button onClick={comecar}>Começar</button>}

      {iniciado && (
        <>
          <section style={{ marginTop: 16 }}>
            <label>
              Faixa:{' '}
              <select value={faixaId} onChange={e => escolherFaixa(e.target.value)}>
                <option value="">— escolher —</option>
                {faixas.map(f => <option key={f.id} value={f.id}>{f.titulo}</option>)}
              </select>
            </label>
            <span style={{ marginLeft: 12 }}>estado: {estado}</span>
          </section>

          <section style={{ marginTop: 16, display: 'flex', gap: 8, alignItems: 'center' }}>
            <button onClick={() => audioRef.current?.tocar()}>Play</button>
            <button onClick={() => audioRef.current?.pausar()}>Pausar</button>
            <button onClick={() => audioRef.current?.parar()}>Parar</button>
            <label>
              Volume{' '}
              <input type="range" min={0} max={1} step={0.01} value={volumeValor}
                     onChange={e => mudarVolume(Number(e.target.value))} />
            </label>
          </section>

          <section style={{ marginTop: 16, display: 'flex', gap: 8, alignItems: 'center' }}>
            <label>Início <input style={{ width: 60 }} value={regiaoInicio}
                                  onChange={e => setRegiaoInicio(e.target.value)} /></label>
            <label>Fim <input style={{ width: 60 }} value={regiaoFim}
                               onChange={e => setRegiaoFim(e.target.value)} /></label>
            <button onClick={definirRegiao}>Definir região</button>
            <button onClick={() => audioRef.current?.definirRegiao(null)}>Limpar região</button>
          </section>

          <section style={{ marginTop: 16, display: 'flex', gap: 8, alignItems: 'center' }}>
            <label>Ir para (s) <input style={{ width: 60 }} value={seekAlvo}
                                       onChange={e => setSeekAlvo(e.target.value)} /></label>
            <button onClick={irPara}>Ir para</button>
          </section>

          <section style={{ marginTop: 24 }}>
            <div>posição: {posicao.toFixed(3)}s · seção: {secaoAtual}</div>
            <div style={{ marginTop: 8, display: 'flex', flexDirection: 'column', gap: 4 }}>
              {BANDAS.map(b => (
                <div key={b} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span style={{ width: 70, fontSize: 12 }}>{b}</span>
                  <div style={{ width: 300, height: 14, background: '#222' }}>
                    <div style={{
                      width: `${valores[b] * 100}%`, height: '100%',
                      background: CORES_BANDA[b], transition: 'none',
                    }} />
                  </div>
                  <span style={{ fontVariantNumeric: 'tabular-nums', fontSize: 12 }}>
                    {valores[b].toFixed(3)}
                  </span>
                </div>
              ))}
            </div>
          </section>
        </>
      )}
    </main>
  );
}
```

- [ ] **Step 2: Verificar que compila e sobe**

Run: `pnpm exec tsc --noEmit && pnpm dev`
Expected: sem erros de tipo; `http://localhost:3000/teste` carrega, mostra "Começar".

- [ ] **Step 3: Commit**

```bash
git add src/app/teste/page.tsx
git commit -m "feat: bancada de teste da Fase 1 (/teste)"
```

---

## Task 12: Verificação manual — os 6 testes de aceite (T1–T6)

Não há automação possível aqui (áudio real, ouvido por uma pessoa). Seguir
`Docs/SPEC-fase-1.md` seção 7 à risca, com `pnpm dev` rodando e `http://localhost:3000/teste`
aberto.

- [ ] **T1 — o áudio toca:** escolher cada uma das 3 faixas, dar play, ouvir.
- [ ] **T2 — a posição bate com o som:** tocar "Pulso", conferir `posicao()` contra o
      trecho ouvido; deixar rodando 5 minutos e conferir de novo (deriva = bug de
      acumulação).
- [ ] **T3 — loop de região:** região 10→18s: deve repetir indefinidamente;
      `posicao()` salta de ~18 para ~10.
- [ ] **T4 — trocar a região em execução:** com o loop rodando, mudar para 30→36s.
      Sem estalo, sem silêncio, sem posição errada.
- [ ] **T5 — as bandas batem com o que se ouve:** grave salta com o bumbo em "Pulso";
      em "Névoa", grave e brilho se movem de forma visivelmente diferente.
- [ ] **T6 — seek para trás:** ir para 50s, depois voltar para 5s; áudio e barras
      acompanham, nada trava.
- [ ] **Determinismo:** anotar os 4 valores em `t=20.000`, tocar até o fim, voltar
      para 20.000, conferir que são idênticos.

- [ ] **Step final: registrar o resultado** (usado na Task 14, documentação)

Anotar PASS/FAIL de cada teste e qualquer observação — vai literalmente para a
tabela de `Docs/09-fase-1-implementacao.md`.

---

## Task 13: tag de git + push

**Files:** nenhum (operação de repositório)

- [ ] **Step 1: Confirmar que a árvore de trabalho está limpa**

Run: `git status --short`
Expected: vazio (tudo commitado nas tasks anteriores).

- [ ] **Step 2: Criar a tag**

```bash
git tag -a fase-1 -m "Fase 1: motor de áudio e mapa — testes de aceite T1-T6 verificados"
```

- [ ] **Step 3: Push da branch e da tag**

```bash
git push origin main
git push origin fase-1
```

---

## Task 14: Documentação acadêmica da Fase 1

**Files:**
- Create: `Docs/09-fase-1-implementacao.md`

- [ ] **Step 1: Escrever o documento**

Estrutura mínima (preencher com os resultados reais das tasks anteriores, não
com valores fictícios):

```markdown
# 09 — Implementação da Fase 1 (registro para a dissertação)

**Data de implementação:** [preencher]
**Commits:** do primeiro ao último desta fase — `git log --oneline <hash-inicial>..fase-1`
**Tag:** `fase-1`

## 1. O que foi implementado

| Arquivo | Responsabilidade | Testado por |
|---|---|---|
| `src/engine/tipos.ts` | Contratos de dados (Banda, MapaDaFaixa, Faixa, Regiao) | compilação (tipos) |
| `src/engine/Mapa.ts` | Carrega e consulta o `.map.json`: interpolação, seções, snap, somas acumuladas | 13 testes de unidade (Vitest) |
| `src/engine/Audio.ts` | Web Audio puro: carregar, tocar, pausar, loop de região, seek, posição | função `posicaoNaRegiao` por unidade (6 testes); classe inteira por verificação manual (T1–T6) |
| `src/app/teste/page.tsx` | Bancada de teste descartável — expõe controles e as 4 barras de banda | manual |

## 2. Decisões e desvios em relação à SPEC

- **`BANDAS_INFO`**: o array rico de metadados de banda em `tokens.ts` foi renomeado
  (era `BANDAS`) para não colidir com o `BANDAS: Banda[]` simples de `tipos.ts`.
- **`secaoEm` no limite exato da duração**: tratado como caso especial (última
  seção inclui `fim`), senão `t === duracaoSeg` não caía em seção nenhuma.
- **Vitest**: adicionado como devDependency só para `engine/` — justificativa
  em `Docs/superpowers/plans/2026-09-15-fase-1-audio-e-mapa.md`.
- **`posicaoNaRegiao` extraída como função pura**: para poder testar por unidade
  a única matemática realmente arriscada de `Audio.ts` sem depender de um
  `AudioContext` real.

## 3. Cobertura de testes automatizados

- `pnpm test` — [preencher: N testes, todos verdes]
- Escopo: `engine/Mapa.ts` (completo) e `engine/Audio.ts` (só a função pura
  `posicaoNaRegiao`). A classe `Audio` em si depende de APIs de navegador
  (`AudioContext`, `AudioBufferSourceNode`) que não existem em Node/Vitest —
  verificada manualmente (seção 4).

## 4. Testes de aceite manuais (SPEC seção 7)

| # | Teste | Resultado | Observações |
|---|---|---|---|
| T1 | O áudio toca | [PASS/FAIL] | |
| T2 | Posição bate com o som (5 min) | [PASS/FAIL] | |
| T3 | Loop de região funciona | [PASS/FAIL] | |
| T4 | Trocar região em execução | [PASS/FAIL] | |
| T5 | Bandas batem com o que se ouve | [PASS/FAIL] | |
| T6 | Seek para trás | [PASS/FAIL] | |
| — | Determinismo em t=20.000 | [PASS/FAIL] | |

## 5. Como rodar

```bash
cd riscos-que-dancam
pnpm install
pnpm dev        # http://localhost:3000/teste
pnpm test       # testes de unidade do engine/
```

## 6. Estado do repositório

- Remote: https://github.com/phcworkspace/Riscosquedan-am
- Tag: `fase-1`
- [Deploy Vercel: preencher URL, ou "não realizado nesta fase — decisão pendente"]

## 7. Próximo passo

Fase 2 — Renderizador (`Docs/04-roadmap-desenvolvimento.md`), que consome
exatamente `Mapa` e `Audio` construídos aqui, sem alterá-los.
```

- [ ] **Step 2: Preencher os campos com os resultados reais** das Tasks 12 e 13
      (contagem de testes, resultado de cada T1–T6, hash de commits).

- [ ] **Step 3: Commit**

```bash
git add Docs/09-fase-1-implementacao.md
git commit -m "docs: registra a implementação da Fase 1 para a dissertação"
git push origin main
```

---

## Task 15 (opcional — decisão do usuário): Deploy na Vercel

A SPEC pede deploy desde o primeiro dia (seção 1) e ao final da fase (seção 10).
Não foi feito como parte deste plano porque depende de uma conta/time da Vercel
que só o usuário pode escolher, e não há CLI (`vercel`) autenticado neste
ambiente.

- [ ] Perguntar ao usuário qual conta/time Vercel usar (ou usar o conector MCP
      `claude_ai_Vercel` já disponível, uma vez autorizado o time/projeto).
- [ ] Rodar o deploy e atualizar a seção 6 de `Docs/09-fase-1-implementacao.md`
      com a URL.
