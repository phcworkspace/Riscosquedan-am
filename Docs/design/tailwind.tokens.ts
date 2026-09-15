// Riscos que Dançam — fragmento para src/tailwind.config.ts
// Cole dentro de `theme.extend`. Os valores são os mesmos de tokens.css;
// mantenha os dois em sincronia ou use só um dos caminhos.

export const riscosTheme = {
  colors: {
    base: '#0B0B0D',
    palco: '#141417',
    surface: { DEFAULT: '#1A1A1F', alt: '#212128' },
    linha: { DEFAULT: '#2A2A31', soft: '#1B1B22' },
    sprocket: '#202026',
    tinta: { DEFAULT: '#EDEDF0', fraca: '#8A8A94' },
    cursor: '#FFFFFF',
    loop: '#FFD60A',
    banda: {
      grave: '#FF3B30',
      medio: '#FFB300',
      agudo: '#0A84FF',
      brilho: '#5AC8FA',
    },
    el: {
      1: '#FF3B30', 2: '#FF7A1A', 3: '#FFB300', 4: '#30D158',
      5: '#0A84FF', 6: '#5AC8FA', 7: '#C77DFF', 8: '#F2F2F7',
    },
  },
  fontFamily: {
    sans: ['Space Grotesk', 'ui-sans-serif', 'system-ui', 'sans-serif'],
    mono: ['JetBrains Mono', 'ui-monospace', 'monospace'],
  },
  fontSize: {
    // a escala inteira da interface — nada acima de 20px
    micro: ['9px', '1.2'],
    mini: ['10px', '1.3'],
    rotulo: ['11px', { lineHeight: '1.3', letterSpacing: '0.08em' }],
    corpo: ['12px', '1.5'],
    forte: ['14px', '1.35'],
    titulo: ['20px', { lineHeight: '1.15', letterSpacing: '-0.01em' }],
  },
  borderRadius: { DEFAULT: '4px', md: '5px', lg: '6px' },
  spacing: {
    cabecalho: '52px',
    tempo: '148px',
    painel: '300px',
  },
  transitionDuration: { rapido: '120ms', ui: '200ms', fade: '400ms' },
} as const;

// Mapa banda → cor sugerida e faixa de frequência.
// A cor é apenas a sugestão inicial: a pessoa pode escolher qualquer
// uma da paleta livre sem mudar a banda.
export const BANDAS = [
  { id: 'grave',  nome: 'Grave',  cor: '#FF3B30', hz: [20, 150] },
  { id: 'medio',  nome: 'Médio',  cor: '#FFB300', hz: [150, 700] },
  { id: 'agudo',  nome: 'Agudo',  cor: '#0A84FF', hz: [700, 3200] },
  { id: 'brilho', nome: 'Brilho', cor: '#5AC8FA', hz: [3200, 11000] },
] as const;

export const PALETA = [
  '#FF3B30', '#FF7A1A', '#FFB300', '#30D158',
  '#0A84FF', '#5AC8FA', '#C77DFF', '#F2F2F7',
] as const;
