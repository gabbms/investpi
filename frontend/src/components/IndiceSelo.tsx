import type { Card } from '../api'
import { valor } from '../format'
import { Ajuda } from './CardKpi'

const FAIXA = {
  verde: 'Faixa verde (75 ou mais)',
  amarelo: 'Faixa amarela (50 a 74)',
  vermelho: 'Faixa vermelha (abaixo de 50)',
}

/** O índice do pilar em destaque, com a régua de 0 a 100 e as faixas do semáforo. */
export function IndiceSelo({ card }: { card: Card }) {
  const v = card.valor
  const pos = v === null ? null : Math.max(0, Math.min(100, v))
  return (
    <section className={`indice ${card.status ? `status-${card.status}` : 'status-vazio'}`} aria-label={card.titulo}>
      <div className="indice-topo">
        <h2>{card.titulo}</h2>
        <Ajuda texto={card.ajuda} />
      </div>
      <p className="indice-valor">
        {valor(v, 'idx')}
        <span className="indice-escala"> de 100</span>
      </p>
      <div className="regua" aria-hidden="true">
        <span className="regua-faixa faixa-vermelha" style={{ width: '50%' }} />
        <span className="regua-faixa faixa-amarela" style={{ width: '25%' }} />
        <span className="regua-faixa faixa-verde" style={{ width: '25%' }} />
        {pos !== null && <span className="regua-marca" style={{ left: `${pos}%` }} />}
      </div>
      <div className="regua-rotulos" aria-hidden="true">
        <span>0</span>
        <span style={{ left: '50%' }}>50</span>
        <span style={{ left: '75%' }}>75</span>
        <span style={{ left: '100%' }}>100</span>
      </div>
      <p className="indice-faixa">{card.status ? FAIXA[card.status] : 'Sem metas com valor neste filtro'}</p>
    </section>
  )
}
