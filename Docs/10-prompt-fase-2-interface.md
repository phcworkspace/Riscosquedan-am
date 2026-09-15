# 10 — Prompt da Fase 2: a tela real

**Data:** 15/09/2026
**Pré-requisito:** Fase 1 concluída (`Docs/09-fase-1-implementacao.md`)

---

## Por que a ordem mudou

O roadmap original punha a interface na Fase 5, depois do renderizador, da linha do tempo
e da interação. O motivo era concreto: *"a linha do tempo depende do `Mapa` e o painel
depende do modelo de dados — construídos antes, viram retrabalho."*

**Com a Fase 1 pronta, esse motivo caiu.** O `Mapa` já entrega tudo que a linha do tempo
precisa: `picos` (1200 valores da forma de onda), `secoes`, `pulso.batidas` para o snap.
E o `Audio` já toca, faz loop de região e reporta posição. Construir a tela agora **usa**
o que existe em vez de antecipar o que não existe.

Então a nova Fase 2 é **a casca da interface + a linha do tempo funcionando**, sobre o
motor que já está de pé. O renderizador do palco (desenhar os elementos) vira Fase 3, e a
interação de criar elementos, Fase 4.

O que você ganha: uma tela de verdade, com o design aplicado, que **toca a música e navega
a faixa**. O palco fica vazio — mas com a película, o grão e a vinheta, então já parece a
peça.

---

## Antes de rodar: uma limpeza

Em `Docs/design/` ainda existem dois arquivos de uma versão anterior, escritos para
Tailwind 3:

- `tokens.css`
- `tailwind.tokens.ts`

**Apague os dois.** Eles são a armadilha mais provável para o agente: ele lê
`tailwind.tokens.ts`, conclui que precisa de um `tailwind.config.ts`, e o Tailwind 4 não
usa isso. Os arquivos corretos são `globals.css` (já aplicado) e `tokens.ts` (já em
`src/engine/`).

---

## O prompt

Rode o Claude Code dentro de `riscos-que-dancam` e cole:

````
Implemente a Fase 2: a casca da interface e a linha do tempo, com o design que já
existe. Leia antes, nesta ordem:

- Docs/06-design-para-codigo.md   (como o design vira código — seções 2, 3.3, 3.4, 3.5)
- Docs/08-correcoes-do-ambiente.md (Next 16 e Tailwind 4 — o que muda)
- Docs/09-fase-1-implementacao.md  (o que o motor já entrega)
- src/engine/Mapa.ts e src/engine/Audio.ts (a API que você vai consumir)

## A fonte da verdade do design

Os valores exatos estão em `Docs/design/fonte/*.dc.html` — HTML com estilos inline.
NÃO meça pixel nos PNGs e NÃO arredonde para grade de 4/8px: abra o .dc.html e copie
o número. Os PNGs em `Docs/design/png/` servem só para conferir se o resultado
PARECE o design.

Artboards relevantes para esta fase:
- Entrada.dc.html          → a tela de abertura
- PalcoVazio.dc.html       → o editor sem nenhum elemento (é o alvo desta fase)
- Escutando.dc.html        → o editor com região de loop ativa e transporte tocando
- Sistema.dc.html          → estados dos componentes

## Limpeza primeiro

Apague `Docs/design/tokens.css` e `Docs/design/tailwind.tokens.ts`. São de uma versão
anterior, escrita para Tailwind 3, e induzem a erro. Os arquivos válidos são
`Docs/design/globals.css` (já aplicado em src/app/globals.css) e `Docs/design/tokens.ts`
(já em src/engine/tokens.ts).

## O que construir

A rota `/` passa a ser a aplicação. Mantenha `/teste` funcionando como está — é a
bancada de diagnóstico do motor e ainda vai ser usada.

### 1. Tela de entrada

Artboard: Entrada.dc.html. Existe por uma razão técnica — o navegador só libera o
AudioContext depois de um gesto do usuário — mas deve parecer intencional, nunca um
aviso. Botão "Começar" chama `Audio.iniciar()`.

### 2. Cabeçalho — 52px

Nome do projeto, subtítulo "Escute. Desenhe o que você vê.", nome da faixa atual ao
centro (clicável, abre a troca de faixa), botão "?" circular de 32px à direita.
O tutorial em si NÃO entra nesta fase — o botão fica inerte.

### 3. Palco — o que sobra da altura

Nesta fase o palco está VAZIO de elementos. Construa só a moldura:
- fundo --color-palco
- perfurações de película nas bordas superior e inferior (14×10px, raio 2, passo 34px,
  #202026, 6px da borda) — renderize como elementos num loop, não com background-repeat
- grão (classe .grao do globals.css) e vinheta (.vinheta), sobrepostos em DOM
- estado vazio central: "Selecione um trecho na linha do tempo e escute. Depois
  desenhe o que você vê."

O <canvas> pode já existir, dimensionado com devicePixelRatio correto, mas sem nada
desenhado. O Renderizador é a Fase 3.

ATENÇÃO ao layout: no design o palco tem 700px porque a janela tem 900. NÃO fixe isso.
O palco é o que sobra — `h-dvh` no contêiner, `flex-1` no meio, e `min-h-0` na linha
intermediária. Sem o min-h-0 o flex não deixa o filho encolher e a linha do tempo é
empurrada para fora da tela.

### 4. Painel direito — 300px

- Seção FERRAMENTA: três botões de 76×76px (ponto, linha, forma). Visualmente
  funcionais (seleção alterna), mas ainda não criam nada — isso é a Fase 4.
- Divisor de 1px.
- Abaixo: o estado vazio, "Selecione um elemento no palco para ajustá-lo". O painel
  do elemento selecionado é Fase 4.
- Rodapé: contador "0 / 120 elementos" em mono.

### 5. Linha do tempo — 148px, o componente central desta fase

É onde está o trabalho real. Quatro camadas empilhadas:

- régua (18px): marcas e tempo em mono a cada 5 segundos
- forma de onda (54px): desenhada a partir de `mapa.dados.picos` (1200 valores, 0..1),
  envelope simétrico. Divisores verticais nas fronteiras de `mapa.dados.secoes`, com a
  letra do rótulo em 9px no topo.
- trilhas dos elementos (44px): a área existe e fica vazia nesta fase
- transporte (32px): play/pause, stop, botão de loop (aceso em --color-loop quando há
  região), tempo atual e duração em mono, volume, e o botão ASSISTIR (pílula,
  26px de altura, fundo --color-tinta). O Modo Cinema é Fase 6 — o botão fica inerte.

Comportamentos que DEVEM funcionar nesta fase:
- clique na forma de onda posiciona o cursor (`audio.buscar`)
- arraste na forma de onda define a região de loop (`audio.definirRegiao`), desenhada
  como retângulo translúcido em --color-loop com bordas de 2px e alças arrastáveis
- as alças ajustam as bordas da região
- snap das bordas: use `mapa.encaixe(t)` — ele já decide entre batida e seção conforme
  `pulso.temPulsoClaro`
- o cursor de reprodução atravessa as quatro camadas, 2px, com glow
- play/pause/stop/loop e volume ligados ao `Audio`

### 6. Troca de faixa

Ler `/audio/faixas.json`, listar as três, e ao escolher carregar o mp3 e o mapa novos.
Estado de carregando visível — `decodeAudioData` demora.

## O que NÃO fazer nesta fase

- Não desenhe elementos no palco (Renderizador = Fase 3)
- Não implemente criação, seleção ou edição de elementos (Fase 4)
- Não implemente o painel do elemento selecionado, o tutorial nem o Modo Cinema
- Não altere `src/engine/Audio.ts` nem `src/engine/Mapa.ts`. Se precisar de algo que
  eles não expõem, PARE e me diga qual é a falta — não contorne por fora nem edite o
  motor por conta própria.
- Não crie `tailwind.config.ts` (Tailwind 4 não usa)
- Não instale nenhuma dependência nova sem justificar antes

## Regras de arquitetura

- `src/components/` para os componentes React. `src/engine/` continua sem importar React.
- O cursor de reprodução se move num `requestAnimationFrame` que lê `audio.posicao()` a
  cada quadro. Nunca acumule tempo.
- A forma de onda é estática: desenhe uma vez por faixa (canvas ou SVG), não a cada
  quadro.
- Componentes de apresentação recebem tudo por props, sem buscar estado por conta
  própria — assim a Fase 4 pluga o store sem reescrevê-los.
- Use os utilitários do Tailwind vindos do @theme (`bg-palco`, `text-tinta-fraca`,
  `border-linha`…), não hex soltos no JSX. O canvas e os SVGs leem de
  `src/engine/tokens.ts`.
- Nomes de domínio em português; APIs do navegador e do React em inglês.

## Fontes

Troque Geist por Space Grotesk e JetBrains Mono via next/font/google, apontando para
as variáveis `--font-sans` e `--font-mono` que o @theme do globals.css já declara.

## Verificação antes de terminar

- `pnpm exec tsc --noEmit` sem erros
- `pnpm build` passa
- `pnpm test` continua 25/25 (não quebre os testes do motor)
- `/teste` continua funcionando
- em `/`: o áudio toca, o cursor anda junto com o som, arrastar na forma de onda cria
  uma região que repete, e as bordas encaixam em batida ou seção
- compare a tela com `Docs/design/png/PalcoVazio.png` e `Escutando.png` e me diga onde
  divergiu e por quê

Ao terminar, escreva `Docs/10-fase-2-implementacao.md` no mesmo formato do
`09-fase-1-implementacao.md`: o que foi feito, decisões e desvios, o que foi verificado
automaticamente, e o que depende de conferência humana.
````

---

## Depois desta fase

```
Fase 3  Renderizador       desenhar os elementos no palco
Fase 4  Interação          criar, selecionar, editar + o painel do elemento
Fase 5  Tutorial e polimento da interface
Fase 6  Modo Cinema
Fase 7  Verificação final
```

A tela vai existir antes dos elementos existirem. É estranho de olhar por uma fase, mas
é a ordem que não gera retrabalho: a linha do tempo é o componente mais difícil do
projeto e já pode ser construída de verdade, contra dados reais.
