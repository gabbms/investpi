// Regras do simulador de pesos (a tela fica em pages/Simulador.tsx).
export const PESO_MAXIMO = 5

export interface Indices {
  geral: number | null
  Ambiental: number | null
  Social: number | null
  Governança: number | null
}

export interface MetaSimulada {
  id_meta: string
  pilar: 'Ambiental' | 'Social' | 'Governança'
  indicador: string
  atingimento: number | null
  status: string | null
  peso_oficial: number
  peso: number
}

export interface Simulacao {
  oficial: Indices
  simulado: Indices
  metas: MetaSimulada[]
}

/** Peso digitado → inteiro de 0 a 5, ou null se não vale. */
export function pesoValido(texto: string): number | null {
  if (!/^\d+$/.test(texto.trim())) return null
  const n = Number(texto)
  return n >= 0 && n <= PESO_MAXIMO ? n : null
}

/** Só os pesos diferentes dos oficiais (é o que vai para o servidor). */
export function alterados(oficial: Record<string, number>, atual: Record<string, number>): Record<string, number> {
  return Object.fromEntries(Object.entries(atual).filter(([id, p]) => oficial[id] !== p))
}

/** Algum campo digitado fora de 0–5 (ou vazio)? Enquanto houver, salvar fica travado. */
export function temInvalido(textos: Record<string, string>): boolean {
  return Object.values(textos).some((t) => pesoValido(t) === null)
}

/** Faixa do índice, igual à do painel: verde ≥ 75, amarelo ≥ 50, vermelho abaixo. */
export function corDoIndice(v: number | null): 'verde' | 'amarelo' | 'vermelho' | 'neutro' {
  if (v === null) return 'neutro'
  return v >= 75 ? 'verde' : v >= 50 ? 'amarelo' : 'vermelho'
}
