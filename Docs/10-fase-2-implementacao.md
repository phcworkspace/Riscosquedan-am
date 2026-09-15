# 10 — Implementação da Fase 2 (registro para a dissertação)

**Data de implementação:** 15/09/2026
**Branch:** `fase-2-interface` (a partir de `main`, já com a tag `fase-1`)
**Plano seguido:** [`Docs/superpowers/plans/2026-09-15-fase-2-interface.md`](superpowers/plans/2026-09-15-fase-2-interface.md) — escrito e revisado por um agente reviewer dedicado; a primeira versão teve 3 problemas reais (estado de carregando ausente, troca de faixa cíclica em vez de listar as opções, cores em hex cru contra a regra do próprio prompt) corrigidos antes da execução.
**Prompt que originou a fase:** [`Docs/10-prompt-fase-2-interface.md`](10-prompt-fase-2-interface.md) — reordena o roadmap: a interface entra antes do renderizador (agora Fase 3) porque a Fase 1 já entrega tudo que a linha do tempo precisa.

---

## 1. O que foi implementado

| Arquivo | Responsabilidade |
|---|---|
| `src/app/layout.tsx` | Fontes do design: Space Grotesk + JetBrains Mono via `next/font/google`, `lang="pt-BR"` |
| `src/components/TelaDeEntrada.tsx` | Overlay de abertura — botão "Começar" libera o `AudioContext` (gesto do usuário) |
| `src/components/Cabecalho.tsx` | 52px: nome, subtítulo, faixa atual com menu listando as 3 faixas, botão "?" inerte |
| `src/components/Palco.tsx` | Moldura vazia: sprockets dinâmicos, grão, vinheta, canvas dimensionado (Fase 3 desenha nele), estado vazio e estado de carregando |
| `src/components/PainelFerramentas.tsx` | 300px: 3 botões de ferramenta (seleção visual, sem criar elementos), estado vazio, contador "0/120" |
| `src/components/LinhaDoTempo.tsx` | O componente central: régua, forma de onda (de `mapa.dados.picos`), divisores/rótulos de seção, região de loop com arraste + alças + snap (`mapa.encaixe`), cursor de reprodução |
| `src/components/Transporte.tsx` | Play/pausa/stop/loop/tempo/volume; ASSISTIR desabilitado (Modo Cinema é Fase 6) |
| `src/app/page.tsx` | Orquestra tudo: instancia `Audio`/`Mapa`, mantém o `requestAnimationFrame`, passa dados por props |

`src/engine/` **não foi tocado** (regra do prompt). `/teste` (Fase 1) continua no ar, sem alterações.

## 2. Decisões e desvios em relação ao prompt/mockup

- **Layout proporcional, não 1440×900 fixo.** Toda posição horizontal da linha do tempo (`x = t/duracaoSeg * largura`) é calculada contra a largura real do contêiner via `ResizeObserver`, nunca contra os pixels absolutos do artboard.
- **Forma de onda com N barras, não 320 fixas.** `picos` tem 1200 valores; o número de barras desenhadas é `largura / 4.5px`, reamostrando o array proporcionalmente.
- **Sprockets em quantidade dinâmica**, mesma lógica.
- **Decoração da Tela de Entrada simplificada**: a técnica (formas com a paleta de elementos, vinheta, grão) é a mesma do mockup; as 13 coordenadas exatas do artboard não são reproduzidas — são preenchimento de moodboard, não contrato de design.
- **Troca de faixa por menu**, não por clique cíclico — corrigido durante o review do plano para atender "listar as três" do prompt.
- **Estado de carregando visível** em `Palco` e no bloco da linha do tempo enquanto `decodeAudioData` roda — também corrigido durante o review (a primeira versão do plano deixava a linha do tempo simplesmente desaparecer nesse intervalo).
- **Cores via utilitários Tailwind do `@theme`** (`bg-surface`, `text-tinta-fraca`, `border-loop`, `h-cabecalho`/`w-painel`/`h-tempo` de `--spacing-*` etc.), com duas exceções documentadas em hex direto por não terem token: o fundo `#08080A` da Tela de Entrada e o `#22222A` do botão de ferramenta ativo.
- **ASSISTIR fica `disabled`**, não só visualmente inerte — evita que a pessoa clique e ache que quebrou.

## 3. Verificação automatizada realizada

Tudo abaixo foi executado e **passou**:

```
pnpm exec tsc --noEmit     → sem erros
pnpm build                  → build de produção OK; rotas: /, /_not-found, /teste
pnpm test                   → 25/25 (intactos — engine/ não foi tocado)
```

**Checagem HTTP** (servidor local, `pnpm dev`):

| Recurso | Status | Observação |
|---|---|---|
| `/` | 200 | HTML inicial correto: `lang="pt-BR"`, classes das novas fontes (Space Grotesk/JetBrains Mono) presentes |
| `/teste` | 200 | Fase 1 intacta |
| Log do `next dev` | sem erros | Nenhum erro/warning de render após as requisições |

**Por que o corpo de `/` vem "vazio" no HTML server-rendered:** `page.tsx` é um Client
Component que só mostra a `TelaDeEntrada` depois que `faixas.json` chega (`faixas.length`).
No SSR essa `fetch` ainda não rodou, então o servidor renderiza `null` — o conteúdo aparece
após a hidratação no navegador. Isso é esperado, não um defeito; só significa que `curl`
não é suficiente para ver a tela pronta, só para confirmar que o HTML inicial é válido e
sem erro.

## 4. Pendente de verificação humana

Sem navegador real nem audição, esta sessão não pode confirmar:

| # | O que verificar | Como |
|---|---|---|
| 1 | A Tela de Entrada aparece e "Começar" libera o áudio | Abrir `/`, clicar Começar |
| 2 | O menu de faixas no cabeçalho lista as 3 e troca corretamente, mostrando "Carregando faixa…" durante a troca | Clicar no nome da faixa |
| 3 | Arrastar na forma de onda cria a região amarela; alças redimensionam; snap encaixa em batida/seção | Arrastar na linha do tempo |
| 4 | O cursor acompanha a reprodução, atravessando as camadas | Dar play e observar |
| 5 | Comparação visual com `Docs/design/png/PalcoVazio.png` e `Escutando.png` | Lado a lado com `/` |
| 6 | Interação por toque (mobile/tablet) | Sem dispositivo físico nesta sessão |

**Como rodar agora:** `pnpm dev` e abrir `http://localhost:3000/`. Servidor de
desenvolvimento já estava rodando ao final desta sessão de implementação.

## 5. Estado do repositório

- Remote: https://github.com/phcworkspace/Riscosquedan-am
- Branch desta fase: `fase-2-interface` (não mesclada em `main` ainda)
- Tag: nenhuma criada para esta fase ainda — depende da seção 4

## 6. Próximo passo

Confirmar a seção 4 e então mesclar `fase-2-interface` em `main`. Depois, Fase 3 —
Renderizador (`Docs/10-prompt-fase-2-interface.md`, seção "Depois desta fase"): desenhar
os elementos no `<canvas>` que `Palco.tsx` já deixou dimensionado e em branco.
