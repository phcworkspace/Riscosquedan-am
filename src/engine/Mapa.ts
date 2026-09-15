// Riscos que Dançam — carrega e consulta o .map.json de uma faixa.
// engine/ não importa nada de React.

import { BANDAS, type Banda, type MapaDaFaixa, type Secao } from './tipos';

function interpolar(curva: number[] | Float64Array, fps: number, t: number): number {
  if (!curva?.length) return 0;
  const q = t * fps;
  const i = Math.floor(q);
  if (i < 0) return curva[0];
  if (i >= curva.length - 1) return curva[curva.length - 1];
  return curva[i] + (curva[i + 1] - curva[i]) * (q - i);
}

export class Mapa {
  readonly dados: MapaDaFaixa;
  private acumuladas: Record<Banda, Float64Array>;

  private constructor(dados: MapaDaFaixa) {
    this.dados = dados;
    this.acumuladas = this.calcularAcumuladas(dados);
  }

  /** Só para teste — expõe o construtor privado sem abrir mão dele em produção. */
  static __criarParaTeste(dados: MapaDaFaixa): Mapa {
    return new Mapa(dados);
  }

  static async carregar(url: string): Promise<Mapa> {
    const resposta = await fetch(url);
    if (!resposta.ok) {
      throw new Error(`Falha ao carregar o mapa em ${url}: ${resposta.status}`);
    }
    const dados = (await resposta.json()) as MapaDaFaixa;
    return new Mapa(dados);
  }

  private calcularAcumuladas(dados: MapaDaFaixa): Record<Banda, Float64Array> {
    const resultado = {} as Record<Banda, Float64Array>;
    for (const banda of BANDAS) {
      const curva = dados.bandas[banda] ?? [];
      const soma = new Float64Array(curva.length);
      let acc = 0;
      for (let i = 0; i < curva.length; i++) {
        acc += curva[i];
        soma[i] = acc;
      }
      resultado[banda] = soma;
    }
    return resultado;
  }

  /** Valor da banda no instante t, interpolado entre quadros. 0..1 */
  valor(banda: Banda, t: number): number {
    return interpolar(this.dados.bandas[banda], this.dados.fps, t);
  }

  /** Energia geral no instante t. 0..1 */
  energia(t: number): number {
    return interpolar(this.dados.rms, this.dados.fps, t);
  }

  /** Integral da banda de 0 até t. Usada pelo comportamento "girar" na Fase 2. */
  acumulado(banda: Banda, t: number): number {
    return interpolar(this.acumuladas[banda], this.dados.fps, t);
  }

  /** Seção que contém t, ou null. */
  secaoEm(t: number): Secao | null {
    const secoes = this.dados.secoes;
    for (let i = 0; i < secoes.length; i++) {
      const s = secoes[i];
      const ehUltima = i === secoes.length - 1;
      // a última seção fecha nos dois extremos: t === duracaoSeg precisa
      // continuar pertencendo a ela, senão nenhuma seção cobre esse instante.
      if (t >= s.inicio && (ehUltima ? t <= s.fim : t < s.fim)) return s;
    }
    return null;
  }

  /** Batida ou fronteira de seção mais próxima de t, dentro de `tolerancia`. */
  encaixe(t: number, tolerancia = 0.12): number | null {
    const candidatos = this.dados.pulso.temPulsoClaro
      ? this.dados.pulso.batidas
      : this.dados.secoes.flatMap(s => [s.inicio, s.fim]);

    let melhor: number | null = null;
    let menorDist = Infinity;
    for (const c of candidatos) {
      const dist = Math.abs(c - t);
      if (dist < menorDist) { menorDist = dist; melhor = c; }
    }
    return melhor !== null && menorDist <= tolerancia ? melhor : null;
  }
}
