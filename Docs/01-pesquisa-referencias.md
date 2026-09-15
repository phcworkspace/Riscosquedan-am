# 01 — Pesquisa: Projetos Semelhantes e Referências Visuais

**Data da pesquisa:** 14/09/2026 · *revisto após a correção do conceito — o desenho não gera som*

---

## Parte A — Projetos semelhantes (o que já existe e o que aproveitar)

### A.1 Chrome Music Lab — Kandinsky (Google Creative Lab / Active Theory)
🔗 https://musiclab.chromeexperiments.com/kandinsky/
🔗 Making-of: https://medium.com/active-theory/chrome-music-lab-making-kandinsky-7de5ab04f4fe

**O que é:** a pessoa rabisca no canvas e aperta play; o desenho vira som.

**O que aproveitar — 3 lições diretas:**
1. **Todas as notas pertencem a uma única escala.** Qualquer combinação soa coerente. É a decisão que separa "instrumento lúdico" de "barulho". → Adotado: escala pentatônica.
2. **A posição horizontal define o ritmo** — formas próximas tocam juntas, formando acordes naturalmente.
3. **Timing pré-calculado**, não calculado no loop de desenho. → Adotado: `Tone.Transport`.

**O que NÃO copiar:** eles migraram para WebGL porque desenham traço livre com espessura variável. Nosso caso é geometria simples — Canvas 2D resolve com folga. Também não adotamos o reconhecimento de gestos ($1 Recognizer); nossas formas são escolhidas na ferramenta, não adivinhadas.

**Diferencial do nosso projeto:** no Kandinsky o mapeamento é opaco e "mágico". No nosso, o mapeamento é **explícito e legível** (cor = timbre, Y = altura, espessura = volume) — porque o objetivo é pedagógico/de pesquisa, não só lúdico.

### A.2 Editores de vídeo e DAWs — a referência de mecânica
A linha do tempo do nosso protótipo se parece muito mais com a de um editor de vídeo
(Premiere, DaVinci) ou de uma DAW (Ableton, Reaper) do que com um sequenciador musical:
forma de onda no topo, **trilhas empilhadas** mostrando quando cada elemento existe, região
de loop com alças, cursor atravessando tudo. É de lá que vêm as convenções que a pessoa já
conhece — arrastar para selecionar, alça para ajustar a borda, clique para posicionar.

Vale olhar especificamente a **seleção de região com loop** do Ableton e do Audacity: é o
gesto central da nossa experiência e os dois resolvem bem, de formas diferentes.

### A.3 UPIC — Iannis Xenakis (1977) e IanniX
🔗 https://www.iannis-xenakis.org/en/dictionary-upic/
🔗 https://econtact.ca/19_3/scordato_iannix.html
🔗 ZKM: https://zkm.de/en/from-xenakiss-upic-to-graphic-notation-today

O UPIC era uma prancheta em que o compositor desenhava e o traço virava som: eixo X =
tempo, eixo Y = frequência, linha inclinada = glissando.

**É o espelho invertido do nosso projeto, e vale exatamente por isso.** O UPIC é o extremo
do desenho-como-instrumento; o nosso é o desenho-como-escuta. Citá-lo na dissertação
permite situar o protótipo por contraste: as duas metades da mesma relação entre gesto e
som, uma partindo da mão para o ouvido, a outra do ouvido para a mão.

### A.4 Patatap (Jono Brandel + Lullatone)
🔗 https://patatap.com/
Cada tecla dispara simultaneamente uma animação e um som. **Lição que permanece:** o
feedback precisa ser instantâneo e cheio. → Adotado: o elemento recém-criado **já começa a
reagir na hora**, dentro do loop que está tocando. A pessoa vê imediatamente o que fez.

### A.5 PictureWaves (open source, Canvas + Tone.js)
🔗 https://github.com/kennyxli/PictureWaves
Desenho→som em JS puro. Ficou fora do caminho depois da correção do conceito, mas segue
útil como leitura sobre estrutura de canvas interativo.

### A.6 p5-music-viz (Jason Sigal) — agora a referência central
🔗 https://therewasaguy.github.io/p5-music-viz/
Coletânea de técnicas de visualização reativa a áudio: bandas de frequência, amplitude,
detecção de batida, mapeamento de energia para parâmetros visuais. Com a correção do
conceito, **isto deixou de ser ornamento e virou o mecanismo principal** do protótipo.

A diferença em relação a um visualizer comum é que aqui quem decide o mapeamento é a
pessoa, elemento por elemento — e não o programador, uma vez para todos.

### A.7 Awesome Audio Visualization
🔗 https://github.com/willianjusten/awesome-audio-visualization
Lista curada — banco de referências para consulta durante o desenvolvimento.

---

## Parte B — Referências conceituais (fundamentação para a dissertação)

### B.1 Norman McLaren — som animado
- NFB, *Some Notes on Animated Sound*: https://www3.nfb.ca/photogallery/archives_mclaren/notech/NT33EN.pdf
- BFI: https://www.bfi.org.uk/sight-and-sound/features/how-write-film-piano-norman-mclarens-visual-music
- NFB, *Norman McLaren: Animated Musician*: https://www.nfb.ca/film/norman_mclaren_animated_musician/

**Filmes para citar e para inspirar o visual:**

| Filme | Ano | O que extrair |
|---|---|---|
| *Dots* | 1940 | Pontos coloridos sobre fundo escuro; som desenhado |
| *Loops* | 1940 | Geometria em movimento contínuo |
| *Begone Dull Care* | 1949 | Textura pintada à mão, riscos, arranhões, cor saturada |
| *Blinkity Blank* | 1955 | Gravura direta na película; aparições intermitentes |
| *Lines: Vertical / Horizontal* | 1960/62 | Linha como sujeito único — minimalismo radical |
| *Synchromy* | 1971 | **A referência visual principal:** colunas verticais coloridas que *são* a trilha sonora |
| *Mosaic* | 1965 | Percussão tipo código Morse |

### B.2 Kandinsky — *Ponto e Linha sobre Plano* (1926)
Base teórica dos "elementos básicos das artes visuais" citados no pré-projeto. Fundamenta por que ponto/linha/forma/cor são as primitivas da interface — e não uma escolha arbitrária.

### B.3 Visual Music — linhagem
- Oskar Fischinger, Len Lye, Hans Richter, Walther Ruttmann
- ACMI, *The Art of Visual Music*: https://www.acmi.net.au/education/school-program-and-resources/the-art-of-visual-music/
- Artsper sobre Fischinger: https://blog.artsper.com/en/a-closer-look/the-father-of-visual-music-oskar-fischingers-experimental-legacy/

---

## Parte C — Direção de arte (o que vai virar prompt)

### C.1 Conceito visual: **"Mesa de montagem"**

A interface não é um app moderno com cantos arredondados. É uma **bancada de moviola** — a mesa onde McLaren riscava a película: superfície escura, luz vinda de baixo, a película como faixa de trabalho, instrumentos ao lado.

### C.2 Paleta

**Fundo e estrutura (o "laboratório"):**

| Token | Hex | Uso |
|---|---|---|
| `--bg-base` | `#0B0B0D` | Fundo da aplicação |
| `--bg-palco` | `#141417` | Área de criação (a "película") |
| `--surface` | `#1A1A1F` | Painéis e barras |
| `--surface-alt` | `#212128` | Linha do tempo |
| `--border` | `#2A2A31` | Bordas de 1px |
| `--text` | `#EDEDF0` | Texto primário |
| `--text-muted` | `#8A8A94` | Rótulos, ajuda |
| `--cursor` | `#FFFFFF` | Cursor de reprodução, com glow |
| `--loop` | `#FFD60A` | Região de loop selecionada |

**Cores das quatro bandas de frequência.** Quente para grave, frio para agudo — a
progressão é sinestésica e se lê sem legenda:

| Banda | Hex | Faixa |
|---|---|---|
| Grave | `#FF3B30` | 20–150 Hz |
| Médio | `#FFB300` | 150–700 Hz |
| Agudo | `#0A84FF` | 700–3200 Hz |
| Brilho | `#5AC8FA` | 3200–11000 Hz |

**Paleta livre dos elementos (8).** A cor da banda escolhida vem pré-selecionada, mas a
pessoa pode trocar por qualquer uma — porque o projeto é sobre o que ela sente, e ela
pode muito bem sentir o grave como roxo:

`#FF3B30` · `#FF7A1A` · `#FFB300` · `#30D158` · `#0A84FF` · `#5AC8FA` · `#C77DFF` · `#F2F2F7`

### C.3 Tipografia
- **Interface:** Space Grotesk ou Inter — geométrica, neutra, discreta
- **Números (BPM, tempo, compasso):** JetBrains Mono ou IBM Plex Mono — remete a equipamento de laboratório
- Rótulos curtos, caixa alta, tracking aberto, tamanho pequeno

### C.4 Texturas e detalhes que citam o filme
- **Perfurações de película (sprockets)** desenhadas nas bordas superior e inferior da área de canvas — detalhe decorativo que amarra tudo ao conceito
- **Grão sutil** (noise overlay, opacidade ≤ 4%) sobre o fundo
- **Vinheta suave** nas bordas
- **Glow** no cursor de reprodução e nos elementos reagindo — é "luz atravessando película", não neon de dashboard
- **Zero** sombra difusa estilo Material, zero gradiente colorido de SaaS

### C.5 Movimento
- Cursor de reprodução: movimento linear constante, sem easing (é uma máquina)
- Elementos reagindo: o movimento vem da curva da banda, contínuo — não é um "flash" de
  evento, é respiração. Quem define a intensidade é o slider de reação
- Todo elemento carrega um piso de variação de brilho (~15%) junto do comportamento
  escolhido, para que nada fique visualmente morto
- Entrada e saída de um elemento no seu trecho: fade de 400ms
- Criação: fade + leve escala, 120ms
- Interface: transições ≤ 200ms, sem bounce

---

## Fontes

Todas as URLs desta pesquisa:

- [Kandinsky — Chrome Music Lab](https://musiclab.chromeexperiments.com/kandinsky/)
- [Chrome Music Lab: Making 'Kandinsky' — Active Theory](https://medium.com/active-theory/chrome-music-lab-making-kandinsky-7de5ab04f4fe)
- [UPIC — Iannis Xenakis](https://www.iannis-xenakis.org/en/dictionary-upic/)
- [From UPIC to IanniX — eContact! 19.3](https://econtact.ca/19_3/scordato_iannix.html)
- [From Xenakis's UPIC to Graphic Notation Today — ZKM](https://zkm.de/en/from-xenakiss-upic-to-graphic-notation-today)
- [Patatap](https://patatap.com/)
- [PictureWaves — GitHub](https://github.com/kennyxli/PictureWaves)
- [MDN — AudioBufferSourceNode (loop de região)](https://developer.mozilla.org/en-US/docs/Web/API/AudioBufferSourceNode)
- [librosa — documentação](https://librosa.org/doc/latest/index.html)
- [Visualizing Music with p5.js](https://therewasaguy.github.io/p5-music-viz/)
- [Awesome Audio Visualization — GitHub](https://github.com/willianjusten/awesome-audio-visualization)
- [Some Notes on Animated Sound — NFB (PDF)](https://www3.nfb.ca/photogallery/archives_mclaren/notech/NT33EN.pdf)
- [How to write a film on a piano — BFI Sight and Sound](https://www.bfi.org.uk/sight-and-sound/features/how-write-film-piano-norman-mclarens-visual-music)
- [Norman McLaren: Animated Musician — NFB](https://www.nfb.ca/film/norman_mclaren_animated_musician/)
- [The Art of Visual Music — ACMI](https://www.acmi.net.au/education/school-program-and-resources/the-art-of-visual-music/)
- [Oskar Fischinger — Artsper Magazine](https://blog.artsper.com/en/a-closer-look/the-father-of-visual-music-oskar-fischingers-experimental-legacy/)
