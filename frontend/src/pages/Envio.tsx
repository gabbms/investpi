import { Fragment, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { api, ErroApi, type ErroEstrutura, type Previa, type Versao } from '../api'
import { BotaoAbrir, ListaOcorrencias } from '../components/ListaOcorrencias'
import { valor } from '../format'

type Etapa =
  | { tipo: 'inicio' }
  | { tipo: 'validando' }
  | { tipo: 'previa'; previa: Previa }
  | { tipo: 'gravando'; previa: Previa }
  | { tipo: 'gravado'; versao: Versao }

function local(e: ErroEstrutura) {
  return [e.aba, e.linha ? `linha ${e.linha}` : null, e.coluna].filter(Boolean).join(', ')
}

export function Envio() {
  const entrada = useRef<HTMLInputElement>(null)
  const [arquivo, setArquivo] = useState<File | null>(null)
  const [etapa, setEtapa] = useState<Etapa>({ tipo: 'inicio' })
  const [erro, setErro] = useState<string | null>(null)
  const [abertas, setAbertas] = useState<Set<string>>(new Set())

  async function validar(f: File) {
    setArquivo(f)
    setErro(null)
    setAbertas(new Set())
    setEtapa({ tipo: 'validando' })
    try {
      setEtapa({ tipo: 'previa', previa: await api.upload<Previa>('/api/importacao/previa', f) })
    } catch (e) {
      setErro(e instanceof Error ? e.message : 'Não foi possível ler o arquivo.')
      setEtapa({ tipo: 'inicio' })
    }
  }

  async function confirmar(previa: Previa) {
    if (!arquivo) return
    setErro(null)
    setEtapa({ tipo: 'gravando', previa })
    try {
      const r = await api.upload<{ versao: Versao }>('/api/importacao/confirmar', arquivo)
      setEtapa({ tipo: 'gravado', versao: r.versao })
    } catch (e) {
      const msg =
        e instanceof ErroApi && typeof e.detalhe === 'object' && e.detalhe
          ? (e.detalhe as { mensagem?: string }).mensagem
          : e instanceof Error
            ? e.message
            : null
      setErro(msg ?? 'Não foi possível gravar a planilha.')
      setEtapa({ tipo: 'previa', previa })
    }
  }

  function recomecar() {
    setArquivo(null)
    setErro(null)
    setEtapa({ tipo: 'inicio' })
    if (entrada.current) entrada.current.value = ''
  }

  const previa = etapa.tipo === 'previa' || etapa.tipo === 'gravando' ? etapa.previa : null

  return (
    <div className="pagina admin" style={{ ['--cor-pagina' as string]: '#4B5563' }}>
      <header className="pagina-cabecalho">
        <h1>Enviar planilha</h1>
        <p>
          Envie a planilha ASG completa. O sistema confere a estrutura antes de gravar; a versão em uso só muda quando você confirma.
        </p>
      </header>

      {etapa.tipo === 'gravado' ? (
        <section className="bloco sucesso">
          <h2>Versão {etapa.versao.numero} gravada e ativa</h2>
          <p>
            {etapa.versao.nome_arquivo}: {Object.values(etapa.versao.linhas_por_aba).reduce((a, b) => a + b, 0).toLocaleString('pt-BR')} linhas.
            O painel já mostra os novos dados.
          </p>
          <div className="acoes">
            <Link className="botao" to="/">
              Ver o painel
            </Link>
            <button type="button" className="botao secundario" onClick={recomecar}>
              Enviar outra planilha
            </button>
          </div>
        </section>
      ) : (
        <section className="bloco">
          <div className="envio-escolha">
            <label className="botao">
              {arquivo ? 'Escolher outro arquivo' : 'Escolher arquivo .xlsx'}
              <input
                ref={entrada}
                type="file"
                accept=".xlsx,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                className="oculto"
                onChange={(e) => e.target.files?.[0] && validar(e.target.files[0])}
              />
            </label>
            <span className="suave">{arquivo ? arquivo.name : 'Nenhum arquivo escolhido'}</span>
            <button
              type="button"
              className="link-botao"
              onClick={() => api.baixar('/api/importacao/modelo', 'planilha_modelo_ASG.xlsx')}
            >
              Baixar planilha modelo
            </button>
          </div>
          {etapa.tipo === 'validando' && <p className="suave">Conferindo a planilha…</p>}
          {erro && (
            <p className="erro" role="alert">
              {erro}
            </p>
          )}
        </section>
      )}

      {previa && (
        <>
          <section className="bloco">
            <h2>{previa.erros.length ? `${previa.erros.length} erro(s) impedem a gravação` : 'Estrutura correta'}</h2>
            {previa.erros.length > 0 ? (
              <>
                <p>Corrija a planilha e envie de novo. Nada foi gravado.</p>
                <ul className="lista-erros">
                  {previa.erros.map((e, i) => (
                    <li key={i}>
                      <strong>{local(e) || 'Planilha'}</strong>: {e.mensagem}
                    </li>
                  ))}
                </ul>
              </>
            ) : (
              <p>Todas as abas e colunas obrigatórias foram encontradas, com tipos e códigos válidos.</p>
            )}
          </section>

          <div className="envio-grade">
            <section className="bloco">
              <h2>Linhas lidas por aba</h2>
              <table className="compacta">
                <tbody>
                  {Object.entries(previa.linhas_por_aba).map(([aba, n]) => (
                    <tr key={aba}>
                      <td>{aba}</td>
                      <td className="num">{valor(n, 'num')}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </section>

            {previa.checagens.length > 0 && (
              <section className="bloco">
                <h2>Checagens de qualidade</h2>
                <p className="suave pequeno">Avisos não impedem a gravação.</p>
                <table className="compacta">
                  <tbody>
                    {previa.checagens.map((c) => {
                      const aberta = abertas.has(c.id)
                      const temLista = !!c.ocorrencias?.length
                      return (
                        <Fragment key={c.id}>
                          <tr>
                            <td>
                              {temLista && (
                                <BotaoAbrir
                                  aberto={aberta}
                                  aoAlternar={() =>
                                    setAbertas((a) => {
                                      const n = new Set(a)
                                      if (!n.delete(c.id)) n.add(c.id)
                                      return n
                                    })
                                  }
                                  rotulo={c.id}
                                />
                              )}
                            </td>
                            <td className="suave">{c.id}</td>
                            <td title={c.regra}>{c.checagem}</td>
                            <td>
                              {c.problemas === 0 ? (
                                <span className="selo selo-verde">OK</span>
                              ) : (
                                <span className="selo selo-amarelo">Verificar: {c.problemas}</span>
                              )}
                            </td>
                          </tr>
                          {aberta && temLista && (
                            <tr>
                              <td className="ocorrencias-celula" colSpan={4}>
                                <ListaOcorrencias ocorrencias={c.ocorrencias!} mais={c.mais} />
                              </td>
                            </tr>
                          )}
                        </Fragment>
                      )
                    })}
                  </tbody>
                </table>
              </section>
            )}
          </div>

          <div className="acoes">
            <button
              type="button"
              className="botao"
              disabled={!previa.pode_confirmar || etapa.tipo === 'gravando'}
              onClick={() => confirmar(previa)}
            >
              {etapa.tipo === 'gravando' ? 'Gravando…' : 'Confirmar envio'}
            </button>
            <button type="button" className="botao secundario" onClick={recomecar}>
              Cancelar
            </button>
          </div>
        </>
      )}
    </div>
  )
}
