'use client';

// Paleta livre dos elementos (--color-el-1..8 no @theme) — as mesmas cores que a
// pessoa vai usar para colorir o que desenha, aqui só como textura de fundo.
const FORMAS_DECORATIVAS = [
  { tipo: 'circulo' as const, x: 18, y: 24, r: 2.4, classe: 'fill-el-1' },   // #FF3B30
  { tipo: 'circulo' as const, x: 82, y: 68, r: 1.1, classe: 'fill-el-6' },   // #5AC8FA
  { tipo: 'circulo' as const, x: 30, y: 78, r: 1.6, classe: 'fill-el-4' },   // #30D158
  { tipo: 'linha' as const, x1: 12, y1: 55, x2: 24, y2: 50, classe: 'stroke-el-5' }, // #0A84FF
  { tipo: 'linha' as const, x1: 70, y1: 20, x2: 80, y2: 26, classe: 'stroke-el-7' }, // #C77DFF
  { tipo: 'circulo' as const, x: 88, y: 14, r: 1.8, classe: 'fill-el-3' },   // #FFB300
];

/**
 * Tela de abertura. Existe por uma razão técnica — o navegador só libera o
 * AudioContext depois de um gesto do usuário — mas não deve parecer um aviso.
 *
 * O fundo `#08080A` e o gradiente da vinheta são exceções deliberadas à regra de
 * "sem hex solto": são um preto ligeiramente mais escuro que `--color-base`
 * (#0B0B0D), específico desta tela no mockup, sem token próprio no @theme — criar
 * um token só para uma diferença de 3 valores de RGB não vale a pena.
 */
export function TelaDeEntrada({ onComecar }: { onComecar: () => void }) {
  return (
    <div className="fixed inset-0 flex items-center justify-center z-50" style={{ background: '#08080A' }}>
      <svg
        width="100%" height="100%" viewBox="0 0 100 100" preserveAspectRatio="none"
        className="absolute inset-0 opacity-50"
      >
        {FORMAS_DECORATIVAS.map((f, i) =>
          f.tipo === 'circulo' ? (
            <circle key={i} cx={f.x} cy={f.y} r={f.r} className={f.classe} opacity={0.21} />
          ) : (
            <line key={i} x1={f.x1} y1={f.y1} x2={f.x2} y2={f.y2} className={f.classe}
                  strokeWidth={0.4} strokeLinecap="round" opacity={0.21} />
          )
        )}
      </svg>
      <div
        className="absolute inset-0"
        style={{ background: 'radial-gradient(ellipse at 50% 50%, rgba(8,8,10,0) 0%, rgba(8,8,10,.55) 38%, rgba(8,8,10,.94) 100%)' }}
      />
      <div className="grao absolute inset-0" />
      <div className="relative flex flex-col items-center">
        <div className="text-[11px] tracking-[0.34em] uppercase text-tinta-fraca mb-[26px]">
          Protótipo · pesquisa de mestrado
        </div>
        <div className="text-titulo font-bold tracking-[-0.01em]">Riscos que Dançam</div>
        <div className="text-[13px] text-tinta-fraca mt-3.5 max-w-[420px] text-center leading-[1.6]">
          Escute uma música e desenhe o que você percebe nela. No final, assista à sua composição.
        </div>
        <button
          onClick={onComecar}
          className="mt-[38px] h-10 px-[30px] rounded-[20px] bg-tinta text-base text-[13px] font-semibold border-none cursor-pointer"
        >
          Começar
        </button>
      </div>
    </div>
  );
}
