# SPEC — Fase 1: Motor de áudio e mapa

**Projeto:** Riscos que Dançam
**Fase:** 1 de 7 · a fundação
**Insumos:** `02-PRD-arquitetura-tecnica.md` (seções 2, 3) · `04-roadmap-desenvolvimento.md`

---

## Objetivo

Provar que dá para tocar uma faixa, fazer loop de uma região arbitrária, saber com
precisão onde o áudio está, e consultar as quatro curvas de banda naquele instante.

**Sem interface de verdade.** Uma página de teste feia, com botões e números na tela.
Se esta fase não ficar sólida, nada construído por cima vai funcionar.

**Pronto quando:** os seis testes de aceite da seção 7 passam.

---

## 1. Setup

```bash
npx create-next-app@latest riscos-que-dancam \
  --typescript --tailwind --eslint --app --src-dir --import-alias "@/*"
cd riscos-que-dancam
npm i zustand
```

Copiar da pasta `MP3/` do projeto para `public/audio/`:

```
public/audio/
  01-pulso.mp3        01-pulso.map.json
  02-correnteza.mp3   02-correnteza.map.json
  03-nevoa.mp3        03-nevoa.map.json
  faixas.json
```

Commit inicial + deploy na Vercel. **Deployar no primeiro dia**, não no fim — é grátis e
descobre cedo qualquer problema de build.

**Nada de Supabase nesta fase.** Nada de Tone.js, p5.js, howler ou qualquer biblioteca de
áudio.

---

## 2. Estrutura de arquivos desta fase

```
src/
  engine/
    tipos.ts        ← contratos de dados
    Mapa.ts         ← carrega e consulta o .map.json
    Audio.ts        ← Web Audio: carregar, tocar, seek, loop de região
  app/
    teste/page.tsx  ← página de teste desta fase (descartável depois)
```

Regra de arquitetura: **`engine/` não importa nada de React.** São classes e funções
TypeScript puras. O React só as instancia.

---

## 3. `engine/tipos.ts`

```ts
export type Banda = 'grave' | 'medio' | 'agudo' | 'brilho';

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

---

## 4. `engine/Mapa.ts`

```ts
export class Mapa {
  readonly dados: MapaDaFaixa;
  private acumuladas: Record<Banda, Float64Array>;

  private constructor(dados: MapaDaFaixa) { /* ... */ }

  static async carregar(url: string): Promise<Mapa>;

  /** Valor da banda no instante t, interpolado entre quadros. 0..1 */
  valor(banda: Banda, t: number): number;

  /** Energia geral no instante t. 0..1 */
  energia(t: number): number;

  /** Integral da banda de 0 até t. Usada pelo comportamento "girar" na Fase 2. */
  acumulado(banda: Banda, t: number): number;

  /** Seção que contém t, ou null. */
  secaoEm(t: number): Secao | null;

  /** Batida ou fronteira de seção mais próxima de t, dentro de `tolerancia`. */
  encaixe(t: number, tolerancia = 0.12): number | null;
}
```

### Regras de implementação

**Interpolação linear entre quadros.** O mapa é 30fps e o desenho roda a 60:

```ts
valor(banda: Banda, t: number): number {
  const c = this.dados.bandas[banda];
  if (!c?.length) return 0;
  const q = t * this.dados.fps;
  const i = Math.floor(q);
  if (i < 0) return c[0];
  if (i >= c.length - 1) return c[c.length - 1];
  return c[i] + (c[i + 1] - c[i]) * (q - i);
}
```

**Somas acumuladas calculadas uma vez** no construtor, uma `Float64Array` por banda.
Existem para que `girar` não precise acumular ângulo quadro a quadro — o que quebraria o
scrub e o determinismo (PRD seção 5).

**`encaixe`** usa `pulso.batidas` quando `pulso.temPulsoClaro` é `true`; caso contrário
usa as fronteiras de `secoes`. Retorna `null` se nada estiver dentro da tolerância.

**Nunca mutar `dados`.** O mapa é somente leitura.

---

## 5. `engine/Audio.ts`

A classe mais delicada da fase. Web Audio puro.

```ts
export type EstadoAudio = 'vazio' | 'carregando' | 'pronto' | 'tocando';

export class Audio {
  get estado(): EstadoAudio;
  get duracao(): number;
  get regiao(): Regiao | null;
  get tocando(): boolean;

  /** Cria o AudioContext. Precisa ser chamado dentro de um gesto do usuário. */
  static async iniciar(): Promise<Audio>;

  async carregar(url: string): Promise<void>;

  tocar(de?: number): void;
  pausar(): void;
  parar(): void;            // pausa e volta ao início da região (ou a 0)

  /** Define a região de loop. null desliga o loop. */
  definirRegiao(r: Regiao | null): void;

  buscar(t: number): void;  // seek; mantém tocando se estava tocando
  volume(v: number): void;  // 0..1

  /** Posição atual em segundos. Chamada a cada quadro. */
  posicao(): number;

  destruir(): void;
}
```

### Regras de implementação — leia com atenção, é aqui que dá errado

**1. O `AudioContext` só é criado dentro de um gesto do usuário.** Política de autoplay
de todos os navegadores. Por isso `iniciar()` é estático e assíncrono, e a aplicação tem
uma tela de entrada com botão "Começar". Se o contexto vier `suspended`, chamar
`await ctx.resume()`.

**2. `AudioBufferSourceNode` é descartável.** Não dá para pausar e retomar o mesmo node,
nem mudar `loopStart` de forma confiável com ele tocando. O padrão:

```ts
private criarSource(de: number) {
  this.src?.stop();
  this.src?.disconnect();

  const src = this.ctx.createBufferSource();
  src.buffer = this.buffer;
  if (this.reg) {
    src.loop = true;
    src.loopStart = this.reg.inicio;
    src.loopEnd = this.reg.fim;
  }
  src.connect(this.ganho);
  src.start(0, de);

  this.src = src;
  this.offset = de;                    // posição do buffer em que começamos
  this.iniciadoEm = this.ctx.currentTime;
}
```

Toda mudança de região, seek ou play recria o node. Isso é o uso correto da API, não um
contorno.

**3. `posicao()` é sempre calculada, nunca acumulada.**

```ts
posicao(): number {
  if (!this.tocando) return this.pausadoEm;
  const decorrido = this.ctx.currentTime - this.iniciadoEm;
  if (!this.reg) return Math.min(this.offset + decorrido, this.duracao);

  const janela = this.reg.fim - this.reg.inicio;
  const dentro = (this.offset - this.reg.inicio + decorrido) % janela;
  return this.reg.inicio + dentro;
}
```

Somar `dt` a cada quadro acumula erro e sai de sincronia com o que se ouve em poucos
minutos. **Nunca faça isso.**

**4. Pausar** guarda `posicao()` em `pausadoEm` e para o node. **Tocar** recria o node a
partir de `pausadoEm`.

**5. `definirRegiao`** com o áudio tocando: se a posição atual está fora da nova região,
recomeça no início dela; se está dentro, recria o node na posição atual.

**6. Um `GainNode` só**, entre o source e o destination. O volume vive nele.

**7. Sem `AnalyserNode`.** Nenhuma FFT no navegador — o mapa já tem tudo.

**8. `decodeAudioData`** é a parte lenta (alguns segundos). Estado `'carregando'` e
feedback na tela.

---

## 6. `app/teste/page.tsx`

Página descartável. Feia de propósito — o design entra na Fase 5.

**O que precisa ter:**

- Botão **"Começar"** que chama `Audio.iniciar()` (o gesto que libera o contexto)
- Seletor das 3 faixas; ao escolher, carrega o mp3 e o mapa em paralelo
- **Play · Pausar · Parar** e um slider de volume
- Dois campos numéricos (início e fim em segundos) + botão **"Definir região"** e botão
  **"Limpar região"**
- Campo de seek + botão **"Ir para"**
- Um `requestAnimationFrame` mostrando, atualizado a cada quadro:
  - `posicao()` com 3 casas
  - os quatro valores de banda com 3 casas
  - a seção atual
  - **quatro barras horizontais** — a leitura visual é o que revela se as curvas fazem
    sentido; números sozinhos não mostram

```tsx
// as quatro barras — o instrumento de verificação desta fase
{BANDAS.map(b => (
  <div key={b} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
    <span style={{ width: 70, fontSize: 12 }}>{b}</span>
    <div style={{ width: 300, height: 14, background: '#222' }}>
      <div style={{
        width: `${valores[b] * 100}%`, height: '100%',
        background: CORES[b], transition: 'none',
      }} />
    </div>
    <span style={{ fontVariantNumeric: 'tabular-nums', fontSize: 12 }}>
      {valores[b].toFixed(3)}
    </span>
  </div>
))}
```

`CORES`: grave `#FF3B30` · medio `#FFB300` · agudo `#0A84FF` · brilho `#5AC8FA`.

**Limpeza:** `destruir()` no unmount e cancelamento do `requestAnimationFrame`. O
Fast Refresh do Next em desenvolvimento remonta muito — sem isso acumulam contextos de
áudio e o som começa a dobrar.

---

## 7. Testes de aceite

Rodar todos antes de fechar a fase.

| # | Teste | Como verificar |
|---|---|---|
| **T1** | **O áudio toca** | Escolher cada uma das 3 faixas, dar play, ouvir |
| **T2** | **A posição bate com o som** | Tocar "Pulso" e conferir se o número de `posicao()` corresponde ao trecho ouvido. Deixar rodando **5 minutos** e conferir de novo — se tiver derivado, `posicao()` está acumulando em vez de calcular |
| **T3** | **Loop de região funciona** | Região 10 → 18s. Deve repetir esse trecho indefinidamente, e `posicao()` deve saltar de ~18 para ~10 |
| **T4** | **Trocar a região em execução** | Com o loop rodando, mudar para 30 → 36s. Sem estalo, sem silêncio, sem posição errada |
| **T5** | **As bandas batem com o que se ouve** | A barra de **grave** precisa saltar junto com o bumbo em "Pulso". Em "Névoa", grave e brilho precisam se mover de forma visivelmente diferente. **Se as quatro barras subirem e descerem juntas, algo está errado** — provavelmente lendo a banda errada ou o mapa errado |
| **T6** | **Seek para trás** | Ir para 50s, depois voltar para 5s. O áudio e as barras acompanham; nada trava nem fica preso no valor antigo |

**Verificação extra de determinismo:** anotar os quatro valores em `t = 20.000`, tocar
até o fim, voltar para 20.000 e conferir. Precisam ser idênticos — é o que garante que a
Fase 2 possa fazer scrub.

---

## 8. Armadilhas conhecidas

| Sintoma | Causa provável |
|---|---|
| Nenhum som, sem erro no console | `AudioContext` criado fora de gesto do usuário, ou `suspended` sem `resume()` |
| Som dobrado, cada vez pior | Fast Refresh remontando sem `destruir()`; mais de um `AudioContext` vivo |
| Posição derivando com o tempo | `posicao()` acumulando `dt` em vez de calcular de `ctx.currentTime` |
| Estalo ao mudar a região | Tentando alterar `loopStart` com o node tocando, em vez de recriar |
| Barras todas iguais | Lendo a mesma banda quatro vezes, ou o mapa de outra faixa |
| Barras quase sempre no máximo | Mapa gerado com versão antiga da ferramenta (escala linear) — regerar |
| Nada acontece ao trocar de faixa | `decodeAudioData` ainda rodando; falta estado de carregando |

---

## 9. O que NÃO fazer nesta fase

- Não instalar biblioteca de áudio
- Não criar canvas nem desenhar nada
- Não mexer em layout, cores ou fontes — a página é feia de propósito
- Não criar o store do Zustand ainda (Fase 4)
- Não configurar Supabase
- Não rodar FFT nem usar `AnalyserNode`
- Não acumular tempo entre quadros, em lugar nenhum

---

## 10. Ao terminar

Tag no git (`fase-1`), deploy na Vercel, e a página `/teste` fica no ar. Ela continua
útil como bancada de diagnóstico durante as fases seguintes — só sai do projeto no
polimento final.

Próximo: **Fase 2 — renderizador**, que consome exatamente estas duas classes.
