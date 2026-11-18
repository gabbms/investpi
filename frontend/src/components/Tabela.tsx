import { Fragment, useMemo, useState } from 'react'
import type { Coluna, Ocorrencia, Tabela as TTabela } from '../api'
import { BotaoAbrir, ListaOcorrencias } from './ListaOcorrencias'
import { chaveDaLinha, corDoStatus, normalizar, textoSemLinhas, valor } from '../format'

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
  const [abertas, setAbertas] = useState<Set<string>>(new Set())
  const alternar = (chave: string) =>
    setAbertas((a) => {
      const n = new Set(a)
      if (!n.delete(chave)) n.add(chave)
      return n
    })
  const textos = useMemo(
    () => tabela.linhas.map((l) => normalizar(tabela.colunas.map((c) => String(l[c.chave] ?? '')).join(' '))),
    [tabela],
  )
  const termo = normalizar(busca.trim())
  const linhas = tabela.linhas
    .map((l, original) => ({ l, original }))
    .filter(({ original }) => !termo || textos[original].includes(termo))

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
                {tabela.expansivel && <th aria-label="Registros" />}
                {tabela.colunas.map((c) => (
                  <th key={c.chave} className={['texto', 'status', 'simnao'].includes(c.formato) ? '' : 'num'}>
                    {c.rotulo}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {linhas.map(({ l, original }) => {
                const chave = chaveDaLinha(l, original)
                const ocorrencias = (l.ocorrencias as Ocorrencia[] | undefined) ?? []
                const aberta = abertas.has(chave)
                return (
                  <Fragment key={chave}>
                    <tr>
                      {tabela.expansivel && (
                        <td>
                          {ocorrencias.length > 0 && (
                            <BotaoAbrir aberto={aberta} aoAlternar={() => alternar(chave)} rotulo={String(l.id ?? original + 1)} />
                          )}
                        </td>
                      )}
                      {tabela.colunas.map((c) => (
                        <td key={c.chave} className={['texto', 'status', 'simnao'].includes(c.formato) ? '' : 'num'}>
                          <Celula coluna={c} v={l[c.chave]} />
                        </td>
                      ))}
                    </tr>
                    {aberta && ocorrencias.length > 0 && (
                      <tr>
                        <td className="ocorrencias-celula" colSpan={tabela.colunas.length + 1}>
                          <ListaOcorrencias ocorrencias={ocorrencias} mais={l.mais as number | undefined} />
                        </td>
                      </tr>
                    )}
                  </Fragment>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </section>
  )
}
