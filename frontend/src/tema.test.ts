import { describe, expect, it } from 'vitest'
import { temaInicial } from './tema'

describe('temaInicial', () => {
  it('sem escolha salva, segue o sistema', () => {
    expect(temaInicial(null, true)).toBe('escuro')
    expect(temaInicial(null, false)).toBe('claro')
  })
  it('a escolha salva vence o sistema', () => {
    expect(temaInicial('claro', true)).toBe('claro')
    expect(temaInicial('escuro', false)).toBe('escuro')
  })
  it('valor_invalido_segue_o_sistema', () => {
    expect(temaInicial('azul', true)).toBe('escuro')
    expect(temaInicial('', false)).toBe('claro')
  })
})
