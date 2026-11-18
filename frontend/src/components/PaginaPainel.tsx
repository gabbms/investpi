import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api, ErroApi, type Pagina } from '../api'
import { nomeExportacao } from '../format'
import { useAuth } from '../auth'
import { useFiltros } from '../filtros'
import { CardKpi } from './CardKpi'
import { Grafico } from './Grafico'
import { IndiceSelo } from './IndiceSelo'
import { Tabela } from './Tabela'

interface Props {
  endpoint: string
  /** cor do pilar ou do setor, usada na faixa do cabeçalho */
  cor: string
}

type Estado = { tipo: 'carregando' } | { tipo: 'ok'; pagina: Pagina } | { tipo: 'erro'; erro: ErroApi | Error }

/** Busca uma tela do painel com os filtros atuais e desenha índice, cards, gráficos e tabelas. */
export function PaginaPainel({ endpoint, cor }: Props) {
  const { query } = useFiltros()
  const { usuario } = useAuth()
  const [estado, setEstado] = useState<Estado>({ tipo: 'carregando' })
  const chave = `${endpoint}?${query.toString()}`
  const [anterior, setAnterior] = useState<Pagina | null>(null)
  const [gerando, setGerando] = useState(false)
  const [erroExportar, setErroExportar] = useState<string | null>(null)

  async function exportar() {
    const caminho = endpoint.replace('/api/painel/', '')
    setGerando(true)
    setErroExportar(null)
    try {
      await api.baixar(`/api/painel/exportar/${caminho}`, nomeExportacao(caminho), query)
    } catch (erro) {
      setErroExportar(erro instanceof Error ? erro.message : 'Não foi possível gerar o arquivo.')
    } finally {
      setGerando(false)
    }
  }

  useEffect(() => {
    let ativo = true
    setEstado({ tipo: 'carregando' })
    api
      .get<Pagina>(endpoint, query)
      .then((pagina) => {
        if (!ativo) return
        setEstado({ tipo: 'ok', pagina })
        setAnterior(pagina)
      })
      .catch((erro) => ativo && setEstado({ tipo: 'erro', erro }))
    return () => {
      ativo = false
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [chave])

  if (estado.tipo === 'erro') {
    const semVersao = estado.erro instanceof ErroApi && estado.erro.status === 409
    return (
      <div className="aviso-tela">
        <h1>{semVersao ? 'Ainda não há dados carregados' : 'Não foi possível carregar esta tela'}</h1>
        <p>
          {semVersao
            ? 'Envie a planilha ASG para que o painel mostre os indicadores.'
            : estado.erro.message}
        </p>
        {semVersao && usuario?.perfil === 'admin' && (
          <Link className="botao" to="/admin/envio">
            Enviar planilha
          </Link>
        )}
      </div>
    )
  }

  const pagina = estado.tipo === 'ok' ? estado.pagina : anterior
  if (!pagina) return <div className="carregando-tela">Carregando indicadores…</div>

  return (
    <div className={`pagina ${estado.tipo === 'carregando' ? 'atualizando' : ''}`} style={{ ['--cor-pagina' as string]: cor }}>
      <header className="pagina-cabecalho">
        <div>
          <h1>{pagina.titulo}</h1>
          {pagina.subtitulo && <p>{pagina.subtitulo}</p>}
        </div>
        <div className="exportar">
          {erroExportar && (
            <p className="erro" role="alert">
              {erroExportar}
            </p>
          )}
          <button type="button" className="botao secundario" onClick={exportar} disabled={gerando}>
            {gerando ? 'Gerando…' : 'Exportar Excel'}
          </button>
        </div>
      </header>

      <div className={`linha-kpi ${pagina.indice ? 'com-indice' : ''}`}>
        {pagina.indice && <IndiceSelo card={pagina.indice} />}
        <div className="cards">
          {pagina.cards.map((c) => (
            <CardKpi key={c.id} card={c} />
          ))}
        </div>
      </div>

      {pagina.graficos.length > 0 && (
        <div className="graficos">
          {pagina.graficos.map((g) => (
            <Grafico key={g.id} grafico={g} />
          ))}
        </div>
      )}

      {pagina.tabelas.map((t) => (
        <Tabela key={t.id} tabela={t} />
      ))}
    </div>
  )
}
