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
