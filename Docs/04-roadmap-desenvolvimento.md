# 04 — Roadmap de Desenvolvimento

**Projeto:** Riscos que Dançam
**Data:** 14/09/2026 · *terceira revisão*

---

## Fase 0 — Duas frentes em paralelo

### 0A — Design (Claude Design) ✅ **concluída**
**Entregue:** 11 artboards publicados no Claude Design, mais `Docs/design/` com as
imagens de referência, os artboards em HTML (a fonte dos valores exatos), `tokens.css`,
`tailwind.tokens.ts` e o gerador.
**Como usar no código:** [`06-design-para-codigo.md`](06-design-para-codigo.md).

### 0B — Faixas
**Não bloqueia mais nada.** A pasta `MP3/` já tem 3 faixas de referência com os mapas
prontos, e a exigência de BPM e tonalidade desapareceu com a correção do conceito.

**Para cada faixa definitiva:**
1. Confirmar a licença — **obra e fonograma**, prazos independentes — e anotar o crédito
2. `python mapear_faixa.py faixa.mp3` para gerar o `.map.json`
3. Conferir no relatório: nenhuma banda com média acima de 0,6 (senão a animação fica
   chapada) e correlação entre bandas abaixo de ~0,85 (senão a escolha da banda não
   significa nada)
4. Copiar mp3 + map.json para `/public/audio/` e registrar em `faixas.json`

**Aceite:** o relatório do mapa mostra quatro bandas com relevos distintos, e as seções
detectadas batem com o que se ouve.

> Gravações históricas com andamento livre **agora servem** — não há mais grade
> rítmica a respeitar. Isso abre boa parte do acervo de domínio público que a
> arquitetura anterior teria descartado.

---

## Fase 1 — Áudio e mapa (a fundação)

> **Spec detalhada:** [`SPEC-fase-1.md`](SPEC-fase-1.md) — contratos de arquivo, regras de
> implementação, 6 testes de aceite e as armadilhas conhecidas.

> Sem interface. Uma página em branco, dois botões, e o console imprimindo os quatro
> valores de banda a cada quadro, no tempo certo.

**Tarefas:**
1. Projeto Next.js + TS + Tailwind, deploy inicial na Vercel
2. `engine/Audio.ts` — `AudioContext`, carregar e decodificar o mp3, play, pause, seek
3. **Loop de região** com `AudioBufferSourceNode` (`loop`, `loopStart`, `loopEnd`);
   trocar a região recria o node
4. `posicao()` calculada de `ctx.currentTime` a cada consulta — nunca acumulada
5. `engine/Mapa.ts` — carregar o `.map.json`, consulta interpolada por tempo, somas
   acumuladas por banda (para o comportamento `girar`)

**Aceite:**
- A posição reportada bate com o áudio ouvido, inclusive dentro do loop
- Mudar a região de loop em execução não estala nem perde a posição
- `valorDaBanda(mapa, 'grave', t)` acompanha o bumbo que se ouve
- Nenhum `AnalyserNode` / FFT roda no navegador

---

## Fase 2 — Renderizador

**Tarefas:**
1. `engine/Renderizador.ts` — loop de desenho, `devicePixelRatio` correto
2. Fundo do palco, perfurações de película, vinheta, grão
3. Primitivas: ponto, linha, polígono
4. `engine/comportamentos.ts` — as 4 funções puras + o piso de "acender"
5. Culling por janela temporal — só desenha quem existe no instante atual
6. Fade de entrada e saída de cada elemento

**Aceite:** 60fps com 120 elementos; arrastar o cursor para trás produz exatamente o
mesmo quadro que a reprodução normal naquele instante (teste de determinismo); nenhum
comportamento guarda estado mutável.

---

## Fase 3 — Linha do tempo

> O componente central. Vale tratar como uma fase própria.

**Tarefas:**
1. Forma de onda a partir do array `picos`
2. Seções com divisores e rótulos
3. Seleção de região por arraste, com alças; clique posiciona o cursor
4. Snap: às batidas quando `pulso.temPulsoClaro`, às seções quando não
5. Trilhas dos elementos — barras coloridas, empilhamento, clique seleciona, arraste
   move o trecho
6. Cursor de reprodução atravessando as camadas
7. Transporte: play, stop, loop, volume, tempo

**Aceite:** dá para navegar a faixa inteira só pela linha do tempo; selecionar uma
região e ouvi-la em loop é uma ação de um gesto.

---

## Fase 4 — Interação e composição

**Tarefas:**
1. `engine/Entrada.ts` — criar por clique (ponto) e arraste (linha, forma)
2. **Herança do trecho:** elemento criado com região ativa recebe `entrada`/`saida` dela
3. Hit-testing, seleção, mover, redimensionar, apagar
4. `store/useComposicao.ts` — documento, seleção, região, undo/redo
5. Painel do elemento: banda, comportamento, cor, reação, tamanho, opacidade, trecho
6. Mini-gráfico da curva da banda no trecho do elemento
7. Autosave em `localStorage`
8. Atalhos: Espaço, Delete, Ctrl+Z, Ctrl+Shift+Z, 1/2/3, L, Esc

**Aceite:** criar 20 elementos ouvindo trechos diferentes, sem erro no console;
undo/redo em 20 passos; recarregar recupera a composição.

---

## Fase 5 — Interface

**Tarefas:**
1. Implementar a casca a partir dos artboards
2. Tokens do design no `tailwind.config.ts`
3. Troca de faixa (carrega mp3 + mapa novos, mantém ou descarta a composição — decidir)
4. Tutorial em 3 passos, estado vazio instrutivo
5. Responsivo: tablet e mobile

**Aceite:** diferença visual mínima em relação aos artboards; uma pessoa que nunca viu
o projeto consegue ouvir um trecho e desenhar algo que reage, em menos de um minuto,
sem instrução verbal.

---

## Fase 6 — Modo Cinema

**Tarefas:**
1. Estado `cinema` no store; transição de layout com fade de 400ms
2. Loop desligado, posição zerada, reprodução do início ao fim
3. Densidade visual aumentada (halos, partículas, escala)
4. Barra de progresso fina que some com o mouse parado
5. `Entrada.ts` desabilitado
6. Fullscreen API com alternativa em overlay
7. Card de fim: *Assistir de novo* · *Voltar a editar* · *Baixar PNG*
8. `Esc` volta ao editor

**Aceite:** entrar e sair **não recria** o `AudioContext` nem recarrega o buffer; a
animação roda inteira sem queda de quadros; o PNG sai em boa resolução.

---

## Fase 7 — Polimento e verificação

1. Testes em Chrome, Firefox, Safari, Edge; desktop e mobile
2. Auditoria de acessibilidade (contraste, teclado)
3. Observar 3 pessoas usando sem orientação — teste de usabilidade, não pesquisa
4. Revisar os textos da interface
5. Créditos das faixas visíveis
6. Deploy final + link registrado na dissertação
7. `README.md` do repositório com créditos e referências

---

## Estimativa de esforço

| Fase | Esforço | Risco |
|---|---|---|
| 0A — Design | 10% | Baixo |
| 0B — Faixas | 5% | Baixo |
| 1 — Áudio e mapa | 15% | Médio |
| 2 — Renderizador | 15% | Médio |
| 3 — Linha do tempo | 20% | **Alto** |
| 4 — Interação | 20% | Médio |
| 5 — Interface | 10% | Baixo |
| 6 — Modo Cinema | 3% | Baixo |
| 7 — Polimento | 2% | Baixo |

O risco migrou. Com a síntese fora do projeto, o ponto mais delicado passou a ser a
**linha do tempo** — seleção de região, trilhas, snap e sincronia com o áudio
concentram a maior parte da complexidade de interação.

---

## Registro de decisões

| Data | Decisão | Motivo |
|---|---|---|
| 14/09 | **O desenho não gera som.** O áudio é sempre a faixa original | Correção do conceito pelo Pedro. A pessoa compõe a resposta visual ao som, não o som |
| 14/09 | **BPM e tonalidade deixam de ser requisito** | Sem síntese, não há o que afinar. Abre o acervo de domínio público inteiro |
| 14/09 | **Tone.js removido; Web Audio puro** | O scheduler musical era a única razão dele existir aqui |
| 14/09 | **Mapa da faixa pré-calculado em Python**, sem FFT no navegador | Determinismo, funciona em scrub, e libera quadro |
| 14/09 | **Quatro bandas, não seis** | Medido: com 6, pares vizinhos chegavam a 0,97 de correlação — a escolha da pessoa não significaria nada |
| 14/09 | **Curvas em dB com gama 1,6** | Em escala linear ficavam acima de 0,5 em 90% do tempo; a animação sairia chapada |
| 14/09 | **Cor livre, banda escolhida à parte** | O projeto é sobre o que a pessoa sente; ela pode sentir o grave como azul |
| 14/09 | **O elemento herda o trecho do loop** em que foi criado | É o gesto central: você desenha o que ouve, no trecho que ouve |
| 14/09 | **Linha do tempo vira o componente central** | O trabalho é percorrer a faixa, não preencher um quadro |
| 14/09 | **Modo Cinema** no lugar de exportar vídeo | Elimina o risco de gravação no navegador e entrega qualidade melhor |
| 14/09 | Imagens ficam no backlog | Confirmado com o Pedro; ponto, linha, forma e cor bastam |
| 14/09 | Log de eventos cortado | Não haverá teste com usuários |
| 14/09 | Canvas 2D puro, sem p5.js | Geometria simples; evita conflito com o ciclo de vida do React |
| 14/09 | **Supabase adiado para a Fase 6**, não entra no começo | O protótipo funciona inteiro com localStorage. O banco serve para salvar e compartilhar composições — feature boa, mas que não pode competir com a fase de risco pela atenção |
| 14/09 | Vercel desde o primeiro commit | Grátis, e descobre problema de build cedo. Os áudios (~5 MB no total) cabem com folga nos limites do plano Hobby |
