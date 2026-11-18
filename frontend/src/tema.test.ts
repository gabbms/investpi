import { describe, expect, it } from 'vitest'
import { seguirSistema, temaDoEvento, temaInicial } from './tema'

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

describe('seguirSistema', () => {
  it('sem escolha válida guardada, a página acompanha o tema do sistema ao vivo', () => {
    expect(seguirSistema(null)).toBe(true)
    expect(seguirSistema('azul')).toBe(true)
    expect(seguirSistema('escuro')).toBe(false)
  })
})

describe('temaDoEvento', () => {
  it('troca feita em outra aba vale nesta; outras chaves são ignoradas', () => {
    expect(temaDoEvento('asg_tema', 'escuro', false)).toBe('escuro')
    expect(temaDoEvento('asg_tema', null, true)).toBe('escuro') // escolha apagada → volta ao sistema
    expect(temaDoEvento('asg_token', 'x', false)).toBeNull()
  })
})
