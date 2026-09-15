# Riscos que Dançam — Documentação do Projeto

Protótipo web em que a pessoa **escuta uma música e desenha o que percebe**. Artefato de
pesquisa de mestrado, inspirado em Norman McLaren.

> **Escute. Desenhe o que você vê.**

---

## A regra que organiza tudo

**O áudio é sempre a faixa original. Nada do que a pessoa desenha produz som.**

Ela seleciona um trecho, ouve em repetição, e cria elementos que respondem a uma parte
específica daquele som — ao grave, ao médio, ao agudo, ao brilho. No final, assiste à
composição inteira rodando sobre a faixa.

---

## Índice

| Documento | Conteúdo |
|---|---|
| [`00-visao-geral.md`](00-visao-geral.md) | O conceito, a correção que o definiu, como a experiência funciona, escopo do MVP |
| [`01-pesquisa-referencias.md`](01-pesquisa-referencias.md) | Projetos semelhantes, referências conceituais e direção de arte |
| [`02-PRD-arquitetura-tecnica.md`](02-PRD-arquitetura-tecnica.md) | Stack, o mapa da faixa, modelo de dados, comportamentos, riscos |
| [`03-prompt-claude-design.md`](03-prompt-claude-design.md) | Prompt pronto para o Claude Design + refinamentos + checklist |
| [`04-roadmap-desenvolvimento.md`](04-roadmap-desenvolvimento.md) | Fases, critérios de aceite e registro de decisões |
| [`05-supabase-quando-e-como.md`](05-supabase-quando-e-como.md) | Por que o banco entra só na Fase 6, o schema pronto e os limites dos planos gratuitos |
| [`06-design-para-codigo.md`](06-design-para-codigo.md) | Como levar o design do Claude Design para o projeto Next.js — tokens, medidas, o que é DOM e o que é canvas |
| [`08-correcoes-do-ambiente.md`](08-correcoes-do-ambiente.md) | ⚠ **leia antes de codar** — o que foi instalado de fato (Next 16, Tailwind 4) e o que muda |
| [`07-rodar-no-cursor.md`](07-rodar-no-cursor.md) | ⬅ **do zero ao `npm run dev`** — criar o projeto, regras do agente e o primeiro prompt |
| [`SPEC-fase-1.md`](SPEC-fase-1.md) | ⬅ **comece aqui para codar** — motor de áudio e mapa, com contratos e testes de aceite |
| [`../MP3/README.md`](../MP3/README.md) | Faixas de referência, mapas e ferramentas de análise |

Material original do pré-projeto: pasta `Estudo/`.

---

## Resumo de uma página

**O gesto central:** o elemento desenhado **herda o trecho que está sendo ouvido**. Você
seleciona uma região, ela toca em loop, e tudo que você desenhar existe naquele trecho da
faixa. Você não configura isso — é consequência de ter desenhado ali.

**Cada elemento tem:**

| Propriedade | O que é |
|---|---|
| Tipo | ponto · linha · forma |
| Banda | a que parte do som responde: grave · médio · agudo · brilho |
| Comportamento | pulsar · girar · vibrar · acender |
| Cor | livre (a cor da banda vem pré-selecionada) |
| Reação | 0 a 1 — o quanto se move com o som |
| Trecho | quando existe na faixa |

Posição e tamanho no palco são composição visual pura — não têm significado sonoro.

**Stack:** Next 16 + React 19 + TypeScript · **Tailwind 4** (tokens em `@theme`, sem
`tailwind.config.ts`) · Canvas 2D puro · **Web Audio API pura, sem biblioteca de
áudio** · Zustand · Vercel · pnpm · análise em Python/librosa, offline.

**Três decisões técnicas que carregam o projeto:**

1. **O mapa da faixa é pré-calculado** em Python e servido como JSON. Nada de FFT no
   navegador. A animação fica determinística, funciona com o cursor arrastado para trás, e
   sobra quadro.
2. **Quatro bandas, não seis.** Medido: com seis, pares vizinhos chegavam a 0,97 de
   correlação — duas escolhas diferentes dariam a mesma animação.
3. **Nenhum comportamento guarda estado.** É o que torna o scrub possível e a peça
   reproduzível.

---

## Ordem de trabalho

```
Design (Claude Design)  +  Faixas e mapas
   →  Áudio e mapa  →  Renderizador  →  Linha do tempo
   →  Interação  →  Interface  →  Modo Cinema  →  Polimento
```

Comece pelo motor de áudio com o console imprimindo as curvas de banda. A parte mais
delicada depois é a **linha do tempo** — é onde o trabalho acontece.

Para montar o projeto e começar a codar: [`07-rodar-no-cursor.md`](07-rodar-no-cursor.md).
