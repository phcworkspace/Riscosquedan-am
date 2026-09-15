import { describe, expect, it } from 'vitest';
import { posicaoNaRegiao } from './Audio';

describe('posicaoNaRegiao', () => {
  it('no início do loop, decorrido=0, retorna o próprio início do offset', () => {
    expect(posicaoNaRegiao(10, 10, 18, 0)).toBe(10);
  });

  it('avança normalmente dentro da janela', () => {
    expect(posicaoNaRegiao(10, 10, 18, 5)).toBe(15);
  });

  it('dá a volta exatamente no fim da janela (8s de região)', () => {
    expect(posicaoNaRegiao(10, 10, 18, 8)).toBeCloseTo(10, 10);
  });

  it('dá a volta e continua depois do wrap', () => {
    expect(posicaoNaRegiao(10, 10, 18, 8.5)).toBeCloseTo(10.5, 10);
  });

  it('funciona quando o offset inicial não é o início da região', () => {
    // offset=12, região [10,18] (janela 8), decorrido=20 -> 12-10+20=22; 22 % 8 = 6
    expect(posicaoNaRegiao(12, 10, 18, 20)).toBeCloseTo(16, 10);
  });

  it('janela inválida (fim <= início) retorna o início, defensivamente', () => {
    expect(posicaoNaRegiao(5, 10, 10, 3)).toBe(10);
  });
});
