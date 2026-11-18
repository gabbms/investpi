import { describe, expect, it } from 'vitest'
import { normalizar, valor } from './format'

describe('valor', () => {
  it('formata reais em bilhões e milhões', () => {
    expect(valor(42829000000, 'brl')).toBe('R$ 42,8 bi')
    expect(valor(5330000000, 'brl')).toBe('R$ 5,3 bi')
    expect(valor(9000000000, 'brl')).toBe('R$ 9,0 bi')
    expect(valor(283000000, 'brl')).toBe('R$ 283 mi')
    expect(valor(1500000, 'brl')).toBe('R$ 1,5 mi')
    expect(valor(45000, 'brl')).toBe('R$ 45 mil')
    expect(valor(950, 'brl')).toBe('R$ 950')
  })
  it('formata percentuais, números, decimais e índices', () => {
    expect(valor(0.5417, 'pct')).toBe('54,2%')
    expect(valor(0.55, 'pct')).toBe('55,0%')
    expect(valor(7236, 'num')).toBe('7.236')
    expect(valor(3477889.4, 'num')).toBe('3.477.889')
    expect(valor(2.119, 'dec')).toBe('2,12')
    expect(valor(67.9, 'idx')).toBe('68')
  })
  it('mostra traço quando não há valor', () => {
    expect(valor(null, 'pct')).toBe('—')
    expect(valor(undefined, 'brl')).toBe('—')
  })
})

describe('normalizar', () => {
  it('ignora acentos e maiúsculas na busca', () => {
    expect(normalizar('Água Reutilizada')).toContain(normalizar('agua'))
    expect(normalizar('GOVERNANÇA')).toBe('governanca')
  })
})
