'use client';

import { useState } from 'react';
import type { Faixa } from '@/engine/tipos';

export function Cabecalho({
  faixa, faixas, onEscolherFaixa,
}: {
  faixa: Faixa | null;
  faixas: Faixa[];
  onEscolherFaixa: (id: string) => void;
}) {
  const [menuAberto, setMenuAberto] = useState(false);

  return (
    <header className="h-cabecalho shrink-0 flex items-center justify-between px-[18px] bg-surface border-b border-linha box-border">
      <div className="flex items-baseline gap-3">
        <span className="text-[14px] font-semibold tracking-[-0.01em]">Riscos que Dançam</span>
        <span className="text-rotulo text-tinta-fraca">Escute. Desenhe o que você vê.</span>
      </div>
      <div className="flex items-center gap-4">
        {faixa && (
          <div className="relative">
            <button
              onClick={() => setMenuAberto(a => !a)}
              className="text-[12px] text-tinta border-b border-dotted border-linha pb-0.5 bg-transparent cursor-pointer"
            >
              {faixa.titulo} · {faixa.caracter}
            </button>
            {menuAberto && (
              <div className="absolute right-0 top-full mt-2 w-56 bg-surface border border-linha rounded-md overflow-hidden z-10">
                {faixas.map(f => (
                  <button
                    key={f.id}
                    onClick={() => { onEscolherFaixa(f.id); setMenuAberto(false); }}
                    className={`w-full text-left px-3 py-2 text-[12px] bg-transparent border-none cursor-pointer ${f.id === faixa.id ? 'text-tinta' : 'text-tinta-fraca'}`}
                  >
                    {f.titulo} · {f.caracter}
                  </button>
                ))}
              </div>
            )}
          </div>
        )}
        <div
          className="w-8 h-8 rounded-full border border-linha flex items-center justify-center text-tinta-fraca"
          title="Tutorial (ainda não implementado)"
        >
          <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor"
               strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="9" />
            <path d="M9.6 9.2a2.4 2.4 0 1 1 2.9 2.4v1.4" />
            <path d="M12.4 16.4h.01" />
          </svg>
        </div>
      </div>
    </header>
  );
}
