'use client';

import { useEffect, useMemo, useRef, useState } from 'react';
import type { Mapa } from '@/engine/Mapa';
import type { Regiao } from '@/engine/tipos';

const PASSO_REGUA_SEG = 5;
const PASSO_BARRA_PX = 4.5;
const LARGURA_BARRA_PX = 3.3;

function Regua({ duracaoSeg, largura }: { duracaoSeg: number; largura: number }) {
  const marcas = [];
  for (let t = 0; t <= duracaoSeg; t += PASSO_REGUA_SEG) {
    const x = (t / duracaoSeg) * largura;
    marcas.push(
      <div key={t}>
        <div className="absolute bg-linha" style={{ left: x, top: 0, height: 6, width: 1 }} />
        <div className="absolute text-tinta-fraca font-mono" style={{ left: x + 4, top: 2, fontSize: 9 }}>
          {t}s
        </div>
      </div>
    );
  }
  return <div className="relative h-[18px] border-b border-linha-soft">{marcas}</div>;
}

function FormaDeOnda({
  mapa, largura,
}: {
  mapa: Mapa; largura: number;
}) {
  const barras = useMemo(() => {
    if (largura <= 0) return [];
    const picos = mapa.dados.picos;
    if (!picos?.length) return [];
    const n = Math.floor(largura / PASSO_BARRA_PX);
    const resultado: { x: number; altura: number }[] = [];
    for (let i = 0; i < n; i++) {
      // reamostra picos (1200 valores) para n barras — mesma técnica de downsampling
      // usada pelo mockup, só que com n dinâmico em vez de fixo em 320
      const idx = Math.min(picos.length - 1, Math.floor((i / n) * picos.length));
      resultado.push({ x: i * PASSO_BARRA_PX, altura: picos[idx] });
    }
    return resultado;
  }, [mapa, largura]);

  const divisores = useMemo(() => {
    if (largura <= 0) return [];
    return mapa.dados.secoes
      .filter(s => s.inicio > 0) // a primeira seção não tem divisor à esquerda
      .map(s => ({ x: (s.inicio / mapa.dados.duracaoSeg) * largura, rotulo: s.rotulo }));
  }, [mapa, largura]);

  const altura = 54;
  return (
    <div className="relative border-b border-linha-soft" style={{ height: altura }}>
      <svg width={largura} height={altura} className="absolute inset-0">
        {barras.map((b, i) => {
          const h = b.altura * altura;
          return (
            <rect key={i} x={b.x} y={(altura - h) / 2} width={LARGURA_BARRA_PX} height={h}
                  className="fill-tinta-fraca" opacity={0.4} />
          );
        })}
      </svg>
      {divisores.map((d, i) => (
        <div key={i}>
          <div className="absolute bg-linha" style={{ left: d.x, top: 0, bottom: 0, width: 1 }} />
          <div className="absolute text-tinta-fraca" style={{ left: d.x + 5, top: 3, fontSize: 9 }}>
            {d.rotulo}
          </div>
        </div>
      ))}
    </div>
  );
}

function RegiaoDeLoop({
  regiao, duracaoSeg, largura,
}: {
  regiao: Regiao | null; duracaoSeg: number; largura: number;
}) {
  if (!regiao || largura <= 0) return null;
  const x1 = (regiao.inicio / duracaoSeg) * largura;
  const x2 = (regiao.fim / duracaoSeg) * largura;
  return (
    <div
      className="absolute box-border pointer-events-none border-l-2 border-r-2 border-loop bg-loop/12"
      style={{ left: x1, top: 0, width: x2 - x1, height: 116 }} // 18+54+44
    >
      <div className="absolute bg-loop rounded-[3px]" style={{ left: -4, top: '50%', marginTop: -13, width: 6, height: 26 }} />
      <div className="absolute bg-loop rounded-[3px]" style={{ right: -4, top: '50%', marginTop: -13, width: 6, height: 26 }} />
    </div>
  );
}

function Cursor({ t, duracaoSeg, largura }: { t: number; duracaoSeg: number; largura: number }) {
  if (largura <= 0) return null;
  const x = (t / duracaoSeg) * largura;
  return (
    <div
      className="absolute bg-cursor pointer-events-none shadow-[0_0_10px_rgba(255,255,255,0.75)]"
      style={{ left: x, top: 0, width: 2, height: 148 }}
    />
  );
}

type Alca = 'inicio' | 'fim' | null;

export function LinhaDoTempo({
  mapa, posicao, regiao, onBuscar, onDefinirRegiao,
}: {
  mapa: Mapa;
  posicao: number;
  regiao: Regiao | null;
  onBuscar: (t: number) => void;
  onDefinirRegiao: (r: Regiao | null) => void;
}) {
  const containerRef = useRef<HTMLDivElement>(null);
  const scrubRef = useRef<HTMLDivElement>(null); // área de régua+onda+trilhas, onde se arrasta
  const [largura, setLargura] = useState(0);
  const arrastandoRef = useRef<{ tipo: 'nova-regiao' | 'alca'; alca: Alca; inicioFixo: number } | null>(null);

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const obs = new ResizeObserver(([e]) => setLargura(e.contentRect.width));
    obs.observe(el);
    return () => obs.disconnect();
  }, []);

  function xParaTempo(clientX: number): number {
    const rect = scrubRef.current!.getBoundingClientRect();
    const fracao = Math.min(1, Math.max(0, (clientX - rect.left) / rect.width));
    return fracao * mapa.dados.duracaoSeg;
  }

  const TOLERANCIA_ALCA_PX = 8;

  function aoPressionar(e: React.PointerEvent) {
    const t = xParaTempo(e.clientX);
    (e.target as Element).setPointerCapture(e.pointerId);

    if (regiao && largura > 0) {
      const xInicio = (regiao.inicio / mapa.dados.duracaoSeg) * largura;
      const xFim = (regiao.fim / mapa.dados.duracaoSeg) * largura;
      const xClique = e.clientX - scrubRef.current!.getBoundingClientRect().left;
      if (Math.abs(xClique - xInicio) <= TOLERANCIA_ALCA_PX) {
        arrastandoRef.current = { tipo: 'alca', alca: 'inicio', inicioFixo: regiao.fim };
        return;
      }
      if (Math.abs(xClique - xFim) <= TOLERANCIA_ALCA_PX) {
        arrastandoRef.current = { tipo: 'alca', alca: 'fim', inicioFixo: regiao.inicio };
        return;
      }
    }

    arrastandoRef.current = { tipo: 'nova-regiao', alca: null, inicioFixo: t };
    onBuscar(t);
  }

  function aplicarSnap(t: number): number {
    return mapa.encaixe(t) ?? t;
  }

  function aoMover(e: React.PointerEvent) {
    const arraste = arrastandoRef.current;
    if (!arraste) return;
    const t = aplicarSnap(xParaTempo(e.clientX));

    if (arraste.tipo === 'alca') {
      const outraBorda = arraste.inicioFixo;
      const novaRegiao = arraste.alca === 'inicio'
        ? { inicio: Math.min(t, outraBorda), fim: Math.max(t, outraBorda) }
        : { inicio: Math.min(outraBorda, t), fim: Math.max(outraBorda, t) };
      if (novaRegiao.fim - novaRegiao.inicio > 0.05) onDefinirRegiao(novaRegiao);
      return;
    }

    // nova-regiao: só vira região de fato se o arraste passou de um clique simples
    const inicio = Math.min(arraste.inicioFixo, t);
    const fim = Math.max(arraste.inicioFixo, t);
    if (fim - inicio > 0.05) onDefinirRegiao({ inicio, fim });
  }

  function aoSoltar() {
    arrastandoRef.current = null;
  }

  return (
    <div ref={containerRef} className="relative w-full h-tempo bg-surface-alt border-t border-linha box-border overflow-hidden">
      <div
        ref={scrubRef}
        onPointerDown={aoPressionar}
        onPointerMove={aoMover}
        onPointerUp={aoSoltar}
        className="absolute cursor-pointer"
        style={{ inset: '0 0 32px 0' }}
      >
        <Regua duracaoSeg={mapa.dados.duracaoSeg} largura={largura} />
        <FormaDeOnda mapa={mapa} largura={largura} />
        <div style={{ height: 44 }} /> {/* trilhas dos elementos — vazio nesta fase */}
      </div>
      <RegiaoDeLoop regiao={regiao} duracaoSeg={mapa.dados.duracaoSeg} largura={largura} />
      <Cursor t={posicao} duracaoSeg={mapa.dados.duracaoSeg} largura={largura} />
    </div>
  );
}
