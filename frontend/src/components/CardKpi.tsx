import { useId } from 'react'
import type { Card, Semaforo } from '../api'
import { valor } from '../format'

export const TEXTO_STATUS: Record<Semaforo, string> = {
  verde: 'Meta atingida',
  amarelo: 'Em atenção',
  vermelho: 'Abaixo da meta',
}

export function Ajuda({ texto }: { texto: string | null }) {
  const id = useId()
  if (!texto) return null
  return (
    <span className="ajuda">
      <button type="button" className="ajuda-botao" aria-describedby={id} aria-label="O que é este indicador?">
        ?
      </button>
      <span role="tooltip" id={id} className="ajuda-texto">
        {texto}
      </span>
    </span>
  )
}

export function CardKpi({ card }: { card: Card }) {
  return (
    <article className={`card-kpi ${card.status ? `status-${card.status}` : ''}`}>
      <header className="card-kpi-topo">
        <h3>{card.titulo}</h3>
        <Ajuda texto={card.ajuda} />
      </header>
      <p className="card-kpi-valor">{valor(card.valor, card.formato)}</p>
      {card.status && (
        <p className="card-kpi-status">
          <span className="ponto" aria-hidden="true" />
          {TEXTO_STATUS[card.status]}
        </p>
      )}
    </article>
  )
}
