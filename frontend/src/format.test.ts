import { describe, expect, it } from 'vitest'
import { corDoStatus, nomeExportacao, normalizar, textoOcorrencia, textoSemLinhas, valor } from './format'

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

describe('corDoStatus', () => {
  it('pinta metas e checagens com as cores do semáforo', () => {
    expect(corDoStatus('Atingida')).toBe('verde')
    expect(corDoStatus('Atenção')).toBe('amarelo')
    expect(corDoStatus('Abaixo')).toBe('vermelho')
    expect(corDoStatus('OK')).toBe('verde')
    expect(corDoStatus('Verificar')).toBe('amarelo')
    expect(corDoStatus('outro')).toBe('neutro')
  })
})

describe('textoSemLinhas', () => {
  it('culpa a busca quando há termo, e os filtros quando não há', () => {
    expect(textoSemLinhas('xyz')).toBe('Nenhum resultado para a busca.')
    expect(textoSemLinhas('')).toBe('Nenhuma linha para os filtros escolhidos.')
  })
})

describe('nomeExportacao', () => {
  it('leva o caminho e a data local, como o servidor', () => {
    const dia = new Date(2026, 10, 18, 23, 30) // 18/11/2026, 23h30 no horário local
    expect(nomeExportacao('setor/mineracao', dia)).toBe('ASG_setor_mineracao_2026-11-18.xlsx')
    expect(nomeExportacao('visao-geral', new Date(2026, 0, 5))).toBe('ASG_visao-geral_2026-01-05.xlsx')
  })
})

describe('textoOcorrencia', () => {
  it('mostra aba, linha e identificador', () => {
    expect(textoOcorrencia({ aba: 'dProjeto', linha: 2, identificador: 'PROJ001', detalhe: '' })).toBe('dProjeto · linha 2 · PROJ001')
    expect(textoOcorrencia({ aba: 'fContratos', linha: null, identificador: 'LIC001', detalhe: '' })).toBe('fContratos · LIC001')
  })
  it('omite o identificador vazio', () => {
    expect(textoOcorrencia({ aba: 'dProjeto', linha: 2, identificador: '', detalhe: '' })).toBe('dProjeto · linha 2')
  })
})
