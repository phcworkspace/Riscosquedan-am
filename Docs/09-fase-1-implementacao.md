# 09 — Implementação da Fase 1 (registro para a dissertação)

**Data de implementação:** 15/09/2026
**Branch:** `fase-1-audio-e-mapa` (a partir de `main`)
**Commits desta fase:** `e6b83fc` → `215be1d` (8 commits, `git log --oneline main..fase-1-audio-e-mapa`)
**Plano seguido:** [`Docs/superpowers/plans/2026-09-15-fase-1-audio-e-mapa.md`](superpowers/plans/2026-09-15-fase-1-audio-e-mapa.md) — escrito e revisado por um agente reviewer dedicado antes da execução (status: Approved)
**Tag `fase-1`:** ainda **não criada** — ver seção 4. A SPEC define "pronto" como os 6 testes de aceite passando (seção 1), e três deles exigem confirmação humana ouvindo o áudio.

---

## 1. O que foi implementado

| Arquivo | Responsabilidade | Verificado por |
|---|---|---|
| `src/engine/tipos.ts` | Contratos de dados: `Banda`, `BANDAS` (ordem canônica), `Secao`, `MapaDaFaixa`, `Faixa`, `Regiao` | compilação (`tsc --noEmit`) |
| `src/engine/tokens.ts` | Tokens de UI para o motor (cores, medidas, brilho). Modificado: importa `Banda` de `tipos.ts`; o array rico de metadados foi renomeado de `BANDAS` para `BANDAS_INFO` para não colidir com o `BANDAS: Banda[]` de `tipos.ts` | compilação |
| `src/engine/Mapa.ts` | Carrega e consulta o `.map.json`: interpolação linear, energia geral, somas acumuladas por banda, seção por tempo, snap a batida/seção | **19 testes de unidade** (Vitest) |
| `src/engine/Audio.ts` | Web Audio puro: `AudioContext`, carregar/decodificar mp3, tocar, pausar, parar, loop de região com recriação de node, seek, volume, posição sempre recalculada | função pura `posicaoNaRegiao` com **6 testes de unidade**; classe inteira por verificação manual (seção 4) |
| `src/app/teste/page.tsx` | Bancada de teste descartável (SPEC seção 6): seletor de faixa, transporte, região, seek, 4 barras de banda em `requestAnimationFrame` | build + verificação HTTP (seção 3); testes de aceite T1-T6 pendentes de confirmação humana |
| `src/app/layout.tsx`, `src/app/page.tsx` | Boilerplate do `create-next-app` removido; metadata e página raiz mínimas | build |
| `vitest.config.ts`, `package.json` | Ambiente de testes (Vitest), scripts `test`/`test:watch` | `pnpm test` |

## 2. Decisões e desvios em relação à SPEC

- **`BANDAS_INFO`**: renomeação em `tokens.ts` para eliminar uma colisão de nome com `tipos.ts::BANDAS` antes que virasse um bug de import silencioso em fases futuras (nada ainda importava o nome antigo — confirmado por busca no código antes da mudança).
- **`secaoEm` no limite exato da duração**: a última seção fecha nos dois extremos (`t <= fim`), senão `t === duracaoSeg` não caía em seção nenhuma — bug de fronteira que a SPEC não detalhava.
- **Vitest**: adicionado como devDependency só para `engine/`. Justificativa: `Mapa.ts` é lógica pura, testável sem navegador; o projeto não tinha nenhum test runner. Não conflita com as proibições do `AGENTS.md` (que vetam bibliotecas de **áudio**, não de teste).
- **`posicaoNaRegiao` extraída como função pura**: é a única matemática de `Audio.ts` sem dependência de `AudioContext`, e a mais arriscada segundo a própria SPEC ("é aqui que dá errado", seção 5). Testada isoladamente com 6 casos, incluindo o wrap-around exato e um offset que não coincide com o início da região.
- **Dois reforços de correção não pedidos explicitamente pela SPEC, adicionados após revisão do plano:**
  - `onended` no source sem loop — sem isso, o estado ficava travado em `'tocando'` para sempre após o fim natural da reprodução (afeta o que a bancada mostra, não a corretude de `posicao()`, que já travava corretamente em `duracao`).
  - `try/catch` em `carregar()` — sem isso, uma falha de rede ou decodificação travava o estado em `'carregando'` indefinidamente.

## 3. Verificação automatizada realizada

Tudo abaixo foi executado e **passou**:

```
pnpm exec tsc --noEmit     → sem erros
pnpm build                  → build de produção OK; rotas: /, /_not-found, /teste (estáticas)
pnpm test                   → 25/25 testes verdes (19 Mapa + 6 posicaoNaRegiao)
```

**Checagem adicional de sanidade dos dados reais** (não estava no plano original; feita para
confirmar que a classe `Mapa` lê corretamente os `.map.json` de produção, não só a fixture):

| Faixa | Médias por banda | Banda "chapada" (>0,6)? | Pior correlação entre pares |
|---|---|---|---|
| 01-pulso | grave .438 · médio .445 · agudo .504 · brilho .524 | nenhuma | 0,837 |
| 02-correnteza | grave .524 · médio .408 · agudo .401 · brilho .377 | nenhuma | 0,727 |
| 03-nevoa | grave .375 · médio .279 · agudo .211 · brilho .126 | nenhuma | 0,722 |

Confirma os critérios de aceite da Fase 0B (`04-roadmap-desenvolvimento.md`) e o risco R3/R4
da SPEC — nenhuma banda perto do teto que indicaria animação chapada, nenhum par de bandas
correlacionado a ponto de a escolha da pessoa não significar nada.

**Checagem HTTP** (servidor local, `pnpm dev`):

| Recurso | Status | Content-Type | Tamanho |
|---|---|---|---|
| `/` | 200 | — | — |
| `/teste` (SSR) | 200 | — | contém o título e o botão "Começar" antes da hidratação |
| `/audio/faixas.json` | 200 | application/json | — |
| `/audio/01-pulso.mp3` | 200 | audio/mpeg | 1.682.978 bytes |
| `/audio/01-pulso.map.json` | 200 | application/json | 70.348 bytes |

## 4. Testes de aceite manuais (SPEC seção 7) — **pendentes de verificação humana**

Estes seis testes envolvem ouvir o áudio de verdade e julgar timing/percepção — nenhuma
ferramenta disponível nesta sessão tem audição ou controla um navegador real com gesto de
usuário (a política de autoplay exige um clique humano). Não foram simulados nem marcados
como aprovados sem essa confirmação.

| # | Teste | Como verificar | Resultado |
|---|---|---|---|
| T1 | O áudio toca | Escolher cada faixa, dar play, ouvir | **pendente** |
| T2 | Posição bate com o som (5 min) | Tocar "Pulso", conferir `posicao()`; deixar 5 min e reconferir | **pendente** |
| T3 | Loop de região funciona | Região 10→18s, repete indefinidamente | **pendente** |
| T4 | Trocar região em execução | Com loop rodando, mudar para 30→36s, sem estalo | **pendente** |
| T5 | Bandas batem com o que se ouve | Grave salta com o bumbo em "Pulso"; grave ≠ brilho em "Névoa" | **pendente** (dados já confirmam bandas distintas — seção 3 — falta o ouvido) |
| T6 | Seek para trás | Ir a 50s, voltar a 5s, sem travar | **pendente** |
| — | Determinismo em t=20.000 | Anotar 4 valores, tocar até o fim, voltar, comparar | **pendente** |

**Como rodar agora:** `pnpm dev` e abrir `http://localhost:3000/teste`. Servidor de
desenvolvimento já estava rodando ao final desta sessão de implementação.

## 5. Como rodar

```bash
cd riscos-que-dancam
pnpm install
pnpm dev        # http://localhost:3000/teste
pnpm test       # testes de unidade do engine/
pnpm build      # build de produção
```

## 6. Estado do repositório

- Remote: https://github.com/phcworkspace/Riscosquedan-am
- Branch desta fase: `fase-1-audio-e-mapa` (não mesclada em `main` ainda)
- Tag `fase-1`: não criada — depende da seção 4
- Deploy Vercel: não realizado nesta fase — requer decisão do usuário sobre qual
  conta/time usar (ver Task 15 do plano)

## 7. Próximo passo

Confirmar a seção 4 (5 minutos com headphones) e então:
1. Criar a tag `git tag -a fase-1`
2. Mesclar `fase-1-audio-e-mapa` em `main` (ver opções em
   `superpowers:finishing-a-development-branch`)
3. Seguir para a Fase 2 — Renderizador (`Docs/04-roadmap-desenvolvimento.md`), que consome
   exatamente `Mapa` e `Audio` construídos aqui, sem alterá-los.
