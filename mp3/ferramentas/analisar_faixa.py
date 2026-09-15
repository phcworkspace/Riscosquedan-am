#!/usr/bin/env python3
"""
analisar_faixa.py — analisa uma faixa de áudio e devolve os metadados que o
protótipo "Riscos que Dançam" precisa: BPM, tonalidade, modo, duração e
estrutura (seções).

Uso:
    python analisar_faixa.py MP3/01-pulso.mp3
    python analisar_faixa.py MP3/*.mp3 --json MP3/tracks.json

Requer:  pip install librosa soundfile
(o librosa usa ffmpeg/audioread para ler mp3 — tenha o ffmpeg no PATH)

IMPORTANTE: a detecção automática é um ponto de partida, não a palavra final.
O BPM pode sair na metade ou no dobro do valor real, e a tonalidade pode sair
como a relativa (maior/menor). Sempre confira à mão — o roteiro de verificação
está impresso no fim do relatório.
"""
import sys, json, argparse
import numpy as np
import librosa

NOTAS = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
PT = {"C": "Dó", "C#": "Dó#", "D": "Ré", "D#": "Mi♭", "E": "Mi", "F": "Fá",
      "F#": "Fá#", "G": "Sol", "G#": "Lá♭", "A": "Lá", "A#": "Si♭", "B": "Si"}

# Perfis de Krumhansl–Schmuckler
PERFIL_MAIOR = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09,
                         2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
PERFIL_MENOR = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53,
                         2.54, 4.75, 3.98, 2.69, 3.34, 3.17])


def detectar_tonalidade(y, sr):
    """Krumhansl–Schmuckler sobre o cromagrama CQT."""
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr, bins_per_octave=36)
    vetor = chroma.mean(axis=1)
    vetor = (vetor - vetor.mean()) / (vetor.std() or 1)

    resultados = []
    for i in range(12):
        for modo, perfil in (("major", PERFIL_MAIOR), ("minor", PERFIL_MENOR)):
            p = np.roll(perfil, i)
            p = (p - p.mean()) / p.std()
            resultados.append((float(np.corrcoef(vetor, p)[0, 1]), NOTAS[i], modo))
    resultados.sort(reverse=True)
    melhor = resultados[0]
    return {
        "tonica": melhor[1], "modo": melhor[2], "confianca": round(melhor[0], 3),
        "alternativas": [{"tonica": t, "modo": m, "confianca": round(c, 3)}
                         for c, t, m in resultados[1:4]],
    }


def detectar_bpm(y, sr):
    onset = librosa.onset.onset_strength(y=y, sr=sr)
    tempo, beats = librosa.beat.beat_track(onset_envelope=onset, sr=sr, units="time")
    tempo = float(np.atleast_1d(tempo)[0])

    # candidatos alternativos a partir do tempograma — o detector principal
    # erra com frequência em faixas sem pulso percussivo claro
    tg = librosa.feature.tempogram(onset_envelope=onset, sr=sr)
    freqs = librosa.tempo_frequencies(tg.shape[0], sr=sr)
    forca = tg.mean(axis=1)
    val = (freqs >= 50) & (freqs <= 200) & np.isfinite(freqs)
    ordem = np.argsort(forca[val])[::-1]
    candidatos = [round(float(freqs[val][i]), 2) for i in ordem[:24]]
    # remove candidatos muito próximos entre si
    reduzidos = []
    for c in candidatos:
        if all(abs(c - r) > 3 for r in reduzidos):
            reduzidos.append(c)
    candidatos = reduzidos[:4]

    # estabilidade: desvio dos intervalos entre batidas
    if len(beats) > 3:
        ivs = np.diff(beats)
        estabilidade = float(np.std(ivs) / (np.mean(ivs) or 1))
    else:
        estabilidade = float("nan")

    return {
        "bpm": round(tempo, 2),
        "bpm_arredondado": int(round(tempo)),
        "candidatos": candidatos,
        "metade": round(tempo / 2, 2), "dobro": round(tempo * 2, 2),
        "n_batidas": int(len(beats)),
        "desvio_intervalos": round(estabilidade, 4),
        "primeira_batida_seg": round(float(beats[0]), 3) if len(beats) else None,
    }


def detectar_estrutura(y, sr, bpm, n_secoes=4):
    """Segmentação por agrupamento espectral sobre MFCC + cromagrama."""
    dur = librosa.get_duration(y=y, sr=sr)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    feat = np.vstack([librosa.util.normalize(mfcc, axis=1),
                      librosa.util.normalize(chroma, axis=1)])

    fronteiras = librosa.segment.agglomerative(feat, n_secoes)
    tempos = librosa.frames_to_time(fronteiras, sr=sr)
    tempos = np.unique(np.concatenate([[0.0], tempos, [dur]]))

    seg_por_compasso = (60.0 / bpm) * 4 if bpm else None
    secoes = []
    for i in range(len(tempos) - 1):
        ini, fim = float(tempos[i]), float(tempos[i + 1])
        s = {"inicio_seg": round(ini, 2), "fim_seg": round(fim, 2),
             "duracao_seg": round(fim - ini, 2)}
        if seg_por_compasso:
            s["compasso_inicio"] = round(ini / seg_por_compasso, 2)
            s["compassos"] = round((fim - ini) / seg_por_compasso, 2)
        secoes.append(s)
    return secoes


def perfil_energia(y, sr, bpm, compassos_por_bloco=1):
    """Energia RMS por compasso — útil para saber onde a faixa cresce."""
    if not bpm:
        return []
    passo = (60.0 / bpm) * 4 * compassos_por_bloco
    rms = librosa.feature.rms(y=y)[0]
    t = librosa.frames_to_time(np.arange(len(rms)), sr=sr)
    blocos, i = [], 0.0
    dur = librosa.get_duration(y=y, sr=sr)
    while i < dur:
        m = (t >= i) & (t < i + passo)
        blocos.append(round(float(rms[m].mean()) if m.any() else 0.0, 5))
        i += passo
    pico = max(blocos) or 1
    return [round(b / pico, 3) for b in blocos]


def conferir_bpm(y, sr, bpm_declarado, subdivisao=4):
    """Confere um BPM declarado medindo o alinhamento dos ataques a uma grade
    fixa nesse andamento, ao longo de toda a faixa.

    Mais confiável que a detecção automática: em vez de adivinhar o andamento,
    testa a hipótese que você já tem. A grade é de semicolcheias (subdivisao=4)
    porque colcheias e semicolcheias também estão "no tempo" — testar só contra
    a grade de tempos reprovaria um chimbau em contratempo. A fase da grade é
    procurada automaticamente. Se a faixa sair de fase no meio, o erro cresce
    nos blocos finais e a deriva denuncia.
    """
    onset = librosa.onset.onset_strength(y=y, sr=sr)
    picos = librosa.onset.onset_detect(onset_envelope=onset, sr=sr, units="time")
    if len(picos) < 8:
        return {"conclusivo": False, "motivo": "ataques insuficientes na faixa"}

    # Faixas sustentadas (pads, drones, ambiente) nao tem ataques nitidos: o
    # detector encontra "picos" no meio de swells e qualquer BPM reprova. O
    # contraste do envelope de ataque revela esse caso antes de dar um veredito
    # que nao significa nada.
    contraste = float(np.percentile(onset, 95) / (onset.mean() + 1e-9))
    if contraste < 2.0:
        return {"conclusivo": False, "contraste": round(contraste, 2),
                "motivo": f"faixa sem ataques nitidos (contraste {contraste:.2f}) "
                          "— material sustentado/ambiente. O alinhamento tem de "
                          "ser conferido de ouvido, com metronomo por cima"}

    periodo = 60.0 / bpm_declarado / subdivisao

    def erro_com_offset(off):
        d = (picos - off) % periodo
        d = np.minimum(d, periodo - d)
        return d / (periodo / 2)

    # procura a fase que melhor encaixa
    offsets = np.linspace(0, periodo, 48, endpoint=False)
    melhor_off = min(offsets, key=lambda o: erro_com_offset(o).mean())
    rel = erro_com_offset(melhor_off)

    dur = librosa.get_duration(y=y, sr=sr)
    blocos, n, MIN_ATAQUES = [], 6, 6
    for i in range(n):
        m = (picos >= dur*i/n) & (picos < dur*(i+1)/n)
        # blocos com poucos ataques (intro, outro, trecho sustentado) nao tem
        # material suficiente para julgar a fase — sao marcados e ignorados
        if m.sum() >= MIN_ATAQUES:
            blocos.append(round(float(rel[m].mean()), 3))
        else:
            blocos.append(None)

    medios = [b for b in blocos if b is not None]
    if len(medios) < 3:
        return {"conclusivo": False,
                "motivo": "ataques percussivos insuficientes (faixa sustentada "
                          "ou ambiente) — o alinhamento precisa ser conferido "
                          "de ouvido"}
    # mediana e intervalo interquartil: um unico bloco atipico (intro esparsa,
    # outro com arpejo rubato) nao deve reprovar a faixa inteira
    erro = float(np.median(medios))
    deriva = float(np.percentile(medios, 75) - np.percentile(medios, 25))
    return {
        "conclusivo": True,
        "contraste": round(contraste, 2),
        "bpm_testado": bpm_declarado,
        "subdivisao": subdivisao,
        "offset_seg": round(float(melhor_off), 4),
        "erro_medio": round(erro, 3),
        "erro_por_bloco": blocos,
        "deriva": round(float(deriva), 3),
        "veredito": ("sai de fase ao longo da faixa" if deriva >= 0.30 else
                     "alinhado" if erro < 0.25 else
                     "não alinha"),
        "nota": "metade e dobro do BPM tambem passam neste teste — so o ouvido "
                "distingue qual e o andamento sentido",
    }


def analisar(caminho, bpm_conferir=None):
    y, sr = librosa.load(caminho, sr=22050, mono=True)
    dur = float(librosa.get_duration(y=y, sr=sr))

    ritmo = detectar_bpm(y, sr)
    tom = detectar_tonalidade(y, sr)
    bpm = ritmo["bpm_arredondado"]
    estrutura = detectar_estrutura(y, sr, bpm)
    energia = perfil_energia(y, sr, bpm)

    conferencia = conferir_bpm(y, sr, bpm_conferir) if bpm_conferir else None
    if bpm_conferir:
        bpm = bpm_conferir
        estrutura = detectar_estrutura(y, sr, bpm)
        energia = perfil_energia(y, sr, bpm)

    compassos = dur / ((60.0 / bpm) * 4) if bpm else None
    return {
        "conferencia_bpm": conferencia,
        "arquivo": caminho,
        "duracao_seg": round(dur, 2),
        "ritmo": ritmo,
        "tonalidade": tom,
        "compassos_estimados": round(compassos, 2) if compassos else None,
        "compassos_inteiros": bool(compassos and abs(compassos - round(compassos)) < 0.15),
        "estrutura": estrutura,
        "energia_por_compasso": energia,
    }


def imprimir(r):
    nome = r["arquivo"].split("/")[-1]
    ton = r["tonalidade"]; rit = r["ritmo"]
    modo_pt = "maior" if ton["modo"] == "major" else "menor"
    print(f"\n{'='*62}\n{nome}\n{'='*62}")
    print(f"Duração           {r['duracao_seg']}s")
    print(f"BPM detectado     {rit['bpm']}   (metade {rit['metade']} · "
          f"dobro {rit['dobro']})")
    print(f"  candidatos      {' · '.join(str(c) for c in rit['candidatos'])}")
    print(f"Batidas           {rit['n_batidas']} · desvio dos intervalos "
          f"{rit['desvio_intervalos']} " +
          ("(pulso firme)" if rit["desvio_intervalos"] < 0.08 else
           "(pulso irregular — conferir à mão)"))
    print(f"Tonalidade        {PT[ton['tonica']]} {modo_pt}  "
          f"({ton['tonica']} {ton['modo']}) · confiança {ton['confianca']}")
    alts = " · ".join(f"{PT[a['tonica']]} {'maior' if a['modo']=='major' else 'menor'}"
                      f" ({a['confianca']})" for a in ton["alternativas"])
    print(f"  alternativas    {alts}")
    print(f"Compassos         {r['compassos_estimados']} " +
          ("✓ fecha em compasso inteiro" if r["compassos_inteiros"]
           else "⚠ não fecha — cortar a faixa num múltiplo de compasso"))
    if r.get("conferencia_bpm"):
        c = r["conferencia_bpm"]
        if c["conclusivo"]:
            marca = "OK" if c["veredito"] == "alinhado" else "FALHOU"
            print(f"Conferência {c['bpm_testado']} BPM   [{marca}] {c['veredito']}"
                  f"  (erro medio {c['erro_medio']} · deriva {c['deriva']})")
            print(f"  erro por bloco  {c['erro_por_bloco']}")
        else:
            print(f"Conferência BPM   inconclusiva — {c['motivo']}")
    print("Estrutura")
    for i, s in enumerate(r["estrutura"], 1):
        cb = s.get("compasso_inicio", "—"); nb = s.get("compassos", "—")
        print(f"  {i}. {s['inicio_seg']:>6.2f}s → {s['fim_seg']:>6.2f}s  "
              f"({s['duracao_seg']:>5.2f}s · compasso {cb} · {nb} compassos)")


ROTEIRO = """
────────────────────────────────────────────────────────────────
CONFERIR À MÃO ANTES DE ACEITAR (a detecção automática erra)

1. BPM — abra a faixa numa DAW ou num metrônomo online no BPM
   detectado e ouça a faixa INTEIRA. Se sair de fase no meio, o
   valor está errado ou a faixa tem variação de andamento (nesse
   caso, descarte a faixa).
   Se o pulso parecer lento ou corrido demais, teste a metade e o
   dobro — é o erro mais comum do detector.

2. TONALIDADE — toque a tônica detectada por cima da faixa. Se
   soar dissonante em algum trecho, teste a relativa (a terceira
   menor abaixo, para maior→menor) e as alternativas listadas.

3. CORTE — a faixa precisa fechar num número inteiro de compassos
   para o loop não engasgar. Se "compassos estimados" não for
   quase inteiro, corte no editor.

4. LICENÇA — registre autor, licença e link em tracks.json. Em
   trabalho acadêmico isso não é opcional.
────────────────────────────────────────────────────────────────
"""

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Analisa faixas para o protótipo")
    ap.add_argument("arquivos", nargs="+")
    ap.add_argument("--json", help="grava o resultado completo neste caminho")
    ap.add_argument("--conferir-bpm", type=float, default=None,
                    help="testa um BPM que voce ja suspeita, medindo o "
                         "alinhamento dos ataques ao longo da faixa inteira")
    a = ap.parse_args()

    todos = []
    for caminho in a.arquivos:
        try:
            r = analisar(caminho, a.conferir_bpm)
        except Exception as e:                      # noqa: BLE001
            print(f"\n!! erro em {caminho}: {e}", file=sys.stderr)
            continue
        todos.append(r); imprimir(r)

    print(ROTEIRO)
    if a.json:
        with open(a.json, "w", encoding="utf-8") as fh:
            json.dump(todos, fh, ensure_ascii=False, indent=2)
        print(f"Resultado completo gravado em {a.json}")
