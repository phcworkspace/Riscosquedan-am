# 00 — Visão Geral e Decisões Conceituais

**Projeto:** Riscos que Dançam (título provisório)
**Tipo:** Protótipo digital interativo — artefato de pesquisa de mestrado
**Data:** 14/09/2026 · *terceira revisão — o conceito foi corrigido pelo Pedro*
**Status:** Conceito fechado → design (Claude Design) e Fase 1

---

## 1. O que é

Uma experiência web em que a pessoa **escuta uma música e desenha o que percebe**.

Ela seleciona um trecho da faixa, ouve em repetição, e cria elementos visuais — ponto,
linha, forma, cor — que traduzem aquilo que sente naquele trecho. Cada elemento é
definido para **responder a uma parte do som**: a um grave, a um agudo, ao brilho. Ela
avança pela faixa trecho a trecho, construindo uma leitura visual inteira.

No final, aperta *Assistir*: a faixa toca do começo ao fim e o desenho dela **ganha
vida sobre o áudio original** — a animação se forma a partir dos padrões que ela
desenvolveu.

A frase-síntese: **"Escute. Desenhe o que você vê."**

## 2. A correção que define o projeto

> **O áudio é sempre a faixa original. Nada do que a pessoa desenha produz som.**

Uma versão anterior deste documento propunha o contrário: os elementos desenhados
gerariam notas próprias por cima da trilha, como um instrumento. Isso estava errado, e
o erro custava caro — exigia faixas com BPM e tonalidade confirmados, escala musical,
quantização, seis sintetizadores. Toda uma camada que o projeto não precisa.

O que a pessoa compõe não é som. É **a resposta visual ao som**.

Isso é mais fiel à linhagem que o projeto invoca. Fischinger, Len Lye e o próprio
McLaren em boa parte da obra ouviam e desenhavam o que ouviam — a marca visual era
transcrição da escuta, não um instrumento a ser tocado.

**Consequências práticas, todas boas:**

| Antes | Agora |
|---|---|
| Faixa precisava de BPM e tonalidade confirmados | **Nenhum metadado musical é obrigatório** |
| Gravações históricas em andamento livre eram descartadas | **Qualquer gravação serve** |
| 6 sintetizadores, escala pentatônica, quantização em 32 passos | Nada disso existe |
| Tone.js pelo scheduler musical | **Web Audio puro** — sem biblioteca de áudio |
| Risco alto de desafinar ou sair do tempo | Esse risco deixou de existir |

O maior risco técnico do projeto simplesmente evaporou com a correção do conceito.

## 3. Referência conceitual — McLaren e a escuta

Norman McLaren desenhava diretamente na película, inclusive na trilha sonora óptica,
fazendo de imagem e som o mesmo material físico. Filmes-chave: *Dots* (1940),
*Begone Dull Care* (1949), *Blinkity Blank* (1955), *Lines: Vertical* (1960),
*Synchromy* (1971).

O protótipo não recria a técnica. Traduz o **princípio**: que existe uma
correspondência direta entre gesto visual e evento sonoro, e que essa correspondência
pode ser construída à mão, marca por marca.

## 4. As três decisões conceituais — resolvidas

### 4.1 Direção da relação visual ↔ som
**Áudio → visual, em sentido único.** A faixa original é a fonte; o desenho é a
resposta. Nenhum som vem do desenho.

### 4.2 Papel na pesquisa
**Demonstração de conceito.** Não haverá teste com usuários — sem log de eventos, sem
coleta, sem instrumentação.

### 4.3 Fidelidade
**Escopo estreito, acabamento alto.** Poucas funcionalidades, todas impecáveis.

## 5. Como a experiência funciona

### 5.1 O gesto central: ouvir um trecho e desenhar nele

Este é o coração da interação, e a decisão de design mais importante do projeto:

> **O elemento desenhado herda o trecho que está sendo ouvido.**

A pessoa seleciona uma região na linha do tempo. O áudio toca aquela região em loop.
Tudo que ela desenhar enquanto o loop roda **existe naquele trecho da faixa** — entra
quando o trecho começa, sai quando ele termina. Ela não precisa definir isso: é
consequência de ter desenhado ali.

Depois ela move a seleção para o trecho seguinte e continua. Ao final, a faixa inteira
está coberta por camadas que ela construiu ouvindo.

### 5.2 O que cada elemento tem

| Propriedade | O que é |
|---|---|
| **Tipo** | ponto · linha · forma |
| **Banda** | a que parte do som ele responde: grave · médio · agudo · brilho |
| **Comportamento** | como ele responde: pulsar · girar · vibrar · acender |
| **Cor** | livre — com a cor da banda como sugestão inicial |
| **Posição e tamanho** | composição visual pura, sem significado sonoro |
| **Reação** | 0 a 1 — o quanto ele se move com o som (0 = imóvel, 1 = salta) |
| **Trecho** | quando ele existe na faixa — herdado do loop em que foi criado |

**Por que a cor é livre e a banda é separada.** Numa versão anterior a cor *era* a
banda. Mas o projeto é sobre "aquilo que a pessoa sente" — e ela pode muito bem sentir
o grave como azul. Então a banda é uma escolha explícita, e a cor é livre, com a cor
canônica da banda pré-selecionada para quem não quiser pensar nisso.

**Por que quatro bandas e não seis.** Medimos a correlação entre as curvas de banda
nas faixas de teste. Com seis bandas, pares vizinhos chegavam a **0,97** — duas
escolhas diferentes produziriam praticamente a mesma animação, e a decisão da pessoa
não significaria nada. Com quatro, o pior par cai para 0,84. Quatro é o que o material
sonoro sustenta de verdade.

### 5.3 O produto final: o Modo Cinema

A pessoa aperta **Assistir**. A interface some com fade, o canvas vai a tela cheia, e
a faixa toca do início ao fim com a animação inteira. Ao terminar: *Assistir de novo* ·
*Voltar a editar* · *Baixar a composição em PNG*.

Não há download de vídeo. A animação é vista no próprio site — decisão que elimina o
outro grande risco técnico (gravação de vídeo com áudio no navegador é frágil e não
funciona no Safari) e ainda entrega qualidade melhor: 60fps na resolução da tela, sem
compressão, sem espera.

## 6. Escopo do MVP

| # | Funcionalidade | Entra |
|---|---|---|
| 1 | Escolher a faixa entre as disponíveis | ✅ |
| 2 | Linha do tempo com forma de onda e seções da faixa | ✅ |
| 3 | Selecionar região e ouvir em loop | ✅ |
| 4 | Desenhar ponto, linha e forma | ✅ |
| 5 | Definir banda, comportamento, cor, reação | ✅ |
| 6 | Trecho herdado do loop, ajustável depois | ✅ |
| 7 | Selecionar, mover, redimensionar, apagar | ✅ |
| 8 | Desfazer / Refazer | ✅ |
| 9 | Prévia ao vivo — o elemento reage enquanto o loop toca | ✅ |
| 10 | **Modo Cinema** | ✅ |
| 11 | Tutorial em 3 passos + estado vazio instrutivo | ✅ |
| 12 | Baixar a composição em PNG | ✅ |
| 13 | Inserir imagens | ❌ Backlog (confirmado com o Pedro) |
| 14 | Upload da própria música | ❌ Backlog |
| 15 | Download de vídeo | ❌ Backlog |
| 16 | Compartilhar por link / colaborativo | ❌ Backlog |
| 17 | Log de eventos para pesquisa | ❌ Cortado |

## 7. As faixas

**Serão de domínio público.** Sem exigência de BPM ou tonalidade — o que abre o acervo
inteiro, incluindo gravações históricas com andamento livre, que a arquitetura
anterior teria descartado.

O único cuidado que permanece é de direitos: uma gravação carrega **dois direitos
independentes** — a obra e o fonograma. Uma composição de 1808 está em domínio
público, mas a gravação feita em 2018 não está. Fontes e detalhamento em
`MP3/README.md`.

**Já disponíveis** na pasta `MP3/`: três faixas de referência sintetizadas (sem
direitos de terceiros), seus mapas prontos, e a ferramenta que gera o mapa de qualquer
faixa nova.

## 8. Próximos documentos

- `01-pesquisa-referencias.md` — projetos semelhantes e direção de arte
- `02-PRD-arquitetura-tecnica.md` — stack, modelo de dados, o mapa da faixa, riscos
- `03-prompt-claude-design.md` — prompt pronto para o Claude Design
- `04-roadmap-desenvolvimento.md` — fases e critérios de aceite
- `MP3/README.md` — faixas, mapas e ferramentas de análise
