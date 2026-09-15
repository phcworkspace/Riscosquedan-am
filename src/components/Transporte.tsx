'use client';

function formatarTempo(s: number): string {
  return s.toFixed(2).padStart(5, '0');
}

export function Transporte({
  tocando, posicao, duracao, temRegiao, volume,
  onTocar, onPausar, onParar, onLimparRegiao, onVolume,
}: {
  tocando: boolean; posicao: number; duracao: number; temRegiao: boolean; volume: number;
  onTocar: () => void; onPausar: () => void; onParar: () => void;
  onLimparRegiao: () => void; onVolume: (v: number) => void;
}) {
  return (
    <div className="absolute left-0 right-0 bottom-0 h-8 flex items-center gap-3.5 px-3.5 box-border border-t border-linha-soft">
      <button
        onClick={tocando ? onPausar : onTocar}
        className="w-[26px] h-[26px] rounded-full flex items-center justify-center bg-tinta border-none cursor-pointer"
        aria-label={tocando ? 'Pausar' : 'Tocar'}
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" className="text-base" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
          {tocando ? <path d="M8 5v14M16 5v14" /> : <path d="M7 4.5 19 12 7 19.5Z" fill="currentColor" stroke="none" />}
        </svg>
      </button>

      <button onClick={onParar} aria-label="Parar" className="bg-transparent border-none cursor-pointer flex text-tinta-fraca">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
          <rect x="6" y="6" width="12" height="12" rx="1" />
        </svg>
      </button>

      <button
        onClick={onLimparRegiao}
        aria-label={temRegiao ? 'Desligar loop de região' : 'Nenhuma região ativa'}
        className={`bg-transparent border-none flex ${temRegiao ? 'text-loop cursor-pointer' : 'text-tinta-fraca cursor-default'}`}
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
          <path d="M4 9h13l-3-3M20 15H7l3 3" />
        </svg>
      </button>

      <span className="text-rotulo text-tinta-fraca font-mono ml-1.5">
        {formatarTempo(posicao)} / {formatarTempo(duracao)}
      </span>

      <div className="ml-auto flex items-center gap-3.5">
        <span className="flex items-center gap-[7px] text-tinta-fraca">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M5 9v6h4l5 4V5L9 9Z" /><path d="M17 9.5a3.6 3.6 0 0 1 0 5" />
          </svg>
          <input
            type="range" min={0} max={1} step={0.01} value={volume}
            onChange={e => onVolume(Number(e.target.value))}
            className="w-[54px] h-[3px] accent-tinta-fraca"
          />
        </span>
        <button
          disabled
          title="Modo Cinema — Fase 6"
          className="h-[26px] px-[18px] rounded-full flex items-center gap-[7px] bg-tinta text-base text-[11px] font-semibold tracking-[0.06em] border-none opacity-50 cursor-not-allowed"
        >
          <svg width="10" height="10" viewBox="0 0 24 24"><path d="M7 4.5 19 12 7 19.5Z" fill="currentColor" /></svg>
          ASSISTIR
        </button>
      </div>
    </div>
  );
}
