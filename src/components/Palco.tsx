'use client';

import { useEffect, useRef, useState } from 'react';

const MARGEM_H_SPROCKET = 19;
const MARGEM_V_SPROCKET = 6;
const PASSO_SPROCKET = 34;

function Sprockets({ largura, borda }: { largura: number; borda: 'top' | 'bottom' }) {
  if (largura <= 0) return null;
  const disponivel = largura - MARGEM_H_SPROCKET * 2;
  const quantidade = Math.max(0, Math.floor(disponivel / PASSO_SPROCKET) + 1);
  return (
    <>
      {Array.from({ length: quantidade }, (_, i) => (
        <div
          key={i}
          className="absolute w-3.5 h-2.5 rounded-sm bg-sprocket"
          style={{ [borda]: MARGEM_V_SPROCKET, left: MARGEM_H_SPROCKET + i * PASSO_SPROCKET }}
        />
      ))}
    </>
  );
}

export function Palco({ vazio, carregando }: { vazio: boolean; carregando: boolean }) {
  const ref = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [tamanho, setTamanho] = useState({ largura: 0, altura: 0 });

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const obs = new ResizeObserver(([entry]) => {
      setTamanho({ largura: entry.contentRect.width, altura: entry.contentRect.height });
    });
    obs.observe(el);
    return () => obs.disconnect();
  }, []);

  // canvas dimensionado com devicePixelRatio correto — o Renderizador (Fase 3)
  // desenha nele; por enquanto fica em branco. Depende de largura E altura: um
  // resize só de altura (janela mais baixa, largura igual) também precisa
  // redimensionar o backing store, senão o canvas fica com pixels obsoletos.
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || tamanho.largura === 0) return;
    const dpr = window.devicePixelRatio || 1;
    canvas.width = tamanho.largura * dpr;
    canvas.height = tamanho.altura * dpr;
    canvas.style.width = `${tamanho.largura}px`;
    canvas.style.height = `${tamanho.altura}px`;
  }, [tamanho]);

  return (
    <main ref={ref} className="flex-1 relative bg-palco overflow-hidden min-w-0">
      <canvas ref={canvasRef} className="absolute inset-0" />
      <div className="vinheta absolute inset-0 pointer-events-none" />
      <div className="grao absolute inset-0 pointer-events-none" />
      <Sprockets largura={tamanho.largura} borda="top" />
      <Sprockets largura={tamanho.largura} borda="bottom" />
      {carregando && (
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div className="text-[12.5px] text-tinta-fraca">Carregando faixa…</div>
        </div>
      )}
      {!carregando && vazio && (
        <div className="absolute inset-0 flex flex-col items-center justify-center gap-5 pointer-events-none">
          <svg width="54" height="54" viewBox="0 0 54 54">
            <circle cx="27" cy="27" r="13" className="fill-tinta-fraca" opacity="0.2" />
            <circle cx="27" cy="27" r="22" fill="none" className="stroke-tinta-fraca" strokeWidth="1"
                    strokeDasharray="3 5" opacity="0.35" />
          </svg>
          <div className="text-[12.5px] text-tinta-fraca text-center leading-[1.65]">
            Selecione um trecho na linha do tempo e escute.<br />Depois desenhe o que você vê.
          </div>
        </div>
      )}
    </main>
  );
}
