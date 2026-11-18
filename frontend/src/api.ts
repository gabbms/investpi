// Cliente HTTP da API. Anexa o token de login e volta ao login se a sessão acabar (401).
import type { Formato } from './format'

export type Semaforo = 'verde' | 'amarelo' | 'vermelho'

export interface Usuario {
  id: number
  email: string
  nome: string
  perfil: 'admin' | 'leitor'
}
export interface UsuarioAdmin extends Usuario {
  ativo: boolean
  criado_em: string
}
export interface Card {
  id: string
  titulo: string
  valor: number | null
  formato: Formato
  status: Semaforo | null
  ajuda: string | null
}
export interface Serie {
  nome: string
  valores: (number | null)[]
  cor: string | null
}
export interface Grafico {
  id: string
  titulo: string
  tipo: 'barra_h' | 'barra_h_empilhada' | 'colunas' | 'rosca'
  categorias: string[]
  series: Serie[]
  formato: Formato
  cores_categorias: (string | null)[] | null
  largura: 'terco' | 'metade' | 'inteira'
}
export interface Coluna {
  chave: string
  rotulo: string
  formato: 'texto' | 'brl' | 'num' | 'pct' | 'dec' | 'status' | 'simnao'
}
export interface Tabela {
  id: string
  titulo: string
  colunas: Coluna[]
  linhas: Record<string, unknown>[]
}
export interface Pagina {
  titulo: string
  subtitulo: string | null
  indice: Card | null
  cards: Card[]
  graficos: Grafico[]
  tabelas: Tabela[]
}
export interface Opcoes {
  setores: string[]
  vps: string[]
  status: string[]
  municipios: string[]
}
export interface ErroEstrutura {
  aba: string | null
  linha: number | null
  coluna: string | null
  mensagem: string
}
export interface Checagem {
  id: string
  checagem: string
  tabela: string
  regra: string
  problemas: number
}
export interface Previa {
  linhas_por_aba: Record<string, number>
  erros: ErroEstrutura[]
  checagens: Checagem[]
  pode_confirmar: boolean
}
export interface Versao {
  id: number
  numero: number
  criado_em: string
  enviado_por: string | null
  nome_arquivo: string
  status: 'ativa' | 'inativa' | 'rejeitada'
  linhas_por_aba: Record<string, number>
  avisos: Checagem[]
  erros: ErroEstrutura[]
}

const CHAVE_TOKEN = 'asg_token'

export const token = {
  ler: () => localStorage.getItem(CHAVE_TOKEN),
  gravar: (t: string) => localStorage.setItem(CHAVE_TOKEN, t),
  apagar: () => localStorage.removeItem(CHAVE_TOKEN),
}

export class ErroApi extends Error {
  status: number
  detalhe: unknown
  constructor(status: number, detalhe: unknown) {
    super(typeof detalhe === 'string' ? detalhe : `Erro ${status}`)
    this.status = status
    this.detalhe = detalhe
  }
}

// Chamado quando a API responde 401 (token ausente, inválido ou expirado).
let aoExpirar: () => void = () => {
  if (location.pathname !== '/login') location.assign('/login')
}
export function quandoSessaoExpirar(fn: () => void) {
  aoExpirar = fn
}

async function requisitar<T>(caminho: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers)
  const t = token.ler()
  if (t) headers.set('Authorization', `Bearer ${t}`)
  const r = await fetch(caminho, { ...init, headers })
  if (r.status === 401 && caminho !== '/api/auth/login') {
    sessionStorage.setItem('asg_expirou', '1')
    token.apagar()
    aoExpirar()
    throw new ErroApi(401, 'Sessão expirada. Entre novamente.')
  }
  if (!r.ok) {
    let detalhe: unknown = `Erro ${r.status}`
    try {
      detalhe = (await r.json()).detail ?? detalhe
    } catch {
      /* resposta sem JSON */
    }
    throw new ErroApi(r.status, detalhe)
  }
  const tipo = r.headers.get('content-type') ?? ''
  if (tipo.includes('application/json')) return (await r.json()) as T
  return (await r.blob()) as T
}

export const api = {
  get<T>(caminho: string, params?: URLSearchParams) {
    const q = params?.toString()
    return requisitar<T>(q ? `${caminho}?${q}` : caminho)
  },
  post<T>(caminho: string, corpo?: unknown) {
    return requisitar<T>(caminho, {
      method: 'POST',
      headers: corpo === undefined ? {} : { 'Content-Type': 'application/json' },
      body: corpo === undefined ? undefined : JSON.stringify(corpo),
    })
  },
  patch<T>(caminho: string, corpo: unknown) {
    return requisitar<T>(caminho, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(corpo),
    })
  },
  upload<T>(caminho: string, arquivo: File) {
    const dados = new FormData()
    dados.append('arquivo', arquivo)
    return requisitar<T>(caminho, { method: 'POST', body: dados })
  },
  async baixar(caminho: string, nome: string) {
    const blob = await requisitar<Blob>(caminho)
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = nome
    a.click()
    URL.revokeObjectURL(url)
  },
}
