import type { Ocorrencia } from '../api'
import { textoOcorrencia } from '../format'

export function ListaOcorrencias({ ocorrencias, mais }: { ocorrencias: Ocorrencia[]; mais?: number }) {
  return (
    <ul className="ocorrencias">
      {ocorrencias.map((o, i) => (
        <li key={i}>
          <strong>{textoOcorrencia(o)}</strong>
          {o.detalhe && <> {o.detalhe}</>}
        </li>
      ))}
      {!!mais && mais > 0 && <li className="suave">e mais {mais}</li>}
    </ul>
  )
}

export function BotaoAbrir({ aberto, aoAlternar, rotulo }: { aberto: boolean; aoAlternar: () => void; rotulo: string }) {
  return (
    <button
      type="button"
      className="alternar"
      aria-expanded={aberto}
      aria-label={`${aberto ? 'Esconder' : 'Mostrar'} os registros de ${rotulo}`}
      onClick={aoAlternar}
    >
      {aberto ? '▾' : '▸'}
    </button>
  )
}
