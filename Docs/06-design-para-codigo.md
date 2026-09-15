# 06 — Do design para o projeto local

**Data:** 14/09/2026
**O que existe:** o canvas com 11 artboards publicado no Claude Design, e os mesmos
artboards em `Docs/design/` — como imagem e como código-fonte.

> Leia antes: [`08-correcoes-do-ambiente.md`](08-correcoes-do-ambiente.md) — o projeto
> nasceu com **Next 16 e Tailwind 4**, e isso muda como os tokens entram.

---

## 1. O que veio do Claude Design

```
Docs/design/
├── png/                     11 imagens de referência, 1440×900 (tablet e celular no
│                            tamanho deles). Abra ao lado do editor enquanto codifica.
├── fonte/                   os artboards em HTML com estilos inline — a fonte real
│   ├── Main.dc.html         dos valores. Mais confiável que medir na imagem.
│   ├── Sistema.dc.html
│   └── ... (11 arquivos + canvas.json)
├── globals.css              substitui src/app/globals.css — tokens no @theme (Tailwind 4)
├── tokens.ts                as constantes que o motor precisa em runtime
└── gerar_artboards.py       o script que gerou tudo — reexecute para variações
```

**O canvas online** continua editável: abrir, clicar num elemento, mexer nas
propriedades, Salvar. As mudanças ficam lá; para trazê-las de volta para o código, o
caminho é o mesmo desta página — reler os valores e ajustar os tokens.

## 2. O caminho certo: ler o HTML, não medir a imagem

Este é o ponto que economiza mais tempo.

Os artboards são **HTML com estilos inline**. Todo valor do design está escrito lá:
padding, altura, raio, cor, tamanho de fonte, letter-spacing. Não meça pixel em PNG e
não arredonde para uma grade de 4/8px — abra o `.dc.html` e copie o número.

```powershell
# quanto mede a pastilha de banda?
Select-String -Path Docs/design/fonte/ElementoSelecionado.dc.html -Pattern 'height:\d+px;padding:0 10px'
# → height:30px

# qual o tracking dos rótulos de seção?
Select-String -Path Docs/design/fonte/Sistema.dc.html -Pattern 'letter-spacing:[^;]*' -AllMatches
```

As imagens servem para outra coisa: conferir se o que você construiu **parece** o
design. Composição, peso visual, densidade.

## 3. Passo a passo

### 3.1 Tokens — Tailwind 4, sem `tailwind.config.ts`

O projeto usa **Tailwind 4**: não existe arquivo de configuração. Os tokens ficam num
bloco `@theme` dentro do CSS e viram utilitários sozinhos (`--color-palco` →
`bg-palco`; `--text-rotulo` → `text-rotulo`; `--radius-lg` → `rounded-lg`).

```powershell
Copy-Item "Docs/design/globals.css" "src/app/globals.css" -Force
Copy-Item "Docs/design/tokens.ts" "src/engine/tokens.ts"
```

Dois arquivos porque são dois consumidores: a casca da UI usa os utilitários do
Tailwind; o **motor** (canvas e SVGs) não enxerga utilitário nenhum e lê as constantes
do `tokens.ts`.

### 3.2 Fontes

**Isto é Fase 5, não agora.** O `layout.tsx` gerado usa Geist; a troca acontece quando
a interface for construída. Space Grotesk e JetBrains Mono via `next/font/google` —
melhor que um `@import` de CSS, porque o Next hospeda os arquivos e evita o salto de
layout:

```ts
// src/app/layout.tsx
import { Space_Grotesk, JetBrains_Mono } from 'next/font/google';

const sans = Space_Grotesk({ subsets: ['latin'], weight: ['400','500','600','700'],
                             variable: '--fonte-ui' });
const mono = JetBrains_Mono({ subsets: ['latin'], weight: ['400','500'],
                              variable: '--fonte-mono' });
```

As famílias já estão declaradas no `@theme` do `globals.css` (`--font-sans` e
`--font-mono`); o `next/font` só precisa apontar as variáveis CSS para elas.

### 3.3 O esqueleto do layout

Três medidas fixas e o resto elástico:

```tsx
<div className="h-dvh flex flex-col bg-base overflow-hidden">
  <header className="h-[52px] shrink-0 border-b border-linha bg-surface" />
  <div className="flex flex-1 min-h-0">
    <main className="flex-1 relative bg-palco" />      {/* palco  */}
    <aside className="w-[300px] shrink-0 border-l border-linha bg-surface" />
  </div>
  <footer className="h-[148px] shrink-0 border-t border-linha bg-surface-alt" />
</div>
```

> No design o palco tem 700px de altura porque a janela tem 900. **Não fixe isso.**
> O palco é o que sobra: `flex-1` no meio, `h-dvh` no contêiner, `min-h-0` na linha
> intermediária (sem ele o flex não deixa o filho encolher e a linha do tempo é
> empurrada para fora da tela).

### 3.4 O que é DOM e o que é canvas

| Parte | Como construir |
|---|---|
| Cabeçalho, painel, linha do tempo | **React + Tailwind**, componente a componente |
| Elementos desenhados no palco | **Canvas 2D**, pelo `Renderizador` (Fase 2) |
| Perfurações, grão, vinheta | **DOM**, sobrepostos ao canvas — não desenhe no canvas |
| Forma de onda da linha do tempo | **Canvas 2D** ou SVG a partir do array `picos` |

As perfurações e a textura ficam fora do canvas de propósito: assim o loop de desenho
não gasta quadro redesenhando moldura, e a textura não entra na exportação em PNG da
composição.

Os artboards desenham os elementos em **SVG** porque era o mais simples para um
mockup estático. Na aplicação eles são Canvas 2D — mas o SVG do artboard serve de
referência direta para o brilho:

```
/* no artboard */  filter: drop-shadow(0 0 7px <cor>55)    /* em repouso  */
                   filter: drop-shadow(0 0 16px <cor>cc)   /* reagindo    */

/* no Canvas 2D  */
ctx.shadowColor = cor;
ctx.shadowBlur  = 7 + v * 9;      // v = valor da banda, 0..1
ctx.globalAlpha = 0.62 + v * 0.33;
```

### 3.5 As medidas que o design fixa

| Elemento | Valor |
|---|---|
| Cabeçalho | 52px · padding lateral 18px |
| Painel direito | 300px · padding 16px |
| Botão de ferramenta | 76×76 · raio 6 |
| Pastilha de banda | altura 30 · padding lateral 10 · raio 4 |
| Botão de comportamento | altura 38 · raio 5 |
| Círculo de cor | 28px · anel de seleção 2px com 3px de folga |
| Linha do tempo | 148 = régua 18 + onda 54 + trilhas 44 + transporte 32 |
| Barra de trilha | altura 7 · raio 2 · 4 linhas empilhadas, passo 10px |
| Cursor de reprodução | 2px · `box-shadow: 0 0 10px rgba(255,255,255,.75)` |
| Região de loop | `rgba(255,214,10,.12)` · bordas 2px · alças 6×26 raio 3 |
| Perfurações | 14×10 · raio 2 · passo 34px · `#202026` · 6px da borda |
| Botão ASSISTIR | altura 26 · pílula · fundo `#EDEDF0` · texto 11px 600 tracking .06em |
| Raio máximo | 6px (exceto o que é círculo por natureza) |

### 3.6 Reaproveitando o gerador

`gerar_artboards.py` é Python puro com numpy zero — só f-strings. Para testar outra
paleta, outro layout de painel ou uma composição diferente, edite e rode:

```powershell
python Docs/design/gerar_artboards.py     # regrava os .dc.html em out/
```

Depois basta abrir os arquivos no navegador para ver. Útil enquanto o design ainda
está em discussão; deixa de ser necessário quando a UI real existir.

---

## 4. Ordem de trabalho

O design **não muda** o roteiro: ele entra na Fase 5, depois que o motor funciona.

```
Fase 1  áudio e mapa        ← comece aqui (SPEC-fase-1.md)
Fase 2  renderizador          usa o brilho e as cores desta página
Fase 3  linha do tempo        usa as medidas da seção 3.5
Fase 4  interação e painel
Fase 5  interface             ← o design vira código aqui
```

Resista a montar a casca bonita antes do motor. A tentação é grande porque o design
já existe — mas a linha do tempo depende do `Mapa` (forma de onda, seções, batidas) e
o painel depende do modelo de dados. Construídos antes, viram retrabalho.

## 5. Quando o design mudar

O canvas online e os arquivos locais são cópias independentes. Se você editar o canvas
e quiser o valor novo no código, leia o valor e atualize o `@theme` do `globals.css`
(ou o `tokens.ts`, se for valor que o motor usa) — não existe sincronização automática,
e não vale a pena montar uma para um protótipo.

Para mudanças grandes, o caminho mais curto é o inverso: ajuste o
`gerar_artboards.py`, regere os artboards e republique o canvas.
