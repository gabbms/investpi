import { useEffect, useMemo, useRef, useState } from 'react'
import { api, ErroApi, type Versao } from '../api'
import { useAuth } from '../auth'
import { useFiltros } from '../filtros'
import { corDoStatus } from '../format'
import { COR } from '../menu'
import {
  alterados,
  corDoIndice,
  pesoValido,
  PESO_MAXIMO,
  type Indices,
  type MetaSimulada,
  type Simulacao,
} from '../simulador'

const PILARES = ['Ambiental', 'Social', 'Governança'] as const
const ROTULO: Record<keyof Indices, string> = {
  geral: 'Índice ASG Geral',
  Ambiental: 'Ambiental',
  Social: 'Social',
  Governança: 'Governança',
}

function inteiro(v: number | null) {
  return v === null ? '—' : String(Math.round(v))
}

function Comparacao({ chave, oficial, simulado }: { chave: keyof Indices; oficial: number | null; simulado: number | null }) {
  const mudou = oficial !== null && simulado !== null && Math.round(oficial) !== Math.round(simulado)
  return (
    <section className="comparacao" aria-label={`${ROTULO[chave]}: oficial ${inteiro(oficial)}, simulado ${inteiro(simulado)}`}>
      <p className="comparacao-titulo">{ROTULO[chave]}</p>
      <p className="comparacao-valores">
        <span className={`indice-num cor-${corDoIndice(oficial)}`}>{inteiro(oficial)}</span>
        <span className="comparacao-seta" aria-hidden="true">→</span>
        <span className={`indice-num cor-${corDoIndice(simulado)} ${mudou ? 'mudou' : ''}`}>{inteiro(simulado)}</span>
      </p>
      <p className="pequeno suave">oficial → simulado</p>
    </section>
  )
}

/** Simulador de pesos das metas: mexe nos pesos e compara os índices com os oficiais. */
export function Simulador() {
  const { query } = useFiltros()
  const { usuario } = useAuth()
  const [dados, setDados] = useState<Simulacao | null>(null)
  const [pesos, setPesos] = useState<Record<string, number>>({})
  const [textos, setTextos] = useState<Record<string, string>>({})
  const [erro, setErro] = useState<string | null>(null)
  const [aviso, setAviso] = useState<string | null>(null)
  const [salvando, setSalvando] = useState(false)
  const pedido = useRef(0)

  const oficiais = useMemo(
    () => Object.fromEntries((dados?.metas ?? []).map((m) => [m.id_meta, m.peso_oficial])),
    [dados],
  )
  const mudancas = alterados(oficiais, pesos)
  const corpo = JSON.stringify(mudancas)

  // recalcula ~300 ms depois da última edição; respostas antigas são ignoradas
  useEffect(() => {
    const meu = ++pedido.current
    const t = setTimeout(async () => {
      try {
        const r = await api.post<Simulacao>(`/api/painel/simular-pesos?${query.toString()}`, { pesos: JSON.parse(corpo) })
        if (meu !== pedido.current) return
        setDados(r)
        setErro(null)
      } catch (e) {
        if (meu !== pedido.current) return
        setErro(e instanceof ErroApi ? e.message : 'Não foi possível calcular a simulação.')
      }
    }, 300)
    return () => clearTimeout(t)
  }, [corpo, query])

  function mudar(m: MetaSimulada, texto: string) {
    setTextos((t) => ({ ...t, [m.id_meta]: texto }))
    const p = pesoValido(texto)
    if (p !== null) setPesos((x) => ({ ...x, [m.id_meta]: p }))
  }

  function restaurar() {
    setPesos({})
    setTextos({})
    setAviso(null)
  }

  async function salvar() {
    if (!confirm('Isso cria a versão nova e passa a valer para todos. Continuar?')) return
    setSalvando(true)
    try {
      const v = await api.post<Versao>('/api/versoes/pesos', { pesos: mudancas })
      setPesos({})
      setTextos({})
      setAviso(`Pesos salvos na versão nº ${v.numero}, que agora está em uso.`)
      pedido.current++
      setDados(await api.post<Simulacao>(`/api/painel/simular-pesos?${query.toString()}`, { pesos: {} }))
    } catch (e) {
      setErro(e instanceof ErroApi ? e.message : 'Não foi possível salvar os pesos.')
    } finally {
      setSalvando(false)
    }
  }

  const qtd = Object.keys(mudancas).length
  return (
    <div className="pagina simulador" style={{ ['--cor-pagina' as string]: COR.metas }}>
      <header className="pagina-cabecalho">
        <div>
          <h1>Simulador de pesos</h1>
          <p>Mude o peso das metas e veja como os índices mudariam. Peso 0 tira a meta do cálculo.</p>
        </div>
      </header>

      <p className="faixa-simulacao" role="note">Simulação — não altera os números oficiais</p>

      {dados && (
        <div className="comparacoes">
          {(['geral', ...PILARES] as const).map((k) => (
            <Comparacao key={k} chave={k} oficial={dados.oficial[k]} simulado={dados.simulado[k]} />
          ))}
        </div>
      )}

      {erro && (
        <p className="erro" role="alert">
          {erro}
        </p>
      )}
      {aviso && <p className="bloco sucesso" role="status">{aviso}</p>}

      <div className="simulador-acoes">
        <span className="suave">{qtd === 0 ? 'Nenhum peso alterado.' : `${qtd} peso(s) alterado(s).`}</span>
        <button type="button" className="botao secundario" onClick={restaurar} disabled={qtd === 0 && !Object.keys(textos).length}>
          Restaurar pesos oficiais
        </button>
        {usuario?.perfil === 'admin' && (
          <button type="button" className="botao" onClick={salvar} disabled={qtd === 0 || salvando || !!erro}>
            {salvando ? 'Salvando…' : 'Salvar como nova versão'}
          </button>
        )}
      </div>

      {dados &&
        PILARES.map((pilar) => (
          <section key={pilar} className="tabela">
            <h3>Pilar {pilar}</h3>
            <div className="tabela-rolagem">
              <table>
                <thead>
                  <tr>
                    <th>Meta</th>
                    <th className="num">Atingimento</th>
                    <th>Status</th>
                    <th className="num">Peso oficial</th>
                    <th className="num">Peso simulado</th>
                  </tr>
                </thead>
                <tbody>
                  {dados.metas
                    .filter((m) => m.pilar === pilar)
                    .map((m) => {
                      const texto = textos[m.id_meta] ?? String(pesos[m.id_meta] ?? m.peso_oficial)
                      const invalido = pesoValido(texto) === null
                      const alterada = m.id_meta in mudancas
                      return (
                        <tr key={m.id_meta} className={alterada ? 'linha-alterada' : undefined}>
                          <td>{m.indicador}</td>
                          <td className="num">{m.atingimento === null ? '—' : m.atingimento.toFixed(2).replace('.', ',')}</td>
                          <td>{m.status ? <span className={`selo selo-${corDoStatus(m.status)}`}>{m.status}</span> : '—'}</td>
                          <td className="num">{m.peso_oficial}</td>
                          <td className="num">
                            <input
                              type="number"
                              min={0}
                              max={PESO_MAXIMO}
                              step={1}
                              inputMode="numeric"
                              className={`peso-campo ${invalido ? 'invalido' : ''}`}
                              aria-label={`Peso simulado de ${m.indicador}`}
                              aria-invalid={invalido}
                              value={texto}
                              onChange={(e) => mudar(m, e.target.value)}
                            />
                          </td>
                        </tr>
                      )
                    })}
                </tbody>
              </table>
            </div>
          </section>
        ))}
    </div>
  )
}
