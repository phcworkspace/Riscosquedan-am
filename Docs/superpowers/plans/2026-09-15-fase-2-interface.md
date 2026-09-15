# Fase 2 — Casca da Interface e Linha do Tempo — Plano de Implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Construir a tela real (rota `/`) sobre o motor da Fase 1: tela de entrada, cabeçalho, moldura do palco (vazio de elementos), painel direito e a linha do tempo funcionando de verdade — forma de onda, seções, seleção de região com loop e snap, cursor de reprodução, transporte. `/teste` continua existindo, intacto.

**Architecture:** Componentes de apresentação em `src/components/`, recebendo tudo por props (nenhum busca estado sozinho) — assim a Fase 4 pluga o Zustand sem reescrevê-los. `src/app/page.tsx` é o único orquestrador: instancia `Audio`/`Mapa` (mesmo padrão de `/teste`), mantém o `requestAnimationFrame`, e passa dados e callbacks para baixo. `src/engine/` não é tocado — é consumido como está.

**Tech Stack:** Next.js 16 (App Router) + React 19 + TypeScript · Tailwind 4 (utilitários do `@theme`) · SVG para a forma de onda · nenhuma dependência nova.

---

## Notas de arquitetura (leia antes de começar)

1. **Por que não há TDD/testes de unidade nesta fase.** Diferente da Fase 1 (lógica pura em `engine/`), esta fase é composição visual e interação de mouse/touch sobre componentes React — não há `jsdom`/Testing Library configurados, e adicionar essa infraestrutura só para esta fase seria desproporcional (o próprio prompt da Fase 2, `Docs/10-prompt-fase-2-interface.md`, define a verificação como `tsc`, `build`, os testes existentes continuando 25/25, e **comparação visual manual** com os PNGs — não pede testes novos). Os 25 testes de `engine/` são a rede de segurança: nenhuma task desta fase deve fazer esse número mudar.

2. **Fonte da verdade do design:** os `.dc.html` em `Docs/design/fonte/`, não os PNGs. Todo valor de px/cor abaixo foi lido diretamente de `Entrada.dc.html`, `PalcoVazio.dc.html`, `Escutando.dc.html` e `Sistema.dc.html` — não arredondado, não estimado.

3. **Layout dinâmico, não os 1440×900 do mockup.** O mockup fixa `1440×900` porque é um artboard estático. A regra real está em `Docs/06-design-para-codigo.md` seção 3.3: `h-dvh` no contêiner, `flex-1` no palco, `min-h-0` na linha intermediária. Toda medida horizontal da linha do tempo (posição do cursor, largura das barras da forma de onda, posição dos divisores de seção) é **proporcional** (`t / duracaoSeg`), nunca um pixel absoluto copiado do mockup.

4. **A decoração de fundo da Tela de Entrada é simplificada.** `Entrada.dc.html` tem 13 formas decorativas em coordenadas fixas — isso é preenchimento aleatório de moodboard, não um contrato de design (o prompt da Fase 2 só exige que a tela "pareça intencional"). Reproduzo a **técnica** (formas com `drop-shadow`, paleta de bandas, opacidade baixa, vinheta radial, grão) com uma composição própria mais simples, não as 13 coordenadas exatas.

5. **`picos` tem 1200 valores; a forma de onda é desenhada com quantas barras couberem.** O mockup usa 320 barras porque é a largura fixa do artboard (1440px ÷ 4.5px de passo). Na tela real, o número de barras é `Math.floor(largura / 4.5)`, reamostrando `picos` proporcionalmente — nunca lendo 1200 índices fixos num container de largura variável.

6. **Perfurações (sprockets):** medidas fixas (14×10px, raio 2, 6px da borda), mas **quantidade dinâmica** — `Math.floor((largura - 12) / 34) + 1`, nunca a lista de 33 `<div>`s hardcoded do mockup (que vale só para 1140px).

7. **Rótulo de seção nos divisores da forma de onda:** confirmado contra os dados reais de "01-pulso" — o divisor de cada seção fica na proporção `secao.inicio / duracaoSeg` da largura, com o rótulo 5px à direita do divisor. A primeira seção (que começa em 0) não tem divisor.

8. **Cores: sempre os utilitários do `@theme`, exceto duas exceções documentadas onde
   nenhum token corresponde.** Regra explícita do prompt da Fase 2 ("não hex soltos no
   JSX"). As duas exceções ficam com hex direto e um comentário explicando por quê: o
   fundo/gradiente `#08080A` da Tela de Entrada (Task 2 — um preto ligeiramente diferente
   de `--color-base`, específico daquela tela) e o fundo `#22222A` do botão de ferramenta
   ativo (Task 5 — não é nenhum dos tons de superfície existentes). Todo o resto usa
   `bg-*`/`text-*`/`border-*`/`fill-*`/`stroke-*` dos tokens já declarados em
   `globals.css`, incluindo `h-cabecalho`/`w-painel`/`h-tempo` (de `--spacing-*`) em vez
   de repetir os pixels em arbitrário.

---

## Estrutura de arquivos

```
src/components/
  TelaDeEntrada.tsx     NOVO — overlay de abertura, botão "Começar" → Audio.iniciar()
  Cabecalho.tsx         NOVO — 52px: nome, subtítulo, faixa atual (troca), botão "?" inerte
  Palco.tsx             NOVO — moldura vazia: sprockets, grão, vinheta, canvas placeholder, estado vazio
  PainelFerramentas.tsx NOVO — 300px: 3 botões de ferramenta (visual), estado vazio, contador
  LinhaDoTempo.tsx      NOVO — régua + forma de onda + trilhas vazias + região de loop + cursor
  Transporte.tsx        NOVO — 32px: play/pause/stop/loop/tempo/volume/ASSISTIR (inerte)
src/app/
  page.tsx              MODIFICADO — orquestra tudo (era o placeholder da Fase 1)
  layout.tsx            MODIFICADO — Space Grotesk + JetBrains Mono via next/font/google
Docs/
  10-fase-2-implementacao.md   NOVO — documentação acadêmica (ao final)
```

`/teste` (`src/app/teste/page.tsx`) e todo `src/engine/` **não são tocados**.

---

## Task 1: Fontes — `layout.tsx`

**Files:**
- Modify: `src/app/layout.tsx`

- [ ] **Step 1: Trocar Geist por Space Grotesk e JetBrains Mono**

```tsx
import type { Metadata } from "next";
import { Space_Grotesk, JetBrains_Mono } from "next/font/google";
import "./globals.css";

const sans = Space_Grotesk({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-sans",
});

const mono = JetBrains_Mono({
  subsets: ["latin"],
  weight: ["400", "500"],
  variable: "--font-mono",
});

export const metadata: Metadata = {
  title: "Riscos que Dançam",
  description: "Protótipo de mestrado — escute uma faixa e desenhe o que percebe.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="pt-BR" className={`${sans.variable} ${mono.variable} h-full antialiased`}>
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}
```

> `--font-sans`/`--font-mono` são as variáveis que `src/app/globals.css` já declara no
> `@theme` (`font-family: var(--font-sans)` no `body`) — o `next/font` só precisa apontar
> para elas, sem duplicar a declaração de família.

- [ ] **Step 2: Verificar**

Run: `pnpm exec tsc --noEmit && pnpm build`
Expected: sem erros. `lang="pt-BR"` é uma correção de acessibilidade barata (o conteúdo é
todo em português) — sem isso, leitores de tela assumem inglês.

- [ ] **Step 3: Commit**

```bash
git add src/app/layout.tsx
git commit -m "feat: fontes do design (Space Grotesk + JetBrains Mono)"
```

---

## Task 2: `TelaDeEntrada.tsx`

**Files:**
- Create: `src/components/TelaDeEntrada.tsx`

Valores de `Entrada.dc.html`: fundo `#08080A`, vinheta radial `rgba(8,8,10,.55)→rgba(8,8,10,.94)`,
grão a 3.5% de opacidade, texto "Protótipo · pesquisa de mestrado" (11px, tracking .34em,
maiúsculo, `#8A8A94`), título 20px/700/tracking -0.01em, subtítulo 13px `#8A8A94` max-width
420px, botão "Começar" 40px altura, pílula `border-radius:20px`, fundo `#EDEDF0`, texto
`#0B0B0D` 13px/600.

- [ ] **Step 1: Escrever o componente**

```tsx
'use client';

// Paleta livre dos elementos (--color-el-1..8 no @theme) — as mesmas cores que a
// pessoa vai usar para colorir o que desenha, aqui só como textura de fundo.
const FORMAS_DECORATIVAS = [
  { tipo: 'circulo' as const, x: 18, y: 24, r: 2.4, classe: 'fill-el-1' },   // #FF3B30
  { tipo: 'circulo' as const, x: 82, y: 68, r: 1.1, classe: 'fill-el-6' },   // #5AC8FA
  { tipo: 'circulo' as const, x: 30, y: 78, r: 1.6, classe: 'fill-el-4' },   // #30D158
  { tipo: 'linha' as const, x1: 12, y1: 55, x2: 24, y2: 50, classe: 'stroke-el-5' }, // #0A84FF
  { tipo: 'linha' as const, x1: 70, y1: 20, x2: 80, y2: 26, classe: 'stroke-el-7' }, // #C77DFF
  { tipo: 'circulo' as const, x: 88, y: 14, r: 1.8, classe: 'fill-el-3' },   // #FFB300
];

/**
 * Tela de abertura. Existe por uma razão técnica — o navegador só libera o
 * AudioContext depois de um gesto do usuário — mas não deve parecer um aviso.
 *
 * O fundo `#08080A` e o gradiente da vinheta são exceções deliberadas à regra de
 * "sem hex solto": são um preto ligeiramente mais escuro que `--color-base`
 * (#0B0B0D), específico desta tela no mockup, sem token próprio no @theme — criar
 * um token só para uma diferença de 3 valores de RGB não vale a pena.
 */
export function TelaDeEntrada({ onComecar }: { onComecar: () => void }) {
  return (
    <div className="fixed inset-0 flex items-center justify-center z-50" style={{ background: '#08080A' }}>
      <svg
        width="100%" height="100%" viewBox="0 0 100 100" preserveAspectRatio="none"
        className="absolute inset-0 opacity-50"
      >
        {FORMAS_DECORATIVAS.map((f, i) =>
          f.tipo === 'circulo' ? (
            <circle key={i} cx={f.x} cy={f.y} r={f.r} className={f.classe} opacity={0.21} />
          ) : (
            <line key={i} x1={f.x1} y1={f.y1} x2={f.x2} y2={f.y2} className={f.classe}
                  strokeWidth={0.4} strokeLinecap="round" opacity={0.21} />
          )
        )}
      </svg>
      <div
        className="absolute inset-0"
        style={{ background: 'radial-gradient(ellipse at 50% 50%, rgba(8,8,10,0) 0%, rgba(8,8,10,.55) 38%, rgba(8,8,10,.94) 100%)' }}
      />
      <div className="grao absolute inset-0" />
      <div className="relative flex flex-col items-center">
        <div className="text-[11px] tracking-[0.34em] uppercase text-tinta-fraca mb-[26px]">
          Protótipo · pesquisa de mestrado
        </div>
        <div className="text-titulo font-bold tracking-[-0.01em]">Riscos que Dançam</div>
        <div className="text-[13px] text-tinta-fraca mt-3.5 max-w-[420px] text-center leading-[1.6]">
          Escute uma música e desenhe o que você percebe nela. No final, assista à sua composição.
        </div>
        <button
          onClick={onComecar}
          className="mt-[38px] h-10 px-[30px] rounded-[20px] bg-tinta text-base text-[13px] font-semibold border-none cursor-pointer"
        >
          Começar
        </button>
      </div>
    </div>
  );
}
```

> `text-titulo` é o token de tamanho (20px, com o tracking -0.01em já embutido em
> `--text-titulo--letter-spacing`) — o `tracking-[-0.01em]` no JSX fica redundante mas
> inofensivo; mantido só por clareza de leitura do componente.

- [ ] **Step 2: Commit**

```bash
git add src/components/TelaDeEntrada.tsx
git commit -m "feat(ui): tela de entrada"
```

---

## Task 3: `Cabecalho.tsx`

**Files:**
- Create: `src/components/Cabecalho.tsx`

Valores de `PalcoVazio.dc.html`/`Escutando.dc.html`: altura 52px, padding lateral 18px,
fundo `#1A1A1F`, borda inferior 1px `#2A2A31`. Título 14px/600/tracking -0.01em + subtítulo
11px `#8A8A94`. Nome da faixa 12px, sublinhado pontilhado, clicável. Botão "?" 32px,
circular, borda 1px `#2A2A31`.

- [ ] **Step 1: Escrever o componente**

```tsx
'use client';

import { useState } from 'react';
import type { Faixa } from '@/engine/tipos';

export function Cabecalho({
  faixa, faixas, onEscolherFaixa,
}: {
  faixa: Faixa | null;
  faixas: Faixa[];
  onEscolherFaixa: (id: string) => void;
}) {
  const [menuAberto, setMenuAberto] = useState(false);

  return (
    <header className="h-cabecalho shrink-0 flex items-center justify-between px-[18px] bg-surface border-b border-linha box-border">
      <div className="flex items-baseline gap-3">
        <span className="text-[14px] font-semibold tracking-[-0.01em]">Riscos que Dançam</span>
        <span className="text-rotulo text-tinta-fraca">Escute. Desenhe o que você vê.</span>
      </div>
      <div className="flex items-center gap-4">
        {faixa && (
          <div className="relative">
            <button
              onClick={() => setMenuAberto(a => !a)}
              className="text-[12px] text-tinta border-b border-dotted border-linha pb-0.5 bg-transparent cursor-pointer"
            >
              {faixa.titulo} · {faixa.caracter}
            </button>
            {menuAberto && (
              <div className="absolute right-0 top-full mt-2 w-56 bg-surface border border-linha rounded-md overflow-hidden z-10">
                {faixas.map(f => (
                  <button
                    key={f.id}
                    onClick={() => { onEscolherFaixa(f.id); setMenuAberto(false); }}
                    className={`w-full text-left px-3 py-2 text-[12px] bg-transparent border-none cursor-pointer ${f.id === faixa.id ? 'text-tinta' : 'text-tinta-fraca'}`}
                  >
                    {f.titulo} · {f.caracter}
                  </button>
                ))}
              </div>
            )}
          </div>
        )}
        <div
          className="w-8 h-8 rounded-full border border-linha flex items-center justify-center text-tinta-fraca"
          title="Tutorial (ainda não implementado)"
        >
          <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor"
               strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="9" />
            <path d="M9.6 9.2a2.4 2.4 0 1 1 2.9 2.4v1.4" />
            <path d="M12.4 16.4h.01" />
          </svg>
        </div>
      </div>
    </header>
  );
}
```

> Os utilitários `bg-surface`, `border-linha`, `text-tinta-fraca`, `h-cabecalho` etc. vêm
> do `@theme` de `globals.css` (já aplicado desde a Fase 0) — `h-cabecalho` em particular
> vem de `--spacing-cabecalho:52px`, que o Tailwind 4 transforma em utilitário de
> width/height/padding/margin/gap automaticamente. `text-rotulo` inclui o tracking de
> 0.08em declarado no token — não precisa repetir `letter-spacing` no JSX.
>
> **Por que um menu simples em vez de um clique único trocando faixa:** o prompt da Fase 2
> pede "listar as três" — um clique cíclico não deixa a pessoa ver as outras opções antes
> de escolher.

- [ ] **Step 2: Commit**

```bash
git add src/components/Cabecalho.tsx
git commit -m "feat(ui): cabecalho"
```

---

## Task 4: `Palco.tsx` — a moldura vazia

**Files:**
- Create: `src/components/Palco.tsx`

Perfurações 14×10, raio 2, `bg-sprocket`, passo 34px, quantidade dinâmica. Margem: 6px
verticalmente (`06-design-para-codigo.md` seção 3.5, "6px da borda" — só o afastamento do
topo/base); horizontalmente os `.dc.html` começam em ~19px (`PalcoVazio.dc.html`, palco de
1140px) — reproduzido aqui como a mesma constante `MARGEM_H`, não estimado. Grão `.grao` e
vinheta `.vinheta` (já em `globals.css`), sobrepostos em DOM — não no canvas. Estado vazio
central: círculo tracejado + texto (ver `PalcoVazio.dc.html`). Estado de carregando: a
própria SPEC original e o prompt da Fase 2 exigem feedback visível enquanto
`decodeAudioData` roda — este componente também cobre isso (prop `carregando`).

- [ ] **Step 1: Escrever o componente**

```tsx
'use client';

import { useEffect, useRef, useState } from 'react';

const MARGEM_H_SPROCKET = 19;
const MARGEM_V_SPROCKET = 6;
const PASSO_SPROCKET = 34;

function Sprockets({ largura, borda }: { largura: number; borda: 'top' | 'bottom' }) {
  if (largura <= 0) return null;
  const disponivel = largura - MARGEM_H_SPROCKET * 2;
  const quantidade = Math.max(0, Math.floor(disponivel / PASSO_SPROCKET) + 1);
  return (
    <>
      {Array.from({ length: quantidade }, (_, i) => (
        <div
          key={i}
          className="absolute w-3.5 h-2.5 rounded-sm bg-sprocket"
          style={{ [borda]: MARGEM_V_SPROCKET, left: MARGEM_H_SPROCKET + i * PASSO_SPROCKET }}
        />
      ))}
    </>
  );
}

export function Palco({ vazio, carregando }: { vazio: boolean; carregando: boolean }) {
  const ref = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [tamanho, setTamanho] = useState({ largura: 0, altura: 0 });

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const obs = new ResizeObserver(([entry]) => {
      setTamanho({ largura: entry.contentRect.width, altura: entry.contentRect.height });
    });
    obs.observe(el);
    return () => obs.disconnect();
  }, []);

  // canvas dimensionado com devicePixelRatio correto — o Renderizador (Fase 3)
  // desenha nele; por enquanto fica em branco. Depende de largura E altura: um
  // resize só de altura (janela mais baixa, largura igual) também precisa
  // redimensionar o backing store, senão o canvas fica com pixels obsoletos.
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || tamanho.largura === 0) return;
    const dpr = window.devicePixelRatio || 1;
    canvas.width = tamanho.largura * dpr;
    canvas.height = tamanho.altura * dpr;
    canvas.style.width = `${tamanho.largura}px`;
    canvas.style.height = `${tamanho.altura}px`;
  }, [tamanho]);

  return (
    <main ref={ref} className="flex-1 relative bg-palco overflow-hidden min-w-0">
      <canvas ref={canvasRef} className="absolute inset-0" />
      <div className="vinheta absolute inset-0 pointer-events-none" />
      <div className="grao absolute inset-0 pointer-events-none" />
      <Sprockets largura={tamanho.largura} borda="top" />
      <Sprockets largura={tamanho.largura} borda="bottom" />
      {carregando && (
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div className="text-[12.5px] text-tinta-fraca">Carregando faixa…</div>
        </div>
      )}
      {!carregando && vazio && (
        <div className="absolute inset-0 flex flex-col items-center justify-center gap-5 pointer-events-none">
          <svg width="54" height="54" viewBox="0 0 54 54">
            <circle cx="27" cy="27" r="13" className="fill-tinta-fraca" opacity="0.2" />
            <circle cx="27" cy="27" r="22" fill="none" className="stroke-tinta-fraca" strokeWidth="1"
                    strokeDasharray="3 5" opacity="0.35" />
          </svg>
          <div className="text-[12.5px] text-tinta-fraca text-center leading-[1.65]">
            Selecione um trecho na linha do tempo e escute.<br />Depois desenhe o que você vê.
          </div>
        </div>
      )}
    </main>
  );
}
```

- [ ] **Step 2: Verificar visualmente que os sprockets não quebram em larguras pequenas**

Run: `pnpm dev`, abrir `/`, redimensionar a janela para ~500px de largura.
Expected: nenhum sprocket ultrapassa a borda do palco; a quantidade se ajusta.

- [ ] **Step 3: Commit**

```bash
git add src/components/Palco.tsx
git commit -m "feat(ui): moldura do palco (sprockets, grao, vinheta, estado vazio)"
```

---

## Task 5: `PainelFerramentas.tsx`

**Files:**
- Create: `src/components/PainelFerramentas.tsx`

300px, padding 16px. Três botões 76×76, raio 6. Ativo: borda `#EDEDF0`, fundo `#22222A`.
Inativo: borda `#2A2A31`, transparente. Divisor 1px. Estado vazio central. Rodapé 44px,
ícone + contador mono "0 / 120".

- [ ] **Step 1: Escrever o componente**

```tsx
'use client';

import { useState } from 'react';

type Ferramenta = 'ponto' | 'linha' | 'forma';

const FERRAMENTAS: { id: Ferramenta; rotulo: string; icone: React.ReactNode }[] = [
  { id: 'ponto', rotulo: 'Ponto', icone: <circle cx="12" cy="12" r="6" fill="currentColor" /> },
  { id: 'linha', rotulo: 'Linha', icone: <path d="M5 19 19 5" /> },
  { id: 'forma', rotulo: 'Forma', icone: <path d="M12 4 21 20H3Z" /> },
];

export function PainelFerramentas({ totalElementos = 0 }: { totalElementos?: number }) {
  // Seleção só visual nesta fase — criar elementos de verdade é Fase 4.
  const [ativa, setAtiva] = useState<Ferramenta>('ponto');

  return (
    <aside className="w-painel shrink-0 bg-surface border-l border-linha flex flex-col box-border">
      <div className="p-4 pb-3.5">
        <div className="text-rotulo text-tinta-fraca uppercase mb-1.5">Ferramenta</div>
        <div className="flex gap-2">
          {FERRAMENTAS.map(f => {
            const estaAtiva = f.id === ativa;
            return (
              <button
                key={f.id}
                onClick={() => setAtiva(f.id)}
                className={`w-[76px] h-[76px] rounded-lg flex flex-col items-center justify-center gap-[7px] box-border border ${
                  estaAtiva ? 'border-tinta bg-[#22222A]' : 'border-linha bg-transparent'
                }`}
              >
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none"
                     className={estaAtiva ? 'text-tinta' : 'text-tinta-fraca'}
                     stroke="currentColor" strokeWidth="1.5"
                     strokeLinecap="round" strokeLinejoin="round">
                  {f.icone}
                </svg>
                <span className={`text-[10px] ${estaAtiva ? 'text-tinta' : 'text-tinta-fraca'}`}>
                  {f.rotulo}
                </span>
              </button>
            );
          })}
        </div>
      </div>
      <div className="h-px bg-linha" />
      <div className="flex-1 flex items-center justify-center px-[34px] text-center">
        <span className="text-[12px] leading-[1.55] text-tinta-fraca">
          Selecione um elemento no palco para ajustá-lo
        </span>
      </div>
      <div className="h-px bg-linha" />
      <div className="h-11 flex items-center justify-between px-4">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" className="text-tinta-fraca"
             stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
          <path d="M4 7h16M9 7V5h6v2M7 7l1 12h8l1-12" />
        </svg>
        <span className="text-rotulo text-tinta-fraca font-mono">{totalElementos} / 120</span>
      </div>
    </aside>
  );
}
```

> `bg-[#22222A]` fica como valor arbitrário mesmo — é um tom só do estado "ferramenta
> ativa" que não tem token próprio no `@theme` (não é `surface`, `surface-alt` nem
> `palco`). Todo o resto da paleta usada aqui (`border-tinta`, `border-linha`,
> `text-tinta-fraca`) tem token.

- [ ] **Step 2: Commit**

```bash
git add src/components/PainelFerramentas.tsx
git commit -m "feat(ui): painel de ferramentas (visual, sem criar elementos ainda)"
```

---

## Task 6: `LinhaDoTempo.tsx` — régua e forma de onda

**Files:**
- Create: `src/components/LinhaDoTempo.tsx`

O componente central. Esta task cobre a base estática: régua (18px, marcas a cada 5s) e
forma de onda (54px, a partir de `mapa.dados.picos`, com divisores/rótulos de seção).
Interação de região, snap e cursor vêm nas próximas tasks, no mesmo arquivo.

- [ ] **Step 1: Escrever a base do componente**

```tsx
'use client';

import { useEffect, useMemo, useRef, useState } from 'react';
import type { Mapa } from '@/engine/Mapa';
import type { Regiao } from '@/engine/tipos';

const PASSO_REGUA_SEG = 5;
const PASSO_BARRA_PX = 4.5;
const LARGURA_BARRA_PX = 3.3;

function Regua({ duracaoSeg, largura }: { duracaoSeg: number; largura: number }) {
  const marcas = [];
  for (let t = 0; t <= duracaoSeg; t += PASSO_REGUA_SEG) {
    const x = (t / duracaoSeg) * largura;
    marcas.push(
      <div key={t}>
        <div className="absolute bg-linha" style={{ left: x, top: 0, height: 6, width: 1 }} />
        <div className="absolute text-tinta-fraca font-mono" style={{ left: x + 4, top: 2, fontSize: 9 }}>
          {t}s
        </div>
      </div>
    );
  }
  return <div className="relative h-[18px] border-b border-linha-soft">{marcas}</div>;
}

function FormaDeOnda({
  mapa, largura,
}: {
  mapa: Mapa; largura: number;
}) {
  const barras = useMemo(() => {
    if (largura <= 0) return [];
    const picos = mapa.dados.picos;
    if (!picos?.length) return [];
    const n = Math.floor(largura / PASSO_BARRA_PX);
    const resultado: { x: number; altura: number }[] = [];
    for (let i = 0; i < n; i++) {
      // reamostra picos (1200 valores) para n barras — mesma técnica de downsampling
      // usada pelo mockup, só que com n dinâmico em vez de fixo em 320
      const idx = Math.min(picos.length - 1, Math.floor((i / n) * picos.length));
      resultado.push({ x: i * PASSO_BARRA_PX, altura: picos[idx] });
    }
    return resultado;
  }, [mapa, largura]);

  const divisores = useMemo(() => {
    if (largura <= 0) return [];
    return mapa.dados.secoes
      .filter(s => s.inicio > 0) // a primeira seção não tem divisor à esquerda
      .map(s => ({ x: (s.inicio / mapa.dados.duracaoSeg) * largura, rotulo: s.rotulo }));
  }, [mapa, largura]);

  const altura = 54;
  return (
    <div className="relative border-b border-linha-soft" style={{ height: altura }}>
      <svg width={largura} height={altura} className="absolute inset-0">
        {barras.map((b, i) => {
          const h = b.altura * altura;
          return (
            <rect key={i} x={b.x} y={(altura - h) / 2} width={LARGURA_BARRA_PX} height={h}
                  className="fill-tinta-fraca" opacity={0.4} />
          );
        })}
      </svg>
      {divisores.map((d, i) => (
        <div key={i}>
          <div className="absolute bg-linha" style={{ left: d.x, top: 0, bottom: 0, width: 1 }} />
          <div className="absolute text-tinta-fraca" style={{ left: d.x + 5, top: 3, fontSize: 9 }}>
            {d.rotulo}
          </div>
        </div>
      ))}
    </div>
  );
}
```

> Envelope simétrico: as barras do mockup crescem a partir do centro vertical (`y =
> (altura-h)/2`), não do topo — reproduzido acima.

- [ ] **Step 2: Verificar que renderiza sem interação ainda**

Adicionar temporariamente ao fim do arquivo:

```tsx
export function LinhaDoTempo({ mapa }: { mapa: Mapa }) {
  const ref = useRef<HTMLDivElement>(null);
  const [largura, setLargura] = useState(0);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const obs = new ResizeObserver(([e]) => setLargura(e.contentRect.width));
    obs.observe(el);
    return () => obs.disconnect();
  }, []);

  return (
    <div ref={ref} className="relative w-full h-tempo bg-surface-alt border-t border-linha box-border overflow-hidden">
      <Regua duracaoSeg={mapa.dados.duracaoSeg} largura={largura} />
      <FormaDeOnda mapa={mapa} largura={largura} />
    </div>
  );
}
```

> `h-tempo` vem de `--spacing-tempo:148px` no `@theme` — mesmo raciocínio de `h-cabecalho`
> (Task 3) e `w-painel` (Task 5).

Run: `pnpm dev`, carregar uma faixa em `/` (ver Task 9) e observar a régua e a forma de
onda desenhadas. Comparar com `Docs/design/png/PalcoVazio.png`.

- [ ] **Step 3: Commit**

```bash
git add src/components/LinhaDoTempo.tsx
git commit -m "feat(ui): linha do tempo — regua e forma de onda"
```

---

## Task 7: `LinhaDoTempo.tsx` — região de loop, arraste, alças e snap

**Files:**
- Modify: `src/components/LinhaDoTempo.tsx`

Substitui o `LinhaDoTempo` provisório do Task 6 pela versão com interação completa.

- [ ] **Step 1: Adicionar o overlay de região e a lógica de arraste**

```tsx
function RegiaoDeLoop({
  regiao, duracaoSeg, largura,
}: {
  regiao: Regiao | null; duracaoSeg: number; largura: number;
}) {
  if (!regiao || largura <= 0) return null;
  const x1 = (regiao.inicio / duracaoSeg) * largura;
  const x2 = (regiao.fim / duracaoSeg) * largura;
  return (
    <div
      className="absolute box-border pointer-events-none border-l-2 border-r-2 border-loop bg-loop/12"
      style={{ left: x1, top: 0, width: x2 - x1, height: 116 }} // 18+54+44
    >
      <div className="absolute bg-loop rounded-[3px]" style={{ left: -4, top: '50%', marginTop: -13, width: 6, height: 26 }} />
      <div className="absolute bg-loop rounded-[3px]" style={{ right: -4, top: '50%', marginTop: -13, width: 6, height: 26 }} />
    </div>
  );
}

function Cursor({ t, duracaoSeg, largura }: { t: number; duracaoSeg: number; largura: number }) {
  if (largura <= 0) return null;
  const x = (t / duracaoSeg) * largura;
  return (
    <div
      className="absolute bg-cursor pointer-events-none shadow-[0_0_10px_rgba(255,255,255,0.75)]"
      style={{ left: x, top: 0, width: 2, height: 148 }}
    />
  );
}

type Alca = 'inicio' | 'fim' | null;

export function LinhaDoTempo({
  mapa, posicao, regiao, onBuscar, onDefinirRegiao,
}: {
  mapa: Mapa;
  posicao: number;
  regiao: Regiao | null;
  onBuscar: (t: number) => void;
  onDefinirRegiao: (r: Regiao | null) => void;
}) {
  const containerRef = useRef<HTMLDivElement>(null);
  const scrubRef = useRef<HTMLDivElement>(null); // área de régua+onda+trilhas, onde se arrasta
  const [largura, setLargura] = useState(0);
  const arrastandoRef = useRef<{ tipo: 'nova-regiao' | 'alca'; alca: Alca; inicioFixo: number } | null>(null);

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const obs = new ResizeObserver(([e]) => setLargura(e.contentRect.width));
    obs.observe(el);
    return () => obs.disconnect();
  }, []);

  function xParaTempo(clientX: number): number {
    const rect = scrubRef.current!.getBoundingClientRect();
    const fracao = Math.min(1, Math.max(0, (clientX - rect.left) / rect.width));
    return fracao * mapa.dados.duracaoSeg;
  }

  const TOLERANCIA_ALCA_PX = 8;

  function aoPressionar(e: React.PointerEvent) {
    const t = xParaTempo(e.clientX);
    (e.target as Element).setPointerCapture(e.pointerId);

    if (regiao && largura > 0) {
      const xInicio = (regiao.inicio / mapa.dados.duracaoSeg) * largura;
      const xFim = (regiao.fim / mapa.dados.duracaoSeg) * largura;
      const xClique = e.clientX - scrubRef.current!.getBoundingClientRect().left;
      if (Math.abs(xClique - xInicio) <= TOLERANCIA_ALCA_PX) {
        arrastandoRef.current = { tipo: 'alca', alca: 'inicio', inicioFixo: regiao.fim };
        return;
      }
      if (Math.abs(xClique - xFim) <= TOLERANCIA_ALCA_PX) {
        arrastandoRef.current = { tipo: 'alca', alca: 'fim', inicioFixo: regiao.inicio };
        return;
      }
    }

    arrastandoRef.current = { tipo: 'nova-regiao', alca: null, inicioFixo: t };
    onBuscar(t);
  }

  function aplicarSnap(t: number): number {
    return mapa.encaixe(t) ?? t;
  }

  function aoMover(e: React.PointerEvent) {
    const arraste = arrastandoRef.current;
    if (!arraste) return;
    const t = aplicarSnap(xParaTempo(e.clientX));

    if (arraste.tipo === 'alca') {
      const outraBorda = arraste.inicioFixo;
      const novaRegiao = arraste.alca === 'inicio'
        ? { inicio: Math.min(t, outraBorda), fim: Math.max(t, outraBorda) }
        : { inicio: Math.min(outraBorda, t), fim: Math.max(outraBorda, t) };
      if (novaRegiao.fim - novaRegiao.inicio > 0.05) onDefinirRegiao(novaRegiao);
      return;
    }

    // nova-regiao: só vira região de fato se o arraste passou de um clique simples
    const inicio = Math.min(arraste.inicioFixo, t);
    const fim = Math.max(arraste.inicioFixo, t);
    if (fim - inicio > 0.05) onDefinirRegiao({ inicio, fim });
  }

  function aoSoltar() {
    arrastandoRef.current = null;
  }

  return (
    <div ref={containerRef} className="relative w-full h-tempo bg-surface-alt border-t border-linha box-border overflow-hidden">
      <div
        ref={scrubRef}
        onPointerDown={aoPressionar}
        onPointerMove={aoMover}
        onPointerUp={aoSoltar}
        className="absolute cursor-pointer"
        style={{ inset: '0 0 32px 0' }}
      >
        <Regua duracaoSeg={mapa.dados.duracaoSeg} largura={largura} />
        <FormaDeOnda mapa={mapa} largura={largura} />
        <div style={{ height: 44 }} /> {/* trilhas dos elementos — vazio nesta fase */}
      </div>
      <RegiaoDeLoop regiao={regiao} duracaoSeg={mapa.dados.duracaoSeg} largura={largura} />
      <Cursor t={posicao} duracaoSeg={mapa.dados.duracaoSeg} largura={largura} />
    </div>
  );
}
```

> **Snap:** `mapa.encaixe(t)` já decide sozinho entre batidas e seções conforme
> `pulso.temPulsoClaro` (Fase 1, `Mapa.ts`) — a linha do tempo só chama o método, não
> reimplementa a decisão.
>
> **Por que `pointerdown`/`pointermove`/`pointerup` e não `mousedown`/`mousemove`:**
> funciona igual para mouse e touch sem lógica duplicada — relevante para o risco R8 da
> SPEC original (desenhar/arrastar no celular).

- [ ] **Step 2: Verificar manualmente (T3/T4 da Fase 1, agora pela UI)**

Run: `pnpm dev`, abrir `/`, carregar uma faixa, arrastar na forma de onda.
Expected: aparece a faixa amarela translúcida com bordas de 2px e alças; arrastar uma
alça redimensiona; um clique simples (sem arraste) só move o cursor via `onBuscar`.

- [ ] **Step 3: Commit**

```bash
git add src/components/LinhaDoTempo.tsx
git commit -m "feat(ui): linha do tempo — regiao de loop, arraste, alcas e snap"
```

---

## Task 8: `Transporte.tsx`

**Files:**
- Create: `src/components/Transporte.tsx`

32px, borda superior 1px `#1B1B22`. Botão play/pause 26px circular `#EDEDF0`. Stop
(quadrado, 16px, `#8A8A94`). Loop (ícone, aceso em `--color-loop` quando há região).
Tempo mono "00.00 / 69.82". Volume (ícone + barra 54×3px). ASSISTIR: pílula 26px,
`#EDEDF0`, texto 11px/600/tracking .06em — **inerte nesta fase** (Modo Cinema é Fase 6).

- [ ] **Step 1: Escrever o componente**

```tsx
'use client';

function formatarTempo(s: number): string {
  return s.toFixed(2).padStart(5, '0');
}

export function Transporte({
  tocando, posicao, duracao, temRegiao, volume,
  onTocar, onPausar, onParar, onLimparRegiao, onVolume,
}: {
  tocando: boolean; posicao: number; duracao: number; temRegiao: boolean; volume: number;
  onTocar: () => void; onPausar: () => void; onParar: () => void;
  onLimparRegiao: () => void; onVolume: (v: number) => void;
}) {
  return (
    <div className="absolute left-0 right-0 bottom-0 h-8 flex items-center gap-3.5 px-3.5 box-border border-t border-linha-soft">
      <button
        onClick={tocando ? onPausar : onTocar}
        className="w-[26px] h-[26px] rounded-full flex items-center justify-center bg-tinta border-none cursor-pointer"
        aria-label={tocando ? 'Pausar' : 'Tocar'}
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" className="text-base" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
          {tocando ? <path d="M8 5v14M16 5v14" /> : <path d="M7 4.5 19 12 7 19.5Z" fill="currentColor" stroke="none" />}
        </svg>
      </button>

      <button onClick={onParar} aria-label="Parar" className="bg-transparent border-none cursor-pointer flex text-tinta-fraca">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
          <rect x="6" y="6" width="12" height="12" rx="1" />
        </svg>
      </button>

      <button
        onClick={onLimparRegiao}
        aria-label={temRegiao ? 'Desligar loop de região' : 'Nenhuma região ativa'}
        className={`bg-transparent border-none flex ${temRegiao ? 'text-loop cursor-pointer' : 'text-tinta-fraca cursor-default'}`}
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
          <path d="M4 9h13l-3-3M20 15H7l3 3" />
        </svg>
      </button>

      <span className="text-rotulo text-tinta-fraca font-mono ml-1.5">
        {formatarTempo(posicao)} / {formatarTempo(duracao)}
      </span>

      <div className="ml-auto flex items-center gap-3.5">
        <span className="flex items-center gap-[7px] text-tinta-fraca">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M5 9v6h4l5 4V5L9 9Z" /><path d="M17 9.5a3.6 3.6 0 0 1 0 5" />
          </svg>
          <input
            type="range" min={0} max={1} step={0.01} value={volume}
            onChange={e => onVolume(Number(e.target.value))}
            className="w-[54px] h-[3px] accent-tinta-fraca"
          />
        </span>
        <button
          disabled
          title="Modo Cinema — Fase 6"
          className="h-[26px] px-[18px] rounded-full flex items-center gap-[7px] bg-tinta text-base text-[11px] font-semibold tracking-[0.06em] border-none opacity-50 cursor-not-allowed"
        >
          <svg width="10" height="10" viewBox="0 0 24 24"><path d="M7 4.5 19 12 7 19.5Z" fill="currentColor" /></svg>
          ASSISTIR
        </button>
      </div>
    </div>
  );
}
```

> `text-base` aqui é o utilitário de cor gerado por `--color-base:#0B0B0D` (o fundo mais
> escuro da aplicação) — usado como cor do ícone/texto quando ele fica **sobre** um fundo
> claro (`bg-tinta`), não como referência ao tamanho de fonte base do Tailwind (o projeto
> não usa a escala de `text-*` padrão para tamanho, só os tokens `text-rotulo`/`text-corpo`/
> etc. — não há colisão de nome na prática).

> ASSISTIR fica com `opacity:0.5` + `cursor:not-allowed` + `disabled` — o prompt pede
> "inerte", e um botão claramente desabilitado comunica isso melhor que um botão idêntico
> ao design que não faz nada ao clicar (o usuário clicaria e acharia que quebrou).

- [ ] **Step 2: Commit**

```bash
git add src/components/Transporte.tsx
git commit -m "feat(ui): transporte (play/pausa/stop/loop/volume, ASSISTIR inerte)"
```

---

## Task 9: `page.tsx` — orquestração final

**Files:**
- Modify: `src/app/page.tsx`

Junta tudo: `TelaDeEntrada` → carrega `Audio`/`Mapa` (mesmo padrão de `/teste`) →
`Cabecalho` + `Palco` + `PainelFerramentas` + `LinhaDoTempo` + `Transporte`.

- [ ] **Step 1: Escrever a página**

```tsx
'use client';

import { useEffect, useRef, useState } from 'react';
import { Audio, type EstadoAudio } from '@/engine/Audio';
import { Mapa } from '@/engine/Mapa';
import type { Faixa, Regiao } from '@/engine/tipos';
import { TelaDeEntrada } from '@/components/TelaDeEntrada';
import { Cabecalho } from '@/components/Cabecalho';
import { Palco } from '@/components/Palco';
import { PainelFerramentas } from '@/components/PainelFerramentas';
import { LinhaDoTempo } from '@/components/LinhaDoTempo';
import { Transporte } from '@/components/Transporte';

export default function Home() {
  const audioRef = useRef<Audio | null>(null);
  const rafRef = useRef<number | null>(null);

  const [iniciado, setIniciado] = useState(false);
  const [faixas, setFaixas] = useState<Faixa[]>([]);
  const [faixaAtual, setFaixaAtual] = useState<Faixa | null>(null);
  const [mapa, setMapa] = useState<Mapa | null>(null);
  const [estado, setEstado] = useState<EstadoAudio>('vazio');
  const [posicao, setPosicao] = useState(0);
  const [regiao, setRegiao] = useState<Regiao | null>(null);
  const [volume, setVolume] = useState(0.8);

  useEffect(() => {
    fetch('/audio/faixas.json').then(r => r.json()).then((lista: Faixa[]) => {
      setFaixas(lista);
    });
  }, []);

  useEffect(() => {
    return () => {
      if (rafRef.current !== null) cancelAnimationFrame(rafRef.current);
      audioRef.current?.destruir();
    };
  }, []);

  function loopDeQuadro() {
    const audio = audioRef.current;
    if (audio) {
      setEstado(audio.estado);
      setPosicao(audio.posicao());
    }
    rafRef.current = requestAnimationFrame(loopDeQuadro);
  }

  async function carregarFaixa(faixa: Faixa) {
    const audio = audioRef.current;
    if (!audio) return;
    setRegiao(null);
    setMapa(null); // Palco mostra "Carregando faixa..." enquanto isto fica null
    const [, mapaCarregado] = await Promise.all([
      audio.carregar(faixa.arquivo),
      Mapa.carregar(faixa.mapa),
    ]);
    setFaixaAtual(faixa);
    setMapa(mapaCarregado);
  }

  async function aoComecar() {
    audioRef.current = await Audio.iniciar();
    audioRef.current.volume(volume);
    setIniciado(true);
    rafRef.current = requestAnimationFrame(loopDeQuadro);
    if (faixas[0]) await carregarFaixa(faixas[0]);
  }

  function aoEscolherFaixa(id: string) {
    const faixa = faixas.find(f => f.id === id);
    if (faixa) carregarFaixa(faixa);
  }

  function aoDefinirRegiao(r: Regiao | null) {
    setRegiao(r);
    audioRef.current?.definirRegiao(r);
  }

  function aoMudarVolume(v: number) {
    setVolume(v);
    audioRef.current?.volume(v);
  }

  if (!iniciado || !faixas.length) {
    return faixas.length
      ? <TelaDeEntrada onComecar={aoComecar} />
      : null; // aguardando faixas.json — instantâneo na prática
  }

  const carregando = estado === 'carregando' || !mapa;

  return (
    <div className="h-dvh flex flex-col bg-base overflow-hidden">
      <Cabecalho faixa={faixaAtual} faixas={faixas} onEscolherFaixa={aoEscolherFaixa} />
      <div className="flex flex-1 min-h-0">
        <Palco vazio={!regiao} carregando={carregando} />
        <PainelFerramentas />
      </div>
      <div className="relative shrink-0 h-tempo bg-surface-alt border-t border-linha">
        {mapa ? (
          <>
            <LinhaDoTempo
              mapa={mapa}
              posicao={posicao}
              regiao={regiao}
              onBuscar={t => audioRef.current?.buscar(t)}
              onDefinirRegiao={aoDefinirRegiao}
            />
            <Transporte
              tocando={estado === 'tocando'}
              posicao={posicao}
              duracao={mapa.dados.duracaoSeg}
              temRegiao={!!regiao}
              volume={volume}
              onTocar={() => audioRef.current?.tocar()}
              onPausar={() => audioRef.current?.pausar()}
              onParar={() => audioRef.current?.parar()}
              onLimparRegiao={() => aoDefinirRegiao(null)}
              onVolume={aoMudarVolume}
            />
          </>
        ) : (
          <div className="h-full flex items-center justify-center text-[12px] text-tinta-fraca">
            Carregando faixa…
          </div>
        )}
      </div>
    </div>
  );
}
```

> **Estado de carregando:** o prompt da Fase 2 exige feedback visível enquanto
> `decodeAudioData` roda (é a parte lenta, segundos em faixas maiores). Antes desta
> correção, o bloco inteiro da linha do tempo simplesmente desaparecia enquanto `mapa`
> era `null` (no primeiro carregamento e em toda troca de faixa) — e o `Palco` mostrava
> "Selecione um trecho..." apontando para uma linha do tempo que não estava na tela.
> Agora: `Palco` mostra "Carregando faixa…" (via prop `carregando`) e o próprio bloco da
> linha do tempo mostra o mesmo aviso em vez de sumir.

> `Transporte` fica sobreposto (`absolute`, ver seu próprio CSS) na base do bloco de
> `LinhaDoTempo` — por isso o `<div className="relative shrink-0">` os envolve juntos: a
> altura do bloco é só a de `LinhaDoTempo` (148px), e o transporte ocupa os 32px finais
> por cima da área de trilhas, exatamente como a régua de camadas do design (seção 3.5 de
> `06-design-para-codigo.md`: `148 = régua 18 + onda 54 + trilhas 44 + transporte 32`).

- [ ] **Step 2: Verificar end-to-end**

Run: `pnpm exec tsc --noEmit && pnpm build`
Expected: sem erros.

Run: `pnpm dev`, abrir `http://localhost:3000/`
Expected:
- Tela de entrada aparece, "Começar" carrega a primeira faixa
- Cabeçalho mostra "Pulso · eletrônica minimalista"
- Palco vazio com sprockets, grão, vinheta, estado vazio central
- Linha do tempo mostra a forma de onda real e os divisores de seção (A–F)
- Arrastar na forma de onda cria a região amarela; o áudio entra em loop nela
- Cursor branco se move com `posicao()`, atravessando régua/onda/trilhas
- Play/pause/stop/volume funcionam
- Clicar no nome da faixa no cabeçalho abre um menu com as 3 faixas; escolher uma
  mostra "Carregando faixa…" no palco e na linha do tempo até o `mapa` novo chegar

- [ ] **Step 3: Commit**

```bash
git add src/app/page.tsx
git commit -m "feat: monta a Fase 2 — tela de entrada, casca e linha do tempo em /"
```

---

## Task 10: Verificação final e comparação com o design

**Files:** nenhum (verificação)

- [ ] **Step 1: Suite completa**

```bash
pnpm exec tsc --noEmit
pnpm build
pnpm test        # tem que continuar 25/25 — engine/ não foi tocado
```

- [ ] **Step 2: `/teste` continua funcionando**

Abrir `http://localhost:3000/teste` — deve estar idêntico à Fase 1.

- [ ] **Step 3: Comparação visual manual**

Colocar `Docs/design/png/PalcoVazio.png` e `Escutando.png` lado a lado com `/` (estado
vazio e com região ativa, respectivamente). Anotar divergências e o motivo de cada uma
(ex.: "forma de onda tem N barras em vez de 320 — largura do container é dinâmica, não
1440px fixo", que é uma divergência **esperada**, não um bug).

---

## Task 11: Documentação acadêmica da Fase 2

**Files:**
- Create: `Docs/10-fase-2-implementacao.md`

Mesmo formato de `Docs/09-fase-1-implementacao.md`: o que foi feito, decisões e desvios,
o que foi verificado automaticamente, e o que depende de conferência humana (a
comparação visual da Task 10 e qualquer teste de interação por toque, que não pode ser
simulado por esta sessão — mesma limitação já registrada na Fase 1 para T1-T6).

- [ ] **Step 1: Escrever o documento** cobrindo:
  - Tabela arquivo → responsabilidade (os 6 componentes + `page.tsx` + `layout.tsx`)
  - Decisões: layout dinâmico em vez de 1440px fixo, downsampling de `picos` para N
    barras, decoração da Tela de Entrada simplificada, ASSISTIR desabilitado (não
    apenas inerte visualmente)
  - Verificado automaticamente: tsc, build, os 25 testes de `engine/` intactos
  - Pendente de verificação humana: a comparação com os PNGs (Task 10) e testes de
    toque em mobile/tablet (fora do escopo desta sessão — sem dispositivo físico)

- [ ] **Step 2: Commit**

```bash
git add Docs/10-fase-2-implementacao.md
git commit -m "docs: registra a implementação da Fase 2 para a dissertação"
```
