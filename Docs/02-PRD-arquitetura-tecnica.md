# 02 — PRD / Arquitetura Técnica

**Projeto:** Riscos que Dançam
**Data:** 14/09/2026 · *terceira revisão — arquitetura refeita após a correção do conceito*
**Resumo:** A pessoa escuta trechos de uma faixa em loop e desenha elementos que respondem a partes específicas do som. No final, assiste à animação completa sobre o áudio original.

---

## 1. Contexto e escopo

Artefato digital de pesquisa de mestrado. Roda inteiramente no navegador, sem backend.
Sem teste com usuários, sem coleta de dados.

**A regra que organiza tudo:**

> O áudio é sempre a faixa original. **Nenhum som é gerado pela aplicação.**

**Camadas:**
- [x] UI (casca, linha do tempo, painéis, Modo Cinema)
- [x] Motor visual (canvas, render loop, hit-testing)
- [x] Reprodução de áudio (play, seek, loop de região)
- [x] Mapa da faixa (pré-calculado em Python, consumido como JSON)
- [x] Estado (documento, undo/redo, autosave)
- [ ] Banco de dados — não existe

---

## 2. Stack

| Camada | Tecnologia | Por quê |
|---|---|---|
| Framework | **Next.js 15 (App Router) + TypeScript** | Stack conhecida; deploy Vercel; página única estática |
| Estilo | **Tailwind + shadcn/ui** | Casca rápida; compatível com o que o Claude Design entrega |
| Render | **Canvas 2D API pura** | Até ~120 primitivas geométricas; 60fps trivial |
| Áudio | **Web Audio API pura — sem biblioteca** | Ver 2.1 |
| Análise | **Python + librosa, offline** | Gera o mapa da faixa uma vez, fora do navegador |
| Estado | **Zustand** | Store simples que o motor consome sem React |
| Deploy | **Vercel** | Estático |

### 2.1 Por que Web Audio puro, e não Tone.js

O Tone.js entrou na arquitetura anterior por causa do **scheduler musical** — agendar
notas com precisão de amostra. Essa necessidade desapareceu junto com a síntese.

O que sobrou é simples: carregar um arquivo, tocar, pausar, buscar uma posição e tocar
uma região em loop. `AudioBufferSourceNode` faz loop de região nativamente
(`loop`, `loopStart`, `loopEnd`) e `audioContext.currentTime` dá o relógio. São menos
de cem linhas, contra 200 KB de biblioteca e uma camada de abstração que não serve mais
para nada.

```ts
// o essencial do motor de áudio
const src = ctx.createBufferSource();
src.buffer = buffer;
src.loop = true;
src.loopStart = regiao.inicio;
src.loopEnd = regiao.fim;
src.connect(ganho).connect(ctx.destination);
src.start(0, regiao.inicio);
iniciadoEm = ctx.currentTime;

// posição atual, consultada pelo loop de desenho
function posicao() {
  const decorrido = ctx.currentTime - iniciadoEm;
  if (!src.loop) return offsetInicial + decorrido;
  const janela = regiao.fim - regiao.inicio;
  return regiao.inicio + ((offsetInicial - regiao.inicio + decorrido) % janela);
}
```

Se durante a implementação isso virar fonte de bugs, Tone.js continua sendo um plano B
válido — mas comece sem ele.

### 2.2 Por que o mapa da faixa é pré-calculado

A animação **não** roda FFT no navegador. Toda a informação sobre o som vem de um
arquivo `.map.json` gerado antes, em Python. Três motivos:

1. **Determinismo.** O mesmo desenho produz exatamente a mesma animação toda vez.
   Importa quando a peça vai ser apresentada.
2. **Funciona fora da reprodução linear.** Com o cursor parado, arrastado, ou voltando
   atrás, o valor de cada banda continua disponível — é consulta por tempo, não
   análise ao vivo.
3. **Sobra quadro.** A FFT sai do loop de desenho.

O custo é um arquivo de ~65 KB por minuto de faixa, carregado junto com o áudio.

---

## 3. O mapa da faixa

Gerado por `MP3/ferramentas/mapear_faixa.py`. Um arquivo por faixa.

```jsonc
{
  "arquivo": "01-pulso.mp3",
  "duracaoSeg": 69.818,
  "fps": 30,                    // resolução temporal do mapa
  "quadros": 2095,
  "bandas": {                   // 0..1 por quadro — o coração do mapa
    "grave":  [0.02, 0.41, 0.88, ...],
    "medio":  [...],
    "agudo":  [...],
    "brilho": [...]
  },
  "faixasDeBanda": { "grave": [20,150], "medio": [150,700],
                     "agudo": [700,3200], "brilho": [3200,11000] },
  "rms":    [...],              // energia geral, por quadro
  "picos":  [...],              // 1200 valores — forma de onda para a régua
  "ataques": [1.23, 1.78, ...], // onsets em segundos
  "secoes": [{ "inicio": 0, "fim": 8.62, "rotulo": "A" }, ...],
  "pulso": {
    "bpmEstimado": 112.35,      // INFORMATIVO — não é requisito
    "contrasteDeAtaque": 7.11,
    "temPulsoClaro": true,
    "batidas": [0.51, 1.05, ...]  // vazio quando o pulso é difuso
  }
}
```

### 3.1 Como as curvas de banda são construídas

Três decisões, todas tomadas medindo o resultado nas faixas de teste:

- **Escala em dB, não linear.** A audição é logarítmica. Na primeira tentativa, em
  escala linear, as curvas ficavam acima de 0,5 em **90% do tempo** — a animação
  ficaria chapada, tudo sempre aceso. Em dB, com gama 1,6, os elementos ficam em
  repouso e saltam nos eventos.
- **Cada banda normalizada pela própria janela dinâmica** (percentil 20 → 99), não
  pelo pico geral. Assim uma faixa sem agudos ainda anima os elementos de agudo, em
  vez de deixá-los parados. O mapa descreve o **relevo** de cada banda, não o volume
  absoluto dela.
- **Seguidor de envelope assimétrico** (sobe rápido, desce devagar). Sem ele as curvas
  tremem quadro a quadro e a animação fica nervosa; com ele cada banda se comporta
  como um VU.

### 3.2 Quatro bandas, não seis — a medida que decidiu

| Divisão | Correlação média entre bandas | Pior par |
|---|---|---|
| 6 bandas | 0,48 | **0,97** |
| 5 bandas | 0,45 | 0,93 |
| **4 bandas** | **0,41** | **0,84** |

Com seis bandas, duas escolhas diferentes da pessoa produziriam praticamente a mesma
animação. Quatro é o que o material sustenta. Grave e agudo ficam com correlação de
0,38 a −0,06 conforme a faixa — genuinamente independentes.

### 3.3 Consumo no runtime

```ts
function valorDaBanda(mapa: MapaDaFaixa, banda: Banda, t: number): number {
  const q = t * mapa.fps;
  const i = Math.floor(q), f = q - i;
  const c = mapa.bandas[banda];
  if (i >= c.length - 1) return c[c.length - 1] ?? 0;
  return c[i] + (c[i + 1] - c[i]) * f;   // interpola 30fps → 60fps
}
```

---

## 4. Modelo de dados

```ts
type Banda = 'grave' | 'medio' | 'agudo' | 'brilho';
type Tipo = 'ponto' | 'linha' | 'forma';
type Comportamento = 'pulsar' | 'girar' | 'vibrar' | 'acender';

interface Elemento {
  id: string;
  tipo: Tipo;
  banda: Banda;              // a que parte do som responde
  comportamento: Comportamento;
  cor: string;               // livre; a cor da banda vem pré-selecionada
  reacao: number;            // 0..1 — quanto se move com o som
  opacidade: number;         // 0..1 — presença em repouso

  x: number; y: number;      // 0..1 — composição visual, sem sentido sonoro
  x2?: number; y2?: number;  // linha: ponto final
  tamanho: number;           // 0..1
  espessura: number;         // 0..1
  lados?: number;            // forma: 3..8
  rotacao?: number;

  entrada: number;           // segundo em que passa a existir
  saida: number;             // segundo em que deixa de existir
  fade: number;              // segundos de entrada/saída suave (padrão 0.4)
}

interface Composicao {
  faixaId: string;
  elementos: Elemento[];
  fundoReage: boolean;       // o fundo responde ao RMS geral
  criadoEm: string;
  versao: 1;
}

interface Faixa {
  id: string;
  titulo: string;
  arquivo: string;           // /audio/01-pulso.mp3
  mapa: string;              // /audio/01-pulso.map.json
  duracaoSeg: number;
  credito: { autor: string; licenca: string; url: string };
}
```

Nada de bpm ou tonalidade em `Faixa` — não são necessários.

---

## 5. Os comportamentos

Cada comportamento é uma função pura de `(elemento, v, t)`, onde `v` é o valor da banda
naquele instante (0..1) e `t` o tempo. Nenhum guarda estado — é o que torna a animação
determinística e o scrub possível.

| Comportamento | O que faz | Fórmula |
|---|---|---|
| **pulsar** | cresce e encolhe | `escala = 1 + v * reacao * 1.4` |
| **girar** | acelera e desacelera | `angulo += (0.2 + v * reacao * 6) * dt` |
| **vibrar** | oscila em torno da posição / ondula ao longo da linha | `desloc = sin(t*18 + fase) * v * reacao * 24px` |
| **acender** | varia brilho e opacidade | `alfa = opacidade * (0.25 + v * reacao * 0.75)` |

**Combinação:** todo elemento sempre recebe um pouco de *acender* junto do
comportamento escolhido — sem isso, um elemento com `reacao` baixa fica visualmente
morto. É um piso de 15% de variação de brilho, não configurável.

**`girar` guarda ângulo acumulado**, o que quebraria o determinismo. Solução: em vez de
acumular, integrar analiticamente a partir do início do elemento usando a soma
acumulada da banda, que é pré-calculada uma vez ao carregar o mapa:

```ts
// somaAcumulada[i] = soma de bandas[banda][0..i] — calculada uma vez
const angulo = (somaAcumulada(banda, t) - somaAcumulada(banda, el.entrada))
             * el.reacao * K;
```

---

## 6. Arquitetura de módulos

```
/app
  page.tsx                   → casca + <Palco />
/components
  Palco.tsx                  → <canvas> + refs; único contato React↔motor
  LinhaDoTempo.tsx           → forma de onda, seções, região de loop, faixas dos elementos
  PainelElemento.tsx         → banda, comportamento, cor, reação (do elemento selecionado)
  Ferramentas.tsx            → ponto / linha / forma
  Transporte.tsx             → play, pause, loop, volume, botão Assistir
  ModoCinema.tsx             → overlay de tela cheia
  Tutorial.tsx
/engine                      ← TypeScript puro, ZERO React
  tipos.ts
  Audio.ts                   → Web Audio: carregar, tocar, seek, loop de região, posição
  Mapa.ts                    → carregar .map.json, consulta interpolada, somas acumuladas
  comportamentos.ts          → as 4 funções puras + o piso de "acender"
  Renderizador.ts            → loop de desenho, culling por janela temporal
  Entrada.ts                 → mouse/touch → criar, selecionar, arrastar, redimensionar
/store
  useComposicao.ts           → documento, seleção, região de loop, undo/redo
/public/audio
  *.mp3 + *.map.json + faixas.json
```

**Separação:** o motor não conhece React. O React monta, passa o canvas por `ref`,
assina o store e destrói no unmount.

---

## 7. A linha do tempo — o componente central

Deixou de ser um detalhe da barra inferior. É onde o trabalho acontece.

**Camadas, de cima para baixo:**
1. **Forma de onda** (do array `picos`), com as **seções** marcadas por divisores verticais e rótulo
2. **Região de loop** — faixa destacada, com alças nas bordas para arrastar
3. **Trilhas dos elementos** — uma barra horizontal por elemento, na cor dele, mostrando seu trecho; clicar seleciona, arrastar move o trecho
4. **Cursor** de reprodução

**Comportamentos:**
- Arrastar na forma de onda define a região de loop; clique simples posiciona o cursor
- Com pulso claro no mapa, as bordas da região dão **snap às batidas**; sem pulso
  claro, snap às fronteiras de seção. (O mapa diz qual dos dois oferecer.)
- Desenhar com uma região ativa faz o elemento **herdar** `entrada` e `saida` dela
- Sem região selecionada, o elemento vale para a faixa inteira

---

## 8. Modo Cinema

Um estado da mesma aplicação, não uma tela nova.

1. A pessoa aperta **Assistir**
2. UI sai com fade de 400ms; o canvas cresce para preencher a viewport
3. Loop desligado, posição zerada, play
4. A faixa roda do início ao fim. Único elemento visível: uma barra de progresso de 2px
   na base, que some após 2s sem mouse
5. No fim: card central com *Assistir de novo* · *Voltar a editar* · *Baixar PNG*
6. `Esc` volta ao editor a qualquer momento

**Requisitos:** a troca **não recria** o `AudioContext` nem recarrega o buffer — é
layout e um flag no store. `Entrada.ts` desabilitado. Fullscreen API quando disponível,
overlay na página como alternativa.

---

## 9. Riscos e mitigações

| # | Risco | Gravidade | Mitigação |
|---|---|---|---|
| R1 | **Autoplay**: o `AudioContext` só inicia após gesto do usuário | Alta | Tela de entrada com botão "Começar" que chama `ctx.resume()`. É a abertura da experiência, não um aviso |
| R2 | **Posição do áudio derivar** do valor calculado | Média | Recalcular de `ctx.currentTime` a cada quadro, nunca acumular. Ao trocar a região de loop, recriar o `AudioBufferSourceNode` (eles são descartáveis por design) |
| R3 | **Animação chapada** — tudo sempre aceso | Alta | Resolvido na geração do mapa (seção 3.1). Verificar em faixa nova: se a média de uma banda passar de 0,6, revisar |
| R4 | **Bandas indistinguíveis** — a escolha da pessoa não muda nada | Alta | Quatro bandas, validadas por correlação (seção 3.2). Rodar a mesma medida em faixa nova |
| R5 | **Peso do mapa** em faixa longa | Baixa | ~65 KB/min a 30fps. Faixa de 4 min ≈ 260 KB. Se incomodar, baixar para 20fps ou 2 casas decimais |
| R6 | **Carregamento** do mp3 + mapa | Média | Carregar só a faixa selecionada, com estado de carregando. Decodificar o áudio é a parte lenta |
| R7 | **Performance** com muitos elementos | Baixa | Limite de 120; culling por janela temporal (só desenha quem existe agora) |
| R8 | **Mobile: desenhar com o dedo** | Média | Alvos grandes, sem gestos complexos. A linha do tempo precisa de atenção especial em tela pequena |
| R9 | **Direitos das faixas** | Média | Obra **e** fonograma. Créditos visíveis na interface |
| R10 | **Scrub para trás** quebrar a animação | Média | Nenhum comportamento guarda estado; `girar` usa soma acumulada (seção 5) |

---

## 10. Requisitos não funcionais

- 60fps com 100 elementos simultâneos, no editor e no Modo Cinema
- Tempo até interativo < 2s (áudio carrega depois, com feedback)
- Sem requisição de rede após o carregamento da faixa
- Acessibilidade: contraste AA; controles por teclado; atalhos (Espaço = play/pause,
  Delete = apagar, Ctrl+Z, 1/2/3 = ferramenta, L = loop da região, Esc = sair do cinema)
- Créditos das faixas visíveis
- Sem coleta de dados

---

## 11. Sequência de implementação

1. **Motor de áudio + mapa**, sem interface: carregar faixa e mapa, tocar, fazer loop de
   uma região, e imprimir os 4 valores de banda no console a cada quadro.
2. **Renderizador**: elementos mockados reagindo às curvas.
3. **Linha do tempo**: forma de onda, seções, seleção de região com loop.
4. **Entrada**: criar, selecionar, mover, apagar — com herança do trecho.
5. **Painel do elemento**: banda, comportamento, cor, reação.
6. **Casca da UI** a partir do design.
7. **Modo Cinema.**
8. **Tutorial, estado vazio, PNG.**
9. **Polimento e testes.**

---

## 12. O que NÃO fazer

- **Não gerar som.** Nenhum sintetizador, nenhuma nota. O áudio é a faixa.
- **Não exigir BPM ou tonalidade** de uma faixa. São informativos, no máximo.
- **Não rodar FFT no navegador** — o mapa já tem tudo, e pré-calculado é determinístico.
- **Não instalar Tone.js, p5.js ou p5.sound.** Canvas 2D e Web Audio puros dão conta.
- **Não guardar estado nos comportamentos** — quebra o scrub e o determinismo.
- **Não implementar MediaRecorder, WebM ou GIF.** O Modo Cinema substitui.
- **Não colocar backend, login ou banco.**
- **Não passar de quatro bandas** sem antes medir a correlação na faixa nova.
- **Não instrumentar log de eventos** — não haverá teste com usuários.

---

## 13. Decisões em aberto

1. **Título definitivo** — "Riscos que Dançam" é provisório. Alternativas: *Escuta
   Desenhada*, *Trilha Óptica*, *Sulco*, *Moviola*.
2. **Idioma da interface** — português apenas, ou PT/EN.
3. **Quantas faixas** entram na versão final, e quais.
