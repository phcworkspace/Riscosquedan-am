'use client';

import { useState } from 'react';

type Ferramenta = 'ponto' | 'linha' | 'forma';

const FERRAMENTAS: { id: Ferramenta; rotulo: string; icone: React.ReactNode }[] = [
  { id: 'ponto', rotulo: 'Ponto', icone: <circle cx="12" cy="12" r="6" fill="currentColor" /> },
  { id: 'linha', rotulo: 'Linha', icone: <path d="M5 19 19 5" /> },
  { id: 'forma', rotulo: 'Forma', icone: <path d="M12 4 21 20H3Z" /> },
];

export function PainelFerramentas({ totalElementos = 0 }: { totalElementos?: number }) {
  // Seleção só visual nesta fase — criar elementos de verdade é Fase 4.
  const [ativa, setAtiva] = useState<Ferramenta>('ponto');

  return (
    <aside className="w-painel shrink-0 bg-surface border-l border-linha flex flex-col box-border">
      <div className="p-4 pb-3.5">
        <div className="text-rotulo text-tinta-fraca uppercase mb-1.5">Ferramenta</div>
        <div className="flex gap-2">
          {FERRAMENTAS.map(f => {
            const estaAtiva = f.id === ativa;
            return (
              <button
                key={f.id}
                onClick={() => setAtiva(f.id)}
                className={`w-[76px] h-[76px] rounded-lg flex flex-col items-center justify-center gap-[7px] box-border border ${
                  estaAtiva ? 'border-tinta bg-[#22222A]' : 'border-linha bg-transparent'
                }`}
              >
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none"
                     className={estaAtiva ? 'text-tinta' : 'text-tinta-fraca'}
                     stroke="currentColor" strokeWidth="1.5"
                     strokeLinecap="round" strokeLinejoin="round">
                  {f.icone}
                </svg>
                <span className={`text-[10px] ${estaAtiva ? 'text-tinta' : 'text-tinta-fraca'}`}>
                  {f.rotulo}
                </span>
              </button>
            );
          })}
        </div>
      </div>
      <div className="h-px bg-linha" />
      <div className="flex-1 flex items-center justify-center px-[34px] text-center">
        <span className="text-[12px] leading-[1.55] text-tinta-fraca">
          Selecione um elemento no palco para ajustá-lo
        </span>
      </div>
      <div className="h-px bg-linha" />
      <div className="h-11 flex items-center justify-between px-4">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" className="text-tinta-fraca"
             stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
          <path d="M4 7h16M9 7V5h6v2M7 7l1 12h8l1-12" />
        </svg>
        <span className="text-rotulo text-tinta-fraca font-mono">{totalElementos} / 120</span>
      </div>
    </aside>
  );
}
