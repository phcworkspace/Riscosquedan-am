
<!-- Acrescente este bloco ao final do AGENTS.md do projeto, DEPOIS da linha
     <!-- END:nextjs-agent-rules -->. O `next dev` reescreve só o bloco dele;
     o que vier abaixo é preservado. -->

# Riscos que Dançam

Protótipo acadêmico de mestrado: a pessoa **escuta uma música e desenha o que
percebe**. Ela seleciona um trecho, ouve em loop, cria elementos visuais que respondem
a uma parte do som, e no final assiste à composição inteira rodando sobre o áudio
original.

## A regra que organiza tudo

**O áudio é sempre a faixa original. Nada do que a pessoa desenha produz som.**

O que ela compõe é a *resposta visual* ao som. Isso não é detalhe de implementação — é
o conceito do trabalho, e foi a correção que reescreveu a arquitetura inteira.

## Documentação (leia antes de codar)

| Arquivo | Quando |
|---|---|
| `Docs/SPEC-fase-1.md` | Antes de qualquer código da fase atual |
| `Docs/02-PRD-arquitetura-tecnica.md` | Arquitetura, modelo de dados, formato do mapa |
| `Docs/06-design-para-codigo.md` | Interface: tokens, medidas, o que é DOM e o que é canvas |
| `Docs/04-roadmap-desenvolvimento.md` | Em que fase estamos e o que é aceite |

## Stack

Next 16 (App Router) + React 19 + TypeScript · Tailwind 4 · **Canvas 2D puro** ·
**Web Audio API pura** · Zustand · Vercel · pnpm.
Sem backend, sem banco, sem login, sem coleta de dados.

Tailwind 4 não tem `tailwind.config.ts`: os tokens estão no `@theme` de
`src/app/globals.css` e viram utilitários sozinhos.

## Proibido neste projeto

- **Instalar Tone.js, p5.js, p5.sound, howler** ou qualquer biblioteca de áudio
- **Gerar som**: nenhum sintetizador, nenhuma nota, nenhuma escala musical
- **Rodar FFT ou `AnalyserNode` no navegador** — o `.map.json` já traz tudo,
  pré-calculado em Python
- **Acumular tempo entre quadros** — a posição vem sempre de `ctx.currentTime`
- **Guardar estado mutável nos comportamentos** — quebra o scrub e o determinismo
- **Exigir BPM ou tonalidade** de uma faixa — são informativos, nunca requisito
- **MediaRecorder, WebM, GIF** — o Modo Cinema substitui a exportação de vídeo
- **Supabase** antes da Fase 6
- **Mais de quatro bandas** de frequência (medido: com seis, bandas vizinhas chegam a
  0,97 de correlação e a escolha da pessoa deixa de significar algo)
- **Grade, régua ou notação musical dentro do palco** — ali a posição é composição
  livre; o tempo vive na linha do tempo

## Arquitetura

```
src/engine/     TypeScript puro, ZERO React — Audio, Mapa, Renderizador, Entrada,
                comportamentos, tokens, tipos
src/store/      Zustand
src/components/ React + Tailwind (casca da UI)
public/audio/   *.mp3 + *.map.json + faixas.json
```

O React monta, passa o canvas por `ref`, assina o store e destrói no unmount.
O motor nunca importa React.

## Convenções

- **Nomes de domínio em português**: palco, banda, comportamento, trecho, composicao,
  regiao, elemento. APIs do navegador e do React ficam em inglês.
- Comentário só quando explica um **porquê** que o código não mostra.
- Antes de instalar qualquer dependência nova, justifique — a lista atual é deliberada.

## Estado atual

Fase 0 concluída (design + faixas + mapas). **Em execução: Fase 1 — áudio e mapa.**
