// Medidas dos rótulos dos gráficos a partir da largura real do gráfico na tela,
// para os nomes e os números dos eixos não se sobreporem em gráficos estreitos.

const EIXO_VALOR = 60 // espaço aproximado do eixo de valores e das margens, em px
const PX_POR_LETRA = 7 // estimativa usada quando não há como medir o texto (testes)

/** Mede a largura de um texto em px; sem navegador, estima pelo número de letras. */
export type Medidor = (texto: string) => number
const estimar: Medidor = (t) => t.length * PX_POR_LETRA

export interface RotulosColunas {
  largura: number // largura máxima de cada nome, em px
  rotacao: number // 0 = nomes quebram em linhas; > 0 = nomes inclinados
}

/** Nomes embaixo das colunas: quebram em linhas se cada palavra cabe na coluna; senão, inclinam. */
export function rotulosColunas(larguraGrafico: number, categorias: string[], medir: Medidor = estimar): RotulosColunas {
  const n = Math.max(1, categorias.length)
  const porColuna = Math.max(40, (larguraGrafico - EIXO_VALOR) / n)
  const largura = Math.floor(porColuna) - 4
  const maiorPalavra = Math.max(0, ...categorias.flatMap((c) => c.split(/\s+/)).map(medir))
  if (n === 1 || maiorPalavra <= largura) return { largura, rotacao: 0 }
  return { largura: 100, rotacao: 30 }
}

/** Quantas marcas o eixo de valores mostra: uma a cada ~80 px, no mínimo 2. */
export function marcasEixo(larguraEixo: number): number {
  return Math.max(2, Math.min(5, Math.floor(larguraEixo / 80)))
}

/** Espaço dos nomes à esquerda das barras horizontais: até 180 px e até um terço do gráfico. */
export function larguraRotuloBarras(larguraGrafico: number): number {
  return Math.max(70, Math.min(180, Math.floor(larguraGrafico / 3)))
}
