// Formatação de números no padrão brasileiro (spec §3): R$ 42,8 bi · 54,2% · 7.236
export type Formato = 'brl' | 'num' | 'pct' | 'dec' | 'idx'

const nf = (casas: number) =>
  new Intl.NumberFormat('pt-BR', { minimumFractionDigits: 0, maximumFractionDigits: casas })

function reais(v: number): string {
  const abs = Math.abs(v)
  const escalas: [number, string][] = [
    [1e9, 'bi'],
    [1e6, 'mi'],
    [1e3, 'mil'],
  ]
  for (const [base, sufixo] of escalas) {
    if (abs >= base) {
      const x = v / base
      // uma casa decimal abaixo de 100 (42,8 bi), nenhuma acima (283 mi)
      return `R$ ${nf(Math.abs(x) < 100 ? 1 : 0).format(x)} ${sufixo}`
    }
  }
  return `R$ ${nf(0).format(v)}`
}

export function valor(v: number | null | undefined, formato: Formato | string): string {
  if (v === null || v === undefined || Number.isNaN(v)) return '—'
  switch (formato) {
    case 'brl':
      return reais(v)
    case 'pct':
      return `${nf(1).format(v * 100)}%`
    case 'dec':
      return nf(2).format(v)
    case 'idx':
      return nf(0).format(Math.round(v))
    default:
      return nf(0).format(v)
  }
}

/** Número compacto para eixos de gráfico. */
export function eixo(v: number, formato: Formato | string): string {
  if (formato === 'brl') return reais(v).replace('R$ ', '')
  if (formato === 'pct') return `${nf(0).format(v * 100)}%`
  if (Math.abs(v) >= 1e6) return `${nf(1).format(v / 1e6)} mi`
  if (Math.abs(v) >= 1e4) return `${nf(0).format(v / 1e3)} mil`
  return nf(1).format(v)
}
