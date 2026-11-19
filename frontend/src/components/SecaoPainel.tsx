import type { Secao } from '../api'
import { CardKpi } from './CardKpi'

/** Bloco da tela com título, descrição, selo opcional e cards; as subseções vêm dentro dele. */
export function SecaoPainel({ secao }: { secao: Secao }) {
  return (
    <section className="secao-painel" aria-labelledby={`secao-${secao.id}`}>
      <div className="secao-painel-topo">
        <h2 id={`secao-${secao.id}`}>{secao.titulo}</h2>
        {secao.selo && <span className="selo selo-amarelo">{secao.selo}</span>}
      </div>
      {secao.descricao && <p className="secao-painel-descricao">{secao.descricao}</p>}
      {secao.cards.length > 0 && (
        <div className="cards">
          {secao.cards.map((c) => (
            <CardKpi key={c.id} card={c} />
          ))}
        </div>
      )}
      {secao.subsecoes.map((sub) => (
        <div key={sub.id} className="subsecao-painel">
          <h3>{sub.titulo}</h3>
          <div className="cards">
            {sub.cards.map((c) => (
              <CardKpi key={c.id} card={c} />
            ))}
          </div>
        </div>
      ))}
    </section>
  )
}
