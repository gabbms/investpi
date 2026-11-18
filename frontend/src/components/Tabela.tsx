import { useMemo, useState } from 'react'
import type { Coluna, Tabela as TTabela } from '../api'
import { corDoStatus, normalizar, textoSemLinhas, valor } from '../format'

function Celula({ coluna, v }: { coluna: Coluna; v: unknown }) {
  if (v === null || v === undefined || v === '') return <span className="suave">—</span>
  switch (coluna.formato) {
    case 'status':
      return <span className={`selo selo-${corDoStatus(String(v))}`}>{String(v)}</span>
    case 'simnao':
      return <span className={v === 'Sim' ? 'sim' : 'nao'}>{String(v)}</span>
    case 'texto':
      return <>{String(v)}</>
    default:
      return <>{valor(Number(v), coluna.formato)}</>
  }
}

export function Tabela({ tabela }: { tabela: TTabela }) {
  const [busca, setBusca] = useState('')
  const textos = useMemo(
    () => tabela.linhas.map((l) => normalizar(tabela.colunas.map((c) => String(l[c.chave] ?? '')).join(' '))),
    [tabela],
  )
  const termo = normalizar(busca.trim())
  const linhas = termo ? tabela.linhas.filter((_, i) => textos[i].includes(termo)) : tabela.linhas

  return (
    <section className="tabela">
      <h3>{tabela.titulo}</h3>
      {tabela.busca && (
        <div className="tabela-busca">
          <input
            type="search"
            value={busca}
            onChange={(e) => setBusca(e.target.value)}
            placeholder="Buscar por nome, código, tema, ODS ou GRI"
            aria-label="Buscar na tabela"
          />
          <p className="suave">
            {linhas.length} de {tabela.linhas.length} indicadores
          </p>
        </div>
      )}
      {linhas.length === 0 ? (
        <p className="vazio">{textoSemLinhas(termo)}</p>
      ) : (
        <div className="tabela-rolagem">
          <table>
            <thead>
              <tr>
                {tabela.colunas.map((c) => (
                  <th key={c.chave} className={['texto', 'status', 'simnao'].includes(c.formato) ? '' : 'num'}>
                    {c.rotulo}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {linhas.map((l, i) => (
                <tr key={i}>
                  {tabela.colunas.map((c) => (
                    <td key={c.chave} className={['texto', 'status', 'simnao'].includes(c.formato) ? '' : 'num'}>
                      <Celula coluna={c} v={l[c.chave]} />
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  )
}
