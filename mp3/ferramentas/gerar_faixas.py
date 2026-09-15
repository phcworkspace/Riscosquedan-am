"""
Gerador das 3 faixas de referência do protótipo "Riscos que Dançam".

Sintetiza áudio do zero com numpy — nenhum material de terceiros é usado,
portanto não há questão de direitos. BPM, tonalidade e estrutura são
conhecidos por construção, o que torna estas faixas ideais para desenvolver
e validar o motor de áudio antes de entrar o material definitivo.
"""
import numpy as np, subprocess, json, os

SR = 44100
OUT = "/home/claude/mp3"
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------- utilidades

def adsr(n, a=0.01, d=0.1, s=0.6, r=0.2):
    a, d, r = max(int(a*SR), 1), max(int(d*SR), 1), max(int(r*SR), 1)
    sus = max(n - a - d - r, 0)
    return np.concatenate([
        np.linspace(0, 1, a), np.linspace(1, s, d),
        np.full(sus, s), np.linspace(s, 0, r)])[:n]


def osc(freq, n, wave="sine", detune=0.0):
    t = np.arange(n) / SR
    f = freq * (1 + detune)
    ph = 2 * np.pi * f * t
    if wave == "sine":  return np.sin(ph)
    if wave == "tri":   return 2/np.pi*np.arcsin(np.sin(ph))
    if wave == "saw":   return 2*((f*t) % 1.0) - 1.0
    if wave == "sq":    return np.sign(np.sin(ph))
    raise ValueError(wave)


def note(freq, dur, wave="sine", amp=0.2, env=(0.01, 0.1, 0.6, 0.2), detune=0.0):
    n = int(dur * SR)
    return osc(freq, n, wave, detune) * adsr(n, *env) * amp


def fm(freq, dur, ratio=2.0, index=3.0, amp=0.2, env=(0.005, 0.3, 0.25, 0.5)):
    n = int(dur * SR); t = np.arange(n)/SR
    mod = np.sin(2*np.pi*freq*ratio*t) * index * np.exp(-t*3)
    return np.sin(2*np.pi*freq*t + mod) * adsr(n, *env) * amp


def kick(dur=0.34, amp=0.75):
    n = int(dur*SR); t = np.arange(n)/SR
    f = 120*np.exp(-t*28) + 46
    sig = np.sin(2*np.pi*np.cumsum(f)/SR)
    return sig * np.exp(-t*9) * amp


def hat(dur=0.05, amp=0.13):
    n = int(dur*SR); t = np.arange(n)/SR
    x = np.random.default_rng(7).standard_normal(n)
    x = np.diff(np.concatenate([[0.0], x]))          # passa-alta grosseiro
    return x * np.exp(-t*70) * amp


def shaker(dur=0.09, amp=0.07, seed=3):
    n = int(dur*SR); t = np.arange(n)/SR
    x = np.random.default_rng(seed).standard_normal(n)
    x = np.diff(np.concatenate([[0.0], x]))
    return x * (np.exp(-t*22) * (1-np.exp(-t*90))) * amp


def place(buf, sig, at):
    i = int(at*SR); j = min(i+len(sig), len(buf))
    if i < len(buf): buf[i:j] += sig[:j-i]


def reverb(x, amount=0.25, decay=1.8):
    """Reverb barata por convolução com ruído em decaimento exponencial."""
    n = int(decay*SR)
    t = np.arange(n)/SR
    ir = np.random.default_rng(11).standard_normal(n) * np.exp(-t*(4.0/decay))
    ir[0] = 1.0
    ir /= np.abs(ir).sum()/3
    wet = np.convolve(x, ir)[:len(x)]
    return x*(1-amount) + wet*amount


def lowpass(x, a=0.25):
    y = np.zeros_like(x); prev = 0.0
    # filtro de 1a ordem vetorizado por blocos seria melhor; aqui basta scipy
    from scipy.signal import lfilter
    return lfilter([a], [1, -(1-a)], x)


MIDI = {  # nota -> midi
    "C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5,
    "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11,
}

def f(name, octave):
    return 440.0 * 2 ** ((MIDI[name] + 12*(octave+1) - 69) / 12)


def normalize(x, peak=0.89):
    m = np.abs(x).max()
    return x * (peak/m) if m > 0 else x


def loopavel(x, dur_exata):
    """Corta no comprimento exato e dobra a cauda de reverb de volta para o
    início, de modo que o fim emende no começo sem estalo."""
    n = int(round(dur_exata * SR))
    corpo, cauda = x[:n].copy(), x[n:]
    if len(cauda):
        k = min(len(cauda), n)
        corpo[:k] += cauda[:k]
    return corpo


def export(mono, path, title, dur_exata=None):
    if dur_exata:
        mono = loopavel(mono, dur_exata)
    x = normalize(mono)
    # leve alargamento estéreo por atraso de 8ms no canal direito
    d = int(0.008*SR)
    right = np.concatenate([np.zeros(d), x[:-d]]) * 0.92 + x * 0.08
    st = np.stack([x, normalize(right, 0.89)], axis=1)
    pcm = (np.clip(st, -1, 1) * 32767).astype("<i2").tobytes()
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "s16le", "-ar", str(SR),
         "-ac", "2", "-i", "pipe:0", "-codec:a", "libmp3lame", "-b:a", "192k",
         "-metadata", f"title={title}", "-metadata", "artist=Gerado para o proto-"
         "tipo Riscos que Dancam", path],
        input=pcm, check=True)
    print(f"  {os.path.basename(path):22} {len(x)/SR:6.2f}s")


# ------------------------------------------------------------ FAIXA 1: Pulso
# Eletrônica minimalista · 110 BPM · Dó menor · 4/4 · 32 compassos
def faixa_pulso():
    bpm, bars = 110, 32
    beat = 60/bpm; bar = beat*4
    buf = np.zeros(int(bars*bar*SR) + SR)

    # progressão: Cm - Ab - Eb - Bb (2 compassos cada)
    prog = [("C", 3, [0, 3, 7]), ("G#", 2, [0, 4, 7]),
            ("D#", 3, [0, 4, 7]), ("A#", 2, [0, 4, 7])]
    semis = list(MIDI.keys())

    def chord_freqs(root, octv, ivs):
        base = MIDI[root] + 12*(octv+1)
        return [440.0*2**((base+i-69)/12) for i in ivs]

    for b in range(bars):
        t0 = b*bar
        sec = "intro" if b < 4 else "A" if b < 12 else "B" if b < 24 else "outro"

        # bateria
        if sec != "intro" or b >= 2:
            for k in range(4):
                place(buf, kick(), t0 + k*beat)
        if sec in ("A", "B"):
            for k in range(8):
                place(buf, hat(amp=0.11 if k % 2 else 0.15), t0 + k*beat/2)
        if sec == "B":
            for k in (2, 6, 10, 14):
                place(buf, shaker(seed=k), t0 + k*beat/4)

        # baixo — pedal na fundamental do acorde
        root, octv, ivs = prog[(b//2) % 4]
        if sec != "intro":
            for k in (0, 1.5, 2, 3.5):
                place(buf, note(f(root, octv-1), beat*0.45, "saw",
                                0.19, (0.004, 0.08, 0.5, 0.12)), t0 + k*beat)

        # pad
        if sec in ("A", "B", "outro") and b % 2 == 0:
            for fr in chord_freqs(root, octv, ivs):
                place(buf, note(fr, bar*2*0.95, "tri", 0.055,
                                (0.6, 0.8, 0.65, 1.2), detune=0.002), t0)
                place(buf, note(fr, bar*2*0.95, "tri", 0.045,
                                (0.6, 0.8, 0.65, 1.2), detune=-0.002), t0)

        # arpejo na seção B
        if sec == "B":
            fr = chord_freqs(root, octv+1, ivs)
            for k in range(8):
                place(buf, note(fr[k % 3], beat*0.3, "sq", 0.055,
                                (0.002, 0.06, 0.2, 0.08)), t0 + k*beat/2)

    return reverb(buf, 0.18, 1.4), dict(
        bpm=bpm, key="C", mode="minor", bars=bars,
        sections=[("intro", 0, 4), ("A", 4, 12), ("B", 12, 24), ("outro", 24, 32)])


# ------------------------------------------------------- FAIXA 2: Correnteza
# Instrumental orgânica · 92 BPM · Sol maior · 4/4 · 24 compassos
def faixa_correnteza():
    bpm, bars = 92, 24
    beat = 60/bpm; bar = beat*4
    buf = np.zeros(int(bars*bar*SR) + 2*SR)

    prog = [("G", 3, [0, 4, 7]), ("E", 3, [0, 3, 7]),
            ("C", 3, [0, 4, 7]), ("D", 3, [0, 4, 7])]
    mel = ["G", "B", "D", "E", "D", "B", "A", "G"]

    def chord_freqs(root, octv, ivs):
        base = MIDI[root] + 12*(octv+1)
        return [440.0*2**((base+i-69)/12) for i in ivs]

    for b in range(bars):
        t0 = b*bar
        sec = "intro" if b < 4 else "A" if b < 12 else "B" if b < 20 else "outro"
        root, octv, ivs = prog[b % 4]

        # piano (FM suave) — acorde arpejado
        fr = chord_freqs(root, octv, ivs)
        for i, x in enumerate(fr):
            place(buf, fm(x, beat*3.2, 1.0, 2.2, 0.16,
                          (0.004, 0.6, 0.18, 1.0)), t0 + i*0.055)
        if sec in ("A", "B"):
            for i, x in enumerate(chord_freqs(root, octv+1, ivs)):
                place(buf, fm(x, beat*1.6, 1.0, 1.6, 0.09,
                              (0.004, 0.4, 0.15, 0.6)), t0 + beat*2 + i*0.045)

        # cordas
        if sec in ("A", "B", "outro"):
            for x in chord_freqs(root, octv, ivs):
                place(buf, note(x, bar*0.98, "saw", 0.035,
                                (1.0, 0.6, 0.7, 1.2), detune=0.0025), t0)
                place(buf, note(x, bar*0.98, "saw", 0.03,
                                (1.0, 0.6, 0.7, 1.2), detune=-0.0025), t0)

        # baixo
        if sec != "intro":
            place(buf, note(f(root, octv-2), beat*1.8, "sine", 0.24,
                            (0.01, 0.3, 0.5, 0.5)), t0)
            place(buf, note(f(root, octv-2), beat*1.2, "sine", 0.17,
                            (0.01, 0.3, 0.4, 0.4)), t0 + beat*2.5)

        # melodia na seção B
        if sec == "B":
            n = mel[(b*2) % 8]; n2 = mel[(b*2+1) % 8]
            place(buf, fm(f(n, 5), beat*1.4, 3.0, 1.2, 0.13,
                          (0.02, 0.4, 0.3, 0.6)), t0 + beat*0.5)
            place(buf, fm(f(n2, 5), beat*1.0, 3.0, 1.2, 0.11,
                          (0.02, 0.4, 0.3, 0.5)), t0 + beat*2.5)

        # percussão leve
        if sec in ("A", "B"):
            for k in range(4):
                place(buf, shaker(amp=0.05 if k % 2 else 0.075, seed=k+b),
                      t0 + k*beat)
            place(buf, shaker(0.14, 0.05, seed=99), t0 + beat*2)

    return reverb(buf, 0.3, 2.2), dict(
        bpm=bpm, key="G", mode="major", bars=bars,
        sections=[("intro", 0, 4), ("A", 4, 12), ("B", 12, 20), ("outro", 20, 24)])


# ------------------------------------------------------------ FAIXA 3: Névoa
# Ambiente · 70 BPM · Ré menor · 4/4 · 20 compassos · sem pulso forte
def faixa_nevoa():
    bpm, bars = 70, 20
    beat = 60/bpm; bar = beat*4
    buf = np.zeros(int(bars*bar*SR) + 3*SR)

    prog = [("D", 3, [0, 3, 7, 10]), ("A#", 2, [0, 4, 7, 11]),
            ("F", 3, [0, 4, 7, 11]), ("A", 2, [0, 3, 7, 10])]

    def chord_freqs(root, octv, ivs):
        base = MIDI[root] + 12*(octv+1)
        return [440.0*2**((base+i-69)/12) for i in ivs]

    # drone contínuo na tônica
    total = len(buf)/SR
    for det in (-0.003, 0.0, 0.003):
        place(buf, note(f("D", 2), total*0.99, "tri", 0.075,
                        (3.0, 2.0, 0.85, 5.0), detune=det), 0.0)

    for b in range(bars):
        t0 = b*bar
        root, octv, ivs = prog[(b//2) % 4]

        # camadas de pad que entram e saem lentamente
        for x in chord_freqs(root, octv, ivs):
            place(buf, note(x, bar*2.2, "saw", 0.028,
                            (1.6, 1.2, 0.7, 2.4), detune=0.002), t0)
            place(buf, note(x, bar*2.2, "tri", 0.032,
                            (2.0, 1.0, 0.75, 2.6), detune=-0.002), t0)

        # sinos esparsos, sem grade rítmica rígida
        if b >= 3 and b % 2 == 1:
            fr = chord_freqs(root, octv+2, ivs)
            place(buf, fm(fr[b % len(fr)], 3.4, 3.5, 4.0, 0.10,
                          (0.01, 1.2, 0.1, 2.0)), t0 + beat*1.3)
        if b >= 6 and b % 3 == 0:
            fr = chord_freqs(root, octv+1, ivs)
            place(buf, fm(fr[(b//3) % len(fr)], 2.6, 2.0, 3.0, 0.075,
                          (0.02, 1.0, 0.1, 1.4)), t0 + beat*2.7)

        # respiração grave muito suave marcando o compasso
        if b >= 2:
            place(buf, note(f(root, octv-1), beat*2.6, "sine", 0.10,
                            (0.35, 0.8, 0.4, 1.4)), t0)

    return reverb(buf, 0.42, 3.4), dict(
        bpm=bpm, key="D", mode="minor", bars=bars,
        sections=[("intro", 0, 4), ("A", 4, 12), ("B", 12, 18), ("outro", 18, 20)])


# ----------------------------------------------------------------------- run
if __name__ == "__main__":
    specs = [
        ("01-pulso.mp3", "Pulso", "eletrônica minimalista", faixa_pulso),
        ("01-correnteza.mp3", "Correnteza", "instrumental orgânica", faixa_correnteza),
        ("01-nevoa.mp3", "Névoa", "ambiente", faixa_nevoa),
    ]
    manifest = []
    print("Gerando faixas de referência:")
    for i, (fname, title, caracter, fn) in enumerate(specs, 1):
        fname = f"{i:02d}-{fname.split('-', 1)[1]}"
        audio, meta = fn()
        beat = 60/meta["bpm"]
        dur_exata = meta["bars"] * beat * 4
        export(audio, os.path.join(OUT, fname), title, dur_exata)
        manifest.append({
            "id": fname.split("-", 1)[1].replace(".mp3", ""),
            "arquivo": fname, "titulo": title, "caracter": caracter,
            "bpm": meta["bpm"], "tonica": meta["key"], "modo": meta["mode"],
            "compasso": [4, 4], "compassos": meta["bars"],
            "duracao_seg": round(meta["bars"]*beat*4, 2),
            "estrutura": [{"secao": s, "compasso_inicio": a, "compasso_fim": z}
                          for s, a, z in meta["sections"]],
            "licenca": "Sintetizado para este projeto — sem direitos de terceiros",
        })
    with open(os.path.join(OUT, "tracks.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=2)
    print("tracks.json escrito.")
