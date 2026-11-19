// Formatação de números no padrão brasileiro (spec §3): R$ 42,8 bi · 54,2% · 7.236
import type { Ocorrencia } from './api'

export type Formato = 'brl' | 'num' | 'pct' | 'dec' | 'idx'

const nf = (casas: number) =>
  new Intl.NumberFormat('pt-BR', { minimumFractionDigits: 0, maximumFractionDigits: casas })

const fixo = (casas: number) =>
  new Intl.NumberFormat('pt-BR', { minimumFractionDigits: casas, maximumFractionDigits: casas })

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
      // uma casa decimal em bi/mi abaixo de 100 (42,8 bi; 9,0 bi), nenhuma acima (283 mi) nem em mil
      return `R$ ${fixo(sufixo !== 'mil' && Math.abs(x) < 100 ? 1 : 0).format(x)} ${sufixo}`
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
      return `${fixo(1).format(v * 100)}%`
    case 'dec':
      return nf(2).format(v)
    case 'idx':
      return nf(0).format(Math.round(v))
    default:
      return nf(0).format(v)
  }
}

/** Linha de comparação do card com o período anterior: "2025: 184 · ▼ 12%". */
export function comparacao(
  atual: number | null,
  anterior: number | null | undefined,
  formato: Formato | string,
  rotulo: string | null | undefined,
): string | null {
  if (anterior === null || anterior === undefined) return null
  const base = `${rotulo ?? 'Anterior'}: ${valor(anterior, formato)}`
  if (atual === null) return base
  if (atual === anterior) return `${base} · =`
  const seta = atual > anterior ? '▲' : '▼'
  // percentual contra percentual: a diferença em pontos (2% → 3% é +1 p.p., não +50%)
  if (formato === 'pct') return `${base} · ${seta} ${fixo(1).format(Math.abs(atual - anterior) * 100)} p.p.`
  if (anterior === 0) return base
  const pct = Math.round((Math.abs(atual - anterior) / Math.abs(anterior)) * 100)
  return `${base} · ${seta} ${pct}%`
}

/** Número compacto para eixos de gráfico. */
export function eixo(v: number, formato: Formato | string): string {
  if (formato === 'brl') return reais(v).replace('R$ ', '')
  if (formato === 'pct') return `${nf(0).format(v * 100)}%`
  if (Math.abs(v) >= 1e6) return `${nf(1).format(v / 1e6)} mi`
  if (Math.abs(v) >= 1e4) return `${nf(0).format(v / 1e3)} mil`
  return nf(1).format(v)
}

/** Texto sem acentos e em minúsculas, para a busca: "Água" e "agua" ficam iguais. */
export function normalizar(texto: string): string {
  return texto.normalize('NFD').replace(/\p{Diacritic}/gu, '').toLowerCase()
}

// Cor do selo de uma coluna `status`: metas (Atingida/Atenção/Abaixo) e checagens (OK/Verificar).
const STATUS_COR: Record<string, string> = {
  Atingida: 'verde',
  'Atenção': 'amarelo',
  Abaixo: 'vermelho',
  OK: 'verde',
  Verificar: 'amarelo',
}
export function corDoStatus(status: string): string {
  return STATUS_COR[status] ?? 'neutro'
}

/** Mensagem da tabela vazia: com busca, a culpa é do termo; sem busca, dos filtros. */
export function textoSemLinhas(termo: string): string {
  return termo ? 'Nenhum resultado para a busca.' : 'Nenhuma linha para os filtros escolhidos.'
}

/** Nome do Excel exportado, igual ao do servidor: ASG_setor_mineracao_2026-11-18.xlsx (data local). */
export function nomeExportacao(caminho: string, hoje: Date = new Date()): string {
  const d = (n: number) => String(n).padStart(2, '0')
  const data = `${hoje.getFullYear()}-${d(hoje.getMonth() + 1)}-${d(hoje.getDate())}`
  return `ASG_${caminho.replace(/\//g, '_')}_${data}.xlsx`
}

/** Onde está o registro: "dProjeto · linha 2 · PROJ001" (sem a linha ou o código quando não há). */
export function textoOcorrencia(o: Ocorrencia): string {
  return [o.aba, o.linha != null ? `linha ${o.linha}` : null, o.identificador || null].filter(Boolean).join(' · ')
}

/** Identidade estável de uma linha (para guardar "aberta"): o `id`, ou o índice na lista sem filtro. */
export function chaveDaLinha(linha: Record<string, unknown>, indiceOriginal: number): string {
  return linha.id != null ? String(linha.id) : String(indiceOriginal)
}

/** Limite de envio de planilha (a Vercel corta pedidos acima de 4,5 MB; o servidor usa 4 MB). */
export const TAMANHO_MAXIMO_ENVIO = 4 * 1024 * 1024
export function arquivoGrandeDemais(bytes: number): boolean {
  return bytes > TAMANHO_MAXIMO_ENVIO
}

/** Texto de um erro da API; o 413 sem detalhe (cortado antes de chegar ao servidor) ganha explicação. */
export function textoDoErro(status: number, detalhe: unknown): string {
  if (typeof detalhe === 'string') return detalhe
  if (status === 413) return 'Arquivo maior que 4 MB. A planilha modelo tem cerca de 0,2 MB.'
  return `Erro ${status}`
}
