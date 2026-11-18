import { useEffect, useId, useRef, useState } from 'react'

interface Props {
  rotulo: string
  opcoes: string[]
  selecionados: string[]
  aoMudar: (valores: string[]) => void
}

/** Lista suspensa com caixas de seleção, para escolher vários valores de um filtro. */
export function MultiSelect({ rotulo, opcoes, selecionados, aoMudar }: Props) {
  const [aberto, setAberto] = useState(false)
  const raiz = useRef<HTMLDivElement>(null)
  const id = useId()

  useEffect(() => {
    if (!aberto) return
    const fechar = (e: MouseEvent | KeyboardEvent) => {
      if (e instanceof KeyboardEvent ? e.key === 'Escape' : !raiz.current?.contains(e.target as Node)) {
        setAberto(false)
      }
    }
    document.addEventListener('mousedown', fechar)
    document.addEventListener('keydown', fechar)
    return () => {
      document.removeEventListener('mousedown', fechar)
      document.removeEventListener('keydown', fechar)
    }
  }, [aberto])

  const resumo =
    selecionados.length === 0 ? 'Todos' : selecionados.length === 1 ? selecionados[0] : `${selecionados.length} selecionados`

  const alternar = (v: string) =>
    aoMudar(selecionados.includes(v) ? selecionados.filter((x) => x !== v) : [...selecionados, v])

  return (
    <div className="multi" ref={raiz}>
      <span className="multi-rotulo" id={`${id}-r`}>
        {rotulo}
      </span>
      <button
        type="button"
        className={`multi-botao ${selecionados.length ? 'ativo' : ''}`}
        aria-haspopup="listbox"
        aria-expanded={aberto}
        aria-labelledby={`${id}-r`}
        onClick={() => setAberto((a) => !a)}
      >
        <span className="multi-resumo">{resumo}</span>
        <span aria-hidden="true" className="multi-seta">▾</span>
      </button>
      {aberto && (
        <div className="multi-lista" role="listbox" aria-multiselectable="true" aria-labelledby={`${id}-r`}>
          {opcoes.map((o) => (
            <label key={o} className="multi-opcao">
              <input type="checkbox" checked={selecionados.includes(o)} onChange={() => alternar(o)} />
              <span>{o}</span>
            </label>
          ))}
          {selecionados.length > 0 && (
            <button type="button" className="multi-limpar" onClick={() => aoMudar([])}>
              Limpar {rotulo.toLowerCase()}
            </button>
          )}
        </div>
      )}
    </div>
  )
}
