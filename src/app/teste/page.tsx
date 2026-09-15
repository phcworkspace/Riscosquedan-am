'use client';

import { useEffect, useRef, useState } from 'react';
import { Audio, type EstadoAudio } from '@/engine/Audio';
import { Mapa } from '@/engine/Mapa';
import { BANDAS, type Banda, type Faixa } from '@/engine/tipos';
import { CORES_BANDA } from '@/engine/tokens';

type ValoresBanda = Record<Banda, number>;
const ZERADO: ValoresBanda = { grave: 0, medio: 0, agudo: 0, brilho: 0 };

export default function PaginaDeTeste() {
  const audioRef = useRef<Audio | null>(null);
  const mapaRef = useRef<Mapa | null>(null);
  const rafRef = useRef<number | null>(null);

  const [iniciado, setIniciado] = useState(false);
  const [faixas, setFaixas] = useState<Faixa[]>([]);
  const [faixaId, setFaixaId] = useState('');
  const [estado, setEstado] = useState<EstadoAudio>('vazio');
  const [posicao, setPosicao] = useState(0);
  const [valores, setValores] = useState<ValoresBanda>(ZERADO);
  const [secaoAtual, setSecaoAtual] = useState('—');

  const [regiaoInicio, setRegiaoInicio] = useState('');
  const [regiaoFim, setRegiaoFim] = useState('');
  const [seekAlvo, setSeekAlvo] = useState('');
  const [volumeValor, setVolumeValor] = useState(0.8);

  useEffect(() => {
    fetch('/audio/faixas.json')
      .then(r => r.json())
      .then((lista: Faixa[]) => setFaixas(lista));
  }, []);

  useEffect(() => {
    // Fast Refresh remonta em dev; sem isto, contextos de áudio se acumulam
    // e o som dobra (SPEC seção 8, armadilhas conhecidas).
    return () => {
      if (rafRef.current !== null) cancelAnimationFrame(rafRef.current);
      audioRef.current?.destruir();
    };
  }, []);

  function loopDeQuadro() {
    const audio = audioRef.current;
    const mapa = mapaRef.current;
    if (audio) setEstado(audio.estado);
    if (audio && mapa) {
      const t = audio.posicao();
      setPosicao(t);
      setValores({
        grave: mapa.valor('grave', t),
        medio: mapa.valor('medio', t),
        agudo: mapa.valor('agudo', t),
        brilho: mapa.valor('brilho', t),
      });
      setSecaoAtual(mapa.secaoEm(t)?.rotulo ?? '—');
    }
    rafRef.current = requestAnimationFrame(loopDeQuadro);
  }

  async function comecar() {
    if (audioRef.current) return;
    audioRef.current = await Audio.iniciar();
    setIniciado(true);
    rafRef.current = requestAnimationFrame(loopDeQuadro);
  }

  async function escolherFaixa(id: string) {
    const audio = audioRef.current;
    const faixa = faixas.find(f => f.id === id);
    if (!audio || !faixa) return;
    setFaixaId(id);
    const [, mapa] = await Promise.all([
      audio.carregar(faixa.arquivo),
      Mapa.carregar(faixa.mapa),
    ]);
    mapaRef.current = mapa;
  }

  function definirRegiao() {
    const inicio = Number(regiaoInicio);
    const fim = Number(regiaoFim);
    if (Number.isFinite(inicio) && Number.isFinite(fim) && fim > inicio) {
      audioRef.current?.definirRegiao({ inicio, fim });
    }
  }

  function irPara() {
    const alvo = Number(seekAlvo);
    if (Number.isFinite(alvo)) audioRef.current?.buscar(alvo);
  }

  function mudarVolume(v: number) {
    setVolumeValor(v);
    audioRef.current?.volume(v);
  }

  return (
    <main style={{ padding: 24, fontFamily: 'monospace', color: '#eee', background: '#111', minHeight: '100vh' }}>
      <h1>Fase 1 — bancada de teste (áudio e mapa)</h1>
      <p style={{ opacity: 0.6, fontSize: 12 }}>Feia de propósito — o design entra na Fase 5.</p>

      {!iniciado && <button onClick={comecar}>Começar</button>}

      {iniciado && (
        <>
          <section style={{ marginTop: 16 }}>
            <label>
              Faixa:{' '}
              <select value={faixaId} onChange={e => escolherFaixa(e.target.value)}>
                <option value="">— escolher —</option>
                {faixas.map(f => <option key={f.id} value={f.id}>{f.titulo}</option>)}
              </select>
            </label>
            <span style={{ marginLeft: 12 }}>estado: {estado}</span>
          </section>

          <section style={{ marginTop: 16, display: 'flex', gap: 8, alignItems: 'center' }}>
            <button onClick={() => audioRef.current?.tocar()}>Play</button>
            <button onClick={() => audioRef.current?.pausar()}>Pausar</button>
            <button onClick={() => audioRef.current?.parar()}>Parar</button>
            <label>
              Volume{' '}
              <input type="range" min={0} max={1} step={0.01} value={volumeValor}
                     onChange={e => mudarVolume(Number(e.target.value))} />
            </label>
          </section>

          <section style={{ marginTop: 16, display: 'flex', gap: 8, alignItems: 'center' }}>
            <label>Início <input style={{ width: 60 }} value={regiaoInicio}
                                  onChange={e => setRegiaoInicio(e.target.value)} /></label>
            <label>Fim <input style={{ width: 60 }} value={regiaoFim}
                               onChange={e => setRegiaoFim(e.target.value)} /></label>
            <button onClick={definirRegiao}>Definir região</button>
            <button onClick={() => audioRef.current?.definirRegiao(null)}>Limpar região</button>
          </section>

          <section style={{ marginTop: 16, display: 'flex', gap: 8, alignItems: 'center' }}>
            <label>Ir para (s) <input style={{ width: 60 }} value={seekAlvo}
                                       onChange={e => setSeekAlvo(e.target.value)} /></label>
            <button onClick={irPara}>Ir para</button>
          </section>

          <section style={{ marginTop: 24 }}>
            <div>posição: {posicao.toFixed(3)}s · seção: {secaoAtual}</div>
            <div style={{ marginTop: 8, display: 'flex', flexDirection: 'column', gap: 4 }}>
              {BANDAS.map(b => (
                <div key={b} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span style={{ width: 70, fontSize: 12 }}>{b}</span>
                  <div style={{ width: 300, height: 14, background: '#222' }}>
                    <div style={{
                      width: `${valores[b] * 100}%`, height: '100%',
                      background: CORES_BANDA[b], transition: 'none',
                    }} />
                  </div>
                  <span style={{ fontVariantNumeric: 'tabular-nums', fontSize: 12 }}>
                    {valores[b].toFixed(3)}
                  </span>
                </div>
              ))}
            </div>
          </section>
        </>
      )}
    </main>
  );
}
