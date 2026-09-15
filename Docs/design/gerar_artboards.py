# -*- coding: utf-8 -*-
"""Gera os artboards .dc.html da interface do protótipo Riscos que Dançam."""
import math, os, json

W, H = 1440, 900
CAB, TL = 52, 148          # cabeçalho, linha do tempo
PAINEL = 300
PW = W - PAINEL            # largura do palco
PH = H - CAB - TL          # altura do palco  = 700

C = dict(
    bg="#0B0B0D", palco="#141417", surface="#1A1A1F", surfalt="#212128",
    border="#2A2A31", text="#EDEDF0", muted="#8A8A94", loop="#FFD60A",
    sprocket="#202026",
)
BANDAS = [("Grave", "#FF3B30", "20–150 Hz"), ("Médio", "#FFB300", "150–700 Hz"),
          ("Agudo", "#0A84FF", "700–3200 Hz"), ("Brilho", "#5AC8FA", "3,2–11 kHz")]
PALETA = ["#FF3B30", "#FF7A1A", "#FFB300", "#30D158",
          "#0A84FF", "#5AC8FA", "#C77DFF", "#F2F2F7"]

GRAO = ("url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' "
        "width='160' height='160'%3E%3Cfilter id='n'%3E%3CfeTurbulence "
        "type='fractalNoise' baseFrequency='0.9' numOctaves='3'/%3E%3C/filter"
        "%3E%3Crect width='160' height='160' filter='url(%23n)'/%3E%3C/svg%3E\")")

# ---------------------------------------------------------------- composição
# x,y em coordenadas do palco. Composição deliberada: aglomerado quente à
# esquerda, diagonal longa atravessando, formas frias à direita, respiro em
# baixo à esquerda e no topo central.
COMP = [
    dict(t="ponto", x=152, y=214, r=27, c="#FF3B30", b=0),
    dict(t="ponto", x=228, y=262, r=11, c="#FF3B30", b=0),
    dict(t="ponto", x=198, y=158, r=7,  c="#FF7A1A", b=0),
    dict(t="ponto", x=272, y=196, r=18, c="#FFB300", b=1),
    dict(t="ponto", x=138, y=302, r=9,  c="#FF7A1A", b=0),
    dict(t="ponto", x=306, y=284, r=5,  c="#FFB300", b=1),
    dict(t="ponto", x=246, y=344, r=13, c="#FF3B30", b=0),

    dict(t="linha", x1=178, y1=596, x2=908, y2=166, w=3, c="#5AC8FA", b=3),
    dict(t="linha", x1=384, y1=432, x2=590, y2=432, w=7, c="#0A84FF", b=2),
    dict(t="linha", x1=408, y1=474, x2=524, y2=474, w=2, c="#C77DFF", b=2),
    dict(t="linha", x1=596, y1=236, x2=688, y2=186, w=2, c="#5AC8FA", b=3),

    dict(t="forma", x=706, y=438, r=56, n=3, rot=-14, c="#30D158", b=1),
    dict(t="forma", x=820, y=506, r=34, n=6, rot=10,  c="#0A84FF", b=2),
    dict(t="forma", x=890, y=408, r=22, n=4, rot=22,  c="#FFB300", b=1),
    dict(t="forma", x=756, y=560, r=17, n=5, rot=-6,  c="#C77DFF", b=2),

    dict(t="ponto", x=968, y=132, r=4,  c="#5AC8FA", b=3),
    dict(t="ponto", x=1004, y=176, r=6, c="#5AC8FA", b=3),
    dict(t="ponto", x=944, y=212, r=3,  c="#F2F2F7", b=3),
    dict(t="ponto", x=1032, y=118, r=3, c="#5AC8FA", b=3),
    dict(t="ponto", x=986, y=256, r=8,  c="#0A84FF", b=2),

    dict(t="ponto", x=880, y=642, r=15, c="#FF3B30", b=0),
    dict(t="ponto", x=946, y=600, r=6,  c="#FF7A1A", b=0),
    dict(t="forma", x=1046, y=520, r=28, n=3, rot=170, c="#C77DFF", b=2),
    dict(t="linha", x1=1006, y1=660, x2=1104, y2=612, w=4, c="#FFB300", b=1),
    dict(t="ponto", x=452, y=228, r=10, c="#30D158", b=1),
]

# elementos "quentes" no estado tocando / cinema
ATIVOS_TOCANDO = {0, 3, 7, 11, 15}
ATIVOS_CINEMA = {0, 1, 3, 6, 7, 8, 11, 12, 14, 16, 20, 22}


def poly(cx, cy, r, n, rot):
    pts = []
    for i in range(n):
        a = math.radians(rot - 90 + i * 360 / n)
        pts.append(f"{cx + r*math.cos(a):.1f},{cy + r*math.sin(a):.1f}")
    return " ".join(pts)


def desenhar(elems, ativos=(), escala=1.0, brilho=1.0, particulas=False,
             indices=None):
    """SVG do conteúdo do palco."""
    out = []
    for i, e in enumerate(elems):
        if indices is not None and i not in indices:
            continue
        on = i in ativos
        g = (1.35 if on else 1.0) * escala
        op = min(1.0, (0.95 if on else 0.62) * brilho)
        blur = 16 if on else 7
        if e["t"] == "ponto":
            r = e["r"] * g
            out.append(
                f'<circle cx="{e["x"]}" cy="{e["y"]}" r="{r:.1f}" '
                f'fill="{e["c"]}" opacity="{op:.2f}" '
                f'style="filter:drop-shadow(0 0 {blur}px {e["c"]}{"cc" if on else "55"})"/>')
            if on:
                out.append(f'<circle cx="{e["x"]}" cy="{e["y"]}" r="{r*1.9:.1f}" '
                           f'fill="none" stroke="{e["c"]}" stroke-width="1" '
                           f'opacity="0.28"/>')
        elif e["t"] == "linha":
            out.append(
                f'<line x1="{e["x1"]}" y1="{e["y1"]}" x2="{e["x2"]}" y2="{e["y2"]}" '
                f'stroke="{e["c"]}" stroke-width="{e["w"]*g:.1f}" stroke-linecap="round" '
                f'opacity="{op:.2f}" '
                f'style="filter:drop-shadow(0 0 {blur}px {e["c"]}{"cc" if on else "44"})"/>')
        else:
            out.append(
                f'<polygon points="{poly(e["x"], e["y"], e["r"]*g, e["n"], e["rot"])}" '
                f'fill="none" stroke="{e["c"]}" stroke-width="{2.2*g:.1f}" '
                f'stroke-linejoin="round" opacity="{op:.2f}" '
                f'style="filter:drop-shadow(0 0 {blur}px {e["c"]}{"cc" if on else "44"})"/>')
            if on:
                out.append(
                    f'<polygon points="{poly(e["x"], e["y"], e["r"]*g*0.55, e["n"], e["rot"]+18)}" '
                    f'fill="{e["c"]}" opacity="0.16"/>')
    if particulas:
        import random
        rnd = random.Random(7)
        for i in ATIVOS_CINEMA:
            e = elems[i]
            cx = e.get("x", (e.get("x1", 0) + e.get("x2", 0)) / 2)
            cy = e.get("y", (e.get("y1", 0) + e.get("y2", 0)) / 2)
            for _ in range(5):
                a = rnd.uniform(0, 6.28); d = rnd.uniform(34, 96)
                out.append(
                    f'<circle cx="{cx + d*math.cos(a):.0f}" cy="{cy + d*math.sin(a):.0f}" '
                    f'r="{rnd.uniform(0.8, 2.0):.1f}" fill="{e["c"]}" '
                    f'opacity="{rnd.uniform(0.2, 0.55):.2f}"/>')
    return "\n".join(out)


def sprockets(w, lado):
    """Perfurações de película. lado: 'top' | 'bottom'."""
    passo, larg, alt = 34, 14, 10
    n = int(w // passo)
    off = (w - (n * passo - (passo - larg))) / 2
    y = 6 if lado == "top" else -16
    r = []
    for i in range(n):
        x = off + i * passo
        r.append(f'<div style="position:absolute;{"top" if lado=="top" else "bottom"}:6px;'
                 f'left:{x:.0f}px;width:{larg}px;height:{alt}px;border-radius:2px;'
                 f'background:{C["sprocket"]}"></div>')
    return "".join(r)


def palco(conteudo_svg, w=PW, h=PH, forte=False, extra=""):
    vin = 0.72 if forte else 0.55
    return f'''<div style="position:relative;width:{w}px;height:{h}px;overflow:hidden;
     background:{C["palco"]}">
  <svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" style="position:absolute;inset:0">
{conteudo_svg}
  </svg>
  <div style="position:absolute;inset:0;pointer-events:none;
       background:radial-gradient(ellipse at 50% 48%, rgba(0,0,0,0) 38%, rgba(0,0,0,{vin}) 100%)"></div>
  <div style="position:absolute;inset:0;pointer-events:none;opacity:0.03;
       background-image:{GRAO}"></div>
  {sprockets(w, "top")}{sprockets(w, "bottom")}
  {extra}
</div>'''


# ------------------------------------------------------------------- chrome
def rotulo(txt, mt=0):
    return (f'<div style="font-size:11px;letter-spacing:0.08em;text-transform:uppercase;'
            f'color:{C["muted"]};margin:{mt}px 0 6px">{txt}</div>')


ICO = {
 "help": '<circle cx="12" cy="12" r="9"/><path d="M9.6 9.2a2.4 2.4 0 1 1 2.9 2.4v1.4"/><path d="M12.4 16.4h.01"/>',
 "linha": '<path d="M5 19 19 5"/>',
 "forma": '<path d="M12 4 21 20H3Z"/>',
 "play": '<path d="M7 4.5 19 12 7 19.5Z" fill="currentColor" stroke="none"/>',
 "pause": '<path d="M8 5v14M16 5v14"/>',
 "stop": '<rect x="6" y="6" width="12" height="12" rx="1"/>',
 "loop": '<path d="M4 9h13l-3-3M20 15H7l3 3"/>',
 "vol": '<path d="M5 9v6h4l5 4V5L9 9Z"/><path d="M17 9.5a3.6 3.6 0 0 1 0 5"/>',
 "trash": '<path d="M4 7h16M9 7V5h6v2M7 7l1 12h8l1-12"/>',
 "pulsar": '<circle cx="12" cy="12" r="4"/><circle cx="12" cy="12" r="9" stroke-dasharray="3 3"/>',
 "girar": '<path d="M12 4a8 8 0 1 1-6.9 4"/><path d="M4.5 4v4.5H9"/>',
 "vibrar": '<path d="M3 12c2-6 4 6 6 0s4 6 6 0 4 6 6 0"/>',
 "acender": '<circle cx="12" cy="12" r="3.6"/><path d="M12 3v2.4M12 18.6V21M3 12h2.4M18.6 12H21M5.6 5.6l1.7 1.7M16.7 16.7l1.7 1.7M18.4 5.6l-1.7 1.7M7.3 16.7l-1.7 1.7"/>',
}


def icone(nome, tam=20, cor="currentColor", sw=1.5):
    d = ICO[nome].replace("currentColor", cor)
    return (f'<svg width="{tam}" height="{tam}" viewBox="0 0 24 24" fill="none" '
            f'stroke="{cor}" stroke-width="{sw}" stroke-linecap="round" '
            f'stroke-linejoin="round">{d}</svg>')


def cabecalho(faixa="Pulso · eletrônica minimalista"):
    return f'''<div style="height:{CAB}px;display:flex;align-items:center;
     justify-content:space-between;padding:0 18px;background:{C["surface"]};
     border-bottom:1px solid {C["border"]};box-sizing:border-box">
  <div style="display:flex;align-items:baseline;gap:12px">
    <span style="font-size:14px;font-weight:600;letter-spacing:-0.01em">Riscos que Dançam</span>
    <span style="font-size:11px;color:{C["muted"]}">Escute. Desenhe o que você vê.</span>
  </div>
  <div style="display:flex;align-items:center;gap:16px">
    <span style="font-size:12px;color:{C["text"]};border-bottom:1px dotted {C["border"]};
          padding-bottom:2px;cursor:pointer">{faixa}</span>
    <div style="width:32px;height:32px;border-radius:50%;border:1px solid {C["border"]};
         display:flex;align-items:center;justify-content:center;color:{C["muted"]}">
      {icone("help", 17)}</div>
  </div>
</div>'''


def ferramenta_btn(tipo, ativo):
    borda = "#EDEDF0" if ativo else C["border"]
    fundo = "#22222A" if ativo else "transparent"
    cor = C["text"] if ativo else C["muted"]
    if tipo == "ponto":
        glifo = f'<svg width="22" height="22" viewBox="0 0 24 24"><circle cx="12" cy="12" r="6" fill="{cor}"/></svg>'
    else:
        glifo = icone(tipo, 22, cor)
    nome = {"ponto": "Ponto", "linha": "Linha", "forma": "Forma"}[tipo]
    return f'''<div style="width:76px;height:76px;border:1px solid {borda};border-radius:6px;
     background:{fundo};display:flex;flex-direction:column;align-items:center;
     justify-content:center;gap:7px;box-sizing:border-box">
  {glifo}<span style="font-size:10px;color:{cor}">{nome}</span></div>'''


def curva_mini(banda_i, w=60, h=16):
    import random
    rnd = random.Random(11 + banda_i)
    pts, n = [], 26
    v = 0.3
    for i in range(n):
        v = max(0.05, min(1.0, v + rnd.uniform(-0.35, 0.4)))
        pts.append(f"{i*w/(n-1):.1f},{h - v*h*0.92:.1f}")
    cor = BANDAS[banda_i][1]
    return (f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'<polyline points="{" ".join(pts)}" fill="none" stroke="{cor}" '
            f'stroke-width="1.2" opacity="0.85"/></svg>')


def pastilha_banda(i, ativa):
    nome, cor, hz = BANDAS[i]
    fundo = "#24242C" if ativa else "transparent"
    barra = (f'<div style="position:absolute;left:0;top:0;bottom:0;width:2px;'
             f'background:{C["text"]}"></div>' if ativa else "")
    return f'''<div style="position:relative;display:flex;align-items:center;gap:9px;
     height:30px;padding:0 10px;background:{fundo};border-radius:4px;
     box-sizing:border-box">{barra}
  <span style="width:9px;height:9px;border-radius:50%;background:{cor};flex:none"></span>
  <span style="font-size:12px;color:{C["text"] if ativa else C["muted"]}">{nome}</span>
  <span style="margin-left:auto;font-size:9px;color:{C["muted"]};
        font-family:'JetBrains Mono',monospace">{hz}</span>
</div>'''


def comp_btn(nome, ico, ativo):
    borda = "#EDEDF0" if ativo else C["border"]
    cor = C["text"] if ativo else C["muted"]
    fundo = "#22222A" if ativo else "transparent"
    return f'''<div style="height:38px;border:1px solid {borda};border-radius:5px;
     background:{fundo};display:flex;align-items:center;justify-content:center;gap:7px;
     box-sizing:border-box">{icone(ico, 16, cor)}
  <span style="font-size:11px;color:{cor}">{nome}</span></div>'''


def slider(pct, esq="", dir_="", cor="#EDEDF0"):
    lado = ""
    if esq or dir_:
        lado = (f'<div style="display:flex;justify-content:space-between;font-size:10px;'
                f'color:{C["muted"]};margin-top:5px"><span>{esq}</span><span>{dir_}</span></div>')
    return f'''<div><div style="position:relative;height:3px;background:{C["border"]};
     border-radius:2px">
  <div style="position:absolute;left:0;top:0;height:3px;width:{pct}%;background:{cor};
       border-radius:2px"></div>
  <div style="position:absolute;left:calc({pct}% - 6px);top:-4.5px;width:12px;height:12px;
       border-radius:50%;background:{C["text"]}"></div></div>{lado}</div>'''


def painel(sel=None):
    """sel=None → estado vazio. sel=dict(...) → elemento selecionado."""
    topo = f'''<div style="padding:16px 16px 14px">
  {rotulo("Ferramenta")}
  <div style="display:flex;gap:8px">{ferramenta_btn("ponto", sel is None or sel["tipo"]=="ponto")}
  {ferramenta_btn("linha", bool(sel) and sel["tipo"]=="linha")}
  {ferramenta_btn("forma", bool(sel) and sel["tipo"]=="forma")}</div>
</div>
<div style="height:1px;background:{C["border"]}"></div>'''

    if sel is None:
        corpo = f'''<div style="flex:1;display:flex;align-items:center;justify-content:center;
     padding:0 34px;text-align:center">
  <span style="font-size:12px;line-height:1.55;color:{C["muted"]}">Selecione um elemento
  no palco para ajustá-lo</span></div>'''
    else:
        bi = sel["banda"]
        past = "".join(pastilha_banda(i, i == bi) for i in range(4))
        cores = "".join(
            f'<div style="width:28px;height:28px;border-radius:50%;background:{c};'
            + (f'box-shadow:0 0 0 3px {C["surface"]},0 0 0 5px {C["text"]}' if c == sel["cor"] else "")
            + '"></div>' for c in PALETA)
        corpo = f'''<div style="flex:1;padding:16px;overflow:hidden">
  <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px">
    <span style="font-size:11px;letter-spacing:0.08em;text-transform:uppercase;
          color:{C["muted"]}">Responde a</span>{curva_mini(bi)}</div>
  <div style="display:flex;flex-direction:column;gap:2px">{past}</div>

  {rotulo("Comportamento", 12)}
  <div style="display:grid;grid-template-columns:repeat(2, minmax(0,1fr));gap:7px">
    {comp_btn("Pulsar","pulsar",sel["comp"]=="pulsar")}{comp_btn("Girar","girar",sel["comp"]=="girar")}
    {comp_btn("Vibrar","vibrar",sel["comp"]=="vibrar")}{comp_btn("Acender","acender",sel["comp"]=="acender")}
  </div>

  {rotulo("Reação", 12)}
  {slider(sel["reacao"], "imóvel", "salta")}

  {rotulo("Cor", 12)}
  <div style="display:grid;grid-template-columns:repeat(4, minmax(0,1fr));gap:7px;
       justify-items:center">{cores}</div>

  <div style="display:grid;grid-template-columns:repeat(2, minmax(0,1fr));gap:14px;margin-top:14px">
    <div>{rotulo("Tamanho")}{slider(sel["tam"])}</div>
    <div>{rotulo("Opacidade")}{slider(sel["op"])}</div>
  </div>

  {rotulo("Trecho", 10)}
  <div style="display:flex;align-items:center;justify-content:space-between">
    <span style="font-size:13px;font-family:'JetBrains Mono',monospace">{sel["trecho"]}</span>
    <span style="font-size:10px;color:{C["muted"]};border:1px solid {C["border"]};
          border-radius:4px;padding:4px 8px">usar o loop atual</span></div>
</div>'''

    rodape = f'''<div style="height:1px;background:{C["border"]}"></div>
<div style="height:44px;display:flex;align-items:center;justify-content:space-between;
     padding:0 16px">
  <span style="font-size:11px;color:{C["muted"]};display:flex;align-items:center;gap:6px">
  {icone("trash", 14, C["muted"])}{"Apagar elemento" if sel else ""}</span>
  <span style="font-size:11px;color:{C["muted"]};font-family:'JetBrains Mono',monospace">
  {sel["contador"] if sel else "0"} / 120</span>
</div>'''
    return f'''<div style="width:{PAINEL}px;height:{PH}px;background:{C["surface"]};
     border-left:1px solid {C["border"]};display:flex;flex-direction:column;
     box-sizing:border-box">{topo}{corpo}{rodape}</div>'''


# -------------------------------------------------------------- linha do tempo
DUR = 69.8

def waveform(w, h, semente=5):
    import random
    rnd = random.Random(semente)
    n = 320
    barras = []
    for i in range(n):
        p = i / n
        base = 0.28 + 0.52 * math.sin(p * math.pi * 1.15)
        if 0.06 < p < 0.12: base *= 0.45
        if 0.38 < p < 0.68: base *= 1.18
        if p > 0.9: base *= 0.5
        v = max(0.05, min(1.0, base * rnd.uniform(0.55, 1.15)))
        x = i * w / n
        barras.append(f'<rect x="{x:.1f}" y="{(h-v*h)/2:.1f}" width="{max(w/n-1.2,0.8):.1f}" '
                      f'height="{v*h:.1f}" fill="{C["muted"]}" opacity="0.4"/>')
    return "".join(barras)


SECOES = [(0, 4.34, "A"), (4.34, 8.62, "B"), (8.62, 43.35, "C"),
          (43.35, 51.87, "D"), (51.87, 60.81, "E"), (60.81, 69.82, "F")]

TRILHAS = [  # (inicio, fim, cor, faixa)
    (1.2, 9.4, "#FF3B30", 0), (2.8, 6.2, "#FFB300", 1), (5.0, 12.6, "#5AC8FA", 2),
    (10.2, 19.8, "#0A84FF", 0), (12.4, 17.0, "#FF7A1A", 1), (14.0, 26.5, "#C77DFF", 3),
    (19.5, 31.0, "#30D158", 2), (22.0, 28.4, "#FF3B30", 1), (26.0, 38.0, "#5AC8FA", 0),
    (31.5, 44.0, "#FFB300", 3), (33.0, 40.2, "#0A84FF", 2), (38.5, 49.0, "#FF7A1A", 1),
    (44.5, 56.0, "#C77DFF", 0), (46.0, 52.5, "#30D158", 3), (50.0, 61.0, "#FF3B30", 2),
    (54.0, 66.0, "#5AC8FA", 1), (57.5, 64.0, "#FFB300", 0), (62.0, 69.0, "#0A84FF", 3),
]


def linha_do_tempo(w=W, cursor=None, regiao=None, sel_trilha=None, vazio=False,
                   tocando=False, compacta=False):
    px = lambda t: t / DUR * w
    reg = ""
    if regiao:
        x0, x1 = px(regiao[0]), px(regiao[1])
        reg = f'''<div style="position:absolute;left:{x0:.0f}px;top:0;width:{x1-x0:.0f}px;
     height:{TL-32}px;background:rgba(255,214,10,0.12);
     border-left:2px solid {C["loop"]};border-right:2px solid {C["loop"]};
     box-sizing:border-box;pointer-events:none">
  <div style="position:absolute;left:-4px;top:50%;margin-top:-13px;width:6px;height:26px;
       border-radius:3px;background:{C["loop"]}"></div>
  <div style="position:absolute;right:-4px;top:50%;margin-top:-13px;width:6px;height:26px;
       border-radius:3px;background:{C["loop"]}"></div></div>'''

    cur = ""
    if cursor is not None:
        cur = (f'<div style="position:absolute;left:{px(cursor):.0f}px;top:0;width:2px;'
               f'height:{TL}px;background:#fff;box-shadow:0 0 10px rgba(255,255,255,0.75);'
               f'pointer-events:none"></div>')

    # régua
    marcas = "".join(
        f'<div style="position:absolute;left:{px(t):.0f}px;top:0;height:6px;width:1px;'
        f'background:{C["border"]}"></div>'
        f'<div style="position:absolute;left:{px(t)+4:.0f}px;top:2px;font-size:9px;'
        f'color:{C["muted"]};font-family:\'JetBrains Mono\',monospace">{t}s</div>'
        for t in range(0, 70, 5))

    # seções
    divs = "".join(
        f'<div style="position:absolute;left:{px(a):.0f}px;top:0;bottom:0;width:1px;'
        f'background:{C["border"]}"></div>'
        f'<div style="position:absolute;left:{px(a)+5:.0f}px;top:3px;font-size:9px;'
        f'color:{C["muted"]}">{r}</div>' for a, _, r in SECOES if a > 0)

    linhas = 4
    alt_tr = 7
    trilhas_html = ""
    if not vazio:
        for i, (a, b, cor, lin) in enumerate(TRILHAS):
            marcado = (i == sel_trilha)
            trilhas_html += (
                f'<div style="position:absolute;left:{px(a):.0f}px;top:{lin*10+2}px;'
                f'width:{px(b)-px(a):.0f}px;height:{alt_tr}px;border-radius:2px;'
                f'background:{cor};opacity:{0.95 if marcado else 0.72};'
                + (f'box-shadow:0 0 0 1px #fff;' if marcado else "")
                + '"></div>')

    icone_play = icone("pause", 16, "#0B0B0D") if tocando else icone("play", 16, "#0B0B0D")
    tempo = f"{cursor:05.2f}" if cursor is not None else "00.00"

    return f'''<div style="position:relative;width:{w}px;height:{TL}px;
     background:{C["surfalt"]};border-top:1px solid {C["border"]};
     box-sizing:border-box;overflow:hidden">
  <div style="position:absolute;inset:0 0 32px 0">
    <div style="position:relative;height:18px;border-bottom:1px solid #1B1B22">{marcas}</div>
    <div style="position:relative;height:54px;border-bottom:1px solid #1B1B22">
      <svg width="{w}" height="54" style="position:absolute;inset:0">{waveform(w,54)}</svg>{divs}</div>
    <div style="position:relative;height:44px">{trilhas_html}</div>
  </div>
  {reg}
  <div style="position:absolute;left:0;right:0;bottom:0;height:32px;display:flex;
       align-items:center;gap:14px;padding:0 14px;box-sizing:border-box;
       border-top:1px solid #1B1B22">
    <div style="width:26px;height:26px;border-radius:50%;background:{C["text"]};
         display:flex;align-items:center;justify-content:center">{icone_play}</div>
    {icone("stop", 16, C["muted"])}
    <span style="color:{C["loop"] if regiao else C["muted"]};display:flex">{icone("loop",16,C["loop"] if regiao else C["muted"])}</span>
    <span style="font-size:11px;color:{C["muted"]};font-family:'JetBrains Mono',monospace;
          margin-left:6px">{tempo} / 69.82</span>
    <div style="margin-left:auto;display:flex;align-items:center;gap:14px">
      <span style="display:flex;align-items:center;gap:7px">{icone("vol",15,C["muted"])}
        <span style="width:54px;height:3px;background:{C["border"]};border-radius:2px;
              position:relative"><span style="position:absolute;left:0;top:0;height:3px;
              width:62%;background:{C["muted"]};border-radius:2px"></span></span></span>
      <div style="height:26px;padding:0 18px;border-radius:13px;background:{C["text"]};
           color:#0B0B0D;font-size:11px;font-weight:600;letter-spacing:0.06em;
           display:flex;align-items:center;gap:7px">
        <svg width="10" height="10" viewBox="0 0 24 24"><path d="M7 4.5 19 12 7 19.5Z" fill="#0B0B0D"/></svg>
        ASSISTIR</div>
    </div>
  </div>
  {cur}
</div>'''


# --------------------------------------------------------------- envelopes
def dc(corpo, style_extra="", fundo=None):
    return f'''<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap">
  <style>
    body {{ margin:0; font-family:'Space Grotesk', ui-sans-serif, system-ui, sans-serif;
            color:{C["text"]}; background:{fundo or C["bg"]}; }}
    a {{ color:#5AC8FA; }} a:hover {{ color:#8FDBFC; }}
    * {{ -webkit-font-smoothing:antialiased; }}
    {style_extra}
  </style>
</helmet>
{corpo}
</x-dc>
</body>
</html>'''


def tela(palco_html, painel_html, tl_html, faixa="Pulso · eletrônica minimalista"):
    return f'''<div style="width:{W}px;height:{H}px;background:{C["bg"]};
     display:flex;flex-direction:column;overflow:hidden">
  {cabecalho(faixa)}
  <div style="display:flex;flex:none">{palco_html}{painel_html}</div>
  {tl_html}
</div>'''


os.makedirs("/home/claude/design/out", exist_ok=True)
def salvar(nome, html):
    p = f"/home/claude/design/out/{nome}"
    open(p, "w", encoding="utf-8").write(html)
    print(f"  {nome:26} {len(html)//1024:>4} KB")
print("Artboards:")

# ============================================================= 1. Entrada
fundo_entrada = desenhar(COMP, escala=0.75, brilho=0.34,
                         indices=set(range(0, 25, 2)))
salvar("Entrada.dc.html", dc(f'''
<div style="position:relative;width:{W}px;height:{H}px;background:#08080A;overflow:hidden">
  <svg width="{W}" height="{H}" viewBox="0 0 {PW} {PH}"
       style="position:absolute;inset:0;opacity:0.5">{fundo_entrada}</svg>
  <div style="position:absolute;inset:0;background:radial-gradient(ellipse at 50% 50%,
       rgba(8,8,10,0.55) 0%, rgba(8,8,10,0.94) 62%)"></div>
  <div style="position:absolute;inset:0;opacity:0.035;background-image:{GRAO}"></div>
  {sprockets(W,"top")}{sprockets(W,"bottom")}
  <div style="position:absolute;inset:0;display:flex;flex-direction:column;
       align-items:center;justify-content:center;gap:0">
    <div style="font-size:11px;letter-spacing:0.34em;text-transform:uppercase;
         color:{C["muted"]};margin-bottom:26px">Protótipo · pesquisa de mestrado</div>
    <div style="font-size:20px;font-weight:700;letter-spacing:-0.01em">Riscos que Dançam</div>
    <div style="font-size:13px;color:{C["muted"]};margin-top:14px;max-width:420px;
         text-align:center;line-height:1.6">Escute uma música e desenhe o que você
         percebe nela. No final, assista à sua composição.</div>
    <div style="margin-top:38px;height:40px;padding:0 30px;border-radius:20px;
         background:{C["text"]};color:#0B0B0D;font-size:13px;font-weight:600;
         display:flex;align-items:center">Começar</div>
  </div>
</div>''', fundo="#08080A"))

# ========================================================= 2. Palco vazio
vazio_extra = f'''<div style="position:absolute;inset:0;display:flex;flex-direction:column;
     align-items:center;justify-content:center;gap:20px;pointer-events:none">
  <svg width="54" height="54" viewBox="0 0 54 54">
    <circle cx="27" cy="27" r="13" fill="{C["muted"]}" opacity="0.2"/>
    <circle cx="27" cy="27" r="22" fill="none" stroke="{C["muted"]}" stroke-width="1"
            stroke-dasharray="3 5" opacity="0.35"/></svg>
  <div style="font-size:12.5px;color:{C["muted"]};text-align:center;line-height:1.65">
    Selecione um trecho na linha do tempo e escute.<br>Depois desenhe o que você vê.</div>
</div>'''
salvar("PalcoVazio.dc.html", dc(tela(
    palco("", extra=vazio_extra), painel(None),
    linha_do_tempo(cursor=0, vazio=True))))

# ==================================================== 3. Escutando um trecho
salvar("Escutando.dc.html", dc(tela(
    palco(desenhar(COMP, ativos=ATIVOS_TOCANDO, indices=set(range(14)))),
    painel(None),
    linha_do_tempo(cursor=18.6, regiao=(14.2, 22.8), tocando=True))))

# ================================================= 4. Elemento selecionado
alcas = ""
_e = COMP[0]
for dx, dy in ((-1,-1),(1,-1),(-1,1),(1,1)):
    ax = _e["x"] + dx * (_e["r"] + 13); ay = _e["y"] + dy * (_e["r"] + 13)
    alcas += (f'<div style="position:absolute;left:{ax-4:.0f}px;top:{ay-4:.0f}px;width:8px;'
              f'height:8px;background:#fff;border-radius:1px"></div>')
alcas += (f'<div style="position:absolute;left:{_e["x"]-_e["r"]-13:.0f}px;'
          f'top:{_e["y"]-_e["r"]-13:.0f}px;width:{2*(_e["r"]+13):.0f}px;'
          f'height:{2*(_e["r"]+13):.0f}px;border:1px solid rgba(255,255,255,0.55)"></div>')
salvar("ElementoSelecionado.dc.html", dc(tela(
    palco(desenhar(COMP, ativos={0}, indices=set(range(16))), extra=alcas),
    painel(dict(tipo="ponto", banda=0, comp="pulsar", reacao=72, cor="#FF3B30",
                tam=58, op=80, trecho="14,2s → 22,8s", contador=16)),
    linha_do_tempo(cursor=18.6, regiao=(14.2, 22.8), sel_trilha=4, tocando=True))))

# ========================================================== 5. Composição (Main)
salvar("Main.dc.html", dc(tela(
    palco(desenhar(COMP, ativos=ATIVOS_TOCANDO)),
    painel(None),
    linha_do_tempo(cursor=42.1, tocando=True))))

# ========================================================== 6. Modo Cinema
cinema_svg = desenhar(COMP, ativos=ATIVOS_CINEMA, escala=1.18, brilho=1.25,
                      particulas=True)
salvar("Cinema.dc.html", dc(f'''
<div style="position:relative;width:{W}px;height:{H}px;background:{C["palco"]};overflow:hidden">
  <svg width="{W}" height="{H}" viewBox="0 0 {PW} {PH}" preserveAspectRatio="xMidYMid slice"
       style="position:absolute;inset:0">{cinema_svg}</svg>
  <div style="position:absolute;inset:0;pointer-events:none;
       background:radial-gradient(ellipse at 50% 48%, rgba(0,0,0,0) 34%, rgba(0,0,0,0.76) 100%)"></div>
  <div style="position:absolute;inset:0;pointer-events:none;opacity:0.035;background-image:{GRAO}"></div>
  {sprockets(W,"top")}{sprockets(W,"bottom")}
  <div style="position:absolute;left:0;right:0;bottom:0;height:2px;background:rgba(255,255,255,0.14)">
    <div style="height:2px;width:61%;background:rgba(255,255,255,0.85)"></div></div>
</div>''', fundo=C["palco"]))

# ===================================================== 7. Fim da animação
salvar("FimDaAnimacao.dc.html", dc(f'''
<div style="position:relative;width:{W}px;height:{H}px;background:{C["palco"]};overflow:hidden">
  <svg width="{W}" height="{H}" viewBox="0 0 {PW} {PH}" preserveAspectRatio="xMidYMid slice"
       style="position:absolute;inset:0;opacity:0.3">{cinema_svg}</svg>
  <div style="position:absolute;inset:0;background:rgba(8,8,10,0.7)"></div>
  {sprockets(W,"top")}{sprockets(W,"bottom")}
  <div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center">
    <div style="width:420px;background:{C["surface"]};border:1px solid {C["border"]};
         border-radius:6px;padding:28px 26px 24px;box-sizing:border-box">
      <div style="font-size:15px;font-weight:600">Sua composição</div>
      <div style="font-size:11.5px;color:{C["muted"]};margin-top:7px">
        26 elementos sobre <span style="color:{C["text"]}">Pulso</span> · 1min 10s</div>
      <div style="height:38px;border-radius:19px;background:{C["text"]};color:#0B0B0D;
           font-size:12.5px;font-weight:600;display:flex;align-items:center;
           justify-content:center;margin-top:24px">Assistir de novo</div>
      <div style="height:38px;border-radius:19px;border:1px solid {C["border"]};
           font-size:12.5px;display:flex;align-items:center;justify-content:center;
           margin-top:10px">Voltar a editar</div>
      <div style="text-align:center;font-size:11px;color:{C["muted"]};margin-top:18px">
        Baixar a composição em PNG</div>
    </div>
  </div>
</div>''', fundo=C["palco"]))

# ============================================================= 8. Tutorial
def passo(n, titulo, ilustra):
    return f'''<div style="flex:1">
  <div style="height:112px;background:{C["palco"]};border:1px solid {C["border"]};
       border-radius:5px;display:flex;align-items:center;justify-content:center;
       box-sizing:border-box">{ilustra}</div>
  <div style="font-size:10px;color:{C["muted"]};margin-top:12px;
       font-family:'JetBrains Mono',monospace">{n}</div>
  <div style="font-size:12.5px;line-height:1.5;margin-top:5px">{titulo}</div>
</div>'''

il1 = ('<svg width="120" height="46" viewBox="0 0 120 46">' +
       "".join(f'<circle cx="{16+i*23}" cy="23" r="{10 if i==1 else 8}" fill="{c}" '
               f'opacity="{1 if i==1 else 0.45}"/>' +
               (f'<circle cx="{16+i*23}" cy="23" r="14" fill="none" stroke="#EDEDF0" '
                f'stroke-width="1.4"/>' if i == 1 else "")
               for i, c in enumerate(["#FF3B30", "#FFB300", "#0A84FF", "#5AC8FA"])) +
       '</svg>')
il2 = ('<svg width="130" height="66" viewBox="0 0 130 66">'
       '<line x1="10" y1="54" x2="118" y2="14" stroke="#5AC8FA" stroke-width="2.5" '
       'stroke-linecap="round"/><circle cx="34" cy="26" r="9" fill="#FF3B30"/>'
       '<circle cx="92" cy="46" r="5" fill="#FFB300"/>'
       '<polygon points="66,22 76,40 56,40" fill="none" stroke="#30D158" stroke-width="2"/></svg>')
il3 = ('<svg width="130" height="52" viewBox="0 0 130 52">'
       '<rect x="4" y="12" width="122" height="28" rx="2" fill="none" stroke="#2A2A31"/>' +
       "".join(f'<rect x="{10+i*7}" y="{26-abs(math.sin(i*0.7))*11:.0f}" width="3" '
               f'height="{abs(math.sin(i*0.7))*22+3:.0f}" fill="#8A8A94" opacity="0.5"/>'
               for i in range(16)) +
       '<line x1="74" y1="6" x2="74" y2="46" stroke="#fff" stroke-width="2"/></svg>')

salvar("Tutorial.dc.html", dc(f'''
<div style="position:relative;width:{W}px;height:{H}px;overflow:hidden">
  <div style="position:absolute;inset:0;filter:blur(1.5px);opacity:0.5">
    {tela(palco(desenhar(COMP, indices=set(range(14)))), painel(None),
          linha_do_tempo(cursor=18.6, regiao=(14.2,22.8)))}
  </div>
  <div style="position:absolute;inset:0;background:rgba(8,8,10,0.76)"></div>
  <div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center">
    <div style="width:660px;background:{C["surface"]};border:1px solid {C["border"]};
         border-radius:6px;padding:28px;box-sizing:border-box">
      <div style="font-size:15px;font-weight:600">Como funciona</div>
      <div style="display:flex;gap:18px;margin-top:22px">
        {passo("01","Escolha um trecho e escute em repetição", il3)}
        {passo("02","Desenhe o que você percebe — e diga a que som ele responde", il1)}
        {passo("03","Assista à sua composição sobre a música", il2)}
      </div>
      <div style="display:flex;align-items:center;justify-content:space-between;margin-top:26px">
        <div style="display:flex;gap:6px">
          <span style="width:16px;height:3px;border-radius:2px;background:{C["text"]}"></span>
          <span style="width:16px;height:3px;border-radius:2px;background:{C["border"]}"></span>
          <span style="width:16px;height:3px;border-radius:2px;background:{C["border"]}"></span></div>
        <div style="height:34px;padding:0 22px;border-radius:17px;background:{C["text"]};
             color:#0B0B0D;font-size:12px;font-weight:600;display:flex;align-items:center">
          Começar</div>
      </div>
    </div>
  </div>
</div>'''))

# ================================================================ 9. Tablet
TW, TH = 834, 1112
t_palco_h = TH - 44 - 148 - 86
tab_elems = [{**e, "x": e.get("x", 0)*0.73, "y": e.get("y", 0)*0.90,
              "x1": e.get("x1", 0)*0.73, "y1": e.get("y1", 0)*0.90,
              "x2": e.get("x2", 0)*0.73, "y2": e.get("y2", 0)*0.90,
              "r": e.get("r", 0)*0.80, "w": e.get("w", 0)*0.80} for e in COMP]
palco_tablet = palco(desenhar(tab_elems, ativos=ATIVOS_TOCANDO), w=TW, h=t_palco_h)
salvar("Tablet.dc.html", dc(f'''
<div style="width:{TW}px;height:{TH}px;background:{C["bg"]};display:flex;
     flex-direction:column;overflow:hidden">
  <div style="height:44px;display:flex;align-items:center;justify-content:space-between;
       padding:0 14px;background:{C["surface"]};border-bottom:1px solid {C["border"]};
       box-sizing:border-box">
    <span style="font-size:13px;font-weight:600">Riscos que Dançam</span>
    <div style="display:flex;align-items:center;gap:12px">
      <span style="font-size:11px;color:{C["muted"]}">Pulso</span>
      <div style="width:28px;height:28px;border-radius:50%;border:1px solid {C["border"]};
           display:flex;align-items:center;justify-content:center">{icone("help",15,C["muted"])}</div>
    </div>
  </div>
  {palco_tablet}
  <div style="height:86px;background:{C["surface"]};border-top:1px solid {C["border"]};
       display:flex;align-items:center;gap:10px;padding:0 14px;box-sizing:border-box;
       overflow:hidden">
    <div style="display:flex;gap:7px;flex:none">
      <div style="width:56px;height:56px;border:1px solid #EDEDF0;border-radius:6px;
           background:#22222A;display:flex;align-items:center;justify-content:center">
        <svg width="18" height="18" viewBox="0 0 24 24"><circle cx="12" cy="12" r="6" fill="#EDEDF0"/></svg></div>
      <div style="width:56px;height:56px;border:1px solid {C["border"]};border-radius:6px;
           display:flex;align-items:center;justify-content:center">{icone("linha",18,C["muted"])}</div>
      <div style="width:56px;height:56px;border:1px solid {C["border"]};border-radius:6px;
           display:flex;align-items:center;justify-content:center">{icone("forma",18,C["muted"])}</div>
    </div>
    <div style="width:1px;height:46px;background:{C["border"]};flex:none"></div>
    <div style="display:flex;flex-direction:column;gap:7px;flex:none">
      <div style="display:flex;gap:7px">{"".join(f'<span style="width:22px;height:22px;border-radius:50%;background:{c}"></span>' for c in PALETA[:4])}</div>
      <div style="display:flex;gap:7px">{"".join(f'<span style="width:22px;height:22px;border-radius:50%;background:{c}"></span>' for c in PALETA[4:])}</div>
    </div>
    <div style="width:1px;height:46px;background:{C["border"]};flex:none"></div>
    <div style="display:flex;gap:6px;flex:none">
      {"".join(f'<div style="height:28px;padding:0 11px;border-radius:14px;border:1px solid '
               f'{"#EDEDF0" if i==0 else C["border"]};display:flex;align-items:center;gap:6px">'
               f'<span style="width:7px;height:7px;border-radius:50%;background:{cor}"></span>'
               f'<span style="font-size:10.5px;color:{C["text"] if i==0 else C["muted"]}">{n}</span></div>'
               for i, (n, cor, _) in enumerate(BANDAS))}
    </div>
  </div>
  {linha_do_tempo(w=TW, cursor=18.6, regiao=(14.2,22.8), tocando=True)}
</div>'''))

# ================================================================ 10. Mobile
MW, MH = 390, 844
m_palco_h = MH - 40 - 66 - 198
mob_elems = [{**e, "x": e.get("x",0)*0.34, "y": e.get("y",0)*0.62,
              "x1": e.get("x1",0)*0.34, "y1": e.get("y1",0)*0.62,
              "x2": e.get("x2",0)*0.34, "y2": e.get("y2",0)*0.62,
              "r": e.get("r",0)*0.44, "w": e.get("w",0)*0.6} for e in COMP]
mob_flutuante = f'''<div style="position:absolute;left:12px;right:12px;bottom:12px;height:44px;
     border-radius:22px;background:rgba(26,26,31,0.82);backdrop-filter:blur(12px);
     border:1px solid rgba(42,42,49,0.9);display:flex;align-items:center;gap:12px;
     padding:0 8px 0 10px;box-sizing:border-box">
  <div style="width:28px;height:28px;border-radius:50%;background:{C["text"]};
       display:flex;align-items:center;justify-content:center">{icone("pause",14,"#0B0B0D")}</div>
  {icone("loop",16,C["loop"])}
  <span style="font-size:10.5px;color:{C["muted"]};font-family:'JetBrains Mono',monospace">18.60</span>
  <div style="margin-left:auto;height:30px;padding:0 15px;border-radius:15px;
       background:{C["text"]};color:#0B0B0D;font-size:10.5px;font-weight:600;
       letter-spacing:0.05em;display:flex;align-items:center">ASSISTIR</div>
</div>'''
def px_m(t): return t / DUR * MW
salvar("Mobile.dc.html", dc(f'''
<div style="width:{MW}px;height:{MH}px;background:{C["bg"]};display:flex;
     flex-direction:column;overflow:hidden">
  <div style="height:40px;display:flex;align-items:center;justify-content:space-between;
       padding:0 14px;background:{C["surface"]};border-bottom:1px solid {C["border"]};
       box-sizing:border-box">
    <span style="font-size:12.5px;font-weight:600">Riscos que Dançam</span>
    <span style="font-size:10.5px;color:{C["muted"]}">Pulso</span>
  </div>
  {palco(desenhar(mob_elems, ativos=ATIVOS_TOCANDO), w=MW, h=m_palco_h, extra=mob_flutuante)}
  <div style="position:relative;height:66px;background:{C["surfalt"]};
       border-top:1px solid {C["border"]};box-sizing:border-box">
    <svg width="{MW}" height="34" style="position:absolute;top:0;left:0">{waveform(MW,34,9)}</svg>
    <div style="position:absolute;left:{px_m(14.2):.0f}px;top:0;width:{px_m(22.8)-px_m(14.2):.0f}px;
         height:66px;background:rgba(255,214,10,0.12);border-left:2px solid {C["loop"]};
         border-right:2px solid {C["loop"]};box-sizing:border-box"></div>
    <div style="position:absolute;top:36px;left:0;right:0;height:26px">
      {"".join(f'<div style="position:absolute;left:{px_m(a):.0f}px;top:{(i%3)*8+1}px;'
               f'width:{max(px_m(b)-px_m(a),3):.0f}px;height:6px;border-radius:2px;'
               f'background:{cor};opacity:0.78"></div>'
               for i,(a,b,cor,_) in enumerate(TRILHAS))}
    </div>
    <div style="position:absolute;left:{px_m(18.6):.0f}px;top:0;width:2px;height:66px;
         background:#fff;box-shadow:0 0 8px rgba(255,255,255,0.7)"></div>
  </div>
  <div style="height:198px;background:{C["surface"]};border-top:1px solid {C["border"]};
       border-radius:14px 14px 0 0;padding:14px 16px;box-sizing:border-box">
    <div style="width:36px;height:3px;border-radius:2px;background:{C["border"]};
         margin:0 auto 14px"></div>
    <div style="display:flex;align-items:center;justify-content:space-between">
      <span style="font-size:11px;letter-spacing:0.08em;text-transform:uppercase;
            color:{C["muted"]}">Responde a</span>{curva_mini(0, 52, 14)}</div>
    <div style="display:grid;grid-template-columns:repeat(2, minmax(0,1fr));gap:7px;margin-top:10px">
      {"".join(f'<div style="height:38px;border:1px solid {"#EDEDF0" if i==0 else C["border"]};'
               f'border-radius:5px;display:flex;align-items:center;gap:8px;padding:0 11px;'
               f'box-sizing:border-box"><span style="width:8px;height:8px;border-radius:50%;'
               f'background:{cor}"></span><span style="font-size:11.5px;'
               f'color:{C["text"] if i==0 else C["muted"]}">{n}</span></div>'
               for i,(n,cor,_) in enumerate(BANDAS))}
    </div>
    <div style="display:flex;gap:9px;margin-top:14px;align-items:center">
      {"".join(f'<span style="width:28px;height:28px;border-radius:50%;background:{c}'
               + ('; box-shadow:0 0 0 2px #1A1A1F,0 0 0 4px #EDEDF0' if c=="#FF3B30" else '')
               + '"></span>' for c in PALETA)}
    </div>
  </div>
</div>''', fundo=C["bg"]))

# =============================================================== 11. Sistema
def amostra(rot, conteudo):
    return (f'<div><div style="font-size:9.5px;color:{C["muted"]};margin-bottom:7px">{rot}</div>'
            f'{conteudo}</div>')

def swatch(nome, hexa, sub=""):
    return f'''<div style="width:118px">
  <div style="height:44px;border-radius:4px;background:{hexa};border:1px solid rgba(255,255,255,0.07)"></div>
  <div style="font-size:10.5px;margin-top:6px">{nome}</div>
  <div style="font-size:9.5px;color:{C["muted"]};font-family:'JetBrains Mono',monospace">{hexa}</div>
  {f'<div style="font-size:9px;color:{C["muted"]};margin-top:2px">{sub}</div>' if sub else ''}
</div>'''

estrutura = "".join(swatch(n, h) for n, h in [
    ("bg-base", C["bg"]), ("bg-palco", C["palco"]), ("surface", C["surface"]),
    ("surface-alt", C["surfalt"]), ("border", C["border"]), ("text", C["text"]),
    ("text-muted", C["muted"]), ("loop", C["loop"])])
bandas_sw = "".join(swatch(n, h, hz) for n, h, hz in BANDAS)
paleta_sw = "".join(
    f'<div style="width:46px;height:46px;border-radius:50%;background:{c}"></div>'
    for c in PALETA)

tipo = f'''<div style="display:flex;flex-direction:column;gap:12px">
  <div><span style="font-size:20px;font-weight:700">Riscos que Dançam</span>
    <span style="font-size:9.5px;color:{C["muted"]};margin-left:10px">Space Grotesk 700 · 20px · o maior da interface</span></div>
  <div><span style="font-size:14px;font-weight:600">Cabeçalho e títulos</span>
    <span style="font-size:9.5px;color:{C["muted"]};margin-left:10px">600 · 14px</span></div>
  <div><span style="font-size:12px">Corpo e rótulos de controle</span>
    <span style="font-size:9.5px;color:{C["muted"]};margin-left:10px">400 · 12px</span></div>
  <div><span style="font-size:11px;letter-spacing:0.08em;text-transform:uppercase;color:{C["muted"]}">Rótulo de seção</span>
    <span style="font-size:9.5px;color:{C["muted"]};margin-left:10px">11px · caixa alta · tracking 0.08em</span></div>
  <div><span style="font-size:13px;font-family:'JetBrains Mono',monospace">18.60 / 69.82</span>
    <span style="font-size:9.5px;color:{C["muted"]};margin-left:10px">JetBrains Mono · tempo e números</span></div>
</div>'''

botoes = f'''<div style="display:flex;gap:14px;align-items:flex-end;flex-wrap:wrap">
  {amostra("Assistir", '<div style="height:26px;padding:0 18px;border-radius:13px;background:#EDEDF0;color:#0B0B0D;font-size:11px;font-weight:600;letter-spacing:0.06em;display:flex;align-items:center">ASSISTIR</div>')}
  {amostra("Play", f'<div style="width:26px;height:26px;border-radius:50%;background:{C["text"]};display:flex;align-items:center;justify-content:center">{icone("play",16,"#0B0B0D")}</div>')}
  {amostra("Contorno", f'<div style="height:30px;padding:0 16px;border-radius:15px;border:1px solid {C["border"]};font-size:12px;display:flex;align-items:center">Voltar a editar</div>')}
  {amostra("Desabilitado", f'<div style="height:30px;padding:0 16px;border-radius:15px;border:1px solid #1E1E25;color:#4A4A54;font-size:12px;display:flex;align-items:center">Indisponível</div>')}
</div>'''

ferramentas = f'''<div style="display:flex;gap:14px;align-items:flex-end">
  {amostra("Ativa", ferramenta_btn("ponto", True))}
  {amostra("Inativa", ferramenta_btn("linha", False))}
  {amostra("Inativa", ferramenta_btn("forma", False))}
</div>'''

pastilhas = f'''<div style="width:250px;display:flex;flex-direction:column;gap:2px">
  {pastilha_banda(0, True)}{pastilha_banda(1, False)}</div>'''

comps = f'''<div style="width:250px;display:grid;grid-template-columns:repeat(2, minmax(0,1fr));gap:7px">
  {comp_btn("Pulsar","pulsar",True)}{comp_btn("Girar","girar",False)}
  {comp_btn("Vibrar","vibrar",False)}{comp_btn("Acender","acender",False)}</div>'''

MUT, MONO, SURFALT, BORD = C['muted'], "'JetBrains Mono',monospace", C['surfalt'], C['border']
camadas = f'''<div style="display:flex;flex-direction:column;gap:9px;width:560px">
  {"".join(f'<div style="display:flex;align-items:center;gap:12px">'
           f'<span style="width:84px;font-size:9.5px;color:{MUT};text-align:right">{n}</span>'
           f'<div style="flex:1;height:{h}px;background:{SURFALT};border:1px solid {BORD};'
           f'border-radius:3px;box-sizing:border-box;position:relative;overflow:hidden">{inner}</div>'
           f'<span style="width:34px;font-size:9.5px;color:{MUT};'
           f'font-family:{MONO}">{h}px</span></div>'
           for n, h, inner in [
             ("régua", 18, "".join(f'<div style="position:absolute;left:{i*46+8}px;top:0;height:6px;width:1px;background:#2A2A31"></div>' for i in range(10))),
             ("forma de onda", 54, f'<svg width="440" height="54">{waveform(440,54)}</svg>'),
             ("trilhas", 44, "".join(f'<div style="position:absolute;left:{(i*37)%400+6}px;top:{(i%4)*11+2}px;width:{60+i*7}px;height:8px;border-radius:2px;background:{PALETA[i%8]};opacity:0.75"></div>' for i in range(9))),
             ("transporte", 32, f'<div style="position:absolute;left:10px;top:3px;display:flex;align-items:center;gap:12px">{icone("play",14,C["muted"])}{icone("stop",14,C["muted"])}{icone("loop",14,C["loop"])}</div>'),
           ])}
</div>'''


pelicula_amostra = palco(desenhar(
    [dict(t="ponto", x=70, y=54, r=17, c="#FF3B30", b=0),
     dict(t="linha", x1=120, y1=92, x2=250, y2=30, w=2.5, c="#5AC8FA", b=3),
     dict(t="forma", x=214, y=78, r=19, n=3, rot=-10, c="#30D158", b=1)],
    ativos={0}), w=282, h=118)

MOVIMENTO = [
    ("Cursor de reprodução", "linear, sem easing — é uma máquina"),
    ("Elemento reagindo", "contínuo, vindo da curva da banda"),
    ("Piso de brilho", "~15% de variação em todo elemento"),
    ("Entrada / saída no trecho", "fade de 400 ms"),
    ("Criação de elemento", "fade + escala, 120 ms"),
    ("Entrar no Modo Cinema", "interface some em 400 ms"),
    ("Interface em geral", "≤ 200 ms, sem bounce"),
]
_linha_mov = lambda a, b: (
    f'<div style="padding:6px 0;border-bottom:1px solid #17171D">'
    f'<div style="font-size:11px">{a}</div>'
    f'<div style="font-size:10px;color:{C["muted"]};margin-top:2px">{b}</div></div>')
movimento_html = (
    '<div style="display:grid;grid-template-columns:repeat(2, minmax(0,1fr));gap:0 24px">'
    + '<div>' + "".join(_linha_mov(a, b) for a, b in MOVIMENTO[:4]) + '</div>'
    + '<div>' + "".join(_linha_mov(a, b) for a, b in MOVIMENTO[4:]) + '</div></div>')

selecao_amostra = f'''<div style="position:relative;width:180px;height:118px;
     background:{C["palco"]};border-radius:4px;overflow:hidden">
  <svg width="180" height="118" style="position:absolute;inset:0">
    <circle cx="90" cy="59" r="22" fill="#FF3B30" opacity="0.95"
            style="filter:drop-shadow(0 0 14px #FF3B30cc)"/></svg>
  <div style="position:absolute;left:55px;top:24px;width:70px;height:70px;
       border:1px solid rgba(255,255,255,0.55)"></div>
  {"".join(f'<div style="position:absolute;left:{51+dx*70}px;top:{20+dy*70}px;width:8px;height:8px;background:#fff;border-radius:1px"></div>' for dx in (0,1) for dy in (0,1))}
</div>'''

salvar("Sistema.dc.html", dc(f'''
<div style="width:{W}px;height:{H}px;background:{C["bg"]};padding:34px 40px;
     box-sizing:border-box;overflow:hidden">
  <div style="font-size:14px;font-weight:600">Sistema visual</div>
  <div style="font-size:11px;color:{C["muted"]};margin-top:5px">Riscos que Dançam · mesa de montagem</div>

  <div style="display:flex;gap:44px;margin-top:26px">
    <div>
      {rotulo("Estrutura")}
      <div style="display:flex;gap:10px;flex-wrap:wrap;width:520px">{estrutura}</div>
      {rotulo("Bandas de frequência", 22)}
      <div style="display:flex;gap:10px">{bandas_sw}</div>
      {rotulo("Paleta livre dos elementos", 22)}
      <div style="display:flex;gap:10px">{paleta_sw}</div>
    </div>
    <div style="width:1px;background:{C["border"]}"></div>
    <div>
      {rotulo("Tipografia")}{tipo}
      {rotulo("Botões", 24)}{botoes}
      {rotulo("Ferramenta", 20)}{ferramentas}
    </div>
  </div>

  <div style="display:flex;gap:44px;margin-top:22px;align-items:flex-start">
    <div>{rotulo("Banda e comportamento")}
      <div style="display:flex;gap:22px">{pastilhas}{comps}</div>
      <div style="display:flex;gap:22px;margin-top:22px">
        <div>{rotulo("Seleção")}{selecao_amostra}</div>
        <div>{rotulo("Película, grão e vinheta")}{pelicula_amostra}</div>
      </div>
    </div>
    <div style="width:1px;height:330px;background:{C["border"]}"></div>
    <div>{rotulo("Camadas da linha do tempo")}{camadas}
      {rotulo("Movimento", 18)}
      <div style="width:560px">{movimento_html}</div>
    </div>
  </div>
</div>'''))

# ------------------------------------------------------------- canvas.json
GAP_X, GAP_Y = 140, 150
linhas = [
    ["Entrada.dc.html", "PalcoVazio.dc.html", "Escutando.dc.html"],
    ["ElementoSelecionado.dc.html", "Main.dc.html", "Cinema.dc.html"],
    ["FimDaAnimacao.dc.html", "Tutorial.dc.html", "Sistema.dc.html"],
]
arts = []
for r, linha in enumerate(linhas):
    for c_, f in enumerate(linha):
        arts.append({"file": f, "x": c_ * (W + GAP_X), "y": r * (H + GAP_Y),
                     "w": W, "h": H})
y4 = 3 * (H + GAP_Y)
arts.append({"file": "Tablet.dc.html", "x": 0, "y": y4, "w": TW, "h": TH})
arts.append({"file": "Mobile.dc.html", "x": TW + GAP_X, "y": y4, "w": MW, "h": MH})

canvas = {
    "artboards": arts,
    "annotations": [
        {"id": "nota-fluxo", "x": 0, "y": -110, "w": 460,
         "text": "Fluxo principal — a pessoa entra, escolhe um trecho, escuta em loop e desenha nele."},
        {"id": "nota-editor", "x": 0, "y": H + GAP_Y - 110, "w": 460,
         "text": "O editor em uso. Main é a composição pronta; à direita, o Modo Cinema — o produto final."},
        {"id": "nota-apoio", "x": 0, "y": 2 * (H + GAP_Y) - 110, "w": 460,
         "text": "Telas de apoio e o sistema visual."},
        {"id": "nota-resp", "x": 0, "y": y4 - 110, "w": 460,
         "text": "Responsivo. No tablet o painel vira barra; no celular, gaveta."},
    ],
    "launch": {"view": "canvas"},
}
json.dump(canvas, open("/home/claude/design/out/canvas.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)
print("  canvas.json")
