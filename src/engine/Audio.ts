// Riscos que Dançam — Web Audio puro: carregar, tocar, pausar, loop de região,
// seek, posição. engine/ não importa nada de React.
//
// AudioContext e AudioBufferSourceNode não existem em Node — por isso só
// `posicaoNaRegiao` (a matemática de posição dentro do loop) tem teste de
// unidade. O resto da classe é verificado manualmente pelos testes de
// aceite T1-T6 de Docs/SPEC-fase-1.md, que já exigem ouvir o áudio de verdade.

import type { Regiao } from './tipos';

/**
 * Posição dentro de uma região de loop, dado o offset onde a reprodução atual
 * começou e o tempo decorrido desde então. Pura: não depende de AudioContext,
 * por isso é a peça de Audio.ts coberta por teste de unidade.
 */
export function posicaoNaRegiao(
  offset: number,
  inicio: number,
  fim: number,
  decorrido: number,
): number {
  const janela = fim - inicio;
  if (janela <= 0) return inicio;
  const bruta = offset - inicio + decorrido;
  const dentro = ((bruta % janela) + janela) % janela; // evita módulo negativo
  return inicio + dentro;
}

export type EstadoAudio = 'vazio' | 'carregando' | 'pronto' | 'tocando';

export class Audio {
  private ctx: AudioContext;
  private ganho: GainNode;
  private buffer: AudioBuffer | null = null;
  private src: AudioBufferSourceNode | null = null;
  private reg: Regiao | null = null;
  private estadoAtual: EstadoAudio = 'vazio';

  private offset = 0;      // posição do buffer onde a reprodução atual começou
  private iniciadoEm = 0;  // ctx.currentTime em que a reprodução atual começou
  private pausadoEm = 0;   // posição guardada ao pausar/parar

  private constructor(ctx: AudioContext) {
    this.ctx = ctx;
    this.ganho = ctx.createGain();
    this.ganho.connect(ctx.destination);
  }

  /** Precisa ser chamado dentro de um gesto do usuário (política de autoplay). */
  static async iniciar(): Promise<Audio> {
    const ctx = new AudioContext();
    if (ctx.state === 'suspended') await ctx.resume();
    return new Audio(ctx);
  }

  get estado(): EstadoAudio { return this.estadoAtual; }
  get duracao(): number { return this.buffer?.duration ?? 0; }
  get regiao(): Regiao | null { return this.reg; }
  get tocando(): boolean { return this.estadoAtual === 'tocando'; }

  async carregar(url: string): Promise<void> {
    this.pararSource();
    this.estadoAtual = 'carregando';
    this.buffer = null;
    this.reg = null;
    this.offset = 0;
    this.pausadoEm = 0;

    try {
      const resposta = await fetch(url);
      if (!resposta.ok) throw new Error(`Falha ao carregar ${url}: ${resposta.status}`);
      const arrayBuffer = await resposta.arrayBuffer();
      this.buffer = await this.ctx.decodeAudioData(arrayBuffer);
      this.estadoAtual = 'pronto';
    } catch (erro) {
      this.estadoAtual = 'vazio'; // sem isto, uma falha trava para sempre em 'carregando'
      throw erro;
    }
  }

  private pararSource(): void {
    this.src?.stop();
    this.src?.disconnect();
    this.src = null;
  }

  /** AudioBufferSourceNode é descartável: toda mudança recria o node (SPEC seção 5). */
  private criarSource(de: number): void {
    if (!this.buffer) return;
    this.pararSource();

    const src = this.ctx.createBufferSource();
    src.buffer = this.buffer;
    if (this.reg) {
      src.loop = true;
      src.loopStart = this.reg.inicio;
      src.loopEnd = this.reg.fim;
    }
    src.connect(this.ganho);
    src.start(0, de);
    if (!src.loop) {
      // sem loop, o node termina sozinho ao fim do buffer — sem isto o estado
      // fica travado em 'tocando' mesmo com o som já parado. A checagem
      // `this.src === src` ignora o onended de um node antigo já substituído
      // (stop() dispara 'ended' de forma assíncrona).
      src.onended = () => {
        if (this.src === src) {
          this.pausadoEm = this.duracao;
          this.estadoAtual = 'pronto';
        }
      };
    }

    this.src = src;
    this.offset = de;
    this.iniciadoEm = this.ctx.currentTime;
    this.estadoAtual = 'tocando';
  }

  tocar(de?: number): void {
    if (!this.buffer) return;
    this.criarSource(de ?? this.pausadoEm);
  }

  pausar(): void {
    if (!this.tocando) return;
    this.pausadoEm = this.posicao();
    this.pararSource();
    this.estadoAtual = 'pronto';
  }

  /** Pausa e volta ao início da região (ou a 0). */
  parar(): void {
    this.pararSource();
    this.pausadoEm = this.reg?.inicio ?? 0;
    this.estadoAtual = this.buffer ? 'pronto' : 'vazio';
  }

  /** Define a região de loop. null desliga o loop. */
  definirRegiao(r: Regiao | null): void {
    const posAtual = this.posicao();
    this.reg = r;

    if (!this.tocando) {
      if (r && (posAtual < r.inicio || posAtual >= r.fim)) this.pausadoEm = r.inicio;
      return;
    }

    // Tocando: fora da nova região, recomeça no início dela;
    // dentro, recria o node na posição atual (SPEC seção 5, regra 5).
    const foraDaRegiao = r != null && (posAtual < r.inicio || posAtual >= r.fim);
    this.criarSource(foraDaRegiao ? r!.inicio : posAtual);
  }

  buscar(t: number): void {
    const alvo = Math.min(Math.max(t, 0), this.duracao || t);
    if (this.tocando) this.criarSource(alvo);
    else this.pausadoEm = alvo;
  }

  volume(v: number): void {
    this.ganho.gain.value = Math.min(Math.max(v, 0), 1);
  }

  /** Sempre calculada de ctx.currentTime — nunca acumulada (SPEC seção 5, regra 3). */
  posicao(): number {
    if (!this.tocando) return this.pausadoEm;
    const decorrido = this.ctx.currentTime - this.iniciadoEm;
    if (!this.reg) return Math.min(this.offset + decorrido, this.duracao);
    return posicaoNaRegiao(this.offset, this.reg.inicio, this.reg.fim, decorrido);
  }

  destruir(): void {
    this.pararSource();
    this.ganho.disconnect();
    void this.ctx.close();
    this.estadoAtual = 'vazio';
  }
}
