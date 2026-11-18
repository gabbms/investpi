// Filtros do painel guardados na URL (?setor=..&municipio=..), valendo em todas as telas.
import { useCallback, useMemo } from 'react'
import { useSearchParams } from 'react-router-dom'

export type ChaveFiltro = 'setor' | 'vp' | 'status' | 'municipio' | 'empresa'
export type Filtros = Record<ChaveFiltro, string[]>

export const CHAVES: ChaveFiltro[] = ['setor', 'vp', 'status', 'municipio', 'empresa']

export function useFiltros() {
  const [params, setParams] = useSearchParams()

  const filtros = useMemo(
    () => Object.fromEntries(CHAVES.map((c) => [c, params.getAll(c)])) as Filtros,
    [params],
  )

  const setFiltro = useCallback(
    (chave: ChaveFiltro, valores: string[]) => {
      setParams((atual) => {
        const novo = new URLSearchParams(atual)
        novo.delete(chave)
        valores.forEach((v) => novo.append(chave, v))
        return novo
      })
    },
    [setParams],
  )

  const limpar = useCallback(() => setParams(new URLSearchParams()), [setParams])

  const query = useMemo(() => {
    const q = new URLSearchParams()
    CHAVES.forEach((c) => filtros[c].forEach((v) => q.append(c, v)))
    return q
  }, [filtros])

  const ativos = CHAVES.reduce((n, c) => n + filtros[c].length, 0)

  return { filtros, setFiltro, limpar, query, ativos }
}
