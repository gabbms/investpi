import { PaginaPainel } from '../components/PaginaPainel'
import { COR } from '../menu'

export function VisaoGeral() {
  return <PaginaPainel endpoint="/api/painel/visao-geral" cor={COR.geral} />
}
