import type { Coluna, Tabela as TTabela } from '../api'
import { valor } from '../format'

const STATUS_COR: Record<string, string> = { Atingida: 'verde', 'Atenção': 'amarelo', Abaixo: 'vermelho' }

function Celula({ coluna, v }: { coluna: Coluna; v: unknown }) {
  if (v === null || v === undefined || v === '') return <span className="suave">—</span>
  switch (coluna.formato) {
    case 'status':
      return <span className={`selo selo-${STATUS_COR[String(v)] ?? 'neutro'}`}>{String(v)}</span>
    case 'simnao':
      return <span className={v === 'Sim' ? 'sim' : 'nao'}>{String(v)}</span>
    case 'texto':
      return <>{String(v)}</>
    default:
      return <>{valor(Number(v), coluna.formato)}</>
  }
}

export function Tabela({ tabela }: { tabela: TTabela }) {
  return (
    <section className="tabela">
      <h3>{tabela.titulo}</h3>
      {tabela.linhas.length === 0 ? (
        <p className="vazio">Nenhuma linha para os filtros escolhidos.</p>
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
              {tabela.linhas.map((l, i) => (
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
