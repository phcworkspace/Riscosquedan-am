#!/usr/bin/env python3
"""
mapear_faixa.py — gera o "mapa" de uma faixa: o arquivo JSON que a animação
do protótipo consome para saber, a cada instante, o que está acontecendo no som.

O mapa é pré-calculado fora do navegador. Isso resolve três problemas de uma vez:

  1. A animação fica DETERMINÍSTICA — o mesmo desenho produz o mesmo resultado
     toda vez, o que importa quando a peça vai ser apresentada.
  2. Funciona com o cursor parado, arrastado ou correndo para trás, porque é
     uma consulta por tempo e não uma análise ao vivo.
  3. Tira a FFT do loop de desenho, sobrando quadro para o resto.

Uso:
    python mapear_faixa.py faixa.mp3                 # gera faixa.map.json
    python mapear_faixa.py *.mp3 --fps 30 --saida mapas/

Requer: pip install librosa soundfile   (+ ffmpeg no sistema)
"""
import os, json, argparse
import numpy as np
import librosa

SR = 22050

# QUATRO bandas, não seis. Medimos a correlação entre as curvas nas faixas de
# teste: com seis bandas os pares vizinhos chegavam a 0,97 — ou seja, duas
# cores diferentes produziriam praticamente a mesma animação, e a escolha da
# pessoa não significaria nada. Com quatro bandas o pior par cai para 0,84 e
# cada banda tem comportamento próprio. Quatro é o que o material sustenta.
BANDAS = [
    ("grave",   20,   150),    # bumbo, baixo, corpo
    ("medio",   150,  700),    # harmonia, notas centrais, voz grave
    ("agudo",   700,  3200),   # ataque, presença, voz aguda
    ("brilho",  3200, 11000),  # ar, pratos, sibilância
]


def envelope(x, ataque=0.55, solta=0.11):
    """Seguidor de envelope assimétrico: sobe rápido, desce devagar.

    Sem isso as curvas tremem quadro a quadro e a animação fica nervosa. Com
    isso cada banda ganha o comportamento de um VU — reage no ataque e
    respira na queda, que é como a percepção funciona.
    """
    y = np.zeros_like(x)
    v = 0.0
    for i, a in enumerate(x):
        k = ataque if a > v else solta
        v += (a - v) * k
        y[i] = v
    return y


def curvas_de_banda(y, sr, fps):
    hop = max(int(round(sr / fps)), 1)
    S = np.abs(librosa.stft(y, n_fft=2048, hop_length=hop))
    freqs = librosa.fft_frequencies(sr=sr, n_fft=2048)

    saida = {}
    for nome, f0, f1 in BANDAS:
        m = (freqs >= f0) & (freqs < f1)
        if not m.any():
            saida[nome] = []
            continue
        banda = S[m].mean(axis=0)

        # Escala em dB, não linear. Audição é logarítmica: em escala linear a
        # curva gruda no topo e a animação fica chapada — foi o que aconteceu
        # na primeira versão (90% do tempo acima de 0,5).
        db = 20 * np.log10(banda + 1e-10)

        # Normaliza CADA banda pela própria janela dinâmica (p20 → p99), não
        # pelo pico geral: assim uma faixa sem agudos ainda anima os elementos
        # de agudo em vez de deixá-los parados. O mapa descreve o RELEVO de
        # cada banda, não o volume absoluto dela.
        lo, hi = np.percentile(db, 20), np.percentile(db, 99)
        norm = np.clip((db - lo) / max(hi - lo, 1e-6), 0, 1)

        # Gama > 1 empurra os valores médios para baixo: o elemento fica em
        # repouso na maior parte do tempo e salta nos eventos.
        norm = norm ** 1.6
        saida[nome] = envelope(norm)
    return saida, hop


def picos_waveform(y, n=1200):
    """Envelope da forma de onda para desenhar a régua de tempo."""
    passo = max(len(y) // n, 1)
    cortes = y[:passo * n].reshape(-1, passo)
    p = np.abs(cortes).max(axis=1)
    return (p / (p.max() or 1))


def secoes(y, sr, n=6):
    dur = librosa.get_duration(y=y, sr=sr)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    feat = np.vstack([librosa.util.normalize(mfcc, axis=1),
                      librosa.util.normalize(chroma, axis=1)])
    fronteiras = librosa.frames_to_time(
        librosa.segment.agglomerative(feat, n), sr=sr)
    t = np.unique(np.concatenate([[0.0], fronteiras, [dur]]))
    rotulos = "ABCDEFGHIJ"
    return [{"inicio": round(float(t[i]), 3), "fim": round(float(t[i+1]), 3),
             "rotulo": rotulos[i % len(rotulos)]}
            for i in range(len(t) - 1) if t[i+1] - t[i] > 0.4]


def mapear(caminho, fps=30, casas=3):
    y, sr = librosa.load(caminho, sr=SR, mono=True)
    dur = float(librosa.get_duration(y=y, sr=sr))

    bandas, hop = curvas_de_banda(y, sr, fps)
    n_quadros = len(next(iter(bandas.values())))

    rms = librosa.feature.rms(y=y, hop_length=hop)[0][:n_quadros]
    rms = envelope(rms); rms = rms / (np.percentile(rms, 98) or 1)
    rms = np.clip(rms, 0, 1)

    onset = librosa.onset.onset_strength(y=y, sr=sr)
    ataques = librosa.onset.onset_detect(onset_envelope=onset, sr=sr, units="time")
    contraste = float(np.percentile(onset, 95) / (onset.mean() + 1e-9))

    # BPM é informativo aqui, não requisito: serve para a régua de tempo
    # oferecer um snap opcional. A faixa funciona com ou sem ele.
    try:
        bpm = float(np.atleast_1d(
            librosa.beat.beat_track(onset_envelope=onset, sr=sr)[0])[0])
        batidas = librosa.beat.beat_track(onset_envelope=onset, sr=sr,
                                          units="time")[1]
    except Exception:                                   # noqa: BLE001
        bpm, batidas = 0.0, np.array([])

    r = lambda a: [round(float(v), casas) for v in a]     # noqa: E731
    return {
        "arquivo": os.path.basename(caminho),
        "duracaoSeg": round(dur, 3),
        "fps": fps,
        "quadros": int(n_quadros),
        "bandas": {k: r(v) for k, v in bandas.items()},
        "faixasDeBanda": {n: [f0, f1] for n, f0, f1 in BANDAS},
        "rms": r(rms),
        "picos": r(picos_waveform(y)),
        "ataques": r(ataques),
        "secoes": secoes(y, sr),
        "pulso": {
            "bpmEstimado": round(bpm, 2),
            "contrasteDeAtaque": round(contraste, 2),
            "temPulsoClaro": bool(contraste >= 2.0),
            "batidas": r(batidas) if contraste >= 2.0 else [],
            "nota": ("grade de batidas confiavel — pode oferecer snap"
                     if contraste >= 2.0 else
                     "faixa sustentada, sem pulso nitido — nao oferecer snap "
                     "por batida; use as secoes como referencia"),
        },
    }


def resumo(m):
    print(f"\n{'='*62}\n{m['arquivo']}\n{'='*62}")
    print(f"Duração        {m['duracaoSeg']}s · {m['quadros']} quadros a "
          f"{m['fps']}fps")
    print(f"Pulso          {'claro' if m['pulso']['temPulsoClaro'] else 'difuso'}"
          f" · contraste {m['pulso']['contrasteDeAtaque']}"
          f" · ~{m['pulso']['bpmEstimado']} BPM (informativo)")
    print(f"Ataques        {len(m['ataques'])}")
    print("Bandas         média · pico · % do tempo acima de 0,5")
    for nome, f0, f1 in BANDAS:
        c = np.array(m["bandas"][nome])
        if not len(c):
            continue
        print(f"  {nome:<11} {f0:>5}–{f1:<5}Hz   {c.mean():.3f} · "
              f"{c.max():.3f} · {100*(c > 0.5).mean():5.1f}%")
    print(f"Seções         {len(m['secoes'])}")
    for s in m["secoes"]:
        print(f"  {s['rotulo']}  {s['inicio']:>6.2f}s → {s['fim']:>6.2f}s")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Gera o mapa de uma faixa")
    ap.add_argument("arquivos", nargs="+")
    ap.add_argument("--fps", type=int, default=30,
                    help="quadros por segundo do mapa (padrão 30)")
    ap.add_argument("--saida", default=None,
                    help="pasta de destino (padrão: ao lado do áudio)")
    a = ap.parse_args()

    for caminho in a.arquivos:
        m = mapear(caminho, a.fps)
        destino = a.saida or os.path.dirname(caminho) or "."
        os.makedirs(destino, exist_ok=True)
        nome = os.path.splitext(os.path.basename(caminho))[0] + ".map.json"
        alvo = os.path.join(destino, nome)
        with open(alvo, "w", encoding="utf-8") as fh:
            json.dump(m, fh, ensure_ascii=False, separators=(",", ":"))
        resumo(m)
        print(f"→ {alvo}  ({os.path.getsize(alvo)/1024:.0f} KB)")
