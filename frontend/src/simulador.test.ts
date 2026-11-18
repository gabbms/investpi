import { describe, expect, it } from 'vitest'
import { alterados, pesoValido, temInvalido } from './simulador'

describe('pesoValido', () => {
  it('aceita inteiros de 0 a 5', () => {
    expect(pesoValido('3')).toBe(3)
    expect(pesoValido('0')).toBe(0)
    expect(pesoValido('5')).toBe(5)
  })
  it('recusa fora da faixa, decimais e vazio', () => {
    expect(pesoValido('6')).toBeNull()
    expect(pesoValido('-1')).toBeNull()
    expect(pesoValido('2.5')).toBeNull()
    expect(pesoValido('')).toBeNull()
  })
})

describe('alterados', () => {
  it('manda só os pesos diferentes dos oficiais', () => {
    expect(alterados({ A: 3, B: 2 }, { A: 5, B: 2 })).toEqual({ A: 5 })
    expect(alterados({ A: 3 }, { A: 3 })).toEqual({})
  })
})

describe('temInvalido', () => {
  it('acusa campo fora de 0–5 ou vazio, para travar o salvar', () => {
    expect(temInvalido({ A: '5', B: '2' })).toBe(false)
    expect(temInvalido({ A: '50' })).toBe(true)
    expect(temInvalido({ A: '' })).toBe(true)
    expect(temInvalido({})).toBe(false)
  })
})
