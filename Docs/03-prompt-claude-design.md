# 03 — Prompt para o Claude Design

**Objetivo:** fechar a direção visual antes de escrever código.

*Terceira revisão — a linha do tempo virou o componente central e o painel agora
edita o elemento selecionado, não a próxima forma a ser criada.*

---

## Como usar

1. Abra o Claude Design e cole o **Prompt Principal** (seção 1) inteiro.
2. Avalie com o **Checklist** (seção 3).
3. Refine com os prompts da seção 2, um por vez.
4. Exporte para `Docs/design/`.

**Regra:** restrições concretas — hex, px, nomes de estado, o que evitar. "Faça bonito"
não funciona.

---

## 1. Prompt Principal (copiar e colar inteiro)

```
Preciso do design de uma aplicação web de página única chamada "Riscos que Dançam".

## O QUE É
Uma pessoa escuta uma música e desenha o que percebe nela.

Ela seleciona um trecho da faixa numa linha do tempo, ouve aquele trecho em
repetição, e cria elementos visuais — ponto, linha, forma — que respondem ao que
ela está ouvindo. Cada elemento é definido para reagir a uma parte do som: ao
grave, ao médio, ao agudo ou ao brilho. Ela percorre a faixa trecho a trecho.

No final ela aperta "Assistir": a música toca do início ao fim e o desenho dela
ganha vida sobre o áudio.

A aplicação NÃO produz som. O áudio é sempre a gravação original. O que a pessoa
compõe é a resposta visual ao som.

É um protótipo acadêmico de mestrado, inspirado em Norman McLaren, que desenhava
diretamente na película — inclusive na trilha sonora óptica — fazendo de imagem e
som o mesmo material.

## CONCEITO VISUAL: "MESA DE MONTAGEM"
Não é um app moderno de produtividade. É uma bancada de moviola — a mesa onde
McLaren riscava película: superfície escura, luz vinda de dentro do material, a
película como faixa de trabalho, instrumentos ao lado. Laboratório, não dashboard.

Referências: Norman McLaren (Synchromy 1971, Begone Dull Care 1949, Lines Vertical
1960), cinema abstrato de Oskar Fischinger e Len Lye, Kandinsky em "Ponto e Linha
sobre Plano".

## PALETA (usar exatamente estes valores)
Estrutura:
  --bg-base      #0B0B0D   fundo da aplicação
  --bg-palco     #141417   área de criação
  --surface      #1A1A1F   painéis e barras
  --surface-alt  #212128   linha do tempo
  --border       #2A2A31   bordas de 1px
  --text         #EDEDF0   texto primário
  --text-muted   #8A8A94   rótulos e ajuda
  --cursor       #FFFFFF   cursor de reprodução, com glow
  --loop         #FFD60A   região de loop selecionada

Cores das quatro bandas de frequência (grave → brilho, quente → frio):
  grave    #FF3B30    20–150 Hz
  médio    #FFB300    150–700 Hz
  agudo    #0A84FF    700–3200 Hz
  brilho   #5AC8FA    3200–11000 Hz

Paleta livre de cores dos elementos (8) — a pessoa escolhe qualquer uma; a cor da
banda escolhida vem pré-selecionada, mas ela pode trocar:
  #FF3B30  #FF7A1A  #FFB300  #30D158
  #0A84FF  #5AC8FA  #C77DFF  #F2F2F7

## TIPOGRAFIA
- Interface: Space Grotesk (fallback Inter). Rótulos em caixa alta, 11px,
  letter-spacing 0.08em, cor --text-muted.
- Números (tempo, segundos): JetBrains Mono.
- O maior texto da interface tem 20px. Nada de títulos grandes.

## LAYOUT — DESKTOP 1440×900
Quatro regiões, aplicação em tela cheia, sem scroll:

1. CABEÇALHO — altura 52px, fundo --surface, borda inferior 1px
   - Esquerda: nome do projeto 14px + subtítulo "Escute. Desenhe o que você vê."
     em 11px --text-muted
   - Centro: nome da faixa atual, clicável, abre a troca de faixa
   - Direita: botão circular "?" de 32px

2. PALCO (canvas) — ocupa a largura total menos 300px à direita, e a altura entre
   o cabeçalho e a linha do tempo
   - fundo --bg-palco
   - PERFURAÇÕES DE PELÍCULA nas bordas superior e inferior: retângulos
     arredondados de 14×10px espaçados uniformemente, cor #202026. Este detalhe
     é o que amarra a interface ao conceito de filme — não o omita
   - grão de ruído de 3% e vinheta suave
   - SEM grade e SEM régua dentro do palco: aqui a posição é composição livre,
     não tem significado sonoro. O tempo vive na linha do tempo, embaixo
   - os elementos desenhados pela pessoa, em cores variadas

3. PAINEL DIREITO — largura fixa 300px, fundo --surface, borda esquerda 1px.
   Duas partes, separadas por divisor:

   PARTE A — FERRAMENTA (sempre visível, no topo)
     Três botões quadrados de 76×76px lado a lado: ponto (●), linha (╱),
     forma (▲). O selecionado tem borda 1px clara e fundo mais claro.

   PARTE B — ELEMENTO SELECIONADO (o miolo do painel)
     Quando nada está selecionado, mostra um estado vazio discreto: "Selecione um
     elemento no palco para ajustá-lo". Quando há seleção, mostra:

     * RESPONDE A — quatro pastilhas largas empilhadas, uma por banda, cada uma
       com um ponto da cor da banda à esquerda, o nome (Grave / Médio / Agudo /
       Brilho) e a faixa de Hz em 10px --text-muted à direita. A selecionada tem
       fundo mais claro e barra vertical de 2px na borda esquerda.
       Ao lado do rótulo da seção, um mini-gráfico de 60×16px mostrando a curva
       daquela banda no trecho do elemento — é a prévia do que ele vai fazer.

     * COMPORTAMENTO — quatro botões em grade 2×2: Pulsar, Girar, Vibrar,
       Acender. Cada um com um ícone geométrico fino (traço 1.5px) que sugere o
       movimento.

     * REAÇÃO — slider horizontal, com "imóvel" à esquerda e "salta" à direita em
       10px --text-muted.

     * COR — oito círculos de 30px em duas fileiras de quatro. O selecionado ganha
       anel externo branco de 2px com 3px de espaço.

     * TAMANHO e OPACIDADE — dois sliders compactos.

     * TRECHO — mostra o intervalo em mono ("12,4s → 19,8s") e um botão pequeno
       "usar o loop atual" para reatribuir.

     * Rodapé: "Apagar elemento" em texto discreto, e o contador "18 / 120
       elementos" em mono 11px.

4. LINHA DO TEMPO — altura 148px, fundo --surface-alt, borda superior 1px.
   ESTE É O COMPONENTE MAIS IMPORTANTE DA TELA depois do palco. Quatro camadas
   empilhadas, ocupando toda a largura:

   a) RÉGUA (18px) — marcas de tempo em mono 10px, a cada 5 segundos

   b) FORMA DE ONDA (54px) — envelope simétrico da faixa, em --text-muted a 40%
      de opacidade. Divisores verticais finos marcam as seções da música, cada
      uma com uma letra (A, B, C…) em 9px no topo

   c) TRILHAS DOS ELEMENTOS (44px, rolável se passar) — uma barra horizontal de
      8px por elemento, na cor dele, posicionada e dimensionada conforme o trecho
      em que existe. Barras de elementos diferentes empilham em até 4 linhas. A do
      elemento selecionado tem contorno branco de 1px

   d) TRANSPORTE (32px) — à esquerda: play (círculo preenchido de 36px), stop, e
      um botão de loop que fica aceso em --loop quando há região ativa. Ao centro:
      o tempo atual e a duração em mono. À direita: slider de volume compacto e o
      botão ASSISTIR — pílula sólida de ~120px, o elemento mais chamativo da
      barra

   SOBRE TODAS AS CAMADAS:
   - a REGIÃO DE LOOP aparece como um retângulo translúcido em --loop a 12% de
     opacidade, com bordas de 2px e alças arrastáveis nas laterais
   - o CURSOR DE REPRODUÇÃO é uma linha vertical branca de 2px com glow, cruzando
     da régua até o transporte

## ARTBOARDS NECESSÁRIOS (nesta ordem)

1. "Entrada" — 1440×900. Abertura sobre fundo preto: nome do projeto, uma linha de
   descrição, botão "Começar". Ao fundo, elementos abstratos coloridos dispersos,
   bem sutis. Esta tela existe por uma razão técnica (o navegador exige um clique
   antes de liberar o áudio) — deve parecer intencional e convidativa.

2. "Palco vazio" — 1440×900. Layout completo, palco sem elementos, faixa carregada
   e linha do tempo já mostrando a forma de onda e as seções. No centro do palco,
   estado vazio discreto: "Selecione um trecho na linha do tempo e escute. Depois
   desenhe o que você vê." O painel direito mostra o estado vazio da Parte B.

3. "Escutando um trecho" — 1440×900. Uma região de loop de cerca de 8 segundos
   selecionada em amarelo na linha do tempo, cursor rodando dentro dela,
   transporte tocando. Alguns elementos já desenhados no palco, com suas barras
   coloridas visíveis nas trilhas. Nenhum elemento selecionado.

4. "Elemento selecionado" — 1440×900. Um dos elementos do palco selecionado, com
   alças de manipulação em volta. O painel direito inteiro preenchido: banda
   "Grave" ativa com o mini-gráfico da curva, comportamento "Pulsar" ativo,
   sliders posicionados, cor vermelha marcada, trecho mostrado. A barra desse
   elemento na trilha está com contorno branco.

5. "Composição" — 1440×900. A faixa coberta: cerca de 25 elementos no palco em
   cores variadas, e as trilhas da linha do tempo densas, com barras distribuídas
   ao longo de toda a duração em 3 ou 4 linhas empilhadas. Este artboard é o que
   vende o projeto — a composição do palco precisa parecer uma peça visual
   deliberada, não um amontoado.

6. "Modo Cinema" — 1440×900. O produto final. Toda a interface desapareceu: sem
   cabeçalho, sem painel, sem linha do tempo. O palco ocupa a viewport inteira,
   com a composição em movimento — elementos maiores, mais brilho, halos,
   partículas finas. As perfurações de película continuam nas bordas: aqui elas
   importam ainda mais, porque a tela virou um quadro de filme. Único elemento de
   interface: barra de progresso de 2px na base absoluta, branca semitransparente.

7. "Fim da animação" — 1440×900. A cena do Modo Cinema escurecida em 70%, com card
   central de 420px (fundo --surface, borda 1px, raio 6px): título curto ("Sua
   composição") e três ações — "Assistir de novo" (botão sólido), "Voltar a
   editar" (contorno), "Baixar em PNG" (link discreto).

8. "Tutorial" — 1440×900. Modal de 660px sobre a tela escurecida, três passos lado
   a lado com ilustração abstrata e texto:
   (1) "Escolha um trecho e escute em repetição"
   (2) "Desenhe o que você percebe — e diga a que som ele responde"
   (3) "Assista à sua composição sobre a música"
   Indicador de progresso e botão "Começar".

9. "Tablet" — 834×1112. Palco no topo, linha do tempo mantém a altura e a
   importância, painel vira uma gaveta lateral que desliza.

10. "Mobile" — 390×844. Palco ocupa o máximo possível. A linha do tempo reduz para
    forma de onda + transporte (as trilhas viram uma faixa única compacta). O
    painel do elemento sobe como gaveta quando algo é selecionado. Alvos de toque
    de no mínimo 44×44px.

11. "Sistema" — 1440×900. Folha de estilo: cores com hex e nome (estrutura, bandas
    e paleta livre), escalas de tipografia, botões em todos os estados, pastilhas
    de banda, botões de comportamento, sliders, círculos de cor, o play e o
    ASSISTIR, e as quatro camadas da linha do tempo destacadas separadamente.

## MICROINTERAÇÕES A INDICAR
- Cursor de reprodução: movimento linear constante, sem easing (é uma máquina).
- Elemento reagindo: cresce, gira, vibra ou acende conforme o som — no artboard
  "Escutando um trecho", mostre dois ou três em estado de reação evidente.
- Seleção: alças aparecem em 120ms, sem bounce.
- Arrastar a borda da região de loop: encaixe visível quando encontra uma batida
  ou fronteira de seção.
- Entrada no Modo Cinema: a interface some com fade de 400ms enquanto o palco
  cresce para preencher a tela — uma transição só, contínua.
- Demais transições: 150–200ms.

## O QUE EVITAR
- Nada de raio de borda acima de 6px, exceto o que é círculo por natureza.
- Nada de sombra difusa estilo Material. A profundidade vem de bordas de 1px e
  diferenças de 4–6% no valor do fundo.
- Nada de gradiente colorido de fundo. O brilho da tela vem do cursor e dos
  elementos reagindo — é luz atravessando película, não neon.
- Nada de grade, régua ou pauta musical dentro do palco. Posição ali é composição
  livre, não tempo nem altura.
- Nada de notação musical, teclado, nota, clave ou BPM em lugar nenhum. A pessoa
  não está compondo música — está respondendo a ela.
- Nada de mascote, emoji ou ícone arredondado amigável. Ícones geométricos, traço
  de 1.5px.
- Nada de texto explicativo longo. A interface se explica pelo uso.
```

---

## 2. Prompts de refinamento

**Se a linha do tempo ficar pequena ou secundária:**
```
A linha do tempo está tratada como barra de controles, e ela é onde o trabalho
acontece. Dê a ela 148px de altura e as quatro camadas separadas: régua, forma de
onda com as seções marcadas, trilhas coloridas dos elementos empilhadas em até 4
linhas, e transporte. A região de loop em amarelo precisa atravessar todas as
camadas, com alças visíveis nas bordas.
```

**Se a composição do palco ficar pobre:**
```
No artboard "Composição", refaça o palco. Precisa parecer uma peça visual
deliberada, no espírito de Begone Dull Care (McLaren, 1949) e do cinema abstrato de
Fischinger: agrupamentos, uma diagonal longa atravessando boa parte do quadro,
densidade em duas regiões e respiro em outras, variação forte de escala entre os
elementos. Evite distribuição uniforme.
```

**Se o conceito de película se perder:**
```
As perfurações de película nas bordas superior e inferior do palco estão discretas
demais ou ausentes. Desenhe retângulos arredondados de 14×10px, espaçados
uniformemente, em #202026, colados às bordas. Adicione grão de ruído de 3% e
vinheta suave. No Modo Cinema, deixe-as ainda mais presentes.
```

**Se o painel do elemento ficar confuso:**
```
O painel direito precisa deixar óbvio que edita o ELEMENTO SELECIONADO, não a
próxima forma a ser criada. Separe visualmente: ferramenta no topo, divisor forte,
e o resto sob um rótulo com o tipo do elemento selecionado. Quando não há seleção,
tudo abaixo do divisor vira estado vazio.
```

**Se o Modo Cinema não parecer especial:**
```
O "Modo Cinema" precisa parecer outra coisa, não a mesma tela sem painéis. Aumente
a densidade: elementos em escala maior, halos, partículas finas, mais contraste no
fundo. As perfurações mais presentes. É um quadro de filme projetado, não um editor
sem interface.
```

---

## 3. Checklist

- [ ] A linha do tempo tem 148px e as quatro camadas distintas
- [ ] As trilhas coloridas dos elementos aparecem e empilham
- [ ] A região de loop em amarelo atravessa as camadas, com alças
- [ ] O palco **não** tem grade nem régua
- [ ] As perfurações de película estão visíveis no palco e no Modo Cinema
- [ ] As 4 cores de banda estão nos hex corretos e associadas às faixas de Hz
- [ ] O painel deixa claro que edita o elemento selecionado, com estado vazio
- [ ] Existe o mini-gráfico da curva da banda no painel
- [ ] Nenhuma notação musical, nota, clave, teclado ou BPM em lugar nenhum
- [ ] O botão ASSISTIR é o elemento mais chamativo da linha do tempo
- [ ] O artboard "Composição" tem uma peça que você mostraria numa apresentação
- [ ] O "Modo Cinema" parece filme, não editor sem painéis
- [ ] Contraste do texto passa em AA
- [ ] Nenhum texto de interface acima de 20px
- [ ] Existe artboard de sistema com os estados dos componentes

---

## 4. Depois do Claude Design

1. Exportar os artboards em PNG para `Docs/design/`
2. Levar os tokens para `tailwind.config.ts`
3. Começar pelo **motor de áudio + mapa**, não pela UI
   (ver `04-roadmap-desenvolvimento.md`)
