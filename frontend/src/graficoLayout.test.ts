import { describe, expect, it } from 'vitest'
import { rotulosColunas, marcasEixo, larguraRotuloBarras } from './graficoLayout'

const SETORES = ['Energia Renovável', 'Hidrogênio Verde', 'Mineração', 'Sustentabilidade Ambiental']

describe('rotulosColunas', () => {
  it('quebra em linhas quando cada palavra cabe no espaço da coluna', () => {
    const r = rotulosColunas(1100, SETORES)
    expect(r.rotacao).toBe(0)
    expect(r.largura).toBeGreaterThan(110)
  })
  it('inclina os nomes quando uma palavra não cabe na coluna (gráfico estreito)', () => {
    const r = rotulosColunas(350, SETORES)
    expect(r.rotacao).toBeGreaterThan(0)
  })
  it('uma categoria só nunca inclina', () => {
    expect(rotulosColunas(350, ['Mineração']).rotacao).toBe(0)
  })
})

describe('marcasEixo', () => {
  it('mostra menos marcas em gráficos estreitos', () => {
    expect(marcasEixo(200)).toBeLessThan(marcasEixo(800))
    expect(marcasEixo(100)).toBeGreaterThanOrEqual(2)
  })
})

describe('larguraRotuloBarras', () => {
  it('reserva no máximo 180 px e nunca mais de um terço do gráfico', () => {
    expect(larguraRotuloBarras(1200)).toBe(180)
    expect(larguraRotuloBarras(360)).toBeLessThanOrEqual(120)
  })
})

describe('rotulosColunas com palavras longas', () => {
  it('não quebra "Armazenamento" no meio num gráfico de meia largura com 5 colunas', () => {
    const fontes = ['Solar', 'Eólica', 'Solar + Armazenamento', 'Biomassa', 'Biogás']
    const r = rotulosColunas(540, fontes)
    expect(r.rotacao > 0 || 'Armazenamento'.length * 7 <= r.largura).toBe(true)
  })
})
