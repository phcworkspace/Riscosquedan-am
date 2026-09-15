# 08 — Correções do ambiente real

**Data:** 14/09/2026
**Motivo:** o projeto foi criado e o que veio instalado não é o que a documentação
supunha. Esta página registra as diferenças e o que muda por causa delas.

---

## 1. O que o `create-next-app` instalou de fato

| Suposto na documentação | Instalado |
|---|---|
| Next.js 15 | **Next.js 16.3.5** |
| Tailwind 3 (com `tailwind.config.ts`) | **Tailwind 4** (tokens em `@theme`, sem config) |
| React 18/19 | React 19.2.8 |
| pnpm | npm (o projeto nasceu com `package-lock.json`) |

## 2. Next 16 — leia a documentação local antes de usar qualquer API

O próprio framework escreve isto no `AGENTS.md` que ele gera:

> *This is NOT the Next.js you know. This version has breaking changes — APIs,
> conventions, and file structure may all differ from your training data. Read the
> relevant guide in `node_modules/next/dist/docs/` before writing any code.*

Vale para mim e vale para o agente do Cursor: **Next 16 é recente demais para estar
confiável no treino de qualquer modelo.** Já dá para ver uma diferença no
`layout.tsx` gerado — a assinatura virou `LayoutProps<"/">`, um tipo gerado
automaticamente que não existia antes.

**A regra prática:** ao mexer em rota, layout, metadata, server/client component,
`next.config.ts` ou fonte, abra `node_modules/next/dist/docs/` antes. Foi
acrescentado às regras do agente.

O que o projeto usa do Next é pequeno — uma página, um layout, arquivos estáticos em
`public/`. O risco concentrado é baixo; o problema seria o agente escrever com
convenções do Next 14 e nada funcionar sem motivo aparente.

## 3. Tailwind 4 — não existe `tailwind.config.ts`

Esta é a correção com efeito imediato. No Tailwind 4 os tokens vivem num bloco
`@theme` dentro do CSS e viram utilitários sozinhos:

```css
@import "tailwindcss";

@theme {
  --color-palco: #141417;   /* gera bg-palco, text-palco, border-palco */
  --text-rotulo: 11px;      /* gera text-rotulo */
  --radius-lg: 6px;         /* gera rounded-lg */
}
```

Não existe mais `@tailwind base; @tailwind components; @tailwind utilities;` — a
diretiva é `@import "tailwindcss"`.

**Consequência:** o `tailwind.tokens.ts` que eu tinha escrito não serve e foi
removido. No lugar:

| Arquivo | O que é |
|---|---|
| `Docs/design/globals.css` | substitui `src/app/globals.css` — todos os tokens no `@theme` |
| `Docs/design/tokens.ts` | as constantes que o **motor** precisa em runtime (bandas, paleta, medidas, brilho) — o canvas não enxerga utilitário do Tailwind |

## 4. O aviso do `package-lock.json`

```
⚠ Next.js ignored package-lock.json in F:\...\Mestrado Louyse because it is
  outside the current Git repository
```

Causa: o `npm install zustand` rodou uma vez na pasta de cima, antes do `cd`. Ficaram
lá um `package.json` de 53 bytes, um `package-lock.json` e uma `node_modules` inteira.
O Next encontra esses arquivos ao procurar a raiz do workspace e avisa que vai
ignorá-los.

É só lixo. Apagar resolve — o procedimento está na seção 6.

**Efeito colateral real:** o `zustand` foi instalado na pasta errada, então **não está
no projeto**. Precisa ser instalado de novo, no lugar certo.

## 5. O projeto ficou dentro de `Mestrado Louyse`

A documentação sugeria criar fora. Ficou dentro, e isso tem os dois lados:

**A favor de manter onde está:** `Mestrado Louyse` é a pasta conectada a esta sessão,
então eu consigo ler e escrever no código diretamente — revisar um arquivo, corrigir
um erro, conferir o que foi gerado. É uma vantagem concreta no dia a dia.

**Contra:** uma `node_modules` com dezenas de milhares de arquivos passa a morar
dentro da pasta de pesquisa, e existe um `.git` em cada nível (o da pasta de cima e o
do projeto), o que confunde qualquer ferramenta que procure a raiz do repositório.

**Recomendação:** manter onde está e apagar o `.git` da pasta de cima, deixando só o
do projeto. Se preferir separar depois, mover a pasta é um `Move-Item` — nada no
projeto depende do caminho.

## 6. O que fazer agora

Na pasta **de cima** (`Mestrado Louyse`), limpar o lixo:

```powershell
cd "F:\Documentos\Programas\Mestrado Louyse"
```

```powershell
Remove-Item -Recurse -Force node_modules
```

```powershell
Remove-Item package.json, package-lock.json
```

Se você não usa git na pasta de pesquisa (o `.git` de cima foi criado pelo comando
errado), apague também — o do projeto continua intacto:

```powershell
Remove-Item -Recurse -Force .git
```

Agora no projeto, passar para pnpm e instalar o que falta:

```powershell
cd riscos-que-dancam
```

```powershell
Remove-Item -Recurse -Force node_modules
```

```powershell
Remove-Item package-lock.json
```

```powershell
pnpm install
```

```powershell
pnpm add zustand
```

Trocar o CSS pelos tokens do design:

```powershell
Copy-Item "..\Docs\design\globals.css" "src\app\globals.css" -Force
```

```powershell
New-Item -ItemType Directory -Force src\engine | Out-Null
Copy-Item "..\Docs\design\tokens.ts" "src\engine\tokens.ts"
```

Levar os áudios e os mapas para `public/audio/`:

```powershell
New-Item -ItemType Directory -Force public\audio | Out-Null
```

```powershell
Copy-Item "..\mp3\*.mp3" public\audio\
Copy-Item "..\mp3\*.map.json" public\audio\
Copy-Item "..\mp3\faixas.json" public\audio\
```

Instalar as regras do agente:

```powershell
New-Item -ItemType Directory -Force .cursor\rules | Out-Null
Copy-Item "..\Docs\cursor\rules\*.mdc" .cursor\rules\
```

```powershell
Get-Content "..\Docs\cursor\AGENTS-riscos.md" | Add-Content AGENTS.md
```

> **Por que acrescentar ao `AGENTS.md` em vez de criar um `CLAUDE.md`.** O `next dev`
> gera e mantém o `AGENTS.md` e cria um `CLAUDE.md` de uma linha (`@AGENTS.md`) que
> aponta para ele. Se você escrever no `CLAUDE.md`, o Next sobrescreve. O bloco dele é
> delimitado por `<!-- BEGIN:nextjs-agent-rules -->` e `<!-- END: -->`; tudo que vier
> depois é preservado. Então as regras do projeto vão **no fim do `AGENTS.md`**, e o
> `CLAUDE.md` de uma linha as importa automaticamente.

Conferir:

```powershell
pnpm dev
```

## 7. Fontes do design

O `layout.tsx` gerado usa Geist. As fontes do projeto são Space Grotesk e JetBrains
Mono — **mas isso é Fase 5**, não agora. O `globals.css` já declara as famílias no
`@theme`; trocar o `next/font` no layout fica para quando a interface for construída.

---

## Registro para os outros documentos

- `02-PRD-arquitetura-tecnica.md` diz "Next.js 15" — leia como **Next 16**
- `06-design-para-codigo.md` descreve `tailwind.config.ts` — leia a seção 3 desta
  página no lugar
- `07-rodar-no-cursor.md` continua válido para quem começar do zero, com pnpm
