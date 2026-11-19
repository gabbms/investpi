import { describe, expect, it } from 'vitest'
import { arquivoGrandeDemais, comparacao, textoDoErro, corDoStatus, nomeExportacao, chaveDaLinha, normalizar, textoOcorrencia, textoSemLinhas, valor } from './format'

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

describe('chaveDaLinha', () => {
  it('não muda com o filtro: usa o id, ou o índice original sem id', () => {
    const linhas: Record<string, unknown>[] = [{ id: 'C01' }, { id: 'C07' }, { nome: 'x' }]
    const filtradas = linhas.filter((l) => l.id === 'C07')
    expect(chaveDaLinha(filtradas[0], 0 + linhas.indexOf(filtradas[0]))).toBe('C07')
    expect(chaveDaLinha(linhas[1], 1)).toBe('C07')
    expect(chaveDaLinha(linhas[2], 2)).toBe('2')
  })
})

describe('envio grande demais', () => {
  it('arquivo acima de 4 MB é barrado antes de enviar', () => {
    expect(arquivoGrandeDemais(4 * 1024 * 1024)).toBe(false)
    expect(arquivoGrandeDemais(4 * 1024 * 1024 + 1)).toBe(true)
  })
  it('o 413 sem detalhe (cortado pela Vercel) vira uma mensagem clara', () => {
    expect(textoDoErro(413, undefined)).toContain('4 MB')
    expect(textoDoErro(413, 'Arquivo maior que 4 MB.')).toBe('Arquivo maior que 4 MB.')
    expect(textoDoErro(500, undefined)).toBe('Erro 500')
  })
})

describe('comparacao', () => {
  it('mostra o valor anterior e a variação em %', () => {
    expect(comparacao(162, 184, 'num', '2025')).toBe('2025: 184 · ▼ 12%')
  })
  it('em percentuais, a diferença vem em pontos percentuais', () => {
    expect(comparacao(0.48, 0.44, 'pct', '2025')).toBe('2025: 44,0% · ▲ 4,0 p.p.')
    expect(comparacao(0.03, 0.02, 'pct', '2025')).toBe('2025: 2,0% · ▲ 1,0 p.p.')
    expect(comparacao(0.5, 0.62, 'pct', '2025')).toBe('2025: 62,0% · ▼ 12,0 p.p.')
    expect(comparacao(0.3, 0, 'pct', '2025')).toBe('2025: 0,0% · ▲ 30,0 p.p.')
  })
  it('sem variação mostra só o valor anterior com "=" ', () => {
    expect(comparacao(12, 12, 'num', '2025')).toBe('2025: 12 · =')
  })
  it('anterior zero mostra só o valor anterior', () => {
    expect(comparacao(0, 0, 'num', '2025')).toBe('2025: 0 · =')
    expect(comparacao(3, 0, 'num', '2025')).toBe('2025: 0')
  })
  it('sem anterior ou sem valor atual não há comparação', () => {
    expect(comparacao(162, null, 'num', '2025')).toBeNull()
    expect(comparacao(null, 184, 'num', '2025')).toBe('2025: 184')
  })
})
