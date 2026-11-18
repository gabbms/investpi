import { useCallback, useEffect, useState } from 'react'
import { api, type Versao } from '../api'

const STATUS: Record<Versao['status'], { texto: string; classe: string }> = {
  ativa: { texto: 'Em uso', classe: 'selo-verde' },
  inativa: { texto: 'Inativa', classe: 'selo-neutro' },
  rejeitada: { texto: 'Rejeitada', classe: 'selo-vermelho' },
}

const dataHora = (iso: string) =>
  new Date(iso).toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' })

const total = (linhas: Record<string, number>) => Object.values(linhas).reduce((a, b) => a + b, 0)

export function Versoes() {
  const [versoes, setVersoes] = useState<Versao[] | null>(null)
  const [erro, setErro] = useState<string | null>(null)
  const [mensagem, setMensagem] = useState<string | null>(null)
  const [aberta, setAberta] = useState<number | null>(null)

  const carregar = useCallback(() => {
    api.get<Versao[]>('/api/versoes').then(setVersoes).catch((e) => setErro(e.message))
  }, [])
  useEffect(carregar, [carregar])

  async function ativar(v: Versao) {
    if (!window.confirm(`Ativar a versão ${v.numero}? O painel passará a mostrar os dados de ${v.nome_arquivo}.`)) return
    setErro(null)
    try {
      await api.post(`/api/versoes/${v.id}/ativar`)
      setMensagem(`Versão ${v.numero} ativada. O painel já mostra esses dados.`)
      carregar()
    } catch (e) {
      setErro(e instanceof Error ? e.message : 'Não foi possível ativar a versão.')
    }
  }

  return (
    <div className="pagina admin" style={{ ['--cor-pagina' as string]: '#4B5563' }}>
      <header className="pagina-cabecalho">
        <h1>Histórico de versões</h1>
        <p>Cada envio confirmado vira uma versão completa dos dados. Só uma fica em uso por vez; você pode voltar a uma anterior.</p>
      </header>
      {mensagem && <p className="bloco sucesso">{mensagem}</p>}
      {erro && (
        <p className="erro" role="alert">
          {erro}
        </p>
      )}
      <section className="tabela">
        {!versoes ? (
          <p className="suave">Carregando…</p>
        ) : versoes.length === 0 ? (
          <p className="vazio">Nenhuma planilha enviada ainda.</p>
        ) : (
          <div className="tabela-rolagem">
            <table>
              <thead>
                <tr>
                  <th className="num">Versão</th>
                  <th>Enviada em</th>
                  <th>Enviada por</th>
                  <th>Arquivo</th>
                  <th className="num">Linhas</th>
                  <th>Avisos e erros</th>
                  <th>Situação</th>
                  <th />
                </tr>
              </thead>
              <tbody>
                {versoes.map((v) => (
                  <tr key={v.id}>
                    <td className="num">{v.numero}</td>
                    <td>{dataHora(v.criado_em)}</td>
                    <td>{v.enviado_por ?? '—'}</td>
                    <td>{v.nome_arquivo}</td>
                    <td className="num">{v.status === 'rejeitada' ? '—' : total(v.linhas_por_aba).toLocaleString('pt-BR')}</td>
                    <td>
                      {v.erros.length + v.avisos.length === 0 ? (
                        <span className="suave">Nenhum</span>
                      ) : (
                        <button type="button" className="link-botao" onClick={() => setAberta(aberta === v.id ? null : v.id)}>
                          {v.erros.length > 0 ? `${v.erros.length} erro(s)` : `${v.avisos.length} aviso(s)`}
                        </button>
                      )}
                      {aberta === v.id && (
                        <ul className="lista-erros">
                          {v.erros.map((e, i) => (
                            <li key={`e${i}`}>
                              {[e.aba, e.linha && `linha ${e.linha}`, e.coluna].filter(Boolean).join(', ')}: {e.mensagem}
                            </li>
                          ))}
                          {v.avisos.map((a) => (
                            <li key={a.id}>
                              {a.id} {a.checagem}: {a.problemas}
                            </li>
                          ))}
                        </ul>
                      )}
                    </td>
                    <td>
                      <span className={`selo ${STATUS[v.status].classe}`}>{STATUS[v.status].texto}</span>
                    </td>
                    <td>
                      {v.status === 'inativa' && (
                        <button type="button" className="botao secundario" onClick={() => ativar(v)}>
                          Ativar
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  )
}
