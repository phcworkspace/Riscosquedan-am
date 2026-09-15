# MP3 — Faixas de referência, mapas e ferramentas

Pasta de trabalho do áudio do protótipo **Riscos que Dançam**.

```
MP3/
├── 01-pulso.mp3 + 01-pulso.map.json          eletrônica minimalista · 69,8s
├── 02-correnteza.mp3 + 02-correnteza.map.json  instrumental orgânica · 62,6s
├── 03-nevoa.mp3 + 03-nevoa.map.json            ambiente · 68,6s
├── faixas.json                               catálogo que a aplicação carrega
└── ferramentas/
    ├── mapear_faixa.py    ⭐ gera o .map.json — a ferramenta que importa
    ├── analisar_faixa.py     relatório de BPM, tonalidade e estrutura (agora opcional)
    ├── gerar_faixas.py       gera as 3 faixas de referência do zero
    └── requirements.txt
```

---

## 1. O que o protótipo precisa de uma faixa

**Nada de musical.** Não há exigência de BPM, tonalidade ou compasso. A aplicação não
gera som — ela só toca a faixa e faz o desenho da pessoa responder a ela.

O que ela precisa é do **mapa**: um arquivo JSON que descreve, a cada 1/30 de segundo,
quanta energia há em cada uma de quatro bandas de frequência. É esse arquivo que a
animação consulta.

> Consequência prática: **gravações históricas com andamento livre servem**. A
> arquitetura anterior, que exigia BPM constante, teria descartado boa parte do acervo
> de domínio público. Agora não.

---

## 2. `mapear_faixa.py` — a ferramenta principal

```bash
pip install -r ferramentas/requirements.txt      # precisa do ffmpeg no sistema

python ferramentas/mapear_faixa.py 01-pulso.mp3            # gera 01-pulso.map.json
python ferramentas/mapear_faixa.py *.mp3 --fps 30 --saida .
```

**O que o mapa contém:**

| Campo | O que é |
|---|---|
| `bandas` | quatro curvas 0..1, uma por quadro — **o coração do mapa** |
| `rms` | energia geral, para o fundo reagir |
| `picos` | 1200 valores para desenhar a forma de onda na linha do tempo |
| `secoes` | onde a música muda de seção, em segundos |
| `ataques` | onsets em segundos |
| `pulso` | BPM estimado e grade de batidas — **informativo**, para oferecer snap opcional |

Peso: cerca de **65 KB por minuto** de faixa a 30fps.

### 2.1 Por que pré-calcular, e não rodar FFT no navegador

1. **Determinismo.** O mesmo desenho produz exatamente a mesma animação toda vez. Isso
   importa quando a peça vai ser apresentada.
2. **Funciona fora da reprodução linear.** Com o cursor parado, arrastado ou voltando
   atrás, o valor de cada banda continua disponível — é consulta por tempo.
3. **Sobra quadro.** A FFT sai do loop de desenho.

### 2.2 As três decisões dentro da ferramenta, e por quê

Cada uma foi tomada medindo o resultado nas faixas de teste, não por intuição.

**Escala em dB, não linear.** Primeira tentativa, em escala linear: as curvas ficavam
acima de 0,5 em **90% do tempo**. Tudo sempre aceso, animação chapada. Em dB com gama
1,6, os elementos ficam em repouso e saltam nos eventos.

**Cada banda normalizada pela própria janela dinâmica** (percentil 20 → 99), não pelo
pico geral. Assim uma faixa sem agudos ainda anima os elementos de agudo, em vez de
deixá-los parados. O mapa descreve o **relevo** de cada banda, não o volume absoluto.

**Quatro bandas, não seis.** Esta foi a medida que mudou o design:

| Divisão | Correlação média | Pior par |
|---|---|---|
| 6 bandas | 0,48 | **0,97** |
| 5 bandas | 0,45 | 0,93 |
| **4 bandas** | **0,41** | **0,84** |

Com seis bandas, duas escolhas diferentes da pessoa produziriam praticamente a mesma
animação — a decisão dela não significaria nada. Quatro é o que o material sustenta.

| Banda | Faixa | Cor | O que costuma pegar |
|---|---|---|---|
| Grave | 20–150 Hz | `#FF3B30` | bumbo, baixo, corpo |
| Médio | 150–700 Hz | `#FFB300` | harmonia, notas centrais, voz grave |
| Agudo | 700–3200 Hz | `#0A84FF` | ataque, presença, voz aguda |
| Brilho | 3200–11000 Hz | `#5AC8FA` | ar, pratos, sibilância |

---

## 3. Como entrar com uma faixa nova

1. **Confirmar a licença** — obra **e** fonograma (ver seção 5) — e anotar o crédito
2. `python ferramentas/mapear_faixa.py faixa.mp3`
3. **Ler o relatório** e conferir dois números:
   - nenhuma banda com média acima de **0,6** — se passar, a animação fica chapada
   - as seções detectadas batem com o que se ouve
4. Se quiser conferir a independência das bandas numa faixa atípica, rode a correlação
   entre as quatro curvas: o pior par deve ficar abaixo de ~0,85
5. Copiar `.mp3` e `.map.json` para `/public/audio/` e registrar em `faixas.json`

---

## 4. As 3 faixas de referência

Sintetizadas do zero com numpy — nenhum material de terceiros, portanto sem qualquer
questão de direitos. Servem como material de teste enquanto as definitivas não chegam, e
como alvo do briefing (mostram o caráter de cada uma das três trilhas). São loopáveis:
comprimento em número exato de compassos, com a cauda de reverb dobrada de volta para o
início.

Para regerar ou ajustar: edite e rode `ferramentas/gerar_faixas.py`.

**Sobre `analisar_faixa.py`:** feita quando o projeto ainda exigia BPM e tonalidade.
Continua útil para entender uma faixa, mas **deixou de ser obrigatória**. Vale registrar
o que ela ensinou: rodada nas três referências, cujos valores reais conhecíamos, acertou
**1 de 3 BPM e 2 de 3 tonalidades** — errou a tonalidade quando o baixo martelava a
quinta, e o BPM quando não havia percussão. Foi por causa desse resultado que o mapa
passou a tratar BPM como informativo, e não como requisito.

---

## 5. Domínio público — o cuidado a tomar

Uma gravação carrega **dois direitos independentes**, e os dois precisam estar livres:

- a **obra** (composição e letra)
- o **fonograma** (aquela gravação específica)

Uma sinfonia de 1808 está em domínio público como obra, mas a gravação feita por uma
orquestra em 2018 **não está** — o fonograma tem prazo próprio, contado da fixação. No
Brasil isso está na Lei 9.610/98 (obras, art. 41) e nos direitos conexos sobre
fonogramas (art. 96). *Este é o seu terreno — vale conferir os prazos aplicáveis ao caso
concreto antes de fechar a lista.*

| Fonte | O que oferece | Observação |
|---|---|---|
| [Musopen](https://musopen.org/) | Gravações de clássico liberadas em domínio público | Existe justamente para resolver o fonograma. A melhor fonte para PD real |
| [Wikimedia Commons](https://commons.wikimedia.org/wiki/Category:Audio_files) | Áudio em PD e CC | Cada arquivo declara sua licença |
| [Internet Archive](https://archive.org/details/audio) | Acervo enorme, inclui gravações históricas em PD | Licença varia item a item |
| [Free Music Archive](https://freemusicarchive.org/) | CC BY, CC BY-SA, alguns CC0 | CC não é domínio público: exige atribuição |
| [ccMixter](https://ccmixter.org/) | CC, muito material eletrônico | Idem |

**O que procurar, agora que o andamento não importa mais:** faixas com **relevo
espectral** — momentos em que o grave entra sozinho, trechos só de agudos, mudanças de
textura entre seções. É isso que dá material para a pessoa perceber e desenhar. Uma
faixa uniforme do início ao fim produz quatro curvas parecidas e uma animação monótona,
por mais bonita que seja a música.

---

## 6. Documentos relacionados

- `../Docs/02-PRD-arquitetura-tecnica.md` — seção 3, o formato do mapa e como é consumido
- `../Docs/04-roadmap-desenvolvimento.md` — Fase 0B
