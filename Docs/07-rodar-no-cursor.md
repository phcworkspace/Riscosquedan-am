# 07 — Rodar o projeto no Cursor

**Data:** 14/09/2026
**Objetivo:** sair do zero e ter a Fase 1 rodando localmente.

---

## 0. Pré-requisitos (Windows)

> **Aviso sobre o `&&`.** O Windows PowerShell 5.1 — o padrão do Windows — **não aceita
> `&&`**. Ele só existe a partir do PowerShell 7. Por isso, nesta página cada comando
> fica em uma linha. Se preferir colar blocos inteiros, troque o terminal do Cursor para
> **Command Prompt** (a setinha ao lado do `+` no painel do terminal), onde o `&&`
> funciona.

Confira o que já existe:

```powershell
node -v
npm -v
$PSVersionTable.PSVersion
```

**Se `node` não for reconhecido**, instale (o npm vem junto):

```powershell
winget install OpenJS.NodeJS.LTS
```

**Feche o terminal e abra outro** — o PATH só é lido quando o terminal nasce. É o passo
que quase todo mundo pula e conclui que a instalação falhou. Sem `winget`, baixe o
instalador LTS em https://nodejs.org.

**Se aparecer `running scripts is disabled on this system`** ao chamar o npm, é a
política de execução do PowerShell bloqueando o `npm.ps1`:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

Libera scripts locais e mantém a exigência de assinatura nos baixados da internet — a
configuração usual de quem desenvolve, e o escopo `CurrentUser` não mexe na máquina
inteira. Alternativa sem alterar nada: chamar `npm.cmd` em vez de `npm`.

`pnpm` não é necessário aqui. Se quiser mesmo assim, depois do Node: `corepack enable pnpm`.

---

## 1. Criar o projeto

Onde você quiser guardar o código — **fora** da pasta `Mestrado Louyse`, que é o
material de pesquisa, não o repositório.

```powershell
npx create-next-app@latest riscos-que-dancam --typescript --tailwind --eslint --app --src-dir --import-alias "@/*" --use-npm
```

```powershell
cd riscos-que-dancam
```

```powershell
npm install zustand
```

```powershell
git init
git add -A
git commit -m "projeto inicial"
```

## 2. Trazer o material para dentro do repositório

O agente do Cursor só usa o que está na pasta aberta. Copie (Windows, PowerShell —
ajuste o caminho do repositório):

```powershell
$P = "C:\dev\riscos-que-dancam"          # onde você criou o projeto
$M = "F:\Documentos\Programas\Mestrado Louyse"

# documentação e design
Copy-Item "$M\Docs" "$P\Docs" -Recurse
Copy-Item "$M\MP3\README.md" "$P\Docs\MP3-README.md"

# áudios e mapas vão para public/
New-Item -ItemType Directory -Force "$P\public\audio" | Out-Null
Copy-Item "$M\MP3\*.mp3"       "$P\public\audio\"
Copy-Item "$M\MP3\*.map.json"  "$P\public\audio\"
Copy-Item "$M\MP3\faixas.json" "$P\public\audio\"

# regras do agente
Copy-Item "$M\Docs\cursor\CLAUDE.md" "$P\CLAUDE.md"
New-Item -ItemType Directory -Force "$P\.cursor\rules" | Out-Null
Copy-Item "$M\Docs\cursor\rules\*.mdc" "$P\.cursor\rules\"
```

Resultado:

```
riscos-que-dancam/
├── CLAUDE.md                    ← conceito, stack e proibições
├── .cursor/rules/
│   ├── projeto.mdc              ← sempre ativo
│   └── engine.mdc               ← ativa em src/engine/**
├── Docs/                        ← toda a documentação
├── public/audio/                ← 3 mp3 + 3 mapas + faixas.json
└── src/
```

> **Por que duas cópias das regras.** `CLAUDE.md` é lido pelo Claude Code; os `.mdc`
> são o formato nativo de regras do Cursor (`description`, `globs`, `alwaysApply`).
> Você usa as duas ferramentas, então as duas existem, com o mesmo conteúdo.

Abra a pasta no Cursor: `File → Open Folder`.

## 3. Conferir que as regras estão ativas

No chat do Cursor, pergunte algo que só as regras respondem:

> Quais bibliotecas estão proibidas neste projeto e por quê?

Se a resposta citar Tone.js e p5.js, as regras carregaram. Se não, confira em
`Settings → Rules` se os `.mdc` aparecem listados.

## 4. O primeiro prompt

Cole isto no chat do Cursor, em modo Agent:

```
Leia @Docs/SPEC-fase-1.md inteiro antes de escrever qualquer código.

Implemente APENAS a Fase 1: src/engine/tipos.ts, src/engine/Mapa.ts,
src/engine/Audio.ts e a página de teste em src/app/teste/page.tsx.

Regras desta fase:
- Web Audio API pura. Nenhuma biblioteca de áudio.
- posicao() calculada de ctx.currentTime a cada chamada, nunca acumulada.
- AudioBufferSourceNode é descartável: toda mudança de região, seek ou play
  recria o node.
- Sem AnalyserNode e sem FFT — o .map.json já traz as curvas.
- src/engine/ não importa React.
- A página /teste é feia de propósito: botões, números e quatro barras
  horizontais mostrando as bandas em tempo real. O design entra na Fase 5.

As faixas e os mapas já estão em public/audio/ (veja faixas.json).

Ao terminar, liste os 6 testes de aceite da seção 7 do SPEC e diga como
verificar cada um na página /teste.
```

Depois:

```powershell
npm run dev
```

Abra `http://localhost:3000/teste`.

## 5. Rodar os testes de aceite

Os seis estão na seção 7 do `SPEC-fase-1.md`. Os dois que mais pegam:

**T2 — a posição bate com o som.** Toque "Pulso" e deixe rodando **cinco minutos**.
Se o número tiver derivado do que se ouve, `posicao()` está acumulando em vez de
calcular. É o erro mais comum e o mais difícil de notar tarde.

**T5 — as bandas batem com o que se ouve.** A barra de *grave* tem que saltar junto
com o bumbo. Em "Névoa", grave e brilho precisam se mover de forma visivelmente
diferente. **Se as quatro barras subirem e descerem juntas, algo está errado** —
provavelmente lendo a mesma banda quatro vezes, ou o mapa de outra faixa.

A tabela de armadilhas (sintoma → causa) está na seção 8 do SPEC.

## 6. Deploy desde o primeiro dia

```powershell
npm install -g vercel
```

```powershell
vercel
```

Aceite os padrões. Use `vercel --prod` quando quiser publicar de verdade.

É grátis e descobre problema de build cedo, em vez de na véspera da apresentação.
Os áudios somam ~4,8 MB, bem dentro dos limites do plano Hobby.

## 7. O ciclo daqui pra frente

Uma fase por vez, cada uma com sua spec:

```
Fase 1  áudio e mapa        ← SPEC-fase-1.md   (agora)
Fase 2  renderizador
Fase 3  linha do tempo        o ponto mais delicado
Fase 4  interação e painel
Fase 5  interface             o design vira código
Fase 6  Modo Cinema           (+ Supabase, se for salvar e compartilhar)
Fase 7  polimento
```

Quando a Fase 1 passar nos seis testes, volte aqui com o resultado — eu escrevo a
`SPEC-fase-2.md` já sabendo o que o motor de áudio de fato entrega, em vez de supor.

**Marque cada fase no git** (`git tag fase-1`). Se uma decisão se provar errada lá na
frente, você volta ao ponto exato em vez de desfazer no escuro.

---

**Fontes:** [Cursor — Rules](https://cursor.com/docs/context/rules) ·
[Vercel — Limits](https://vercel.com/docs/limits) ·
[Node.js — LTS e fim de suporte](https://endoflife.date/nodejs) ·
[winget — OpenJS.NodeJS.LTS](https://winstall.app/apps/OpenJS.NodeJS.LTS)
